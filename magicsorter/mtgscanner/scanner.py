from __future__ import print_function

import numpy as np
import cv2
import math
import json
import sys
import phash
import operator
import signal
import base64

from debugger import MTG_Debugger
from mtgexception import MTGException
from transformer import MTG_Transformer

"""Scanner module

This module is responsible for handling user input and reading the data from
the camera to pass off to other modules.
"""

import os


class MTG_Scanner:
    """Attributes:
        running (bool): Is the scanning loop running
        frame (image): The active frame
        bApplyTransforms (bool): Should transforms be applied
        bVertFlip (bool): Should the frame be flipped vertically?
        threshold (int): Hamming distance threshold
        detected_card (image): The image of the proposed card
        detected_id (int): The MultiverseID of the proposed card
        previous_id (int): The MultiverseID of the last card entered
        blacklist (array): Array of MultiverseIDs to exclude from detection

        referencedb (MTG_Reference_DB): The reference database object
        storagedb (MTG_Storage_DB): The storage database object
        debugger (MTG_Debugger): The debugging object
        transformer (MTG_Transformer): The transformer object
        captureDevice (cv2.VideoCapture): The camera to capture from
    """
    ROOT_PATH = os.path.dirname(__file__)
    
    def __init__(self, source, referencedb, storagedb, debug):
        self.running = False
        self.frame = None
        self.bApplyTransforms = False
        self.bVertFlip = False
        self.threshold = 15
        self.detected_card = None
        self.detected_id = None
        self.previous_id = None
        self.blacklist = []

        self.referencedb = referencedb
        self.storagedb = storagedb
        self.debugger = MTG_Debugger(debug)
        self.transformer = MTG_Transformer(self.debugger)
        self.captureDevice = cv2.VideoCapture(source)

       
        '''
        def rotateImage(self, image, angle):
        image_center = tuple(np.array(image.shape)/2)
        image_center = (image_center[0], image_center[1])	
        #print(image_center)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        #print(rot_mat)
        #print(image.shape)
        shape = (image.shape[0], image.shape[1])
        shape = (375, 520)
        shape = (400, 600)
        #print(shape)
        result = cv2.warpAffine(image, rot_mat, shape,flags=cv2.INTER_LINEAR)
        return result
        '''

        self.bTakePic = True
        
    def run(self):
        """Main execution
        """
        
        
        self.running = True
        while(self.running):
            if (self.detected_card is None):
                #print('x')
                self.debugger.reset()
                
                #bTakePic = False
                #while (self.bTakePic):
                __, frameCam = self.captureDevice.read()
                    #bTakePic = False
                    #height, width, __ = frame2.shape
                    #cv2.rectangle(
                    #    frame,
                    #    (0, 0),
                    #    (width - 1, height - 1),
                    #    (255, 0, 0),
                    #    2)
                cv2.imshow('PreviewCam', frameCam)
                self.handleKey(cv2.waitKey(1) & 0xFF, frameCam)
                #print('x')
                if (self.bTakePic):
                    cv2.imwrite('frameCam.jpg', frameCam)
                    self.bTakePic = False
                    print('savepic')
                    #frame1 = frame
                    #__1 = __
                #frame = frame1
                #__ = __1
                #print('cam')
                frame = cv2.imread(
                            'frameCam.jpg',
                            cv2.IMREAD_UNCHANGED)
                #print(frame)
                #__, frame = self.captureDevice.read()
                
                #frame = cv2.flip(frame, 0)
                #frame = self.rotateImage(frame, 90)
                if (frame is None):
                    print('Error: No frame read from camera')
                    break

                if (self.bApplyTransforms):
                    #print('bApplyTransforms')
                    try:
                        frame = self.transformer.applyTransforms(frame)
                        #pass
                    except MTGException as msg:
                        self.bApplyTransforms = False
                else:
                    height, width, __ = frame.shape
                    cv2.rectangle(
                        frame,
                        (0, 0),
                        (width - 1, height - 1),
                        (255, 0, 0),
                        2)

                if (self.bVertFlip):
                    #print('bVertFlip')
                    height, width, __ = frame.shape
                    M = cv2.getRotationMatrix2D(
                        (width / 2, height / 2),
                        180,
                        1)
                    frame = cv2.warpAffine(frame, M, (width, height))

                self.frame = frame
                cv2.imshow('Preview', self.frame)
                self.debugger.display()
            else:
                cv2.imshow('Detected Card', self.detected_card)

            self.handleKey(cv2.waitKey(1) & 0xFF, frame)

        if (self.captureDevice is not None):
            self.captureDevice.release()

        cv2.destroyAllWindows()
        
    def test(self):
        frame = cv2.imread('frameCam.jpg', cv2.IMREAD_UNCHANGED)
        if (frame is None):
            print('Error: No frame read from camera')

            
        #print('1')
        #self.frame = self.transformer.applyTransforms(frame)
        #self.frame=frame
        self.frame = self.transformer.applyTransforms(frame)
        
        #print('2')
        self.detected_id = self.detectCard()
        #print('3')
        
        name, code, rarity = self.referencedb.get_card_info(self.detected_id)
        #print('4')
        print('Detected: ' + name + ' [' + code + ']')
        cv2.imwrite('frameDet.jpg', self.frame)
        
        s = self.referencedb.IMAGE_FILE % self.detected_id
        s = '%s/%s' % (self.ROOT_PATH, s)
        self.detected_card = cv2.imread(s, cv2.IMREAD_UNCHANGED)
                        
        return self.detected_id, name, code, self.frame,  self.detected_card, rarity
    

    def detectCard(self):
        """Detect the card from the active frame
        """

        # The phash python bindings operate on files, so we have to write our
        # current frame to a file to continue
        cv2.imwrite('frame.jpg', self.frame)

        # Use phash on our frame
        ihash = phash.dct_imagehash('frame.jpg')
        idigest = phash.image_digest('frame.jpg')
        #print('1a')
        candidates = {}
        hashes = self.referencedb.get_hashes()
        for MultiverseID in hashes:
            if (MultiverseID in self.blacklist):
                continue

            hamd = phash.hamming_distance(ihash, int(hashes[MultiverseID]))
            if (hamd <= self.threshold):
                candidates[MultiverseID] = hamd

        if (not len(candidates)):
            print('No matches found')
            return None

        finalists = []
        minV = min(candidates.values())
        for MultiverseID in candidates:
            if (candidates[MultiverseID] == minV):
                finalists.append(MultiverseID)

        #print('1b') 
       
        bestMatch = None
        correlations = {}
        for MultiverseID in finalists:

            
            hamd = candidates[MultiverseID]
            #print(self.ROOT_PATH % self.referencedb.IMAGE_FILE % MultiverseID)
            s = self.referencedb.IMAGE_FILE % MultiverseID
            s = '%s/%s' % (self.ROOT_PATH, s)
            #print(s)
            #digest = phash.image_digest(self.referencedb.IMAGE_FILE % MultiverseID)
            digest = phash.image_digest(s)
            
            corr = phash.cross_correlation(idigest, digest)
            if (bestMatch is None or corr > correlations[bestMatch]):
                bestMatch = MultiverseID
            correlations[MultiverseID] = corr
            
            name, code, rarity = self.referencedb.get_card_info(MultiverseID)
            print('Candidate: ' + name + ' [' + code + '] ' + str(corr))
        #print('1d')
        return bestMatch

    def handleKey(self, key, frame):
        if (self.detected_card is None):
            if (key == 8 or key == 27):
                #print('8 or 27')
                self.bApplyTransforms = not self.bApplyTransforms
            elif (key == ord('d')):
                #print('d')
                self.debugger.toggle()
            elif (key == 171):
                #print('171')
                self.detected_id = self.previous_id
                if (self.detected_id is not None):
                    self.detected_card = cv2.imread(
                        self.referencedb.IMAGE_FILE % self.detected_id,
                        cv2.IMREAD_UNCHANGED)
            elif (key == 10):
                #print('10')
                if (not self.bApplyTransforms):
                    self.bApplyTransforms = True
                else:
                    self.detected_id = self.detectCard()
                    if (self.detected_id is not None):
                        self.detected_card = cv2.imread(
                            self.referencedb.IMAGE_FILE % self.detected_id,
                            cv2.IMREAD_UNCHANGED)
            
            elif (key == ord('t')):
                self.bTakePic =  True
                print('t')
            
        else:
            if (key == ord('n')):
                #print('n')
                cv2.destroyWindow('Detected Card')
                self.blacklist.append(self.detected_id)
                self.detected_id = self.detectCard()
                if (self.detected_id is not None):
                    self.detected_card = cv2.imread(
                        self.referencedb.IMAGE_FILE % self.detected_id,
                        cv2.IMREAD_UNCHANGED)
            if (key == ord('p')):
                #print('p')
                self.blacklist = []
                for i in range(0, 4):
                    self.storagedb.add_card(self.detected_id, 0)
                name, code = self.referencedb.get_card_info(self.detected_id)
                print('Added 4x ' + name + '[' + code + ']...')
                self.previous_id = self.detected_id
                self.detected_card = None
                self.detected_id = None
                self.bApplyTransforms = False
                cv2.destroyWindow('Detected Card')
            if (key == 10 or key == ord('y')):
                #print('10 or y')
                self.blacklist = []
                self.storagedb.add_card(self.detected_id, 0)
                name, code = self.referencedb.get_card_info(self.detected_id)
                print('Added ' + name + '[' + code + ']...')
                self.previous_id = self.detected_id
                self.detected_card = None
                self.detected_id = None
                self.bApplyTransforms = False
                cv2.destroyWindow('Detected Card')
            if (key == ord('f')):
                #print('f')
                self.blacklist = []
                self.storagedb.add_card(self.detected_id, 1)
                name, code = self.referencedb.get_card_info(self.detected_id)
                print('Added foil ' + name + '[' + code + ']...')
                self.previous_id = self.detected_id
                self.detected_card = None
                self.detected_id = None
                self.bApplyTransforms = False
                cv2.destroyWindow('Detected Card')
            elif (key == 8 or key == 27):
                #print('8 or 27')
                self.blacklist = []
                self.detected_card = None
                self.detected_id = None
                self.bApplyTransforms = False
                cv2.destroyWindow('Detected Card')

        if (key == ord('q')):
            #print('q')
            self.running = False
