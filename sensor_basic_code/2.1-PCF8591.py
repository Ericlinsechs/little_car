#!/usr/bin/env python
#   ADC.Setup(Address)  # Check it by sudo i2cdetect -y -1
#   ADC.read(channal)   # Channal range from 0 to 3
#   ADC.write(Value)    # Value range from 0 to 255     
#   guangming->ad0 reming->ad1 dianweiqi->ad4 led->out
#------------------------------------------------------
#导入模块
import smbus
import time

#for RPI version 1 ,use 'bus = smbus.SMBus(1)'
#1代表I2c-1,
bus = smbus.SMBus(1)   #创建一个smbus实例

#在树梅派上查询PCF8591的地址 “sudo i2cdetect -y 1”
def setup(Addr):
    global address
    address = Addr
#读取数据
def read(chn): #channel
    global bus
    if chn == 0:
        bus.write_byte(address,0x40)   #发送一个控制字节到设备
    if chn == 1:
        bus.write_byte(address,0x41)
    if chn == 2:
        bus.write_byte(address,0x42)
    if chn == 3:
        bus.write_byte(address,0x43)
    bus.read_byte(address) # 从设备读取单个字节。
    return bus.read_byte(address)  #返回某通道输入的模拟值A/D转换后的数字值
#发送数据
def write(val):
    temp = val # 将字符串移动到temp
    temp = int(temp) # 将字符串转换为整数类型
    #写入字节数据，将数字值转化成模拟值从Aout输出
    bus.write_byte_data(address, 0x40, temp)
#打印出来    
def loop():
    print ('AIN0 = %03d AIN1 = %03d AIN2 = %03d AIN3 = %03d '% (read(0),read(1),read(2),read(3)))
    tmp = read(3)
    write(tmp)
    time.sleep(0.1)
        
if __name__ == "__main__":
    setup(0x48)
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        pass
