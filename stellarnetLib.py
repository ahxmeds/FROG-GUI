import usb.core
import usb.util
import time
import timeit
import argparse
import sys
import struct
import re
import os
import numpy as np
'''
*****************************************
Static parameters:
*****************************************
'''
DEVICE_ID_ADDR = 0x20 #The address of the stored string containing device identification."""
COEFF_C1_ADDR = 0x80 #The address of the string containing coefficient C1"""
COEFF_C2_ADDR = 0xA0 #The address of the string containing coefficient C2"""
COEFF_C3_ADDR = 0xC0 #The address of the string containing coefficient C3"""
COEFF_C4_ADDR = 0xE0 #The address of the string containing coefficient C4"""
# Ids of the default USB device (Cyprus Semiconductor/EZ-USB):
_DEFAULT_VENDOR_ID = 0x04B4
_DEFAULT_PRODUCT_ID = 0x8613
# Ids of the ReNumerated USB device (StellarNet/USB2EPP):
_STELLARNET_VENDOR_ID = 0x0BD7
_STELLARNET_PRODUCT_ID = 0xA012
# Device to host control request:
_IN_DEVICE = usb.util.CTRL_IN | \
    usb.util.CTRL_TYPE_VENDOR | \
    usb.util.CTRL_RECIPIENT_DEVICE
# Host to device control request:
_OUT_DEVICE = usb.util.CTRL_OUT | \
    usb.util.CTRL_TYPE_VENDOR | \
    usb.util.CTRL_RECIPIENT_DEVICE
# Maps detector type to number of pixels:
_PIXEL_MAP = {
    1:2048, # CCD - 2048
    2:1024, # CCD - 1024
    3:2048, # PDA - 2048
    4:1024, # PDA - 1024
    5:512,  # InGaAs - 512
    6:1024  # InGaAs - 1024
            # PDA - 3600 (don't know the detector type for this one)
}
_WINDOW_MAP = {0:0, 1:5, 2:9, 3:17, 4:33} # Maps smoothing parameter to sliding window size
_next_auto_id = 0    # Next auto-assigned id
    
_parameters= {'int_time':100, 'x_timing':1, 'x_smooth':0, 'scans_to_avg':1, 'temp_comp':0, \
'det_type':1, 'coeffs':0}

'''
*****************************************
Basic functions:
*****************************************
'''
def initialize(dev):
    global _next_auto_id, _parameters
    set_device_parameters(dev,int_time = 100,
                x_timing = 1,
                x_smooth = 0,
                scans_to_avg = 1,
                temp_comp = 0)
    try:
        # Try to fetch and parse lambda coefficients
        coeffs = [float(get_stored_string(dev,addr).split()[0])
            for addr in [COEFF_C1_ADDR, COEFF_C2_ADDR, 
                         COEFF_C3_ADDR, COEFF_C4_ADDR]]
    except:
        # Assume its an older device that doesn't store information
        _parameters['det_type'] = 1
    else:
        _parameters['coeffs'] = coeffs
        
        # Fetch and parse detector type
        det_type = get_stored_bytes(dev,COEFF_C1_ADDR)[31] - ord('0')
        if det_type not in _PIXEL_MAP:
            raise ArgRangeError('det_type')
        _parameters['det_type'] = det_type
        
        # Assign model and device id
        p = re.compile('(.+) #(\d+)')
        m = p.match(get_stored_string(dev,DEVICE_ID_ADDR))
        if m:
            _parameters['model'] = m.group(1)
            _parameters['device_id'] = m.group(2)
            return
    print(_parameters)
    print('DOES NOT UPDATE _parameters VARIABLE!!!')
    # In the absence of device-specific information use:
    if dev.bus and dev.address:
        # bus and address
        auto_id = '{:x}{:x}'.format(dev.bus, dev.address)
    else:
        # next id
        auto_id = str(_next_auto_id)
        _next_auto_id += 1
    
    _parameters['model'] = 'unknown'
    _parameters['device_id'] = 'auto_id_' + auto_id

    return _parameters

def close(dev):
    usb.util.dispose_resources(dev)

