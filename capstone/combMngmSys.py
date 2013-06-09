"""
Combat Management System
Author: David Ernest Lester
Date modified: 04/16/12

Finds the targets coordinates and interacts with the GUI
"""

import zmq
import struct
import time
import json
import sys

import events

from target import Target
from gui import GuiEventHandler

from RadarGUI import RadarGUI
from PyQt4 import QtGui, QtCore


def main():
    # gui is our handler for Qt events.
    gui_event_handlers = GuiEventHandler()

    # Create our Qt application and initialize the main window.
    app = QtGui.QApplication(sys.argv)
    gui = RadarGUI(gui_event_handlers)

    # Create our combat widget so we can thread our combat management system
    cms = CombatManagementSystem(gui)
    gui.connect_slots(cms)
    cms.start()

    # Execute the Qt application (no ctrl+c now!)
    sys.exit(app.exec_())


class CombatManagementSystem(QtCore.QThread):
    def run(self):
        context = zmq.Context(1)

        # Setup socket to receive data from radar simulation
        receiver = context.socket(zmq.REP)
        receiver.bind("tcp://*:4001")

        # Socket to send message back to the radar simulation to  kill vehicle
        destroy_target = context.socket(zmq.PUB)
        destroy_target.connect("tcp://localhost:3000")

        # Dict of targets
        target_dict = {}

        self.target_list = []
        self.coordinate_list = []
        self.engagement_list = []

        while True:
            data = json.loads(receiver.recv())
            event = data['event']

            if event & events.EVENT_RADAR_OUTPUT:
                bearing, range1, angle, identification, dt = (
                        events.unpack_radar_output(data))

                # Add id to targets if not already there
                if identification not in target_dict:
                    target = Target(bearing, range1, angle, identification, dt)
                    target_dict[identification] = target

                # Update incoming cordinates and priority
                target_dict[identification].update(bearing, range1, angle, dt)
                target_dict[identification].priority()

                for target_key in target_dict.keys():
                    if target_dict[target_key].status():
                        del target_dict[target_key]

                # Prioritize list of targets automatically
                self.target_list = target_dict.values()
                self.target_list_sorted = sorted(self.target_list,
                        key = lambda target: target.priority_score,
                        reverse = True)

                for target_key in target_dict.keys():
                    self.coordinate_list.append(
                            target_dict[target_key].tuple_data())
                    #print 'Real: ', self.coordinate_list

                for target_key in target_dict.keys():
                    self.engagement_list.append(
                            target_dict[target_key].to_engage())

                self.emit(QtCore.SIGNAL('target_list'), self.target_list)
                receiver.send('ack!')

                self.emit(QtCore.SIGNAL('system_status'), None)

                self.emit(QtCore.SIGNAL('missile_count'), None)

                self.emit(QtCore.SIGNAL('paint_background'),
                        self.coordinate_list)

                self.emit(QtCore.SIGNAL('engagement_list'),
                        self.engagement_list)

                self.engagement_list = []
                self.coordinate_list = []


if __name__ == '__main__':
    main()
