import usb.core
import usb.util
import time
import argparse
import sys
import struct
import re
import os
import numpy as np
#import seabreeze.spectrometers as sb


devLib=None

'''
*****************************************
Selction of device librries:
*****************************************
'''
deviceLibs = {
    '0xbd70xa012': 'stellarnetLib'
    #'StellarNetUSB2EPP': 'stellarnetLib',
    #'USB2000Ocean': 'OceanOpticsLib',
    #'SeabreezeUSB2000': 'SeaBreezeLib'
    }
 

'''
*****************************************
Basic functions:
*****************************************
'''
def find_devices():
    """
    Find all USB-connected StellarNet devices.
    This function returns a tuple of objects.
    """
    device_count=0
    
    try:
        devices = usb.core.find(find_all=True)
      
        for dev in devices: 
             
             device_count+=1
             #print(device_count)
             if device_count==1:
                device_list= str(device_count)#(dev,)
               
                device_models={ \
                    str(device_count): { \
                       # 'iProduct':usb.util.get_string(dev, dev.iProduct).split(' ', 1)[0], 
                        #'iManufacturer':usb.util.get_string(dev, dev.iManufacturer).split(' ', 1)[0],
                        'idProduct':hex(dev.idProduct),
                        'idVendor':hex(dev.idVendor),
                        
                        }
                }
                
             else:
                device_list=device_list + str(device_count)#(dev,)
               
                device_models[str(device_count)]= { \
                        #'iProduct':usb.util.get_string(dev, dev.iProduct).split(' ', 1)[0],
                        #'iManufacturer':usb.util.get_string(dev, dev.iManufacturer).split(' ', 1)[0],
                        'idProduct':hex(dev.idProduct),
                        'idVendor':hex(dev.idVendor),
		        		
                }
          
        #print(DeviceList['1']['iProduct'])
        # print(DeviceList['1']['iManufacturer'])
        #print(DeviceList['1']['idProduct'], end='\n')
        #print(DeviceList['1']['idVendor'])
    except:
        print('No USB devices found')

        ''' try:
            devices = sb.list_devices()
            for dev in devices: 
                device_count+=1
                if device_count==1:
                    device_list=str(device_count)#(sb.Spectrometer(dev),)
                    device_models={ \
                            str(device_count): { \
                                'iProduct':dev.model,
                                'iManufacturer':'Seabreeze',
                                'idProduct':'0x00',
                                'idVendor':'0x00',
                            }
                    }
                else:
                    device_list=device_list+str(device_count)#(sb.Spectrometer(dev),)
                    device_models[str(device_count)]= { \
                            'iProduct':dev.model,
                            'iManufacturer':'Seabreeze',
                            'idProduct':'0x00',
                            'idVendor':'0x00',
                    }
                print(dev.model)
        except:
            print('No Seabreeze OceanOptics devices found')
            pass
        '''

    if device_count == 0:
        print('No devices found')
        pass
        # raise NotFoundError('No devices found')
    else:
       
        return device_models, device_list

def select_device(currentRow,device_models,device_list):
    global devLib
    #device_count=0
    found=0
    if True: #try:
        devices = usb.core.find(find_all=True)
        for dev in devices:
            #device_count+=1
            if (device_models[str(currentRow)]['idProduct']== hex(dev.idProduct) and device_models[str(currentRow)]['idVendor']==hex(dev.idVendor)):  #usb.util.get_string(dev, dev.iProduct).split(' ', 1)[0] and \
                #device_models[str(currentRow)]['iManufacturer']==usb.util.get_string(dev, dev.iManufacturer).split(' ', 1)[0]):
                selected_device=dev
                selected_model=device_models[str(currentRow)]
                found=1
    ''' #except: 
        #print('no spectromoters detected')
        #if found==0:
        dev_list = sb.list_devices()
        for dev in dev_list: 
            device_count+=1
            if device_models[str(currentRow)]['iProduct']==dev.model:
                selected_device=sb.Spectrometer(dev)
                selected_model=device_models[str(currentRow)]
                break
    '''
    devname1=selected_model['idVendor']
    devname2=selected_model['idProduct']
    devLib=__import__(deviceLibs[(devname1+devname2)])
    devLib.initialize(selected_device)
    return selected_device, selected_model

def getWv(dev):
    wv=devLib.get_wavelengths(dev)
    return wv

def getdata(dev):
    A=devLib.format_spectrum(dev)
    return A

def _set_usb_config(dev):
    """Set USB configuration"""
    value = -1
    try:
        value = dev.get_active_configuration().bConfigurationValue
    except usb.core.USBError:
        pass

    if value != 1:
        dev.set_configuration()


def close(dev):
    if dev:
        devLib.close(dev)
        # dev.reset()
        dev = None
        return(dev)

def _load_firmware(device, filename):
    """Load firmware into device from Intel-hex-formatted file."""

    CPUCS = 0xE600 #  CPU control and status register address
    # Put CPU into reset:
    device.ctrl_transfer(TransferDirectionOut, 0xA0, CPUCS, 0, [0x01])
    # Load firmware:
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, filename), 'r') as fh:
        for line in fh:
            count = int(line[1:1 + 2], 16)
            if count:
                address = int(line[3:3 + 4], 16)
                payload = bytearray(line[9:9 + count*2].decode("hex"))
                device.ctrl_transfer(
                    TransferDirectionOut, 0xA0, address, 0, payload)

    # Take CPU out of reset
    device.ctrl_transfer(TransferDirectionOut, 0xA0, CPUCS, 0, [0x00])

def update_integration_time(dev,integr):
    devLib.set_device_parameters(dev,int_time=integr)


class SpectrometerError(Exception):
    """Base class for Spectrometer errors."""
    def __init__(self, message):
        Exception.__init__(self, message)

class NotFoundError(SpectrometerError):
    """Raised when USB device cannot be found."""
    pass
