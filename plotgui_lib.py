from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QGridLayout, QGroupBox

import matplotlib
matplotlib.use("QT5Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.widgets import Button, TextBox

import numpy as np


def ffigure(self, position=[100, 100, 500, 500]):
    self.fig = Figure()
    self.move(position[0], position[1])
    self.resize(position[2], position[3])
    self.fig.set_size_inches(position[2] / self.fig.dpi, position[3] / self.fig.dpi)
    plt.ion()

    self.canvas = FigureCanvas(self.fig)

    self.main_widget = QWidget(self)
    self.setCentralWidget(self.main_widget)

    self.layout = QGridLayout()
    self.layout.addWidget(self.canvas, 1, 0, 5, 1)
    self.main_widget.setLayout(self.layout)

    # matplotlib.interactive(self)
    #return (self.main_widget, self.layout)
    return(self.fig, self.main_widget, self.canvas, self.layout)


def aaxes(self, fig, position=[10, 10, 500, 500], ffontsize=10, ffontweight='normal', llinewidth=3,
 xxlabel='x label', yylabel='y label', ttitle='Title', xxscale='linear', yyscale='linear', xticklbl=[-5, 0, 5], yticklbl=None, xlim=[-6, 9]):
    ax = fig.add_axes(position)
    ax.cla()
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(llinewidth)
        # self.ax.spines[axis].set_color('g')
    for item in ([ax.xaxis.label, ax.yaxis.label, ax.title] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(ffontsize)
        item.set_fontweight(ffontweight)
    ax.tick_params(width=1, direction='in', length=6)
    ax.set_xlabel(xxlabel)
    ax.set_ylabel(yylabel)
    ax.set_title(ttitle, fontsize=ffontsize, fontweight=ffontweight)
    ax.set_xscale(xxscale)
    ax.set_yscale(yyscale)
    ax.set_xlim(xlim)
    if xticklbl:
        ax.set_xticklabels(xticklbl)
    if yticklbl:
        ax.set_yticklabels(yticklbl)
    return(ax)



def bbutton(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, Text='Ok',eenable=True):
    btn = QtWidgets.QPushButton(Text, main_widget)
    btn.setEnabled(eenable)
    btn.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    font = QtGui.QFont('Arial', ffontsize)
    font.setBold(ffontbold)
    btn.setFont(font)
    return(btn)


def ccheckbox(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, Text='ON?',eenable=True, ccolor='black'):
    chkbox = QtWidgets.QCheckBox(Text, main_widget)
    chkbox.setEnabled(eenable)    
    chkbox.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    font = QtGui.QFont('Arial', ffontsize)
    font.setBold(ffontbold)
    chkbox.setFont(font)
    chkbox.setChecked(True)
    chkbox.setStyleSheet("color: "+ccolor)
    return(chkbox)


def eeditdblbox(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, value=-200, rrange=[-1e10, 1e10], step=0.1, decims=3,eenable=True, ccolor='black', bbuttonsymbol=0):
    editbox = QtWidgets.QDoubleSpinBox(main_widget)
    editbox.setEnabled(eenable)
    editbox.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    editbox.setRange(rrange[0],rrange[1])
    editbox.setDecimals(decims)
    editbox.setSingleStep(step)
    editbox.setProperty("value", value)
    font = QtGui.QFont('Arial', ffontsize)
    font.setBold(ffontbold)
    editbox.setStyleSheet("color: "+ccolor)
    editbox.setButtonSymbols(bbuttonsymbol)
    return(editbox)

def rradiobutton(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, Text='radiobutton', sstate=True):
    #radiobutton = QtWidgets.QRadioButton(Text, main_widget)
    radiobutton = QtWidgets.QRadioButton(Text, main_widget)
    radiobutton.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    font = QtGui.QFont('Arial', ffontsize)
    font.setBold(ffontbold)
    radiobutton.setFont(font)
    radiobutton.setChecked(sstate)
    return radiobutton


def llistwidget(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, llist=['0','1'], eenable=True, ccolor='black'):
    llistwidget = QtWidgets.QListWidget(main_widget)
    llistwidget.setEnabled(eenable)
    # llistwidget.setObjectName(sstring)
    llistwidget.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    for ii in llist: llistwidget.addItem(ii)
    # font = QtGui.QFont('Arial', ffontsize)
    # font.setBold(ffontbold)
    # mmenu.setStyleSheet("color: "+ccolor)
    return(llistwidget)

def ddropdownwidget(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, llist=['0','1'], eenable=True, ccolor='black'):
    ddropdownwidget = QtWidgets.QComboBox(main_widget)
    ddropdownwidget.setEnabled(eenable)
    # ddropdownwidget.setObjectName(sstring)
    ddropdownwidget.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    for ii in llist: ddropdownwidget.addItem(ii)
    # font = QtGui.QFont('Arial', ffontsize)
    # font.setBold(ffontbold)
    # mmenu.setStyleSheet("color: "+ccolor)
    return(ddropdownwidget)

def llineedit(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, sstring='text', eenable=True, ccolor='black'):
    llineedit = QtWidgets.QLineEdit(main_widget)
    llineedit.setEnabled(eenable)
    llineedit.setText(sstring)
    llineedit.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    font = QtGui.QFont('Arial', ffontsize)
    font.setBold(ffontbold)
    return(llineedit)


def eeditintbox(self, main_widget, position=[10, 10, 30, 15], ffontsize=13, ffontbold=False, value=1, \
    rrange=[-1e10, 1e10], step=1, decims=0,eenable=True, ccolor='black', bbuttonsymbol=0):
    editbox = QtWidgets.QSpinBox(main_widget)
    editbox.setEnabled(eenable)    
    editbox.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    editbox.setRange(rrange[0],rrange[1])
    # editbox.setDecimals(decims)
    editbox.setSingleStep(step)
    editbox.setProperty("value", value)
    font = QtGui.QFont('Arial', ffontsize)
    font.setBold(ffontbold)
    editbox.setStyleSheet("color: "+ccolor)
    editbox.setButtonSymbols(bbuttonsymbol)
    # QtWidgetsQAbstractSpinBox.UpDownArrows   0   Little arrows in the classic style.
    # QtWidgetsQAbstractSpinBox.PlusMinus  1   + and - symbols.
    # QtWidgetsQAbstractSpinBox.NoButtons  2   Don't display buttons.
    return(editbox)

def llabel(self, main_widget, position=[10, 10, 30, 15], sstring="label",ffontsize=13, ffontbold=False, ccolor='black', bgndccolor='transparent'):
    llabel1 = QtWidgets.QLabel(main_widget)
    llabel1.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    llabel1.setMinimumWidth(position[2])
    llabel1.setText(sstring)
    font = QtGui.QFont('Arial', ffontsize)
    font.setBold(ffontbold)
    llabel1.setFont(font)
    llabel1.setStyleSheet("color: "+ccolor+"; background-color: "+bgndccolor)
    return(llabel1)

def mmovie(self, main_widget, position=[10, 10, 30, 15], filename="gif.gif"):
    llabel1 = QtWidgets.QLabel(main_widget)
    llabel1.setGeometry(QtCore.QRect(position[0], position[1], position[2], position[3]))
    llabel1.setMinimumWidth(position[2])
    movie1 = QtGui.QMovie(filename, QtCore.QByteArray(), self)
    llabel1.setMovie(movie1);
    movie1.setCacheMode(QtGui.QMovie.CacheAll)        
    movie1.setScaledSize(QtCore.QSize(position[2], position[3]))
    movie1.setSpeed(1000)
    movie1.start()
    return(llabel1)

def pplot(self, ax1, nnum=1, xxdata=[0], yydata=[0], mmarker='-',
 pltclr='b', llegend='Legend', legloc=0, leganchor=None, ffontsize=13, ffontweight='normal', llinewidth=3, mmsize=2, legendframe=True, ccolor='blue', xlim=None, yyscale='linear'):
    for ii in range(0, nnum):
        xxd = np.squeeze(xxdata[:][ii])
        yyd = np.squeeze(yydata[:][ii])
        if xlim:
            minind = (np.abs(xxd - xlim[0])).argmin()
            maxind = (np.abs(xxd - xlim[1])).argmin()
            if minind > maxind:
                xxd = xxd[maxind:minind]
                yyd = yyd[maxind:minind]
            else:
                xxd = xxd[minind:maxind]
                yyd = yyd[minind:maxind]
            # print(xlim, minind, maxind)
        if mmarker == 'rand':
            plot1 = ax1.plot(xxd, yyd)  # mmarker[ii]) #,[1.5,2.3,3.1,4.5],[4,2,6,1],'-*b') xxdata[ii],yydata[ii]
        else:
            plot1 = ax1.plot(xxd, yyd, mmarker[ii], color=pltclr[ii])
        # print(ii)

    leg = ax1.legend(llegend[:], loc=legloc, fontsize=ffontsize, frameon=legendframe, bbox_to_anchor=leganchor)  # , bbox_to_anchor = (1.025, 0.5))
    # if leganchor!=None:
    #     leg(bbox_to_anchor=leganchor)
    ltext = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_edgecolor(ccolor)      # set the frame face color to light gray
    plt.setp(ltext, fontsize=ffontsize, fontweight=ffontweight)    # the legend text fontsize
    plt.setp(llines, linewidth=llinewidth)      # the legend linewidth
    ax1.axis('tight')
    # self.ax1.set_yscale(yyscale)

    return(plot1)