import os
import sys
import usb
sys.path.append('C:/Users/Laser-Arpes/Desktop/SHADAB/RunFROG')

import stellarnetLib, functions
import plotgui_lib as plg
import gl3_esp300 as esp

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QMessageBox
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import FROG_GUI
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
import scipy as sp
from scipy.optimize import curve_fit
import tables
import numpy as np
import time
from datetime import date
import fnmatch
from drawnow import drawnow


class TheMainWindow(QMainWindow, FROG_GUI.GUI):

    # initializes the main GUI and adds the animated figure into it
    def __init__(self):
        try:
            self.selected_model={ \
                    'iProduct':'0',
                    'iManufacturer':'0',
                    'idProduct':'0',
                    'idVendor':'0',
            }
            super(TheMainWindow, self).__init__()
            self.setup_GUI(self)  # sets up layout and widgets that are defined in design.py
            self.spectrometer=None
            self.initialized=False
            kk=0
            self.animatedAxes = AnimationCanvas()  # initialize animation routine
            self.layout.addWidget(self.animatedAxes)  # create animation axes
            self.instr_list.activated.connect(self.instrumentChanged)

            self.startbtn.clicked.connect(self.start) 
            self.timeZerobtn.clicked.connect(self.goto_time_zero)
            #self.stopbtn.clicked.connect(self.stop)
            self.plot_button.clicked.connect(self.plot_2D_data)

            self.closebtn.clicked.connect(self.close_app)  # When the Close button is pressed
            self.savebtn.clicked.connect(self.save_trace_to_file)
            self.path_list.returnPressed.connect(self.set_path)
            self.get_bgrnd_btn.clicked.connect(self.animatedAxes.take_background)
            self.show()
            
            self.updateDeviceList()
            self.integr_SpinBox.editingFinished.connect(self.integrationTime)
            self.wv=np.asarray([3,])
            self.data=np.asarray([3,])
            self.animatedAxes.importData(self.wv,self.data)

            self.radiobutton1.toggled.connect(self.radiobutton1_clicked)
            self.radiobutton2.toggled.connect(self.radiobutton2_clicked)
            

        except:
            print('No spectrometer found')
            pass

    def updateDeviceList(self):
        if self.spectrometer:#self.selected_model['iManufacturer']=='Seabreeze':
            functions.close(self.spectrometer)
        self.instr_list.clear()
        self.instr_list.addItem('Instruments:')
        self.device_models,self.device_list=functions.find_devices()
        for ii in range(1,(1+len(self.device_models))): 
            self.instr_list.addItem(self.device_models[str(ii)]['idVendor']+':'+self.device_models[str(ii)]['idProduct'])

    def wait_until(self,period=1):
        while self.initialized==False:
            time.sleep(period)

    def close_app(self):
        functions.close(self.spectrometer)  # closes window
        self.close()

    def instrumentChanged(self):
        if self.instr_list.currentIndex()==0:
            currentrow=1
        else:
            currentrow=self.instr_list.currentIndex()
        if self.instr_list.itemText((currentrow))==(self.selected_model['idVendor']+':'+self.selected_model['idProduct']):
            pass
        else:
            try:
                self.updateDeviceList()
            except:
                pass
            self.spectrometer,self.selected_model=functions.select_device(currentrow,self.device_models,self.device_list)
            self.wv=functions.getWv(self.spectrometer)
            self.integrationTime()
            self.acquireData()
            self.initialized=True

    def acquireData(self):
        self.data=functions.getdata(self.spectrometer)
        return self.data

    def integrationTime(self):
        integr=self.integr_SpinBox.value()
        functions.update_integration_time(self.spectrometer,integr)

    def set_path(self):
        self.ppathh=self.path_list.text()
        return self.ppathh

    def goto_time_zero(self):
        stage = esp.gl_esp300()
        stage.open()
        if self.radiobutton1.isChecked():
            stage.moveA(self.timeZeroSpinBox.value())

        if self.radiobutton2.isChecked():
            stage.moveA(self.convert_to_length_unit(self.timeZeroSpinBox.value()))
            
        stage.close()
    
    def start(self):
        start_time = time.time()
        stage = esp.gl_esp300()

        if self.radiobutton1.isChecked():
            self.trange=self.timeRangeSpinBox.value()
            self.delay_step=self.timeStepSpinBox.value()
            self.delay_0=self.timeZeroSpinBox.value()
            self.delay_min = self.delay_0 - self.trange
            self.delay_max = self.delay_0 + self.trange
        elif self.radiobutton2.isChecked():
            self.trange=self.convert_to_length_unit(self.timeRangeSpinBox.value())
            self.delay_step=self.convert_to_length_unit(self.timeStepSpinBox.value())
            self.delay_0=self.convert_to_length_unit(self.timeZeroSpinBox.value())
            self.delay_min = self.delay_0 - self.trange
            self.delay_max = self.delay_0 + self.trange


        delay = self.delay_min
        self.trace = np.array([])

        while delay < (self.delay_max+0.001):

            print(delay)
            stage.open()
            stage.moveA(delay)
            self.add_spectrum_to_trace()
            stage.close()
            delay += self.delay_step

        self.goto_time_zero()

        self.plot_2D_data()
        self.plot_button.setEnabled(True)

        elapsed = time.time() - start_time

        print("Total time taken (in s) = ",  elapsed)

    def make_delay_array(self):

        delay_array = []

        if self.radiobutton1.isChecked():
            delay_0 = self.convert_to_time_unit(self.timeZeroSpinBox.value())
            delay_step = self.convert_to_time_unit(self.timeStepSpinBox.value())
            trange = self.convert_to_time_unit(self.timeRangeSpinBox.value())
            delay_min = delay_0 - trange
            delay_max = delay_0 + trange

            delay = delay_min
            while delay < delay_max + 0.001:
                delay_array = np.append(delay_array, [delay])
                delay += delay_step

        elif self.radiobutton2.isChecked():
            delay_0 = self.timeZeroSpinBox.value()
            delay_step = self.timeStepSpinBox.value()
            trange = self.timeRangeSpinBox.value()
            delay_min = delay_0 - trange
            delay_max = delay_0 + trange

            delay = delay_min
            while delay < delay_max + 0.001:
                delay_array = np.append(delay_array, [delay])
                delay += delay_step

        for i in range(len(delay_array)):
            delay_array[i] = delay_array[i] - delay_0

        print(delay_array)
        return delay_array


    def add_spectrum_to_trace(self):
        spectrum=self.acquireData()-self.animatedAxes.background
        if self.trace.size == 0:
            self.trace = np.array(spectrum)
        else:
            self.trace = np.column_stack((self.trace, np.array(spectrum)))
        
    

    def plot_2D_data(self):
        
        delay_array = self.make_delay_array()
        
        wv_min_pixel_index = sp.argmin(abs(self.wv - self.wavelength_minSpinBox.value()))
        wv_max_pixel_index = sp.argmin(abs(self.wv - self.wavelength_maxSpinBox.value()))

        del_min_pixel_index = sp.argmin(abs(delay_array - self.delay_minSpinBox.value()))
        del_max_pixel_index = sp.argmin(abs(delay_array - self.delay_maxSpinBox.value()))

        print(del_min_pixel_index)
        print(del_max_pixel_index)

        if self.radiobutton1.isChecked():
            self.delay_minSpinBox.setProperty("value", self.convert_to_time_unit(-self.trange))
            self.delay_maxSpinBox.setProperty("value", self.convert_to_time_unit(self.trange))
        elif self.radiobutton2.isChecked():
            self.delay_minSpinBox.setProperty("value", -self.trange)
            self.delay_maxSpinBox.setProperty("value", self.trange)

        self.animatedAxes.ax2.set_ylim([self.wv[wv_min_pixel_index], self.wv[wv_max_pixel_index]])
        self.animatedAxes.ax2.set_xlim([self.delay_minSpinBox.value(), self.delay_maxSpinBox.value()])
        
        trace_cropped = self.trace[wv_min_pixel_index:wv_max_pixel_index, del_min_pixel_index: del_max_pixel_index]

        self.animatedAxes.ax2.imshow(np.flipud(trace_cropped), aspect="auto",
                                     extent=(self.delay_minSpinBox.value() ,self.delay_maxSpinBox.value(), 
                                        self.wv[wv_min_pixel_index], self.wv[wv_max_pixel_index]), cmap='jet')



    def save_trace_to_file(self):
        try:
            self.set_path()
            if (self.ppathh[-1]=='\\'):
                datefolder=date.today().strftime('%Y_%m_%d\\')
                print("flag1")
            else:
                datefolder=date.today().strftime('\\%Y_%m_%d\\')
                print("flag2")

            ppath=str(self.ppathh+datefolder)
            try:
                os.mkdir(ppath)
            except:
                pass

            lastfile='000000000'
            numm=0
            for file in os.listdir(ppath):
                if fnmatch.fnmatch(file, 'sp*.txt'):
                    lastfile=list(file)
                    numm=int(''.join(lastfile[2:-4]))

            
            if self.animatedAxes.save_file_num < numm:
                self.animatedAxes.save_file_num = numm + 1

            if self.ASCII_chkBox.isChecked():
                np.savetxt(str(ppath+"sp"+str(self.animatedAxes.save_file_num)+".txt"), self.trace)
            else:
                np.save(str(ppath+"sp"+str(self.animatedAxes.save_file_num)), self.trace)

            self.animatedAxes.save_file_num+=1
            self.savebtn.setChecked(False)
        except:
            QMessageBox.about(self,"Error","Wrong path! Use existing directory, e.g 'C:\Data\'")
            pass
    

    def convert_to_time_unit(self, stage_delay):
        total_path_delay = 2*stage_delay
        total_time_delay = (float(total_path_delay/2.998))*(10**4)
        return total_time_delay

    def convert_to_length_unit(self, total_time_delay):
        total_path_delay = (2.998*total_time_delay)*(10**(-4))
        stage_delay = float(total_path_delay/2)
        return stage_delay
        
    def radiobutton1_clicked(self, enabled):
        if enabled:
            self.timeZeroSpinBox.setProperty("value", self.convert_to_length_unit(self.timeZeroSpinBox.value()))
            self.timeRangeSpinBox.setProperty("value", self.convert_to_length_unit(self.timeRangeSpinBox.value()))
            self.timeStepSpinBox.setProperty("value", self.convert_to_length_unit(self.timeStepSpinBox.value()))
    def radiobutton2_clicked(self, enabled):
        if enabled:
            self.timeZeroSpinBox.setProperty("value", self.convert_to_time_unit(self.timeZeroSpinBox.value()))
            self.timeRangeSpinBox.setProperty("value", self.convert_to_time_unit(self.timeRangeSpinBox.value()))
            self.timeStepSpinBox.setProperty("value", self.convert_to_time_unit(self.timeStepSpinBox.value()))

    
