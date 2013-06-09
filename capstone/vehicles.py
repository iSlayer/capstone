"""
Vehicles definition
Author: David Ernest Lester
Date modified: 04/07/12

Defines Vehicles class
"""

import math
import events
import numpy as np


class Vehicles:
    def __init__(self, identity, x, y, z,
            oldx, oldy, oldz, dt, *args, **kwargs):
        self.identity = identity
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.oldx = float(oldx)
        self.oldy = float(oldy)
        self.oldz = float(oldz)
        self.dt = float(dt)

    def check_distance(self, dist_range, check):
        if check:
            return self.x ** 2 + self.y ** 2 + self.z ** 2 <= dist_range ** 2
        else:
            return self.x ** 2 + self.y ** 2 + self.z ** 2 >= dist_range ** 2

    def invisible_cone(self, cone_angle):
        return self.get_elevation_angle() < cone_angle

    def get_range(self):
        return np.sqrt(self.x ** 2 + self.y ** 2)

    def get_bearing(self):
        if self.y < 0:
            return  360 + math.degrees(math.atan2(self.y, self.x))
        else:
            return math.degrees(math.atan2(self.y, self.x))

    def get_elevation_angle(self):
        return math.degrees(math.atan2(self.z, self.get_range()))

    def package_data(self):
        return events.create_radar_output(self.get_bearing(), self.get_range(),
                self.get_elevation_angle(), self.identity, self.dt)

    def __str__(self):
        s = ("%s %f %f %f %f %f %f %f")
        return s % (self.identity, self.x, self.y,
                self.z, self.oldx, self.oldy, self.oldz,
                self.dt)
