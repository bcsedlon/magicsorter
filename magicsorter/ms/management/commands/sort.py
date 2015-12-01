from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import File

from ms.models import Card, Scan

import cv2

import numpy as np
from matplotlib import pyplot as plt
import pickle
import sys

from StringIO import StringIO

import tesseract

import copy
from ms.management.commands.modbus import ModbusServer
#from PIL import Image    

THUMB_RATIO = 0.5
THUMB_RATIO2 = 0.2

import threading
import modbus
import time

import ConfigParser


def t():
        mImgFile = '2a.jpg'
        
        import os
        DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'commands/')
        os.putenv('TESSDATA_PREFIX', DIR)
 
        api = tesseract.TessBaseAPI()
        api.Init('.','eng', tesseract.OEM_DEFAULT)
        api.SetVariable('tessedit_char_whitelist', '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        #api.SetPageSegMode(tesseract.PSM_AUTO)
        
        mBuffer=open(mImgFile,'rb').read()
        result = tesseract.ProcessPagesBuffer(mBuffer,len(mBuffer),api)
        print result
        api.End()
        return
        
        
        print 'ocr'
        mImgFile = '2a.jpg'
        img = cv2.imread(mImgFile, 0)
        
        api = tesseract.TessBaseAPI()
        api.SetOutputName('outputName');
        api.Init('.', 'eng', tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_AUTO)
        
        print 'ocr2'
        #mage=cv2.LoadImage(mImgFile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        tesseract.SetCvImage(img, api)
        #pixImage=tesseract.pixRead(mImgFile)
        #api.SetImage(pixImage)
        print 'ocr3'
        text=api.GetUTF8Text()
        conf=api.MeanTextConf()
        
        print text
        api.End()
        
        #outText=api.GetUTF8Text()
        #print("OCR output:\n%s"%outText);
        #api.End()
        #print pytesseract.image_to_string(im)
        #print(pytesseract.image_to_string(Image.open(filename), lang='eng'))
        return


class Sorter():
    
    outbox_num = 1
    
    RUN = True
    thr = None
    
    @staticmethod 
    def init(outbox_num):
        Sorter.outbox_num = outbox_num
    
    @staticmethod 
    def sort():
    
        sortingout = []
    
        while Sorter.RUN:
            print 'Sorter: go to take card'
            modbus.Scanner.outServo.value = 0
            time.sleep(1)
            #while modbus.Scanner.inServo.value != 0:
            #    pass
    
            print 'Sorter: go to scan position'
            modbus.Scanner.outServo.value = 100
            time.sleep(1)
            #while modbus.Scanner.inServo.value != 100:
            #    pass
    
            print 'Sorter: scan card'
            scan = Scanner.scan()
        
            if len(sortingout) <  Sorter.outbox_num - 1 and not scan.fk_card_id in sortingout:
                sortingout.append(scan.fk_card_id)
            #print sortingout
        
            if scan.fk_card_id in sortingout :
                outbox = sortingout.index(scan.fk_card_id) + 1
                scan.position = 0
                scan.save()
            else:
                outbox = 0 
        
            print 'Sorter: set out box {} for card_id {}'.format(outbox, scan.fk_card_id)
            modbus.Scanner.outFeeder.value = outbox
            time.sleep(1)
            #while modbus.Scanner.inFeeder.value != OUTBOX:
            #    pass
        
            print 'Sorter: go to release card'
            modbus.Scanner.outServo.value = 120
            time.sleep(1)
            #while modbus.Scanner.inServo.value != 120:
            #    pass
        

    @staticmethod    
    def start():
        Sorter.RUN = TRUE
        Sorter.thr = threading.Thread(target= Sorter.sorter, args=(), kwargs={})
        Sorter.thr.start()

    @staticmethod    
    def stop():
        Sorter.RUN = False
        if Sorter.thr:
            Sorter.thr.join()

    #second round, no scan, only sort out
    @staticmethod 
    def sort2():
    
        sortingout = []
    
        for s in Scan.objects.raw('SELECT id, fk_card_id, outbox, SUM(1) AS cnt FROM ms_scan WHERE position>0 GROUP BY fk_card_id ORDER BY cnt DESC'):
            if len(sortingout) >=  Sorter.outbox_num - 1:
                break
        
            sortingout.append(s.fk_card_id)
            print 'Sorter2: card_id {} count {} out box {}'.format(s.fk_card_id, s.cnt, len(sortingout)) 
                     
        #print sortingout 
        scans = Scan.objects.filter(position__gt=0).order_by('position')
     
        for scan in scans:
            
            if scan.fk_card_id in sortingout :
                outbox = sortingout.index(scan.fk_card_id) + 1
                scan.position = 0
                scan.save()
            else:
                outbox = 0 
            print 'Sorter2: set out box {} for card_id {}'.format(outbox, scan.fk_card_id)
            modbus.Scanner.outFeeder.value = outbox
            
            print 'Sorter2: go to take card'
            modbus.Scanner.outServo.value = 0
            time.sleep(1)
            #while modbus.Scanner.inServo.value != 0:
            #    pass
    
            
            
            #if scan.fk_card_id in sortingout :
            #    outbox = sortingout.index(scan.fk_card_id) + 1
            #    scan.position = 0
            #    scan.save()
            #else:
            #    outbox = 0 
            #print 'Sorter2: set out box {} for card_id {}'.format(outbox, scan.fk_card_id)
            #modbus.Scanner.outFeeder.value = outbox
            #time.sleep(1)
            #while modbus.Scanner.inFeeder.value != OUTBOX:
            #    pass
        
            print 'Sorter2: go to release card'
            modbus.Scanner.outServo.value = 120
            time.sleep(1) 

class Scanner():
    
    position = 0
    outbox = 0
    
    text = None
    
    img = None
    img1 = None
    img2 = None
    
    RUN = True
    thr = None
    
    @staticmethod 
    def run():
        cap = cv2.VideoCapture(1)
        ret = cap.set(3, 1280)#320) 
        ret = cap.set(4, 720)#240)
        
        ret, frame = cap.read()
        #Scanner.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        Scanner.img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        title = 'esc for quit'
        cv2.namedWindow(title)
        cv2.setMouseCallback(title, mouseclick)
        
        Scanner.img1 = None
        
        while Scanner.RUN:  
            ret, frame = cap.read()
            Scanner.img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            img0 = copy.copy(Scanner.img)
         
            if Scanner.img1 is not None:
                height, width = Scanner.img1.shape 
                img0[0:height, 0:width] = Scanner.img1
             
                if Scanner.img2 is not None:
                    img0[height:height*2, 0:width]=Scanner.img2
         
            #cv2.putText(img0 , Scanner.text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            cv2.imshow(title, img0)
            
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                Scanner.RUN = False
                Sorter.RUN = False
                #Sorter.stop()
                
            #    break
            
            #print k
            #if k == 113 or SCAN== -1:
                # q
            #    break
        cap.release()
        cv2.destroyAllWindows()  

    @staticmethod    
    def start():
        Scanner.RUN = True
        Scanner.thr = threading.Thread(target= Scanner.run, args=(), kwargs={})
        Scanner.thr.start()

    @staticmethod    
    def stop():
        Scanner.RUN = False
        if Scanner.thr:
            Scanner.thr.join()
    
    
    @staticmethod    
    def scan():
        #OUTBOX = 0
        #SCAN = 0
    
        Scanner.position = Scanner.position + 1
                
        img_hist = cv2.calcHist([Scanner.img],[0],None,[256],[0,256])
        
        card_id = 0
        cards = Card.objects.order_by('pk')
    
        for card in cards:
            template = cv2.imread(card.image.name, 1)
            
            if card.hist:
                tempalte_hist = pickle.loads(card.hist)
            else:
                tempalte_hist = cv2.calcHist([template],[0],None,[256],[0,256])
                card.hist = pickle.dumps(tempalte_hist)
                card.save()
            
            #TODO compare images
            #method = eval('CV_COMP_CORREL')
            result = cv2.compareHist(img_hist, tempalte_hist, 0)
            #print result
        
            if result > 0.99:
                card_id = card.id
                card.count = card.count + 1
                card.save()
                    
                Scanner.img1 = cv2.imread(card.image.path, 0)
                Scanner.img1 = cv2.resize(Scanner.img1, (0,0), fx=THUMB_RATIO2, fy=THUMB_RATIO2)   
                Scanner.img2 = cv2.resize(Scanner.img, (0,0), fx=THUMB_RATIO2, fy=THUMB_RATIO2)   
                    
                Scanner.text = 'Scanner: match ' + str(card.id)
                print Scanner.text
                break
        
        #print card_id
        if card_id == 0:
            card = Card.objects.create()
                
            Scanner.img1 = cv2.resize(Scanner.img, (0,0), fx=THUMB_RATIO2, fy=THUMB_RATIO2)
            Scanner.img2 = None
                
            Scanner.text = 'Scanner: new ' + str(card.id)
            print Scanner.text
                
            card.count = 1
            Scanner.outbox = Scanner.outbox + 1
            card.outbox = Scanner.outbox
            
            card_id = card.id
            card.hist = pickle.dumps(img_hist)
                        
            tmpfilename = '..jpg'             
            cv2.imwrite(tmpfilename, Scanner.img)
            f = open(tmpfilename, 'rb')
            content = File(f)
            card.image.save(str(card.id) + '.jpg', content)#, save=True)
        
            img = cv2.resize(Scanner.img, (0,0), fx=THUMB_RATIO, fy=THUMB_RATIO)   
            cv2.imwrite(tmpfilename, img)
            f = open(tmpfilename, 'rb')
            content = File(f)
            card.thumb.save(str(card.id) + '.jpg', content)
            
            card.save()
            content.close()
            f.close()
            
        scan = Scan.objects.create(position=Scanner.position, fk_card=card)
        scan.outbox = card.outbox
                
        tmpfilename = '..jpg'   
        img = cv2.resize(Scanner.img, (0,0), fx=THUMB_RATIO, fy=THUMB_RATIO)   
        cv2.imwrite(tmpfilename, img)
        f = open(tmpfilename, 'rb')
        content = File(f)
        scan.image.save(str(card.id) + '-'+ str(Scanner.position) + '.jpg', content)
        content.close()
        f.close()
            
        #print '{} / {}'.format(scan.outbox, OUTBOX_NUM)
        #if scan.outbox < OUTBOX_NUM:
        #    scan.position = 0
        #        
        #    OUTBOX = scan.outbox + 1
        #else:
            #1st outbox for notsorted cards
        #    OUTBOX = 1
        #OUTBOX = scan.outbox + 1
        
        scan.save()
        return scan
     

def mouseclick(event,x,y,flags,param):
        #if event == cv2.EVENT_LBUTTONDBLCLK:
        global SCAN
        if event == cv2.EVENT_LBUTTONDOWN:
            SCAN = 1
        if event == cv2.EVENT_RBUTTONDOWN:
            SCAN = -1   
            
class Command(BaseCommand):

    help = 'magic sorter'
     
    def handle(self, *args, **options):

        Config = ConfigParser.ConfigParser()
        try:
            Config.read('magicsorter.ini')
            port = Config.get('modbus', 'port')
            outbox_num = int(Config.get('sorter', 'outbox_num'))
        except:
            cfgfile = open('magicsorter.ini','w+')
            # add the settings to the structure of the file, and lets write it out...
            Config.add_section('modbus')
            Config.set('modbus','port','COM1')
            Config.add_section('sorter')
            Config.set('sorter','outbox_num','1')
            
            Config.write(cfgfile)
            cfgfile.close()
            print 'Please check magicsorter.ini and try again!'
            return
                
        #ModbusServer.startServer()
        modbus.ModbusServer.init(port)
        modbus.ModbusServer.startServerAsync()
        
        Sorter.init(outbox_num)
        
        if Scan.objects.filter(position__gt=0):
            Sorter.sort2()
        else:
            #Card.objects.all().delete()
            Card.objects.all().update(count=0, outbox=0)
            
            Scan.objects.all().delete()
        
            Scanner.start()  
            #Sorter.start()
            Sorter.sort()
        
            #while Scanner.RUN:
            #    pass
        
            #Sorter.stop()
            #Scanner.stop()
        
        modbus.ModbusServer.stopServer()
        
        return
    
############################################################################     
        
        #thr = threading.Thread(target= sorter, args=(), kwargs={})
        #thr.start()
        
        
        
        
        
        
        position = 0
        outbox = 0
                
        cap = cv2.VideoCapture(1)
        ret = cap.set(3, 1280)#320) 
        ret = cap.set(4, 720)#240)
        
        ret, frame = cap.read()
        #img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        title = 'esc for scan, q for quit'
        cv2.namedWindow(title)
        #cv2.imshow("image", img)
        cv2.setMouseCallback(title, mouseclick)
        
        text = ''
        img1 = None
        
        while True:  
         ret, frame = cap.read()
         img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         
         
         #print img1
         
         img0 = copy.copy(img)
         
         if img1 is not None:
             height, width = img1.shape 
             img0[0:height, 0:width]=img1
             
             if img2 is not None:
                img0[height:height*2, 0:width]=img2
         #cv2.putText(img0 , text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
         cv2.imshow(title, img0)
         k = cv2.waitKey(20) & 0xFF
         #print k
         if k == 113 or SCAN== -1:
             # q
             break
         
         
         
         if k == 27 or SCAN == 1:
             
             
             # esc
           
            #inp = raw_input('Press Enter for next, q for quit: ')
            #if inp == 'q':
             #   break;
            #print 'vfrv'
            #while SCAN == 0:
            #    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #    cv2.imshow("image", img)
            #    if cv2.waitKey(20) & 0xFF == 27:
            #        break
            #    pass
            #print 'pass'
            OUTBOX = 0
            SCAN = 0
                #if event == cv2.EVENT_LBUTTONDOWN:
                #    refPt = [(x, y)]
                #    cropping = True
            #TODO for each card in stock
            position = position + 1
        
        
        
            #get image
            #filename = '1.jpg'
            #img = cv2.imread(filename, 1)

            
        
            #ret, frame = cap.read()
            #img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #cv2.imshow("image", img)
            
            img_hist = cv2.calcHist([img],[0],None,[256],[0,256])
        
        
        
    
            #match template
            card_id = 0
            cards = Card.objects.order_by('pk')
            #if False:
            for card in cards:
                template = cv2.imread(card.image.name, 1)
            
                #TODO get histogram from from model
                if card.hist:
                    tempalte_hist = pickle.loads(card.hist)
                else:
                    tempalte_hist = cv2.calcHist([template],[0],None,[256],[0,256])
                    card.hist = pickle.dumps(tempalte_hist)
                    card.save()
            
                #TODO compare images
                #method = eval('CV_COMP_CORREL')
                result = cv2.compareHist(img_hist, tempalte_hist, 0)
                #print result
                if result > 0.99:
                    card_id = card.id
                    card.count = card.count + 1
                    card.save()
                    
                    #print card.image.path
                    img1 = cv2.imread(card.image.path, 0)
                    img1 = cv2.resize(img1, (0,0), fx=THUMB_RATIO2, fy=THUMB_RATIO2)   
                    img2 = cv2.resize(img, (0,0), fx=THUMB_RATIO2, fy=THUMB_RATIO2)   
                    
                    
                    text = 'Scanner: match ' + str(card.id)
                    print text
                    break
        
            #print card_id
            if card_id == 0:
                   
                
                card = Card.objects.create()
                
                img1 = cv2.resize(img, (0,0), fx=THUMB_RATIO2, fy=THUMB_RATIO2)
                img2 = None
                
                
                text = 'Scanner: new ' + str(card.id)
                print text
                
                card.count = 1
                outbox = outbox + 1
                card.outbox = outbox
            
                card_id = card.id
                card.hist = pickle.dumps(img_hist)
                        
                tmpfilename = '..jpg'             
                cv2.imwrite(tmpfilename, img)
                f = open(tmpfilename, 'rb')
                content = File(f)
                card.image.save(str(card.id) + '.jpg', content)#, save=True)
                #card.image.save(str(card.id) + '.jpg', cv2.imwrite(img), save=True)
                
                img = cv2.resize(img, (0,0), fx=THUMB_RATIO, fy=THUMB_RATIO)   
                cv2.imwrite(tmpfilename, img)
                f = open(tmpfilename, 'rb')
                content = File(f)
                card.thumb.save(str(card.id) + '.jpg', content)
            
            
                card.save()
                content.close()
                f.close()
            
            
            
            #s = Scan.objects.raw('SELECT * FROM ms_scan WHERE fk_card_id=' + str(card_id) + ' LIMIT 1'):
            #if s:
            #    scanoutbox = s.outbox
            #else:
            #    outbox = outbox + 1
            #    scanoutbox = outbox  
                
                  
            # Data retrieval operation - no commit required
            #from django.db import connection, transaction
            #cursor = connection.cursor()
            #cursor.execute('SELECT * FROM ms_scan WHERE fk_card_id=1')# [self.baz])
            #row = cursor.fetchone()
            #print row
                
            scan = Scan.objects.create(position=position, fk_card=card)
            
            scan.outbox = card.outbox
                
            tmpfilename = '..jpg'   
            img = cv2.resize(img, (0,0), fx=THUMB_RATIO, fy=THUMB_RATIO)   
            cv2.imwrite(tmpfilename, img)
            f = open(tmpfilename, 'rb')
            content = File(f)
            scan.image.save(str(card.id) + '-'+ str(position) + '.jpg', content)
            content.close()
            f.close()
            
            #print '{} / {}'.format(scan.outbox, OUTBOX_NUM)
            if scan.outbox < OUTBOX_NUM:
                scan.position = 0
                
                OUTBOX = scan.outbox + 1
                #put card to outbox
            else:
                #1st outbox for notsorted cards
                OUTBOX = 1
                
            scan.save()

            OUTBOX = scan.outbox + 1
            
        
        cap.release()
        cv2.destroyAllWindows()    
        
       
        thr.join()
        modbus.ModbusServer.stopServer()
          
        return       
        
        hist = cv2.calcHist([img],[0],None,[256],[0,256])
        #print pickle.dumps(hist)
        
        hist = cv2.calcHist([template],[0],None,[256],[0,256])
        #print pickle.dumps(hist)
        

        
        
        plt.subplot(221)
        plt.hist(img.ravel(),256,[0,256]);
        #plt.imshow(img, cmap = 'CMRmap')
        plt.title('ImageH')
        plt.xticks([])
        plt.yticks([])
        
        plt.subplot(222)
        #plt.imshow(template, cmap = 'gray')
        plt.hist(template.ravel(),256,[0,256]);
        plt.title('TemplateH')
        plt.xticks([])
        plt.yticks([])
  
        plt.subplot(223)
        plt.imshow(img, cmap = 'CMRmap')
        plt.title('Image')
        plt.xticks([])
        plt.yticks([])  
        
        plt.subplot(224)
        plt.imshow(template, cmap = 'CMRmap')
        plt.title('Template')
        plt.xticks([])
        plt.yticks([])     
        
        #plt.suptitle(meth)

        plt.show()




if False:

 img = cv2.imread('2a.jpg',0)
 img2 = img.copy()

 template = cv2.imread('2.jpg',0)
 w, h = template.shape[::-1]



 # All the 6 methods for comparison in a list
 methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

 for meth in methods:
    img = img2.copy()
    method = eval(meth)

    # Apply template Matching
    res = cv2.matchTemplate(img, template, method)
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    cv2.rectangle(img,top_left, bottom_right, 64, 4)

    plt.subplot(121),plt.imshow(res,cmap = 'gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(img,cmap = 'gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle(meth)

    plt.show()