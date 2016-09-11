from django.core.management.base import BaseCommand, CommandError
import cv2

class Command(BaseCommand):

    help = 'magic sorter'
     
    def handle(self, *args, **options):

 
        video_device = 0
        print('Handle: Capturing from device %i' % video_device) 
        cam = cv2.VideoCapture(video_device)
        print('Handle: Capturing from device %i done' % video_device) 

        mirror = False

        while True:
            ret_val, img = cam.read()
            if mirror: 
                img = cv2.flip(img, 1)
            cv2.imshow('my webcam', img)
            if cv2.waitKey(1) == 27: 
                break  # esc to quit
        cv2.destroyAllWindows()
        
        return