def set_device_parameters(dev,**kwargs):
    """
    Sets the device configuration.
    
    :param int_time: (optional) Integer; the integration time in milliseconds.          [100]
    :param x_timing: (optional) Integer; the XTiming rate.                              [3]
    :param x_smooth: (optional) Integer; the boxcar smoothing window size.              [0]
    :param scans_to_avg: (optional) Integer; the # of scans to be averaged together.    [1]
    :param temp_comp: (optional) Integer; temperature compensation (not implemented).   [0]
    """
    update_int_time = False
    for key in kwargs:
        value = kwargs[key]
        if key == 'int_time':
            if value<2:
                value=2
            elif value>65536:
                value=65536
             # not in range(2, 65536):
             #    raise ArgRangeError(key)
            update_int_time = True
            int_time=value
        elif key == 'x_timing':
            if value not in range(1, 4):
                raise ArgRangeError(key)
            update_int_time = True
            x_timing=value
        elif key == 'x_smooth':
            if value not in _WINDOW_MAP:
                raise ArgRangeError(key)
        elif key == 'scans_to_avg':
            if value < 1:
                raise ArgRangeError(key)
        elif key == 'temp_comp':
            if value != 0:
                raise ArgRangeError(key)
        else:
            # Ignore unknown keys
            continue
        
        _parameters[key] = value

    if update_int_time:
        _set_device_timing(dev,int_time, _parameters['x_timing'])

def _set_device_timing(dev,int_time, x_timing):
    """Send device timing information to the device."""
    msb = int_time>>8
    lsb = int_time&0xFF
    xt = 1<<(x_timing + 1)
    msd = 0x1F if int_time > 1 else 0x0F
    dev.ctrl_transfer(_OUT_DEVICE, 0xB4, 0, 0, [msb, lsb, xt, msd])

def format_spectrum(dev):
    """Reads and returns a spectrum from the spectrometer. Returns an array 
    of short integers.
    
    See :class:`StellarNet`.set_config() for a description of the parameters 
    that control the operation of the spectrometer or the post-processing of 
    the spectrum.
    """
    dd=_read_data(dev)
    data = _smooth_data(dd)
    scans_to_avg = _parameters['scans_to_avg']
    if scans_to_avg > 1:
        summed = list(data)
        for i in range(2, scans_to_avg + 1):
            data = _smooth_data(_read_data(dev))
            for j in range(len(summed)):
                summed[j] = int(summed[j]*((i - 1)/float(i)) + data[j]/float(i))
        data = summed
    return data

def get_wavelengths(dev):
    pixels = _PIXEL_MAP[_parameters['det_type']]
    wv=np.empty(pixels)
    for i in range(0, pixels):
        wv[i]=int(round(compute_lambda(i)*1000))/1000
    return wv
    
def _read_data(dev):
    """Read data from the device."""
    # Start the integration
    # print('reading data')
    dev.ctrl_transfer(_OUT_DEVICE, 0xB2, 0, 0)

    # Set the timeout to be 500ms longer than the expected integration time
    int_time = _parameters['int_time']
    timeout = (int_time + 500)/1000.0

    # Sleep for 90% of the integration time to avoid busy waiting
    # for the result and causing unnecessary usb traffic
    start = time.time()
    time.sleep(int_time*.0009)
    
    while True:
        # Check if data is available
        reponse = dev.ctrl_transfer(_IN_DEVICE, 0xB3, 0, 0, 2)

        # If device is busy wait for next check else if device is ready wait
        # before reading data. Note: reading data without waiting occasionally
        # results in a right-shifted spectrum which becomes more frequent with
        # shorter integration times..
        time.sleep(.003)
        if reponse[1]:
            break
        
        if time.time() - start > timeout:
            raise TimeoutError('Read spectrum')

    # Read the CCD data and convert it to an array of 
    # 16-bit integers from the little-endian data buffer
    pixels = _PIXEL_MAP[_parameters['det_type']]
    # data=np.asarray(struct.unpack_from('<{}H'.format(pixels),
    #     dev.read(usb.util.ENDPOINT_IN | 8, pixels*2)))
    data=np.frombuffer(dev.read(usb.util.ENDPOINT_IN | 8, pixels*2),np.dtype('<H'))
    return data

