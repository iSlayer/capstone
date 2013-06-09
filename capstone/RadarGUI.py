"""
RadarGUI
Author: David Ernest Lester
Date modified: 04/19/12

Creates a GUI that the user interacts with
"""

from PyQt4 import QtGui, QtCore

import pprint
import json
import zmq
import sys
import events
import numpy as np

imagePath = "image.png"


class ListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.targets = []
        self.engage_list = []
        self.setViewMode(QtGui.QListView.IconMode)
        self.setLayoutMode(QtGui.QListView.SinglePass)
        self.setResizeMode(QtGui.QListView.Adjust)
        self.setGridSize(QtCore.QSize(181, 70))

    def get_active_target(self):
        row = self.currentRow()
        return self.targets[row]


class RadarGUI(QtGui.QMainWindow):
    targets_priority = set()
    coordinates = []
    check = True

    def __init__(self, gui, *args, **kwargs):
        super(RadarGUI, self).__init__(*args, **kwargs)
        self.gui = gui
        self.gui.connect_radar_gui(self)
        self.init_ui()
        self.canvas = QtGui.QPainter(self)
        self.old_count = ''
        self.old_status = ''

    def init_ui(self):
        # Background box of Launch button
        self.box1 = QtGui.QLabel(self)
        self.box1.setGeometry(570, 470, 251, 171)
        self.box1.setStyleSheet("border:1px solid rgb(3, 0, 0);\n"
                "background-color: rgb(255, 255, 255);")

        # Background box of System status
        self.box2 = QtGui.QLabel(self)
        self.box2.setGeometry(290, 470, 281, 171)
        self.box2.setText("  Status:\n\n\n\n  Missile Count:")
        self.box2.setStyleSheet("border:1px solid rgb(3, 0, 0);\n"
                "background-color: rgb(255, 255, 255);")

        # Background box of selected target attributes
        self.box3 = QtGui.QLabel(self)
        self.box3.setStyleSheet("border:1px solid rgb(3, 0, 0);\n"
                "background-color: rgb(255, 255, 255);")
        self.box3.setPixmap(QtGui.QPixmap('raytheon.png'))
        self.box3.setGeometry(0, 470, 291, 171)

        # Target list txt box
        self.target_list_box = QtGui.QLabel(self)
        self.target_list_box.setGeometry(470, 0, 181, 31)
        self.target_list_box.setAlignment(QtCore.Qt.AlignCenter)
        self.target_list_box.setText("Target List")
        self.target_list_box.setStyleSheet("border:1px solid rgb(3, 0, 0);\n"
                "background-color: rgb(255, 255, 255);")

        # Target Engagement box
        self.target_engage_box = QtGui.QLabel(self)
        self.target_engage_box.setGeometry(650, 0, 171, 31)
        self.target_engage_box.setAlignment(QtCore.Qt.AlignCenter)
        self.target_engage_box.setStyleSheet("border:1px solid rgb(3, 0, 0);\n"
                "background-color: rgb(255, 255, 255);")
        self.target_engage_box.setText("Instructions to Engage")

        # Create a warm up button
        self.warmup = QtGui.QPushButton("Warm Up", self)
        self.warmup.setGeometry(590, 490, 101, 31)
        self.warmup.clicked.connect(self.gui.warmup)

        # Create a cool down button
        self.cooldown = QtGui.QPushButton("Cool Down", self)
        self.cooldown.setGeometry(700, 490, 101, 31)
        self.cooldown.clicked.connect(self.gui.cooldown)

        # Create launch buttons
        self.launch = QtGui.QPushButton("Launch", self)
        self.launch.setGeometry(640, 540, 121, 61)
        self.launch.clicked.connect(self.gui.launch)

        # Create reload button
        self.reload = QtGui.QPushButton("Reload", self)
        self.reload.setGeometry(470, 570, 71, 51)
        self.reload.clicked.connect(self.gui.reload_missile)

        # Target information, get list of targets from the radar subsystem
        self.target_list = ListWidget(self)
        self.target_list.setGeometry(470, 30, 181, 441)
        self.target_list.setStyleSheet('spacing: 15px')
        self.target_list.setAcceptDrops(False)
        self.target_list.setDragEnabled(False)

        # Target Priority List, get list of targets from the radar subsystem
        self.engagement_list = ListWidget(self)
        self.engagement_list.setGeometry(650, 30, 171, 441)
        self.engagement_list.setAcceptDrops(False)
        self.engagement_list.setDragEnabled(False)

        # Status label, gives the status of the system
        self.system_status = QtGui.QLabel(self)
        self.system_status.setGeometry(360, 510, 141, 41)
        self.system_status.setAlignment(QtCore.Qt.AlignCenter)
        self.system_status.setStyleSheet("border:1px solid rgb(3, 0, 0);\n"
                "background-color: rgb(255, 255, 255);")

        # Missile count
        self.missile_count = QtGui.QLabel(self)
        self.missile_count.setGeometry(410, 570, 41, 41)
        self.missile_count.setAlignment(QtCore.Qt.AlignCenter)
        self.missile_count.setStyleSheet("border:1px solid rgb(3, 0, 0);\n"
                "background-color: rgb(255, 255, 255);")

        # Initialize our status bar and set the window geometries
        self.statusBar()
        self.setGeometry(0, 0, 842, 658)
        self.setWindowTitle('Radar GUI')
        self.show()

    def connect_slots(self, sender):
        # Initialize our signals
        self.connect(sender, QtCore.SIGNAL('target_list'),
                self.update_target_list)

        self.connect(sender, QtCore.SIGNAL('engagement_list'),
                self.update_engagement_list)

        self.connect(sender, QtCore.SIGNAL('system_status'),
                self.update_system_status)

        self.connect(sender, QtCore.SIGNAL('missile_count'),
                self.update_missile_count)

        self.connect(sender, QtCore.SIGNAL('paint_background'),
                self.save_coordinates)

    def update_target_list(self, targets):
        if self.target_list.targets != targets:
            self.target_list.clear()
            self.target_list.targets = []
            for target in targets:
                self.target_list.targets.append(target)
                self.target_list.addItem(str(target))
        else:
            for pk, target in enumerate(self.target_list.targets):
                self.target_list.item(pk).setText(str(target))

    def update_engagement_list(self, engage_list):
        if self.engagement_list.engage_list != engage_list:
            self.engagement_list.clear()
            self.engagement_list.engage_list = []
            for direction in engage_list:
                self.engagement_list.engage_list.append(direction)
                self.engagement_list.addItem(direction)
        else:
            for pk, direction in enumerate(self.engagement_list.engage_list):
                self.engagement_list.item(pk).setText(direction)

    def update_system_status(self):
        status = self.gui.status
        if status != self.old_status:
            self.system_status.clear()
            self.system_status.setText(status)
            self.old_status = status

    def update_missile_count(self):
        count = self.gui.display_missile_count()
        if count != self.old_count:
            self.missile_count.clear()
            self.missile_count.setText(count)
            self.old_count = count

    def paintEvent(self, pEvt):
        # Radar paint background
        self.canvas = QtGui.QPainter(self)
        self.canvas.begin(self)

        self.update()
        pic = QtGui.QPixmap(imagePath)
        self.canvas.setRenderHint(self.canvas.Antialiasing)
        self.canvas.drawPixmap(0, 0, pic)

        # Scaling parameters to match the GUIs pixels
        k1 = 215. / 20000
        k2 = 245. / 20000
        ds1 = 245
        ds2 = 20000

        if self.coordinates:
            for x, y in self.coordinates:
                x = int(x)
                y = int(y)

                if y >= 0:
                    if x >= 0:
                        self.paint_target(k1 * x + ds1, k2 * np.abs(y - ds2))
                    else:
                        self.paint_target(k2 * x + ds1, k2 * np.abs(y - ds2))
                else:
                    if x <= 0:
                        self.paint_target(k2 * x + ds1, k1 * np.abs(y) + 245)
                    else:
                        self.paint_target(k1 * x + ds1, k1 * np.abs(y) + 245)

        self.canvas.end()

    def save_coordinates(self, coordinates):
        # Save new list of coordinates
        self.coordinates = coordinates

    def paint_target(self, x, y):
        if self.check:
            pic = QtGui.QPixmap(imagePath)
            self.canvas.drawPixmap(0, 0, pic)
            self.canvas.SmoothPixmapTransform
            self.check = False

        self.canvas.setBrush(1000)

        self.canvas.setViewTransformEnabled(True)
        self.canvas.fillRect(x, y, 10, 10, QtCore.Qt.red)

        return None
