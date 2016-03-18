#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from time import sleep
from PyQt5.QtCore import pyqtSlot , QDir , QAbstractListModel , Qt , QModelIndex,QObject,QItemSelectionModel
from PyQt5.uic import loadUiType,loadUi
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QWidget,QApplication,QHBoxLayout,QDialog,QListView,QListWidget,QTableWidget,QTableView,QFileDialog,QTableWidgetItem,QWidget,QTreeView,QMainWindow,QPushButton 
from PyQt5.QtCore import QStringListModel
from PyQt5.QtGui import  QStandardItemModel , QStandardItem

# for development of pyCamera, use git version
libs_path = os.path.abspath('./../3rdparty/pyvisca')
print libs_path
sys.path.append(libs_path)

from pyvisca.PyVisca import Viscam

# a camera is created in visca_app
# create a visca bus object
cams = Viscam()
# get a list of serial ports available and select the last one
ports = cams.serial.listports()
port = None
for item in ports:
    if 'usbserial' in item:
        port = item
if not port:
    port = ports[0]
print('serial port opening : ' + port)
# open a connection on the serial object
cams.reset(port)

cams = cams.get_instances()
v = cams[0]

debug = True
update_run=False

# LOAD THE UI FILE GENERATED BY QT CREATOR / DESIGNER
filepath=os.getcwd()+'/visca.ui'
form_class, base_class = loadUiType(filepath)

