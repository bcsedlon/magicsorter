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
        
    def __init__(self, port):
        try:
            self.board = Arduino(port)
        except Exception as err:
            print(err) 
            return None
            
        self.feederServoPin = self.board.get_pin('d:10:s')
        self.realeaseServoPin = self.board.get_pin('d:11:s')

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
    
if __name__ == '__main__':
    app = hw('/dev/ttyUSB0')
    
    app.prepare()
    time.sleep(1)

    app.block()
    app.feed()
    time.sleep(1)    
    
    print('scanning')
    
    app.prepare()
    app.release()
    time.sleep(1)   
    
    print('---')
    
    
    app.takeCard()
    print('sacnning')
    time.sleep(2)   
    app.releaseCard()
    
        