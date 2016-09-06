#!/usr/bin/env python2

'''
    >>> from pyfirmata import Arduino, util
    >>> board = Arduino('/dev/tty.usbserial-A6008rIF')
    >>> board.digital[13].write(1)

To use analog ports, it is probably handy to start an iterator thread.
Otherwise the board will keep sending data to your serial, until it overflows::

    >>> it = util.Iterator(board)
    >>> it.start()
    >>> board.analog[0].enable_reporting()
    >>> board.analog[0].read()
    0.661440304938

If you use a pin more often, it can be worth it to use the ``get_pin`` method
of the board. It let's you specify what pin you need by a string, composed of
'a' or 'd' (depending on wether you need an analog or digital pin), the pin
number, and the mode ('i' for input, 'o' for output, 'p' for pwm). All
seperated by ``:``. Eg. ``a:0:i`` for analog 0 as input or ``d:3:p`` for
digital pin 3 as pwm.::

    >>> analog_0 = board.get_pin('a:0:i')
    >>> analog_0.read()
    0.661440304938
    >>> pin3 = board.get_pin('d:3:p')
    >>> pin3.write(0.6)

Board layout
============

If you want to use a board with a different layout than the standard Arduino
or the Arduino Mega (for which there exist the shortcut classes
``pyfirmata.Arduino`` and ``pyfirmata.ArduinoMega``), instantiate the Board
class with a dictionary as the ``layout`` argument. This is the layout dict
for the Mega for example::

    >>> mega = {
    ...         'digital' : tuple(x for x in range(54)),
    ...         'analog' : tuple(x for x in range(16)),
    ...         'pwm' : tuple(x for x in range(2,14)),
    ...         'use_ports' : True,
    ...         'disabled' : (0, 1, 14, 15) # Rx, Tx, Crystal
    ...         }

'''

from pyfirmata import Arduino, util
import time

class hw():
    board = None
    
    feederServoPin = None #PWM
    releaseServoPin = None #PWM
        
    #def __init__(self, port):
    #    try:
    #        self.board = Arduino(port)
    #    except Exception as err:
    #        print(err) 
    #        return None
    #        
    #    self.feederServoPin = self.board.get_pin('d:10:s')
    #    self.realeaseServoPin = self.board.get_pin('d:11:s')
    #    self.ledPin = self.board.get_pin('d:13:o')

    def prepare(self):
        pos = 0
        print('feeder servo preparing')
        self.feederServoPin.write(pos)
    
    def feed(self):
        pos = 128
        print('feeder servo taking')
        self.feederServoPin.write(pos)
        
    def release(self):
        pos = 0
        print('realese servo releasing')
        self.realeaseServoPin.write(pos)

    def block(self):
        print('realese servo blocking')
        self.realeaseServoPin.write(128)
        
    def takeCard(self):
        self.block()
        self.feed()
  
    def takeCard2(self):
        self.block()
        self.prepare()
        time.sleep(1)
        self.feed()
        
    def releaseCard(self):
        self.prepare()
        self.release()
 
import time
import serial
class hw2X(): 
    ser = None
    def open2(self):
        pass
    def open(self):
        # configure the serial connections (the parameters differs on the device you are connecting to)
        self.ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff = False,
        rtscts = False, 
        dsrdtr = False)
        #self.ser.open()
        time.sleep(2)
        #print 'ok'
    
    def close(self):
        self.ser.close()  
        
    def takeCard(self):
        f = '0'
        h = '100'
        data=f + 'f,' + h +'h'
        b = bytearray()
        b.extend(data)
        print data
        self.ser.write(data)
        
        
        
        # let's wait one second before reading output (let's give device time to answer)
        out = ''
        time.sleep(1)
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1)
        print out    
        
        #time.sleep(1)
        
        f = '180'
        h = '175'
        data=f + 'f,' + h +'h'
        b = bytearray()
        b.extend(data)
        print data
        self.ser.write(data)
        
        
        # let's wait one second before reading output (let's give device time to answer)
        out = ''
        time.sleep(1)
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1)
        print out    


#ser.isOpen()

if __name__ == '__main__':
    hw = hw2X()
    hw.open()
    hw.takeCard()
    hw.close()
    

if __name__ == '__main__X':
    app = hw('/dev/ttyUSB0')
    #app = hw('COM2')
    
    app.prepare()
    time.sleep(1)

    app.block()
    app.feed()
    time.sleep(1)    
    
    app.ledPin.write(1)
    print('scanning...')
    time.sleep(2)  
    app.ledPin.write(0)
    
    app.prepare()
    app.release()
    time.sleep(1)   
    
    print('---')
    
    
    app.takeCard()
    
    app.ledPin.write(1)
    print('scanning...')
    time.sleep(2)  
    app.ledPin.write(0)
    
    time.sleep(2)   
    app.releaseCard()
    
        