class ViscaUI(QMainWindow, form_class):
    """create span view and controller (MVC)"""
    def __init__(self):
        super(ViscaUI, self).__init__()
        self.setupUi(self)
        self.pan_value = 0
        self.tilt_value = 0
        power = v._query('power') 
        self.power.setChecked(power)
        zoom = v._query('zoom')
        self.zoom_direct_value.setValue(zoom)
        self.zoom_tele_speed_label.setText(str(0))
        self.zoom_wide_speed_label.setText(str(0))
        focus = v._query('focus')
        self.focus_direct_value.setValue(focus)
        nearlimit = v._query('nearlimit')
        self.focus_nearlimit_value.setValue(nearlimit)
        pan,tilt = v._query('pan_tilt')
        self.tilt.setValue(tilt)
        self.pan.setValue(pan)
        # exposition parameters
        IR = v._query('IR')
        self.IR.setChecked(IR)
        AE = v._query('AE')
        self.AE.setCurrentText(AE)
        v.video = (720, 50)
        VIDEO = v._query('video')
        if AE != 'auto':
            aperture = v._query('aperture')
            if aperture:
                self.aperture.setCurrentIndex(aperture)
            iris = v._query('iris')
            if iris:
                self.iris.setCurrentIndex(iris)
            shutter = v._query('shutter')
            if shutter:
                self.shutter.setCurrentIndex(shutter)
            gain = v._query('gain')
            if gain:
                self.gain.setCurrentIndex(gain)
        if self.AE.currentText() == 'auto':
            self.AE_manual.setVisible(False)
    
    def on_AE_currentIndexChanged(self,mode):
        if type(mode) == unicode:
            mode = mode.encode('utf-8')
            v.AE = mode
            if mode == 'auto':
                self.AE_manual.setVisible(False)
            if mode == 'manual':
                self.AE_manual.setVisible(True)
                self.shutter.setVisible(True)
                self.shutter_label.setVisible(True)
                self.iris.setVisible(True)
                self.iris_label.setVisible(True)
                self.gain.setVisible(True)
                self.gain_label.setVisible(True)
            if mode == 'shutter':
                self.AE_manual.setVisible(True)
                self.shutter.setVisible(True)
                self.shutter_label.setVisible(True)
                self.iris.setVisible(False)
                self.iris_label.setVisible(False)
                self.gain.setVisible(False)
                self.gain_label.setVisible(False)
            if mode == 'iris':
                self.AE_manual.setVisible(True)
                self.iris.setVisible(True)
                self.iris_label.setVisible(True)
                self.shutter.setVisible(False)
                self.shutter_label.setVisible(False)
                self.gain.setVisible(False)
                self.gain_label.setVisible(False)

    def on_shutter_currentIndexChanged(self,index):
        if debug : print 'from UI :','SHUTTER',index
        if type(index) == unicode:
            print 'index is F…'
        else:
            v.shutter = index

    def on_iris_currentIndexChanged(self,index):
        if debug : print'from UI :','IRIS',index
        if type(index) == unicode:
            print 'index is F…'
        else:
            v.iris = index

    def on_gain_currentIndexChanged(self,index):
        if debug : print'from UI :','gain',index
        if type(index) == unicode:
            print 'gain is ', index, 'dB'
        else:
            v.gain = index

    def on_aperture_currentIndexChanged(self,index):
        if debug : print'from UI :','aperture',index
        if type(index) == unicode:
            print 'index is F…'
        else:
            v.aperture = index

    def on_slowshutter_currentIndexChanged(self,state):
        if type(state) == unicode:
            state = state.encode('utf-8')
        if state:
            if debug : print'from UI :','slowshutter',state
            v.slowshutter = 'auto'
        else:
            print 'SLOWSHUTTER MANUAL'
            v.slowshutter = 'manual'
    
    def on_IR_toggled(self,state):
        if debug : print'from UI :','IR',state
        v.IR = state

    def on_mem_recall_1_toggled(self,state):
        if debug : print'from UI :','memory_recall',0
        if state:
            v.memory_recall(0)
    def on_mem_recall_2_toggled(self,state):
        if debug : print'from UI :','memory_recall',1
        if state:
            v.memory_recall(1)
    def on_mem_recall_3_toggled(self,state):
        if debug : print'from UI :','memory_recall',2
        if state:
            v.memory_recall(2)
    def on_mem_recall_4_toggled(self,state):
        if debug : print'from UI :','memory_recall',3
        if state:
            v.memory_recall(3)
    def on_mem_recall_5_toggled(self,state):
        if debug : print'from UI :','memory_recall',4
        if state:
            v.memory_recall(4)

    def on_mem_set_1_toggled(self,state):
        if debug : print'from UI :','memory_set',0
        if state:
            v.memory_set(0)
    def on_mem_set_2_toggled(self,state):
        if debug : print'from UI :','memory_set',1
        if state:
            v.memory_set(1)
    def on_mem_set_3_toggled(self,state):
        if debug : print'from UI :','memory_set',2
        if state:
            v.memory_set(2)
    def on_mem_set_4_toggled(self,state):
        if debug : print'from UI :','memory_set',3
        if state:
            v.memory_set(3)
    def on_mem_set_5_toggled(self,state):
        if debug : print'from UI :','memory_set',4
        if state:
            v.memory_set(4)

    def on_power_toggled(self,state):
        if debug : print'from UI :','power' , state
        #visca_app.h_bool(state)
        v.power = state
    
    def on_zoom_tele_pressed(self):
        if debug : print'from UI :','zoom_tele'
        v.zoom_tele()

    def on_zoom_wide_pressed(self):
        if debug : print'from UI :','zoom_wide'
        v.zoom_wide()

    def on_zoom_stop_pressed(self):
        if debug : print'from UI :','zoom_stop'
        v.zoom_stop()
        zoom = v._query('zoom')
        self.zoom_direct_value.setValue(zoom)

    def on_zoom_tele_speed_valueChanged(self,speed):
        if debug : print'from UI :','zoom_tele_speed',speed
        v.zoom_tele_speed(speed)

    def on_zoom_wide_speed_valueChanged(self,speed):
        if debug : print'from UI :','zoom_wide_speed',speed
        v.zoom_wide_speed(speed)
    
    def on_zoom_direct_valueChanged(self,zoom):
        if debug : print'from UI :','zoom',zoom
        v.zoom = zoom

    def on_focus_mode_currentIndexChanged(self,mode):
        if type(mode) == unicode:
            mode = mode.encode('utf-8')
        if debug : print'from UI :','zoom_mode',mode
        v.focus_mode(mode)
        sleep(0.1)
        focus = v._query('focus')
        self.focus_direct_value.setValue(focus)
        sleep(0.1)
        nearlimit = v._query('nearlimit')
        self.focus_nearlimit_value.setValue(nearlimit)

    def on_focus_near_pressed(self):
        if debug : print'from UI :','focus_near'
        v.focus_near()

    def on_focus_far_pressed(self):
        if debug : print'from UI :','focus_far'
        v.focus_far()

    def on_focus_stop_pressed(self):
        if debug : print'from UI :','focus_stop'
        v.focus_stop()
        focus = v._query('focus')
        self.focus_direct_value.setValue(focus)

    def on_focus_near_speed_valueChanged(self,speed):
        if debug : print'from UI :','focus_near_speed',speed
        v.focus_near_speed(speed)

    def on_focus_far_speed_valueChanged(self,speed):
        if debug : print'from UI :','focus_far_speed',speed
        v.focus_far_speed(speed)
    
    def on_focus_direct_valueChanged(self, value):
        if debug : print'from UI :','focus', value
        v.focus = value
    
    def on_focus_nearlimit_valueChanged(self, nearlimit):
        if debug : print'from UI :','focus_nearlimit', nearlimit
        v.focus_nearlimit(nearlimit)

    def on_pan_speed_valueChanged(self,value):
        if debug : print'from UI :','pan_speed',value
        v.pan_speed(value)

    def on_tilt_speed_valueChanged(self,value):
        if debug : print'from UI :','tilt_speed',value
        v.tilt_speed(value)

    def on_pan_valueChanged(self,value):
        if debug : print'from UI :','pan',value
        value = int(value)
        v.pan(value)

    def on_tilt_valueChanged(self,value):
        if debug : print'from UI :','tilt',value
        value = int(value)
        v.tilt(value)

    def on_up_pressed(self):
        if debug : print'from UI :','up'
        v.up()

    def on_left_pressed(self):
        if debug : print'from UI :','left'
        v.left()

    def on_down_pressed(self):
        if debug : print'from UI :','down'
        v.down()

    def on_right_pressed(self):
        if debug : print'from UI :','right'
        v.right()

    def on_upleft_pressed(self):
        if debug : print'from UI :','upleft'
        v.upleft()

    def on_downleft_pressed(self):
        if debug : print'from UI :','downleft'
        v.downleft()

    def on_downright_pressed(self):
        if debug : print'from UI :','downright'
        v.downright()

    def on_upright_pressed(self):
        if debug : print'from UI :','upright'
        v.upright()
        
    def on_home_pressed(self):
        if debug : print'from UI :','home'
        v.home()
        
    def on_reset_pressed(self):
        if debug : print'from UI :','reset'
        v.reset()

    def on_stop_pressed(self):
        if debug : print'from UI :','stop'
        v.stop()
        pan,tilt = v._query('pan_tilt')
        self.tilt.setValue(tilt)
        self.pan.setValue(pan)

    def on_WB_currentIndexChanged(self,index):
        if type(index) == unicode:
            index = index.encode('utf-8')
            if debug : print'from UI :','WB',index
            v.WB(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    appWindow = ViscaUI()
    appWindow.move(5,12)
    appWindow.show()
    sys.exit(app.exec_())
    sdRef.close()