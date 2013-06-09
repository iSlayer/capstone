"""
Gui event handler
Author: David Ernest Lester
Date modified: 04/04/12

Interfaces with the GUIs events
"""

import time
import zmq
import events
import json

from PyQt4 import QtCore

START_TIME = 3
MISSILE_CAPACITY = 8


class Timer(QtCore.QThread):
    def __init__(self, wait, callback, *args, **kwargs):
        self.wait = wait
        self.callback = callback
        super(Timer, self).__init__(*args, **kwargs)

    def run(self):
        start_time = time.time()
        while (time.time() - start_time < self.wait):
            pass
        self.callback()


class GuiEventHandler(object):
    warming = False
    cooling = False
    ready = False
    radar_gui = None
    status = 'Stand By'
    cool_flag = False

    def __init__(self, *args, **kwargs):
        self.warmup_timer = Timer(START_TIME, self.warmed_up)
        self.coolup_timer = Timer(START_TIME, self.cooled_down)
        self.standby_timer = Timer(START_TIME, self.standby)
        self.status = 'Stand By'
        self.missile_count = 8

    def connect_radar_gui(self, radar_gui):
        self.radar_gui = radar_gui

    def status(self):
        return self.status

    def standby(self):
        self.status = 'Stand By'

    def warmup(self):
        if self.warming and not self.ready:
            self.status = 'Already Warming'
            return
        elif self.cooling:
            self.status = 'Still Cooling'
            return
        elif self.missile_count < 1:
            self.status = 'Out of Missiles'
            return
        elif self.ready:
            self.status = 'Already Warmed'
            return
        self.status = 'Warming Up'
        self.warming = True
        self.warmup_timer.start()

    def warmed_up(self):
        self.ready = True
        self.warming = False
        self.status = 'Armed'

    def cooldown(self):
        if self.ready and not self.warming:
            self.cooling = True
            self.coolup_timer.start()
            self.ready = False
            self.status = 'Cooling Down'
        elif self.warming:
            self.status = 'Still Warming'
        elif self.cooling:
            self.status = 'Still Cooling'
        else:
            self.status = 'In Standby Mode'

    def cooled_down(self):
        self.status = 'Cooled Down'
        self.cooling = False
        self.warming = False
        self.ready = False
        self.standby_timer.start()

    def launch(self):
        if not self.ready:
            self.status = 'Not Ready'
            return None

        active = self.radar_gui.target_list.get_active_target()
        target_id = active.identification

        if not target_id:
            self.status = 'Select Target'
            return None
        self.ready = False
        self.warming = False
        self.status = 'Firing'
        #print 'Killing %s' % target_id

        self.missile_count -= 1

        # Socket to send kill event back to the radar system
        context = zmq.Context()
        destroy_target = context.socket(zmq.PUSH)
        destroy_target.connect("tcp://localhost:3000")
        d = events.create_kill_event(str(target_id))
        destroy_target.send(json.dumps(d))
        destroy_target.close()
        self.standby_timer.start()

    def target_data(self):
        active = self.radar_gui.target_list.currentItem()
        target_id = active.txt()

    def reload_missile(self):
        self.missile_count = MISSILE_CAPACITY

    def display_missile_count(self):
        s = ('%s') % self.missile_count
        return s
