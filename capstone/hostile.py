"""
Hostile definition
Author: David Ernest Lester
Date modified: 04/01/12

Defines Hostile class
"""

import random
import numpy as np
import time


class Hostile:
    def __init__(self, identity, vehicle_type, x, y, z, oldx, oldy, oldz):
        # Initializing the vehicle parameters
        self.identity = identity
        self.vehicle_type = vehicle_type
        self.x = x
        self.y = y
        self.z = z
        self.oldx = oldx
        self.oldy = oldy
        self.oldz = oldz
        self.dt = 0

        # Randomly assign a theta value between 0 and 2pi
        theta = random.random() * 2 * np.pi
        #print "theta within hostile: ", theta

        # Distance relative to center of radar
        dist = 20000

        # Based on the vehicle type randomize a speed
        speed = {
            0: random.randint(7, 38),
            1: random.randint(51, 140),
            2: random.randint(90, 191),
                }[self.vehicle_type]
        #print "Speed: ", speed

        # Chooses a random point around radar to travel to linearly
        self.x_mod = dist * np.cos(theta) - self.x
        self.y_mod = dist * np.sin(theta) - self.y

        # Used in lines 48-49 to normalize
        total_mod = np.sqrt(self.x_mod ** 2 + self.y_mod ** 2)

        # Increases a dx and dy
        self.x_mod *= speed / total_mod
        self.y_mod *= speed / total_mod

        #print "identification: ", self.identity

        #print "dx: %f, dy: %f" % (self.x_mod, self.y_mod)

        #print "Actual Speed: %f" % (np.sqrt(self.y_mod ** 2 + self.x_mod ** 2))

    @property
    def to_dict(self):
        return {
            'identity': self.identity,
            'vehicle_type': self.vehicle_type,
            'x': self.x, 'y': self.y, 'z': self.z,
            'oldx': self.oldx, 'oldy': self.oldy, 'oldz': self.oldz,
            'dt': self.dt
        }

    def old_data(self, oldx, oldy, oldz):
        self.oldx = oldx
        self.oldy = oldy
        self.oldz = oldz

    def move_to(self, dx, dy, dz, time_old):
        self.dt = time.time() - time_old
        self.x += self.dt * dx
        self.y += self.dt * dy
        self.z += self.dt * dz

    def __str__(self):
        s = ("%s %f %f %f %f %f %f %f")
        return s % (self.identity, self.x, self.y, self.z, self.oldx,
                self.oldy, self.oldz, self.dt)
