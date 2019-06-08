#!/usr/bin/env python
import serial
import time
#        """ A class to monitor and control the delay stage ESP300.
#	    Implemented by Giorgio Levy 20140211. """



class gl_esp300:
        _term = ' \r\n'
        _limit = 0.0
        _twait = 300.0/1000.0	
        _limitpos= 0.0
        _limitneg= 0.0
        _precision = 0.0001
        _port = 'COM6'
        _range_short_min, _range_short_max = 0, 25
        _range_long_min, _range_long_max = 0, 152

	
        def __init__(self,log_path=''):
               	self.current_read=0
                self.log_path=log_path
                self.port=serial.Serial(self._port, baudrate=19200, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
                self.port.write(('1MF'+self._term).encode())
                self.port.write(('2MF'+self._term).encode())
               	self.port.write(('3MF'+self._term).encode())

        def ON(self, axis):
	        	self.port.write((str(axis)+'MO'+self._term).encode())

        def OFF(self, axis):
        		self.port.write((str(axis)+'MF'+self._term).encode())

        def open(self, axis=None):
                if axis is not None:
                    if self.port.isOpen()==0:
                        self.port.open()
                        time.sleep(self._twait)
                    self.ON(axis)
                else:
                    print("Please provide axis number to open.")
        
        def close(self, axis = None):
        		if axis is None:
        			self.OFF(1)
        			self.OFF(2)
        			self.OFF(3)
        			self.port.close()
        		else:
        			self.OFF(axis)

        def send(self, axis, comm, value=0):
                command = str(axis)+comm+ str(value)+self._term
                self.port.write(command.encode())
                time.sleep(self._twait)

        def ask(self, axis, comm):
                command = str(axis)+comm+self._term
                self.port.write(command.encode())
                self.line = self.port.readline()
                time.sleep(self._twait)
                return self.line[0:(len(self.line)-2)]

        def home(self, axis):
                self.open(axis)
                home_mode = 4 
                command = str(axis)+"OR"+str(home_mode)+self._term
                print("Homing Axis:" + str(axis))
                self.port.write(command.encode())
                print("Done.")
                time.sleep(self._twait)

        def OutOfRange(self, axis):
                print("Axis-" + str(axis)+ ": Hardware Limit (Out Of Range)")

        def getpos(self, axis):
                result = self.ask(axis, 'TP')
                value = float(result)
                return value
	
        def waitmotion(self, axis, position):
                print('Moving delay stage: ' + 'Axis-' + str(axis))
                value = self.getpos(axis)
                condition = abs(value-position)
                while condition > self._precision:
                        value = self.getpos(axis)
                        condition = abs(value-position)
                print('Done.')


        def moveA(self, axis, position):
                self.open(axis)
                if axis == 1 or axis == 2:
                    if position < self._range_short_min or position > self._range_short_max:
                        self.OutOfRange(axis)
                        return
                    else:
                        self.send(axis, 'PA', value=position)
                        self.waitmotion(axis, position)

                else:
                    if position < self._range_long_min or position > self._range_long_max:
                        self.OutOfRange(axis)
                        return
                    else:
                        self.send(axis, 'PA', value=position)
                        self.waitmotion(axis, position)

            
        def moveR(self, axis, increment):
                result = self.ask(axis, 'TP')
                value = float(result)
                position = value+increment
                self.moveA(axis, position)		
		
        def moveR2(self, axis, increment):
                value = self.getpos(axis)
                position = value+increment
                self.send(axis, 'PR', value=increment)
                self.waitmotion(axis, position)


if __name__=="__main__":
        S = gl_esp300()
        axis = 1
        (delay_min, delay_max, delay_d) = (1, 2, 0.1)
        delay = delay_min
        while delay <=(delay_max+0.005):
                print(delay)
                S.open(axis)
                S.moveA(axis, delay)
                pos1 = S.getpos(axis)
                print(pos1)
                S.close(axis)
                delay += delay_d

        S.close()