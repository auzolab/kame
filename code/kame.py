import os
import sys
sys.path.append(os.path.abspath(__file__).replace('kame/code/kame.py', '') + 'pybotics/')

import time
import smbus
from driver.pca9685.pca9685 import ServoController
import control.octosnake.octosnake as octosnake

#  Servos:
#   _________   ________   _________
#  |(2)______)(0)      (1)(______(3)|
#  |__|       |   KAME   |       |__|
#             |          |
#             |          |
#             |          |
#   _________ |          | _________
#  |(6)______)(4)______(5)(______(7)|
#  |__|                          |__|
#                  /\
#                  |
#             USBs |


class Kame(object):

    def __init__(self, servo_trims, servo_pins, i2c_bus=1, pca9685_address=0x40, name='kame'):

        # Configuration
        self._name = name
        self._i2c_bus = i2c_bus
        self._servo_trims = servo_trims
        self._servo_pins = servo_pins
        self._pca9685_address = pca9685_address

        # Setting up hardware
        self._bus = smbus.SMBus(self._i2c_bus)
        if not self._bus:
            raise Exception('I2C bus connection failed!')

        self.controller = ServoController(self._bus, self._pca9685_address)

        # Setting up OctoSnake
        self.osc = []
        self.osc.append(octosnake.Oscillator())
        self.osc.append(octosnake.Oscillator())
        self.osc.append(octosnake.Oscillator())
        self.osc.append(octosnake.Oscillator())
        self.osc.append(octosnake.Oscillator())
        self.osc.append(octosnake.Oscillator())
        self.osc.append(octosnake.Oscillator())
        self.osc.append(octosnake.Oscillator())

        self.osc[1].ref_time = self.osc[0].ref_time
        self.osc[2].ref_time = self.osc[0].ref_time
        self.osc[3].ref_time = self.osc[0].ref_time
        self.osc[4].ref_time = self.osc[0].ref_time
        self.osc[5].ref_time = self.osc[0].ref_time
        self.osc[6].ref_time = self.osc[0].ref_time
        self.osc[7].ref_time = self.osc[0].ref_time

        # Setting up servo controller
        for i in range(len(self._servo_pins)):
            self.controller.addServo(self._servo_pins[i], self._servo_trims[i])

        self.controller.servos[self._servo_pins[1]].reverse = True
        # self.controller.servos[self._servo_pins[3]].reverse = True
        self.controller.servos[self._servo_pins[5]].reverse = True
        # self.controller.servos[self._servo_pins[6]].reverse = True

    def back(self, steps):

        x_amp = 20
        z_amp = 15
        front_x = 8
        T = 750.0
        i = 0

        period = [T, T, T/2, T/2, T, T, T/2, T/2]
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [front_x, front_x, -25, -25, front_x, front_x, -25, -25]
        phase = [270, 90, i, 270, 90, 270, i, i]

        for i in range(len(self.osc)):
            self.osc[i].period = period[i]
            self.osc[i].amplitude = amplitude[i]
            self.osc[i].phase = phase[i]
            self.osc[i].offset = offset[i]

        init_ref = time.time()
        final = init_ref + float(T*steps/1000)
        self.osc[0].ref_time = init_ref
        self.osc[1].ref_time = self.osc[0].ref_time
        self.osc[2].ref_time = self.osc[0].ref_time
        self.osc[3].ref_time = self.osc[0].ref_time
        self.osc[4].ref_time = self.osc[0].ref_time
        self.osc[5].ref_time = self.osc[0].ref_time
        self.osc[6].ref_time = self.osc[0].ref_time
        self.osc[7].ref_time = self.osc[0].ref_time
        while time.time() < final:
            side = int((time.time()-init_ref) / (T/2000.0)) % 2
            try:
                for i in range(len(self.osc)):
                    self.osc[i].refresh()

                self.controller.move(self._servo_pins[0], self.osc[0].output)
                self.controller.move(self._servo_pins[1], self.osc[1].output)
                self.controller.move(self._servo_pins[4], self.osc[4].output)
                self.controller.move(self._servo_pins[5], self.osc[5].output)
                if side == 0:
                    self.controller.move(self._servo_pins[3], -self.osc[3].output)
                    self.controller.move(self._servo_pins[6], -self.osc[3].output)
                else:
                    self.controller.move(self._servo_pins[2], self.osc[3].output)
                    self.controller.move(self._servo_pins[7], self.osc[3].output)

            except IOError:
                self._bus = smbus.SMBus(self._i2c_bus)

    def walk(self, steps):

        x_amp = 20
        z_amp = 15
        front_x = -12
        T = 450.0
        period = [T, T, T/2, T/2, T, T, T/2, T/2]
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [front_x, front_x, -25, -25, front_x, front_x, -25, -25]
        phase = [90, 270, 90, 270, 270, 90, 270, 90]

        for i in range(len(self.osc)):
            self.osc[i].period = period[i]
            self.osc[i].amplitude = amplitude[i]
            self.osc[i].phase = phase[i]
            self.osc[i].offset = offset[i]

        init_ref = time.time()
        final = init_ref + float(T*steps/1000)
        self.osc[0].ref_time = init_ref
        self.osc[1].ref_time = self.osc[0].ref_time
        self.osc[2].ref_time = self.osc[0].ref_time
        self.osc[3].ref_time = self.osc[0].ref_time
        self.osc[4].ref_time = self.osc[0].ref_time
        self.osc[5].ref_time = self.osc[0].ref_time
        self.osc[6].ref_time = self.osc[0].ref_time
        self.osc[7].ref_time = self.osc[0].ref_time
        while time.time() < final:
            side = int((time.time()-init_ref) / (T/2000.0)) % 2
            try:
                for i in range(len(self.osc)):
                    self.osc[i].refresh()

                self.controller.move(self._servo_pins[0], self.osc[0].output)
                self.controller.move(self._servo_pins[1], self.osc[1].output)
                if side == 0:
                    self.controller.move(self._servo_pins[3], -self.osc[3].output)
                    self.controller.move(self._servo_pins[6], -self.osc[3].output)
                else:
                    self.controller.move(self._servo_pins[2], self.osc[3].output)
                    self.controller.move(self._servo_pins[7], self.osc[3].output)
                self.controller.move(self._servo_pins[4], self.osc[4].output)
                self.controller.move(self._servo_pins[5], self.osc[5].output)

            except IOError:
                self._bus = smbus.SMBus(self._i2c_bus)

    def turnL(self, steps):

        x_amp = 15
        z_amp = 15
        T = 500
        period = [T, T, T, T, T, T, T, T]
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [30, 30, -30, 30, -30, -30, 30, -30]
        phase = [0, 0, 270, 270, 180, 180, 270, 270]

        for i in range(len(self.osc)):
            self.osc[i].period = period[i]
            self.osc[i].amplitude = amplitude[i]
            self.osc[i].phase = phase[i]
            self.osc[i].offset = offset[i]

        final = time.time() + float(T*steps/1000)
        while time.time() < final:
            try:
                for i in range(len(self.osc)):
                    self.osc[i].refresh()
                for i in range(len(self.osc)):
                    self.controller.move(self._servo_pins[i], self.osc[i].output)

            except IOError:
                self._bus = smbus.SMBus(self._i2c_bus)

    def turnR(self, steps):

        x_amp = 15
        z_amp = 15
        T = 500
        period = [T, T, T, T, T, T, T, T]
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [30, 30, -30, 30, -30, -30, 30, -30]
        phase = [0, 0, 90, 90, 180, 180, 90, 90]

        for i in range(len(self.osc)):
            self.osc[i].period = period[i]
            self.osc[i].amplitude = amplitude[i]
            self.osc[i].phase = phase[i]
            self.osc[i].offset = offset[i]

        final = time.time() + float(T*steps/1000)
        while time.time() < final:
            try:
                for i in range(len(self.osc)):
                    self.osc[i].refresh()
                for i in range(len(self.osc)):
                    self.controller.move(self._servo_pins[i], self.osc[i].output)

            except IOError:
                self._bus = smbus.SMBus(self._i2c_bus)

    def dance(self, steps):

        x_amp = 0
        z_amp = 30
        T = 500
        period = [T, T, T, T, T, T, T, T]
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [45, 45, -30, -30, -45, -45, 30, 30]
        phase = [0, 0, 0, 90, 0, 0, 270, 180]

        for i in range(len(self.osc)):
            self.osc[i].period = period[i]
            self.osc[i].amplitude = amplitude[i]
            self.osc[i].phase = phase[i]
            self.osc[i].offset = offset[i]

        final = time.time() + float(T*steps/1000)
        while time.time() < final:
            try:
                for i in range(len(self.osc)):
                    self.osc[i].refresh()
                for i in range(len(self.osc)):
                    self.controller.move(self._servo_pins[i], self.osc[i].output)

            except IOError:
                self._bus = smbus.SMBus(self._i2c_bus)

    def zero(self):
        for i in range(len(self._servo_pins)):
            self.controller.move(self._servo_pins[i], 0)

    def jump(self):
        for i in range(len(self._servo_pins)):
            self.controller.move(self._servo_pins[i], 0)

        self.controller.move(self._servo_pins[2], 10)
        self.controller.move(self._servo_pins[3], -10)
        self.controller.move(self._servo_pins[6], -10)
        self.controller.move(self._servo_pins[7], 10)
        time.sleep(1)

        self.controller.move(self._servo_pins[2], -25)
        self.controller.move(self._servo_pins[3], 25)
        self.controller.move(self._servo_pins[6], 25)
        self.controller.move(self._servo_pins[7], -25)

        time.sleep(0.075)
        self.controller.move(self._servo_pins[2], 10)
        self.controller.move(self._servo_pins[3], -10)
        self.controller.move(self._servo_pins[6], -10)
        self.controller.move(self._servo_pins[7], 10)
