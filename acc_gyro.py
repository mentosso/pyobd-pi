#!/usr/bin/python

import smbus
import math
import time

class AccGyro:
    # Power management registers
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c
    address = 0x68       # This is the address value read via the i2cdetect command

    def __init__(self):
        self.bus = smbus.SMBus(1) # for Revision 2 boards
        # Now wake the 6050 up as it starts in sleep mode
        self.bus.write_byte_data(AccGyro.address, AccGyro.power_mgmt_1, 0)

    def read_byte(self, adr):
        return self.bus.read_byte_data(self.address, adr)

    def read_word(self, adr):
        high = self.bus.read_byte_data(self.address, adr)
        low = self.bus.read_byte_data(self.address, adr+1)
        val = (high << 8) + low
        return val

    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def dist(self, a,b):
        return math.sqrt((a*a)+(b*b))

    def get_y_rotation(self):
        radians = math.atan2(self.get_accel_x_scaled(), self.dist(self.get_accel_y_scaled(), self.get_accel_z_scaled()))
        return -math.degrees(radians)

    def get_x_rotation(self):
        radians = math.atan2(self.get_accel_y_scaled(), self.dist(self.get_accel_x_scaled(), self.get_accel_z_scaled()))
        return math.degrees(radians)

    def get_gyro_x(self):
        return self.read_word_2c(0x43)

    def get_gyro_x_scaled(self):
        return self.read_word_2c(0x43)/131

    def get_gyro_y(self):
        return self.read_word_2c(0x45)

    def get_gyro_y_scaled(self):
        return self.read_word_2c(0x45)/131

    def get_gyro_z(self):
        return self.read_word_2c(0x47)

    def get_gyro_z_scaled(self):
        return self.read_word_2c(0x47)/131

    def get_accel_x(self):
        return self.read_word_2c(0x3b)

    def get_accel_x_scaled(self):
        return self.read_word_2c(0x3b)/16384.0

    def get_accel_y(self):
        return self.read_word_2c(0x3d)

    def get_accel_y_scaled(self):
        return self.read_word_2c(0x3d)/16384.0

    def get_accel_z(self):
        return self.read_word_2c(0x3f)

    def get_accel_z_scaled(self):
        return self.read_word_2c(0x3f)/16384.0

if __name__ == '__main__':
    device = AccGyro()
    while 1:
        print "gyro_xout: ", device.get_gyro_x(), "\t scaled: ", device.get_gyro_x_scaled(), "\t accel_xout: ", device.get_accel_x(), "\t scaled: ", device.get_accel_x_scaled()
        print "gyro_yout: ", device.get_gyro_y(), "\t scaled: ", device.get_gyro_y_scaled(), "\t accel_yout: ", device.get_accel_y(), "\t scaled: ", device.get_accel_y_scaled()
        print "gyro_zout: ", device.get_gyro_z(), "\t scaled: ", device.get_gyro_z_scaled(), "\t accel_zout: ", device.get_accel_z(), "\t scaled: ", device.get_accel_z_scaled()
        print  "x rotation: " , device.get_x_rotation(), "\t y rotation: " , device.get_y_rotation()
        time.sleep(1)
