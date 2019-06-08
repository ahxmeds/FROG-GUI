import plotgui_lib as plg
from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QWidget, QPushButton
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class GUI(object):
    def setup_GUI(self, MWindow):
        canvas_width = 1200
        canvas_height = 600
  
        [self.fig, self.main_widget, self.canvas, self.layout] = plg.ffigure(self, position=[50, 10, canvas_width, canvas_height])

        #Instrument List dropdown menu
        self.instr_list = plg.ddropdownwidget(self, self.main_widget, position=[15, 15, 90, 23], llist=["Instrument:"], ffontsize=10, ccolor="blue")

        #Background subtraction button
        self.get_bgrnd_btn = plg.bbutton(self, self.main_widget, position=[15, 50, 90, 23], Text="Background", ffontsize=9, ffontbold=True)
        self.get_bgrnd_btn.setStyleSheet("color: black; background-color: QColor(20, 240, 220, 127)")

        #Start button
        self.startbtn = plg.bbutton(self, self.main_widget, position=[15, 80, 60, 23], Text="Start", ffontsize = 11, ffontbold=True)
        self.startbtn.setStyleSheet("color: black; background-color: green")

        #Stop button
        self.stopbtn = plg.bbutton(self, self.main_widget, position=[15, 110, 60, 23], Text="Stop", ffontsize = 11, ffontbold=True)
        self.stopbtn.setStyleSheet("background-color: red")

        #Y-Scale checkbox
        self.ysc_chkBox = plg.ccheckbox(self, self.main_widget, position=[130, 15, 130, 23], Text="Y scale:", ffontsize=8, ccolor="blue")
        self.ysc_chkBox.setChecked(True)
        #X-Scale checkbox
        self.xsc_chkBox = plg.ccheckbox(self, self.main_widget, position=[130, 40, 130, 23], Text="X scale:", ffontsize=8, ccolor="blue")        
        self.xsc_chkBox.setChecked(True)
        #MaxScale checkbox
        self.maxsc_chkBox = plg.ccheckbox(self, self.main_widget, position=[130, 75, 130, 23], Text="MaxScale", ffontsize=8, ccolor="blue")
        self.maxsc_chkBox.setChecked(False)
        #LogScale checkbox
        self.logsc_chkBox = plg.ccheckbox(self, self.main_widget, position=[130, 95, 130, 23], Text="LogScale", ffontsize=8, ccolor="blue")
        self.logsc_chkBox.setChecked(False)
        #FWHM checkbox
        self.FWHM_chkBox = plg.ccheckbox(self, self.main_widget, position=[130, 115, 130, 23], Text="FWHM", ffontsize=8, ccolor="blue")
        self.FWHM_chkBox.setChecked(False)

        #Y-Range spinboxes
        self.min_ySpinBox = plg.eeditdblbox(self, self.main_widget, position=[200, 15, 60, 20], value=-200, ccolor="blue", bbuttonsymbol=2,decims=1)
        self.max_ySpinBox = plg.eeditdblbox(self, self.main_widget, position=[273, 15, 60, 20], value=20000, ccolor="blue", bbuttonsymbol=2, decims=1)
        #X-Range spinboxes
        self.min_xSpinBox = plg.eeditdblbox(self, self.main_widget, position=[200, 40, 60, 20], value=350, ccolor="blue", bbuttonsymbol=2, decims=1)
        self.max_xSpinBox = plg.eeditdblbox(self, self.main_widget, position=[273, 40, 60, 20], value=550, ccolor="blue", bbuttonsymbol=2, decims=1)
        #hyphens
        text_hyphenx =  plg.llabel(self, self.main_widget, position=[264, 15, 5, 20], sstring="--", ffontsize=10)
        text_hypheny =  plg.llabel(self, self.main_widget, position=[264, 40, 5, 20], sstring="--", ffontsize=10)


        #Integration time editbox
        text_IntegrationTime = plg.llabel(self, self.main_widget, position=[360, 15, 90, 20], sstring="Integration (ms):", ffontsize=8)
        self.integr_SpinBox = plg.eeditintbox(self, self.main_widget, position=[451, 15, 40, 20], value=10,rrange=[1, 2000])
        #Number of spectrum capture
        text_Nexp = plg.llabel(self, self.main_widget, position=[406, 40, 40, 20], sstring="N exp:", ffontsize=8)
        self.Nexp_SpinBox = plg.eeditintbox(self, self.main_widget, position=[451, 40, 40, 20], value=1,rrange=[1, 2000])


        #Time Zero button and spinbox
        self.timeZerobtn = plg.bbutton(self, self.main_widget, position=[345, 70, 70, 20], Text="Time Zero", ffontsize = 8, ffontbold=True)
        self.timeZeroSpinBox = plg.eeditdblbox(self, self.main_widget, position=[425, 70, 65, 20], value=12.6400, ccolor="blue", bbuttonsymbol=2, decims=5)
        colon_timeZero =  plg.llabel(self, self.main_widget, position=[417, 70, 5, 20], sstring=":", ffontsize=10)


        #Stage position indicator label
        self.PositionIndicator1 = plg.llabel(self, self.main_widget, position=[410, 100, 200, 40], sstring="0", ffontsize=20, ffontbold=True, ccolor='red')
        

        #Time Range spinbox
        text_timeRange = plg.llabel(self, self.main_widget, position=[561, 15, 80, 20], sstring="Range:", ffontsize=8)
        self.timeRangeSpinBox = plg.eeditdblbox(self, self.main_widget, position=[607, 15, 65, 20], value=0.1000, ccolor="blue", bbuttonsymbol=2, decims=4)
        #Time Step spinbox
        text_timeStep = plg.llabel(self, self.main_widget, position=[545, 40, 80, 20], sstring="Time Step:", ffontsize=8)
        self.timeStepSpinBox = plg.eeditdblbox(self, self.main_widget, position=[607, 40, 65, 20], value=0.05, ccolor="blue", bbuttonsymbol=2, decims=4)
        
        
        #Radiobutton for mm/fs
        self.radiobutton_mm = plg.rradiobutton(self, self.main_widget, position=[545, 70, 130, 20], ffontsize=8,  Text='mm', sstate=True)
        self.radiobutton_fs = plg.rradiobutton(self, self.main_widget, position=[620, 70, 130, 20], ffontsize=8, Text='fs', sstate=False)

        #Grouping radiobuttons for mm/fs under one group
        self.mm_fs_group = QtWidgets.QButtonGroup(self.main_widget)
        self.mm_fs_group.addButton(self.radiobutton_mm)
        self.mm_fs_group.addButton(self.radiobutton_fs)



        #Wavelength range spinboxes for the trace plot
        text_wavelength_range = plg.llabel(self, self.main_widget, position=[744, 15, 120, 20], sstring="Wavelength Range (nm):", ffontsize=8)
        self.wavelength_minSpinBox = plg.eeditdblbox(self, self.main_widget, position=[875, 15, 65, 20], value=350, ccolor="blue", bbuttonsymbol=2, decims=1)
        self.wavelength_maxSpinBox = plg.eeditdblbox(self, self.main_widget, position=[953, 15, 65, 20], value=550, ccolor="blue", bbuttonsymbol=2, decims=1)
        text_hyphen_wv =  plg.llabel(self, self.main_widget, position=[944, 15, 5, 20], sstring="--", ffontsize=10)


        #Delay range spinboxes for the trace plot
        text_delay_range = plg.llabel(self, self.main_widget, position=[779, 40, 100, 20], sstring="Delay Range (fs):", ffontsize=8)
        self.delay_minSpinBox = plg.eeditdblbox(self, self.main_widget, position=[875, 40, 65, 20], value=0, ccolor="blue", bbuttonsymbol=2, decims=4)
        self.delay_maxSpinBox = plg.eeditdblbox(self, self.main_widget, position=[953, 40, 65, 20], value=0, ccolor="blue", bbuttonsymbol=2, decims=4)
        text_hyphen_delay =  plg.llabel(self, self.main_widget, position=[944, 40, 5, 20], sstring="--", ffontsize=10)
        

        #Update trace plot button
        self.plot_button = plg.bbutton(self, self.main_widget, position=[1031, 15, 55, 45], Text="Update\nTrace", ffontsize=10, ffontbold=True, eenable=False)


        #Close button
        self.closebtn = plg.bbutton(self, self.main_widget, position=[1126, 15, 60, 23], Text="Close", ffontsize=11, ffontbold=True)
        self.closebtn.setStyleSheet("background-color: red")
        #Save button
        self.savebtn = plg.bbutton(self, self.main_widget, position=[1126, 43, 60, 23], Text="Save", ffontsize=11, ffontbold=True)
        self.savebtn.setCheckable(True)
        self.savebtn.toggle()

        #Path for file saving
        path = plg.llabel(self, self.main_widget, position=[769, 100, 30, 20], sstring="Path:", ffontsize=8)
        self.path_list = plg.llineedit(self, self.main_widget, position=[805, 100, 280, 20], sstring="C:/Users/Laser-Arpes/Desktop/SHADAB/RunFROG", ffontsize=10, ccolor="blue")


       
        #Radiobuttons for saving in Trebino/Matlab format
        self.radiobutton_trebino = plg.rradiobutton(self, self.main_widget, position=[1125, 80, 60, 23], Text="Trebino", ffontsize=8, sstate=True)
        self.radiobutton_matlab  = plg.rradiobutton(self, self.main_widget, position=[1125, 100, 60, 23], Text="Matlab", ffontsize=8, sstate=False)

        #Grouping radiobuttons for Trebino/Matlab under one group
        self.save_group = QtWidgets.QButtonGroup(self.main_widget)
        self.save_group.addButton(self.radiobutton_trebino)
        self.save_group.addButton(self.radiobutton_matlab)


        QtCore.QMetaObject.connectSlotsByName(MWindow)

