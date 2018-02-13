import time
import serial

class hw():
    
    port = None
    ser = None
    
    def open(self, port):
        self.port = port    
        try:    
            # configure the serial connections (the parameters differs on the device you are connecting to)
            self.ser = serial.Serial(
            port=port, #'/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff = False,
            rtscts = False, 
            dsrdtr = False)
        except:
            print('HW: port %s not open!' % port)
            self.port = None
            
        #time.sleep(2)
    
    def close(self):
        if self.port is None:
            return
        self.ser.close()  
      
    def takeCard(self):
        if self.port is None:
            return
        #print('SERIAL')
        self.ser.write('n')

if __name__ == '__main__':
    hw = hw2X()
    hw.open()
    hw.takeCard()
    hw.close()
    


        
