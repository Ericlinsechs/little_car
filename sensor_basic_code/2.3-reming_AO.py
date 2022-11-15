#!/usr/bin/env python
#------------------------------------------------------
#
#       This is a program for PCF8591 Module.
#
#       Warnng! The Analog input MUST NOT be over 3.3V!
#    
#       In this script, we use a poteniometer for analog
#   input, and a LED on AO for analog output.
#
#       you can import this script to another by:
#   import PCF8591 as ADC
#   
#   ADC.Setup(Address)  # Check it by sudo i2cdetect -y -1
#   ADC.read(channal)   # Channal range from 0 to 3
#   ADC.write(Value)    # Value range from 0 to 255     
#   guangming->ad0 reming->ad1 dianweiqi->ad4 led->out
#------------------------------------------------------
import smbus
import time

# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)

def read(chn): #channel
    if chn == 0:
        bus.write_byte(address,0x40)
    if chn == 1:
        bus.write_byte(address,0x41)
    if chn == 2:
        bus.write_byte(address,0x42)
    if chn == 3:
        bus.write_byte(address,0x43)
    bus.read_byte(address) # dummy read to start conversion
    return bus.read_byte(address)

#check your PCF8591 address by type in 'sudo i2cdetect -y -1' in terminal.
def setup(Addr):
    global address
    address = Addr
    
def loop():
    print(read(1))
    time.sleep(0.1)
        
if __name__ == "__main__":
    setup(0x48)
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        pass
