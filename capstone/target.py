"""
Target definition
Author: David Ernest Lester
Date modified: 04/01/12 (Hahahahaha!)

Defines Target class
"""

import numpy as np
import math
import time


class Target:
    def __init__(self, bearing, range1, angle, identification, dt):
        # Data directly from simulation of radar
        self.bearing = bearing
        self.range1 = range1
        self.angle = angle
        self.identification = identification
        self.dt = dt
        self.object_type = None
        self.engage = None

        self.flag = True

        # Targets coordinates data
        self.x = 0
        self.y = 0
        self.z = 0
        self.speed = 0
        self.veloctiy = 0

        # Targets previous coordinates data
        self.oldx = 0
        self.oldy = 0
        self.oldz = 0
        self.oldrange1 = 0

        # Targets score values
        self.priority_score = 0

    def todict(self):
        return {'id': self.identification,
                'range': self.range1,
                'speed': self.speed,
                'elevation': self.angle,
                'bearing': self.bearing}

    def update(self, bearing, range1, angle, dt):
        # Update the bearing, range, and angle
        self.bearing = bearing
        self.range1 = range1
        self.angle = angle
        self.dt = dt
        self.engage_target()

        # Used to check time since last update
        self.time_check = time.time()

        #print "bearing: %f, range: %f, angle: %f, dt: %f" % (self.bearing,
                #self.range1, self.angle, self.dt)

        # Update to new xyz coordinate
        self.x = self.range1 * np.cos(math.radians(self.bearing))
        self.y = self.range1 * np.sin(math.radians(self.bearing))
        self.z = self.range1 * np.tan(math.radians(self.angle))

        #print "(%f, %f, %f)" % (self.x, self.y, self.z)

        # Update velocity and speed of target
        self.veloctiy = ((self.x - self.oldx) / self.dt, (self.y - self.oldy)
                / self.dt)
        self.speed = (np.sqrt((self.x - self.oldx) ** 2 + (self.y - self.oldy)
                ** 2) / self.dt)

        #print "Speed: ", self.speed

        self.update_object_type()

        #print "Vehicle type: ", self.object_type

        # Update the old coordinates
        self.oldx = self.x
        self.oldy = self.y
        self.oldz = self.z

        #print "old: (%f, %f, %f)" % (self.oldx, self.oldy, self.oldz)

        # Updatae the old range
        self.oldrange1 = self.range1

        #print "old Range: ", self.oldrange1
    def update_object_type(self):
        if self.z == 0:
            self.object_type = 'Boat'
        elif self.speed < 90:
            self.object_type = 'Helicopter'
        elif self.speed > 140 or self.z > 12000:
            self.object_type = 'Jet'
        else:
            self.object_type = 'UFO'

    def tuple_data(self):
        return (self.x, self.y)

    def status(self):
        return time.time() - self.time_check > 3

    def range_calc(self):
        # Here is the algorithm to calculate the range score of the vehicle
        if self.range1 >= 0 and self.range1 < 4000:
            return 8
        elif self.range1 >= 4000 and self.range1 < 8000:
            return 7
        elif self.range1 >= 8000 and self.range1 < 12000:
            return 6
        elif self.range1 >= 12000 and self.range1 < 16000:
            return 5
        else:
            return 4

    def speed_calc(self):
        # Here is the point system to add the score for the speeds of targets
        if self.speed >= 0 and self.speed < 27:
            return 4
        elif self.speed >= 27 and self.speed < 54:
            return 6
        elif self.speed >= 54 and self.speed < 108:
            return 7
        else:
            return 8

    def direction_calc(self):
        # Target
        if self.range1 - self.oldrange1 > 0:
            return 0
        else:
            return 2

    def bearing_calc(self):
        # Here is the point system to add the score for the bearing of targets
        if self.bearing >= 0 and self.bearing < 20:
            return 9
        elif self.bearing >= 20 and self.bearing < 40:
            return 7
        elif self.bearing >= 40 and self.bearing < 60:
            return 5
        elif self.bearing >= 60 and self.bearing < 80:
            return 3
        else:
            return 1

    def priority(self):
        # Calculates the priority score of each target
        self.priority_score = (self.range_calc() + self.speed_calc() +
                self.bearing_calc() + self.direction_calc())

        #print "Priority Score: ", self.priority_score

    def engage_target(self):
        engage_angle = int(self.bearing)  # - boat_angle

        if engage_angle >= 0 and engage_angle <= 180:
            s = engage_angle
            self.engage = ('Engage target turn \nCounterClockWise by \n %d degrees') % s

        elif engage_angle > 180 and engage_angle < 360:
            s = 360 - engage_angle
            self.engage = ('Engage target turn \nClockWise by \n %d degrees') % s

        elif engage_angle < 0 and engage_angle >= -180:
            s = -1 * engage_angle
            self.engage = ('Engage target turn \nClockWise by \n %d degrees') % s

        else:
            s = 360 + engage_angle
            self.engage = ('Engage target turn \nCounterClockWise by \n %d degrees') % s

    def to_engage(self):
        return self.engage

    def __str__(self):
        s = (self.object_type, self.range1, self.speed,
                self.angle, self.bearing)
        return ('Type: %20s\nRange: \t%8d\nSpeed: \t%10d\nElevation: \t%10d\nBearing: \t%10d') % s
