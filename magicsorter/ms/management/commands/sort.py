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
#from PIL import Image    

OUTBOX_NUM = 0
THUMB_RATIO = 0.5
THUMB_RATIO2 = 0.2

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
    
SCAN = 0

def mouseclick(event,x,y,flags,param):
        #if event == cv2.EVENT_LBUTTONDBLCLK:
        global SCAN
        if event == cv2.EVENT_LBUTTONDOWN:
            SCAN = 1
        if event == cv2.EVENT_RBUTTONDOWN:
            SCAN = -1   
            
class Command(BaseCommand):

    help = 'Does some magical work'
    global SCAN

    
    def handle(self, *args, **options):
        """ Do your work here """
        global SCAN
        
        #Card.objects.all().delete()
        #cards = Card.objects.order_by('pk')
        #for card in cards:
        #    card.count = 0
        #    card.outbox = 0
        #    card.save()
        Card.objects.all().update(count=0, outbox=0)
        
        #card = Card.objects.create()
        #card.save()
        
        order = 0       
        Scan.objects.all().delete()
        
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
         if k == 27 or SCAN== 1:
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
            SCAN = 0
                #if event == cv2.EVENT_LBUTTONDOWN:
                #    refPt = [(x, y)]
                #    cropping = True
            #TODO for each card in stock
            order = order + 1
        
        
        
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
                    
                    
                    text = 'match: ' + str(card.id)
                    print text
                    break
        
            #print card_id
            if card_id == 0:
                   
                
                card = Card.objects.create()
                
                img1 = cv2.resize(img, (0,0), fx=THUMB_RATIO2, fy=THUMB_RATIO2)
                img2 = None
                
                
                text = 'new: ' + str(card.id)
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
                
            scan = Scan.objects.create(order=order, fk_card=card)
            
            scan.outbox = card.outbox
                
            tmpfilename = '..jpg'   
            img = cv2.resize(img, (0,0), fx=THUMB_RATIO, fy=THUMB_RATIO)   
            cv2.imwrite(tmpfilename, img)
            f = open(tmpfilename, 'rb')
            content = File(f)
            scan.image.save(str(card.id) + '-'+ str(order) + '.jpg', content)
            content.close()
            f.close()
            
            if scan.outbox < OUTBOX_NUM:
                scan.order = 0
                
                #put card to outbox
            
            scan.save()

            
        
        cap.release()
        cv2.destroyAllWindows()      
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