class AnimationCanvas(FigureCanvas, TimedAnimation):

    # initializes the animated figure and initializes the animation procedure
    def __init__(self):
        # initialize two data sets into linear vectors of given size
        self.background=0
        self.xdt1 = np.linspace(0, 1023, 1024) * 0
        self.ydt1 = self.xdt1
        self.arraysize=len(self.xdt1)
        self.maxyval=0
        self.save_file_num=0
        self.timestamp=time.time()
        self.filename="0"

        # Create animation axes as figure, later to be embedded into parent figure
        self.fig = Figure(figsize=(5, 5.3), dpi=100)
        self.ax1 = plg.aaxes(self, self.fig, position=[.08, .1, .45, .85], ffontsize=10, ffontweight='bold', llinewidth=3, xxlabel='Wavelength (nm)', yylabel='Signal (A.U.) ', ttitle='Spectrum', xxscale='linear', yyscale='linear', xticklbl=None, yticklbl=None)
        # initialize two lines for stage coordinate and for signal
        self.line1 = Line2D([], [], color='blue')
        self.line2 = Line2D([], [], color='red', linestyle=':')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line2)
        self.ax1.yaxis.label.set_color('blue')

        self.ax2 = plg.aaxes(self, self.fig, position=[.63, .1, .35, .85], ffontsize=10, ffontweight='bold',llinewidth=3, xxlabel='Delay (fs)', yylabel='Wavelength (nm)',
         ttitle='FROG Trace', xxscale='linear', yyscale='linear', xticklbl=None, yticklbl=None)


        # start animation with interval of xx milliseconds
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=1, blit=True)

    # not sure what it does, but it must take the integer vector of length(data)
    def new_frame_seq(self):
        return iter(range(self.arraysize))

    # not sure what it does
    def _init_draw(self):
        self.line1.set_data(self.xdt1, self.ydt1)
        # self.line2.set_data(self.xdt2, self.ydt2)
    
    def importData(self, wl,sp):
        self.xdt1=wl
        self.ydt1=sp-self.background
        self.arraysize=len(sp)
        print(self.arraysize)
    
    def take_background(self):
        self.background=sum(myGUI.acquireData())/len(myGUI.acquireData())
        print(self.background)
    
    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            # self.abc += 1
            # print(str(self.abc))
            TimedAnimation._stop(self)
            pass
    
    def _draw_frame(self, framedata):
        try:
            try:
                myGUI.ppathh
            except:
                myGUI.set_path()
            spectrum=myGUI.acquireData() - self.background
            self.wv_ax=myGUI.wv
            self.plot_spectrum(spectrum)

            if myGUI.measure_chkBox.isChecked():
                self.dt=myGUI.measure_SpinBox.value()
                if time.time()>self.timestamp+self.dt:
                    self.filename = str(myGUI.ppathh+"sp_array_"+str(self.save_file_num)+'.h5')
                    if os.path.exists(self.filename):
                        f = tables.open_file(self.filename, mode='a')
                        f.root.data.append(spectrum)
                        f.close()
                    else:
                        data_to_save=np.row_stack((self.wv_ax, spectrum))
                        f = tables.open_file(self.filename, mode='w')
                        data_format = tables.Float64Atom()
                        array_c = f.create_earray(f.root, 'data', data_format,(0,))
                        array_c.append(self.wv_ax)
                        array_c.append(spectrum)
                        f.close()
                    self.timestamp=time.time()
        except:
            pass


    def plot_spectrum(self,spectrum):
        if myGUI.logsc_chkBox.isChecked():
            minlevel=np.min(spectrum[np.where(spectrum > 0)])
            spectrum[np.where(spectrum <= 0)]=minlevel
            self.ax1.set_yscale('log')
        else:
            self.ax1.set_yscale('linear')

        self.line1.set_data(self.wv_ax, spectrum)
        if myGUI.maxsc_chkBox.isChecked():
            self.maxyval=max(self.maxyval,max(spectrum))
            self.ax1.set_ylim(min(spectrum),self.maxyval) 
        elif myGUI.ysc_chkBox.isChecked():
            self.ax1.set_ylim((myGUI.min_ySpinBox.value(), myGUI.max_ySpinBox.value()))
            self.maxyval=0
        else:
            self.ax1.set_ylim(min(spectrum[1:]), max(spectrum))
            self.maxyval=0
    

        if myGUI.xsc_chkBox.isChecked():
            self.ax1.set_xlim((myGUI.min_xSpinBox.value(), myGUI.max_xSpinBox.value()))
        else:
            self.ax1.set_xlim(min(self.wv_ax), max(self.wv_ax))

        if myGUI.FWHM_chkBox.isChecked():
            pars=self.FWHM_fit(self.wv_ax,spectrum)
            self.line2.set_data(self.wv_ax, self.FWHMfitData)
            FWHMw=2*np.sqrt(2*np.log(2))*pars[2]
            FWHMt_gaus=0.44/( (1e7/(pars[1]-FWHMw/2)-1e7/(pars[1]+FWHMw/2))*2.99792e10*1e-15)
            FWHMt_sec=0.315/( (1e7/(pars[1]-FWHMw/2)-1e7/(pars[1]+FWHMw/2))*2.99792e10*1e-15)
            self.ax1.legend([str(int(pars[1]))+' nm, FWHM='+str(int(FWHMw))+'nm / '+str(int(FWHMt_gaus))+'fs / '+str(int(FWHMt_sec))+'fs'], fontsize=13, loc=1, bbox_to_anchor = (0.99, 1.0))
        else:
            self.line2.set_data([], [])
            self.ax1.legend_=None
    
    def FWHM_fit(self,xdata,ydata):
        maxval=max(ydata)
        maxpos=np.argmax(ydata)
        FWHM01=(np.abs(ydata[:maxpos]-maxval/2)).argmin()
        FWHM02=(np.abs(ydata[maxpos:]-maxval/2)).argmin()+maxpos
        x0=[maxval,xdata[maxpos],(xdata[FWHM02]-xdata[FWHM01]),ydata[2]]
        [popt, pcov] = curve_fit(self.gaus_fun, xdata, ydata, p0=x0)
        self.FWHMfitData= (self.gaus_fun(xdata, *popt))
        return popt
    
    def gaus_fun(self,x, *p):
        [a,x0,sigma,background]=p
        calc_data=background+a*np.exp(-(x-x0)**2/(2*sigma**2))
        return(calc_data)
    
    def save_data(self):
        try:
            wv_ax=myGUI.wv
            spectrum=myGUI.acquireData()-self.background

            myGUI.set_path()
            if (myGUI.ppathh[-1]=='\\'):
                datefolder=date.today().strftime('%Y_%m_%d\\')
            else:
                datefolder=date.today().strftime('\\%Y_%m_%d\\')

            ppath=str(myGUI.ppathh+datefolder)
            try:
                os.mkdir(ppath)
            except:
                # QMessageBox.about(self,"Error1",str("Directory "+ppath+" already exsist or the path is wrong!")
                pass
            data_to_save=np.column_stack((wv_ax, spectrum))
            lastfile='000000000'
            numm=0
            for file in os.listdir(ppath):
                if fnmatch.fnmatch(file, 'sp*.txt'):
                    lastfile=list(file)
                    numm=int(''.join(lastfile[2:-4])) 
                    # print(numm,int(numm))
            if self.save_file_num<numm:
                print(numm)
                self.save_file_num=numm+1
            if myGUI.ASCII_chkBox.isChecked():
                np.savetxt(str(ppath+"sp"+str(self.save_file_num)+".txt"), data_to_save)

            else:
                np.save(str(ppath+"sp"+str(self.save_file_num)), data_to_save)
            #img = PIL.ImageGrab.grab()
            #img.save(str(ppath+"sp"+str(self.save_file_num)+".jpg"))
            self.save_file_num+=1
            myGUI.savebtn.setChecked(False)
        except:
            QMessageBox.about(self,"Error","Wrong path! Use existing directory, e.g 'C:\Data\'")
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = TheMainWindow()

    sys.exit(app.exec_())

