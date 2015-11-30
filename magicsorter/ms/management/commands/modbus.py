from django.core.management.base import BaseCommand, CommandError

import time
import datetime
from time import gmtime, strftime

from django.utils import timezone, regex_helper
from django.utils import dateformat

from subprocess import call
import sys
import socket

import os
import urllib
import urllib2

import minimalmodbus

import threading

#subprocess.Popen(["python", "archive.py"])


class ScannerInstrument():
    name = None
    address = 0
    value = 0
    status = 0
    output = False
    
    def __init__(self, name=None, address=0, output=False):
        self.name = name
        self.address = address
        self.output = output


class Scanner():
    instruments = []
    
    outServo = ScannerInstrument('outServo', 1, True)
    instruments.append(outServo)
    
    outFeeder = ScannerInstrument('outFeeder', 2, True)
    instruments.append(outFeeder)
    
    inServo = ScannerInstrument('inServo', 3, False)
    instruments.append(inServo)


class ModbusServer(): 
        
    station = minimalmodbus.Instrument('COM3', 1) # port name, slave address (in decimal)

    print station.serial.port          # this is the serial port name
    
    #station.debug = True
    station.serial.baudrate = 9600   # Baud
    station.serial.bytesize = 8
    #station.serial.parity   = serial.PARITY_NONE
    station.serial.stopbits = 2
    station.serial.timeout  = 0.05   # seconds
    station.serial.timeout  = 0.5   # seconds
    
    SERVER = True
       
    thr = None
    
    @staticmethod
    def stopServer():
        
        ModbusServer.SERVER = False
        
        if ModbusServer.thr:
            ModbusServer.thr.join()
        
    @staticmethod
    def startServer():
        
        while ModbusServer.SERVER:
            #time_now = int(strftime("1%H%M%S", gmtime()))
            print 'Modbus: -'
            for instrument in Scanner.instruments:
                
                                
                try:
                    if instrument.output:
                        ModbusServer.station.write_register(instrument.address, instrument.value)
                        instrument.status = 0
                    else:
                        instrument.value =  ModbusServer.station.read_register(instrument.address, 0) 
                        instrument.status = 0                   
                except:
                    instrument.status = 1
                    #print 'sensor does not response, address {}'.format(address)
                
                print 'Modbus: name: {}, value: {} status: {}'.format(instrument.name, instrument.value, instrument.status) 
                    
    
            #time.sleep(5)
    
    @staticmethod
    def startServerAsync():
        ModbusServer.thr = threading.Thread(target= ModbusServer.startServer, args=(), kwargs={})
        ModbusServer.thr.start()


class Command(BaseCommand):

    help = 'modbus master'

    
    def handle(self, *args, **options):
        
        pass
            