def _smooth_data(src):
    """Apply boxcar smoothing to data."""
    
    win_span = _WINDOW_MAP[_parameters['x_smooth']]
    if win_span == 0:
        return src
    
    # Smooth middle, start indexes are inclusive, limit indexes are exclusive
    pixels = _PIXEL_MAP[_parameters['det_type']]
    dst = [0]*len(src)
    half_span = win_span/2
    src_start = half_span
    src_limit = pixels - half_span
    win_start = 0
    win_limit = win_span
    win_sum = sum(src[win_start:win_limit])
    dst[src_start] = win_sum/win_span
    for i in range(src_start + 1, src_limit):
        win_sum += src[win_limit] - src[win_start]
        dst[i] = win_sum/win_span
        win_start += 1
        win_limit += 1
    
    # Smooth left end
    src_start = 0
    win_sum = src[src_start]
    dst[src_start] = src[src_start]
    j = src_start + 1
    for i in range(j, half_span):
        win_sum += src[j + 0] + src[j + 1]
        j += 2
        dst[i] = win_sum/j
        
    # Smooth right end
    src_start = pixels - 1
    win_sum = src[src_start]
    dst[src_start] = src[src_start]
    j = src_start - 1
    for i in range(j, pixels - half_span - 1, -1):
        win_sum += src[j - 0] + src[j - 1]
        j -= 2
        dst[i] = win_sum/(src_start - j)
    
    return dst

# def set_stored_bytes(dev, address, data):
#     """Set stored bytes.
    
#     :param address: Integer; the address of the string to set.
#     :param data: String; the string value to be set
#     """

#     if address not in range(0x00, 0x100, 0x20):
#         raise ArgRangeError('address')

#     if len(data) != 0x20:
#         raise ArgRangeError('data')

#     write_flag = 0x45
#     payload = [0, address, write_flag]
#     payload.extend(bytearray(data))
#     dev.ctrl_transfer(_OUT_DEVICE, 0xB6, 0, 0, payload)

def get_stored_bytes(dev, address):
    """Get stored bytes. Returns bytearray.
    
    :param address: Integer; the address of the string to get.
    """

    if address not in range(0x00, 0x100, 0x20):
        raise ArgRangeError('address')

    payload = [0, address, 0]
    dev.ctrl_transfer(_OUT_DEVICE, 0xB6, 0, 0, payload)

    # The first byte of the data returned from the device is a copy of the
    # command request byte, in this case 0xB5. Since this never useful it is
    # excluded from the value returned by this method
    return dev.ctrl_transfer(_IN_DEVICE, 0xB5, 0, 0, 0x21)[1:]

def get_stored_string(dev,address):
    """Get stored bytes. Returns string.
    
    :param address: Integer; the address of the string to get.
    """
    return ''.join(map(chr, get_stored_bytes(dev,address)))
    
# def _load_firmware(device, filename):
#     """Load firmware into device from Intel-hex-formatted file."""

#     # CPU control and status register address
#     CPUCS = 0xE600

#     # Put CPU into reset
#     device.ctrl_transfer(StellarNet._OUT_DEVICE, 0xA0, CPUCS, 0, [0x01])

#     # Load firmware
#     __location__ = os.path.realpath(
#         os.path.join(os.getcwd(), os.path.dirname(__file__)))
#     with open(os.path.join(__location__, filename), 'r') as fh:
#         for line in fh:
#             count = int(line[1:1 + 2], 16)
#             if count:
#                 address = int(line[3:3 + 4], 16)
#                 payload = bytearray(line[9:9 + count*2].decode("hex"))
#                 device.ctrl_transfer(
#                     StellarNet._OUT_DEVICE, 0xA0, address, 0, payload)

#     # Take CPU out of reset
#     device.ctrl_transfer(StellarNet._OUT_DEVICE, 0xA0, CPUCS, 0, [0x00])

def compute_lambda(pixel):
    """Compute lambda from the pixel index. Returns the pixel's wavelength (float).
    
    :param pixel: Integer; the pixel index on which to perform the computation.
    """

    if not isinstance(pixel, int):
        raise ArgTypeError('pixel')
    
    pixels = _PIXEL_MAP[_parameters['det_type']]
    if pixel < 0 or pixel >= pixels:
        raise ArgRangeError('pixel')

    if 'coeffs' not in _parameters:
        raise ArgumentError('Device has no stored coefficients')
    
    coeffs = _parameters['coeffs']
    return ((pixel**3)*coeffs[3]/8.0 + 
            (pixel**2)*coeffs[1]/4.0 + 
            pixel*coeffs[0]/2.0 + 
            coeffs[2])

class StellarNetError(Exception):
    """Base class for StellarNet errors."""

    def __init__(self, message):
        Exception.__init__(self, message)

class NotFoundError(StellarNetError):
    """Raised when USB device cannot be found."""

    pass

class ArgumentError(StellarNetError):
    """Raised when argument in error."""

    pass

class ArgTypeError(ArgumentError):
    """Raised when argument type is incorrect."""

    pass

class ArgRangeError(ArgumentError):
    """Raised when argument is out of range."""

    pass

class TimeoutError(StellarNetError):
    """Raised when device operation times out."""

    pass
