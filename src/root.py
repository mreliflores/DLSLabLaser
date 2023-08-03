from .serialC import serialCtrl
from .dataMaster import DataMaster
from .contin import CONTIN
from tkinter.filedialog import asksaveasfilename

import os, sys
import tkinter as tk
import re
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import ctypes as ct
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import SubplotParams
from numpy.fft import rfft, irfft
import numpy as np
from sklearn.preprocessing import MinMaxScaler
matplotlib.use('TkAgg')
mplstyle.use('fast')
from multiprocessing import Queue
import time
from concurrent.futures import ThreadPoolExecutor

def findResourceFolder(folder):

    if getattr(sys, "frozen", False):

        # The application is frozen

        datadir = os.path.dirname(sys.executable)
        #print(os.path.join(datadir, folder)+' frozen')

    else:

        # The application is not frozen (here it depends on your folder structure)

        datadir = os.path.dirname(__file__)
        #print(os.path.join(datadir, folder)+' notFro')

    return os.path.join(datadir, folder)

def dark_title_bar(window):
    """
    MORE INFO:
    https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 0x000000FF
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),
                         ct.sizeof(value))
    pass

class root(tk.Tk):
    def __init__(self, serial, data) -> None:
        super().__init__()
        self.iconbitmap("../app.ico")
        self.serial = serial
        self.data = data
        self.queueRTD = Queue()
        self.Acc = tk.IntVar(value=10)
        self.acum_counts = tk.IntVar(value=100)
        self.scaler = MinMaxScaler(feature_range=(0,1))
        self.resizable(True, True)

        #self.trans_data = loadtxt("data.txt", ndmin=2)
        #self.scaler = MinMaxScaler(feature_range=(0,1))
        #self.tope=145
        #self.init = 0
        #self.data_ = array(self.trans_data[:, 1], ndmin=2).reshape(-1,1)
        #self.scaler.fit(self.data_)
        #self.data_ = self.scaler.fit_transform(self.data_)

        #### Program title and style ####
        self.title = "DLS analyzer"
        self.wm_title(self.title)
        self.s = ttk.Style()
        self.s.configure('TFrame', background='#27272a')
        self.s.configure('TButton', font="georgia 12 bold",bordercolor="lightgreen",height=5)
        #self.s.map('TButton',background=[('active','green'),('!disabled',"black")],foreground=[('pressed','green'),('!disabled',"black")])
        self.s.configure('TEntry', background='#27272a', foreground='#27272a')
        self.s.configure('TLabel', background='#27272a', foreground="#fff")
        self.s.configure('TLabelframe', background='#27272a', foreground="#27272a")
        self.s.configure('TLabelframe',
                         background='#27272a',
                         foreground="#27272a",
                         )
        self.s.configure('Vertical.TScrollbar',
                         bordercolor='red',
                         arrowcolor='white',
                         troughcolor='green'
                         )
        self.s.configure(
            'TLabelframe.Label',
            background='#27272a',
            foreground="#fff",
            font=('Verdana', 12, 'bold'),
            bordercolor="black"
        )
        self.s.configure('TScale', background='#27272a')
        self.configure(bg='#27272a')
        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )
        #######################

        self.filterCommand = self.register(self.filterBool)

        #### Contin variables ####
        self.NG = tk.DoubleVar(value=200)
        self.rIdx = tk.DoubleVar(value=1.331)
        self.gamma1 = tk.DoubleVar(value=1)
        self.gamma2 = tk.DoubleVar(value=10000)
        self.theta = tk.DoubleVar(value=90.0)
        self.T = tk.DoubleVar(value=298.0)
        self.viscosity = tk.DoubleVar(value=1.020)
        self.wavelength = tk.DoubleVar(value=650.0)
        self.tauMin = tk.DoubleVar(value=1e-5)
        self.tauMax = tk.DoubleVar(value=1e-1)
        ############################

        #### Software variables ####
        self.varMaxXLimDist = tk.DoubleVar(value=self.gamma2.get())
        self.varMinXLimDist = tk.DoubleVar(value=self.gamma1.get())
        self.varMaxYLimDist = tk.DoubleVar(value=1)
        self.varMinYLimDist = tk.DoubleVar(value=0)
        self.varsDist = [
            None,
            None,
            self.varMaxXLimDist,
            self.varMinXLimDist
        ]
        self.varMaxYLimSS = tk.DoubleVar(value=1024)
        self.varMinYLimSS = tk.DoubleVar(value=0)
        self.varMaxXLimSS = tk.DoubleVar(value=1)
        self.varMinXLimSS = tk.DoubleVar(value=0)

        self.varsSS = [
            self.varMaxYLimSS,
            self.varMinYLimSS,
            self.varMaxXLimSS,
            self.varMinXLimSS
        ]
        ############################

        #### Padding between frames ####
        self.padx = 6
        self.pady = 6
        ################################

        #### Call to *frame
        self.frames()
        self.EXP_PAR = EXP_PAR(self)
        self.SIGNAL_PLOT = SIGNAL_PLOT(self)
        self.G1_PLOT = G1_PLOT(self)
        #self.G1_PLOT.plotG1.ax.plot(self.trans_data[:,0], self.data_, '.', color="#04c3e6", markersize=3)
        self.DIST_PLOT = DIST_PLOT(self)
        self.SETLIMPLOTS_SS = SETLIMPLOTS_SS(
            self,
            self.SIGNAL_PLOT,
        )
        self.SETLIMPLOTS_Dist = SETLIMPLOTS_Dist(
            self,
            self.DIST_PLOT,
        )
        self.FITTING_FRAME = FITTING_FRAME(
            self,
        )
        self.acumm = acumm(self)
        time.sleep(2.5)
        ###################################
        self.SIGNAL_PLOT.setFigure()

        self.executor = ThreadPoolExecutor(max_workers=3)
        self.t1 = self.executor.submit(self.serial.stream, self.queueRTD, self.data)
        self.t2 = self.executor.submit(
            self.SIGNAL_PLOT.update,
            self.queueRTD
        )

        """self.tRealTimeData = threading.Thread(target=self.serial.stream, args=(self.queueRTD, self.data,), daemon=True)
        self.xxx = threading.Thread(target=self.SIGNAL_PLOT.update, args=(self.queueRTD,), daemon=True)
        self.tRealTimeData.start()
        self.xxx.start()"""
        
    def filterBool(self, floatText):
        result = re.match(r"[^a-zA-Z-_:;,\[\]{}^`+*~´¨|°¬!#$%&/='?\¡¿ ]|(\+|\-)?\d+(.\d+)?$", floatText)
        return result is not None
    
    def close_window(self):
        self.serial.threadingRTD = False
        time.sleep(1.5)
        self.destroy() #kill the window
        plt.close('all')
        try:
            self.serial.SerialClose()
        except Exception as e:
            print(e)
            pass
        pass

    def frames(self):

        self.exp_parameters = ttk.Frame(self)
        self.setLimPlotsFrame = ttk.Frame(self)
        self.settingsXYLimLF_ = ttk.LabelFrame(
            self.setLimPlotsFrame,
            text="Settings X-Y Limits",
        )
        self.fittingFrame = ttk.Frame(self)
        self.fittingLF_ = ttk.LabelFrame(
            self.fittingFrame,
            text="Settings CONTIN Fitting",
        )
        self.allPlots = ttk.Frame(self)
        self.canvasScroll = tk.Canvas(
            self.allPlots, width=1024,
            height=700,
            highlightthickness=0,
            bg='#27272a'
        )
        self.scrollbar = ttk.Scrollbar(self.allPlots, orient="vertical", command=self.canvasScroll.yview)
        self.scrollable_frame = ttk.Frame(self.canvasScroll)
        self.live_signal = ttk.Frame(self.scrollable_frame)
        self.acummFrame = ttk.Frame(self.scrollable_frame)
        self.gettingData = ttk.Frame(self.scrollable_frame)
        self.distFrame = ttk.Frame(self.scrollable_frame)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvasScroll.configure(
                scrollregion=self.canvasScroll.bbox("all")
            )
        )

        self.canvasScroll.create_window((1, 1), window=self.scrollable_frame, anchor="nw")
        self.canvasScroll.configure(yscrollcommand=self.scrollbar.set)
        self.canvasScroll.bind_class('Canvas', "<MouseWheel>", self._on_mousewheel)

        self.exp_parameters.grid(
            row=0,
            column=0,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.W+tk.E)
        )
        self.setLimPlotsFrame.grid(
            row=1,
            column=0,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.W+tk.E+tk.N)
        )
        self.settingsXYLimLF_.grid(
            row=0,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.fittingFrame.grid(
            row=2,
            column=0,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.W+tk.E+tk.N)
        )
        self.fittingLF_.grid(
            row=0,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )

        self.allPlots.grid(
            row=0,
            column=1,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.W+tk.E),
            rowspan=50
        )
        self.canvasScroll.grid(
            row=0,
            column=0,
            sticky=(tk.N+tk.S+tk.W+tk.E),
        )
        self.scrollbar.grid(
            row=0,
            column=1,
            sticky=(tk.NS),
        )

        self.live_signal.grid(
            row=0,
            column=0,
            sticky=(tk.N+tk.S+tk.W+tk.E),
        )
        self.acummFrame.grid(
            row=1,
            column=0,
            sticky=(tk.N+tk.S+tk.W+tk.E)
        )
        self.gettingData.grid(
            row=2,
            column=0,
            sticky=(tk.N+tk.S+tk.W+tk.E)
        )
        self.distFrame.grid(
            row=3,
            column=0,
            sticky=(tk.N+tk.S+tk.W+tk.E)
        )
        self.exp_parameters.columnconfigure(0, weight=1)
        self.setLimPlotsFrame.columnconfigure(0, weight=1)
        self.settingsXYLimLF_.columnconfigure(0, weight=1)
        self.fittingFrame.columnconfigure(0, weight=1)
        self.fittingLF_.columnconfigure(0, weight=1)
        self.live_signal.columnconfigure(0, weight=1)
        self.acummFrame.columnconfigure(0, weight=1)
        self.gettingData.columnconfigure(0, weight=1)
        self.distFrame.columnconfigure(0, weight=1)
        pass

    def _on_mousewheel(self, event):
        self.canvasScroll.yview_scroll(int(-1*(event.delta/120)), "units")
        pass
    pass

class EXP_PAR(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.padx = 6
        self.pady = 3

        self.entries = ttk.LabelFrame(
            self.parent.exp_parameters,
            text="Experimental Parameters",
        )

        self.entries.grid(
            row=0,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.entries.columnconfigure(0, weight=1)

        self.showInputs()
        self.setInputs()

    def showInputs(self):
        self.Temperature_ = ttk.Label(
            master = self.entries,
            text='Temperature (K):'
        )
        self.Temperature = ttk.Entry(
            master=self.entries,
            textvariable=self.parent.T,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=30
        )

        self.angle_ = ttk.Label(
            master = self.entries,
            text='Angle (°):'
        )
        self.angle = ttk.Entry(
            master=self.entries,
            textvariable=self.parent.theta,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=30
        )

        self.viscosit_ = ttk.Label(
            master = self.entries,
            text='Viscosity (cP):'
        )
        self.viscosit = ttk.Entry(
            master=self.entries,
            textvariable=self.parent.viscosity,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=30
        )

        self.Lambda_ = ttk.Label(
            master = self.entries,
            text='Wavelength (nm):'
        )
        self.Lambda = ttk.Entry(
            master=self.entries,
            textvariable=self.parent.wavelength,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=30
        )

        self.refractiveIndex_ = ttk.Label(
            master = self.entries,
            text='Wavelength (nm):'
        )
        self.refractiveIndex = ttk.Entry(
            master=self.entries,
            textvariable=self.parent.rIdx,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=30
        )

    def setInputs(self):
        self.Temperature_.grid(
            row=0,
            column=0,
            pady=self.pady,
            sticky=tk.E
        )
        self.Temperature.grid(
            row=0,
            column=1,
            padx=self.padx,
            pady=self.pady,
        )

        self.angle_.grid(
            row=1,
            column=0,
            pady=self.pady,
            sticky=tk.E
        )
        self.angle.grid(
            row=1,
            column=1,
            padx=self.padx,
            pady=self.pady,
        )

        self.viscosit_.grid(
            row=2,
            column=0,
            pady=self.pady,
            sticky=tk.E
        )
        self.viscosit.grid(
            row=2,
            column=1,
            padx=self.padx,
            pady=self.pady,
        )

        self.Lambda_.grid(
            row=3,
            column=0,
            pady=self.pady,
            sticky=tk.E
        )
        self.Lambda.grid(
            row=3,
            column=1,
            padx=self.padx,
            pady=self.pady,
        )

        self.refractiveIndex_.grid(
            row=4,
            column=0,
            pady=self.pady,
            sticky=tk.E
        )
        self.refractiveIndex.grid(
            row=4,
            column=1,
            padx=self.padx,
            pady=self.pady,
        )

class SETLIMPLOTS_SS(ttk.Frame):
    def __init__(self, parent, live):
        super().__init__()
        self.parent = parent
        self.live = live
        s = ttk.Style()
    
        self.parent.varMaxYLimSS.trace_add('write', self.SetSSMaxYLim)
        self.parent.varMinYLimSS.trace_add('write', self.SetSSMinYLim)
        self.parent.varMaxXLimSS.trace_add('write', self.SetSSMaxXLim)
        self.parent.varMinXLimSS.trace_add('write', self.SetSSMinXLim)


        self.SScontrol = SliderScaleControlLim(
            self.parent.settingsXYLimLF_,
            "Scattering Signal",
            self.parent.varsSS,
            0,
            0
        )
        self.SScontrol.setControlsY(1024, 0, 1)
        self.SScontrol.showControlsY()
        self.SScontrol.setControlsX(1, 0, 2500*16e-6)
        self.SScontrol.showControlsX()

    def SetSSMaxYLim(self, var, index, mode):
        try:
            #print(self.parent.varMaxYLimSS.get())
            self.SScontrol.YMinScale["to"] = self.parent.varMaxYLimSS.get()-1
            self.SScontrol.YMinSB["to"] = self.parent.varMaxYLimSS.get()-1
            if (self.parent.varMaxYLimSS.get() < self.parent.varMinYLimSS.get()):
                self.parent.varMinYLimSS.set(self.parent.varMaxYLimSS.get()-1)
            self.live.plotSignal_live.limMaxY(self.parent.varMaxYLimSS.get())
            self.live.plotSignal_live.fig.canvas.draw()
        except Exception as e:
            print(e)

    def SetSSMinYLim(self, var, index, mode):
        try:
            #print(self.parent.varMinYLimSS.get())
            self.SScontrol.YMaxScale["from_"] = self.parent.varMinYLimSS.get()+1
            self.SScontrol.YMaxSB["from_"] = self.parent.varMinYLimSS.get()+1
            if (self.parent.varMaxYLimSS.get() < self.parent.varMinYLimSS.get()):
                self.parent.varMaxYLimSS.set(self.parent.varMinYLimSS.get()+1)
            self.live.plotSignal_live.limMinY(self.parent.varMinYLimSS.get())
            self.live.plotSignal_live.fig.canvas.draw()
        except Exception as e:
            print(e)

    def SetSSMaxXLim(self, var, index, mode):
        try:
            #print(self.parent.varMaxXLimSS.get())
            self.SScontrol.XMinScale["to"] = self.parent.varMaxXLimSS.get()-0.0001
            self.SScontrol.XMinSB["to"] = self.parent.varMaxXLimSS.get()-0.0001
            if (self.parent.varMaxXLimSS.get() < self.parent.varMinXLimSS.get()):
                self.parent.varMinXLimSS.set(self.parent.varMaxXLimSS.get()-0.0001)
            self.live.plotSignal_live.limMaxX(self.parent.varMaxXLimSS.get())
            self.live.plotSignal_live.fig.canvas.draw()
        except Exception as e:
            print(e)

    def SetSSMinXLim(self, var, index, mode):
        try:
            #print(self.parent.varMinXLimSS.get())
            self.SScontrol.XMaxScale["from_"] = self.parent.varMinXLimSS.get()+0.0001
            self.SScontrol.XMaxSB["from_"] = self.parent.varMinXLimSS.get()+0.0001
            if (self.parent.varMaxXLimSS.get() < self.parent.varMinXLimSS.get()):
                self.parent.varMaxXLimSS.set(self.parent.varMinXLimSS.get()-0.0001)
            self.live.plotSignal_live.limMinX(self.parent.varMinXLimSS.get())
            self.live.plotSignal_live.fig.canvas.draw()
        except Exception as e:
            print(e)

class SETLIMPLOTS_Dist(ttk.Frame):
    def __init__(self, parent, dist):
        super().__init__()
        self.parent = parent
        self.dist = dist
        s = ttk.Style()
    
        self.parent.varMaxXLimDist.trace_add('write', self.SetDistMaxXLim)
        self.parent.varMinXLimDist.trace_add('write', self.SetDistMinXLim)

        self.SScontrol = SliderScaleControlLim(
            self.parent.settingsXYLimLF_,
            "Hydrodynamic radius Limits",
            self.parent.varsDist,
            1,
            0
        )
        self.SScontrol.setControlsX(
            self.parent.gamma2.get(),
            self.parent.gamma1.get(), 
            (self.parent.gamma2.get()-self.parent.gamma1.get())/self.parent.NG.get()
        )
        self.SScontrol.showControlsX()

    def SetDistMaxXLim(self, var, index, mode):
        try:
            #print(self.parent.varMaxXLimDist.get())
            self.step = (self.parent.gamma2.get()-self.parent.gamma1.get())/self.parent.NG.get()
            self.dist.distPlot.limMaxX(self.parent.varMaxXLimDist.get())
            self.SScontrol.XMinScale["to"] = self.parent.varMaxXLimDist.get()-self.step
            self.SScontrol.XMinSB["to"] = self.parent.varMaxXLimDist.get()-self.step
            if (self.parent.varMaxXLimDist.get() < self.parent.varMinXLimDist.get()):
                self.parent.varMinXLimDist.set(self.parent.varMaxXLimDist.get()-self.step)
            self.dist.distPlot.fig.canvas.draw()
        except Exception as e:
            #print(e)
            pass

    def SetDistMinXLim(self, var, index, mode):
        try:
            #print(self.parent.varMinXLimDist.get())
            self.step = (self.parent.gamma2.get()-self.parent.gamma1.get())/self.parent.NG.get()
            self.dist.distPlot.limMinX(self.parent.varMinXLimDist.get())
            self.SScontrol.XMaxScale["from_"] = self.parent.varMinXLimDist.get()+self.step
            self.SScontrol.XMaxSB["from_"] = self.parent.varMinXLimDist.get()+self.step
            if (self.parent.varMaxXLimDist.get() < self.parent.varMinXLimDist.get()):
                self.parent.varMaxXLimDist.set(self.parent.varMinXLimDist.get()+self.step)
            self.dist.distPlot.fig.canvas.draw()
        except Exception as e:
            print(e)

class FITTING_FRAME(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.padx = 6
        self.pady = 3
        s = ttk.Style()
        s.configure(
            'fit.TLabel',
            background='#4d4dff',
            anchor='center'
        )

        self.fittingG1_plot = self.parent.G1_PLOT.plotG1.ax.plot(1,
                                                                1,
                                                                color="#FF3131")
        self.sizeDist_plot = self.parent.DIST_PLOT.distPlot.ax.plot(0,
                                                                    0,
                                                                    '.',
                                                                    color="#FF3131")
        
        self.parent.G1_PLOT.plotG1.fig.canvas.draw()
        self.parent.DIST_PLOT.distPlot.fig.canvas.draw()

        #self.parent.gamma2.trace_add('write', self.SetGamma1InLim)
        #self.parent.gamma1.trace_add('write', self.SetGamma2InLim)
        #self.parent.NG.trace_add('write', self.SetNGInLim)
        #self.parent.gamma2.bind('<Return>', self.SetGamma1InLim)
        #self.parent.gamma1.bind('<Return>', self.SetGamma2InLim)
        
        # Follow changes in NG
        self.parent.NG.trace_add('write', self.SetNGInLim)

        self.setWidgetsFit()
        self.showWidgetsFit()

    def SetNGInLim(self, var, index, mode):
        try:
            #print("Hola")
            self.step = (self.parent.gamma2.get()-self.parent.gamma1.get())/self.parent.NG.get()
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMaxSB["increment"] = self.step
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMinSB["increment"] = self.step
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMinScale["to"] = self.parent.varMaxXLimDist.get()-self.step
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMinSB["to"] = self.parent.varMaxXLimDist.get()-self.step
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMaxScale["from_"] = self.parent.varMinXLimDist.get()+self.step
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMaxSB["from_"] = self.parent.varMinXLimDist.get()+self.step
        except Exception as e:
            #print(e)
            pass

    def SetGamma1InLim(self, var):#, index, mode):
        try:
            #print("Hola")
            self.step = (self.parent.gamma2.get()-self.parent.gamma1.get())/self.parent.NG.get()
            self.parent.varMaxXLimDist.set(self.parent.gamma2.get())
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMaxScale["to"] = self.parent.gamma2.get()
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMaxSB["to"] = self.parent.gamma2.get()
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMaxSB["increment"] = self.step
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMinSB["increment"] = self.step
        except Exception as e:
            #print(e)
            pass

    def SetGamma2InLim(self, var):#, index, mode):
        try:
            #print("Hola")
            self.step = (self.parent.gamma2.get()-self.parent.gamma1.get())/self.parent.NG.get()
            self.parent.varMinXLimDist.set(self.parent.gamma1.get())
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMinScale["from_"] = self.parent.gamma1.get()
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMinSB["from_"] = self.parent.gamma1.get()
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMinSB["increment"] = self.step
            self.parent.SETLIMPLOTS_Dist.SScontrol.XMaxSB["increment"] = self.step
        except Exception as e:
            #print(e)
            pass

    def yMax(self, var):#, index, mode):
        try:
            #print("Hola")
            self.parent.DIST_PLOT.distPlot.limMaxY(self.parent.varMaxYLimDist.get())
            self.parent.DIST_PLOT.distPlot.limMinY(-.07*self.parent.varMaxYLimDist.get())
            self.parent.DIST_PLOT.distPlot.fig.canvas.draw()
        except Exception as e:
            #print(e)
            pass

    def yMin(self, var):#, index, mode):
        try:
            #print("Hola")
            self.parent.DIST_PLOT.distPlot.limMinY(self.parent.varMinYLimDist.get())
            self.parent.DIST_PLOT.distPlot.fig.canvas.draw()
        except Exception as e:
            #print(e)
            pass

    def setWidgetsFit(self):
        self.NroDist_ = ttk.Label(
            master = self.parent.fittingLF_,
            text='N° Points Dist:',
            justify=tk.CENTER,
            style='fit.TLabel',
            width=20
        )
        self.NroDist = ttk.Entry(
            master=self.parent.fittingLF_,
            textvariable=self.parent.NG,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=23
        )
        self.tauMinL_ = ttk.Label(
            master = self.parent.fittingLF_,
            text='Min Tau:',
            style='fit.TLabel',
            width=20
        )
        self.tauMaxL_ = ttk.Label(
            master = self.parent.fittingLF_,
            text='Max Tau:',
            style='fit.TLabel',
            width=23
        )
        self.tauMinE = ttk.Entry(
            master=self.parent.fittingLF_,
            textvariable=self.parent.tauMin,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=20
        )
        self.tauMaxE = ttk.Entry(
            master=self.parent.fittingLF_,
            textvariable=self.parent.tauMax,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=23
        )
        self.rMinL_ = ttk.Label(
            master = self.parent.fittingLF_,
            text='Min Radius:',
            style='fit.TLabel',
            width=20
        )
        self.rMaxL_ = ttk.Label(
            master = self.parent.fittingLF_,
            text='Max Radius:',
            style='fit.TLabel',
            width=23
        )
        self.rMinE = ttk.Entry(
            master=self.parent.fittingLF_,
            textvariable=self.parent.gamma1,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=20
        )
        self.rMaxE = ttk.Entry(
            master=self.parent.fittingLF_,
            textvariable=self.parent.gamma2,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=23
        )
        self.rMinL_Y = ttk.Label(
            master = self.parent.fittingLF_,
            text='Min Intensity:',
            style='fit.TLabel',
            width=20
        )
        self.rMaxL_Y = ttk.Label(
            master = self.parent.fittingLF_,
            text='Max Intensity:',
            style='fit.TLabel',
            width=23)
        self.rMinEY  = ttk.Entry(
            master=self.parent.fittingLF_,
            textvariable=self.parent.varMinYLimDist,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=20
        )
        self.rMaxEY = ttk.Entry(
            master=self.parent.fittingLF_,
            textvariable=self.parent.varMaxYLimDist,
            justify='center',
            validate='all',
            validatecommand=(self.parent.filterCommand, '%S'),
            width=23
        )
        self.rMinE.bind('<Return>', self.SetGamma2InLim)
        self.rMaxE.bind('<Return>', self.SetGamma1InLim)

        self.rMinEY.bind('<Return>', self.yMin)
        self.rMaxEY.bind('<Return>', self.yMax)

        self.fitButton = ttk.Button(
            master=self.parent.fittingLF_,
            text='Fit',
            command=self.doFit
        )

    def showWidgetsFit(self):
        self.NroDist_.grid(
            row=0,
            column=0,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W)
        )
        self.NroDist.grid(
            row=0,
            column=1,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W),
        )

        self.tauMinL_.grid(
            row=1,
            column=0,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W)
        )
        self.tauMaxL_.grid(
            row=1,
            column=1,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W),
        )
        self.tauMinE.grid(
            row=2,
            column=0,
            padx=self.padx,
            sticky=(tk.N+tk.S+tk.E+tk.W)
        )
        self.tauMaxE.grid(
            row=2,
            column=1,
            padx=self.padx,
            sticky=(tk.N+tk.S+tk.E+tk.W),
        )
        self.rMinL_.grid(
            row=3,
            column=0,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W)
        )
        self.rMaxL_.grid(
            row=3,
            column=1,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W),
        )
        self.rMinE.grid(
            row=4,
            column=0,
            padx=self.padx,
            sticky=(tk.N+tk.S+tk.E+tk.W)
        )
        self.rMaxE.grid(
            row=4,
            column=1,
            padx=self.padx,
            sticky=(tk.N+tk.S+tk.E+tk.W),
        )
        self.rMinL_Y.grid(
            row=5,
            column=0,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W)
        )
        self.rMaxL_Y.grid(
            row=5,
            column=1,
            padx=self.padx,
            pady=self.pady,
            sticky=(tk.N+tk.S+tk.E+tk.W),
        )
        self.rMinEY.grid(
            row=6,
            column=0,
            padx=self.padx,
            sticky=(tk.N+tk.S+tk.E+tk.W)
        )
        self.rMaxEY.grid(
            row=6,
            column=1,
            padx=self.padx,
            sticky=(tk.N+tk.S+tk.E+tk.W),
        )
        self.fitButton.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky=(tk.W+tk.E),
            padx=self.padx,
            pady=self.pady,
        )

    def doFit(self):
        self.t3 = self.parent.executor.submit(
            self.fitCONTIN
        )
        pass

    def fitCONTIN(self):
        rh1 = self.parent.gamma1.get()
        rh2 = self.parent.gamma2.get()
        NG = self.parent.NG.get()
        angle = self.parent.theta.get()
        T = self.parent.T.get()
        wavelength = self.parent.wavelength.get()
        viscosity = self.parent.viscosity.get()
        ridx = self.parent.rIdx.get()
        tauMin = self.parent.tauMin.get()
        tauMax = self.parent.tauMax.get()
        path = findResourceFolder('contin-exe\contin-windows.exe')
        try:
            if len(self.fittingG1_plot)>0 and len(self.sizeDist_plot)>0:
                fit = self.fittingG1_plot.pop(0)
                dist = self.sizeDist_plot.pop(0)
                fit.remove()
                dist.remove()
            #print('hola')
            self.contin = CONTIN(
                path,
                contin_points=NG,
                angle=angle,
                temperature=T,
                wavelength=wavelength,
                viscosity=viscosity,
                refractive_index=ridx,
                contin_limits=[rh1,rh2],
            )
            self.contin.run(self.parent.acumm.x,
                            self.parent.acumm.y,
                            tauMin,
                            tauMax
                            )
            self.fittingG1_plot = self.parent.G1_PLOT.plotG1.ax.plot(self.contin.tau_fit,
                                                                    self.contin.fit_,
                                                                    color="#FF3131")
            self.sizeDist_plot = self.parent.DIST_PLOT.distPlot.ax.plot(self.contin.Rh,
                                                                        self.contin.amp,
                                                                        '.',
                                                                        color="#FF3131")
            self.parent.DIST_PLOT.distPlot.ax.set_ylim(top=1.1*max(self.contin.amp),
                                                    bottom=-.05*max(self.contin.amp))
            
            self.parent.G1_PLOT.plotG1.fig.canvas.draw()
            self.parent.DIST_PLOT.distPlot.fig.canvas.draw()
            self.parent.G1_PLOT.plotG1.fig.canvas.flush_events()
            self.parent.DIST_PLOT.distPlot.fig.canvas.flush_events()
            self.parent.varMinYLimDist.set(
                min(self.contin.amp)
            )
            self.parent.varMaxYLimDist.set(max(self.contin.amp))
        except Exception as e:
            #print('hola2')
            print(e)
            self.contin = CONTIN(
                path,
                contin_points=NG,
                angle=angle,
                temperature=T,
                wavelength=wavelength,
                viscosity=viscosity,
                refractive_index=ridx,
                contin_limits=[rh1,rh2],
            )
            self.contin.run(self.parent.acumm.x, self.parent.acumm.y, tauMin, tauMax)
            self.fittingG1_plot = self.parent.G1_PLOT.plotG1.ax.plot(self.contin.tau_fit,
                                                                    self.contin.fit_,
                                                                    color="#FF3131")
            self.sizeDist_plot = self.parent.DIST_PLOT.distPlot.ax.plot(self.contin.Rh,
                                                                        self.contin.amp,
                                                                        '.',
                                                                        color="#FF3131")
            self.parent.DIST_PLOT.distPlot.ax.set_ylim(top=1.1*max(self.contin.amp),
                                                    bottom=-0.05*max(self.contin.amp))
            
            self.parent.G1_PLOT.plotG1.fig.canvas.draw()
            self.parent.DIST_PLOT.distPlot.fig.canvas.draw()
            self.parent.G1_PLOT.plotG1.fig.canvas.flush_events()
            self.parent.DIST_PLOT.distPlot.fig.canvas.flush_events()
            self.parent.varMinYLimDist.set(min(self.contin.amp))
            self.parent.varMaxYLimDist.set(
                float("{:e}".format(max(self.contin.amp)))
            )
            pass

class SIGNAL_PLOT(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.dimx = 10
        self.dimy = 2

        self.plotSignal_live = CHART(
            self.parent.live_signal,
            "Scattering Signal",
            "Time (s)",
            "Amplitude (V)",
            row=0,
            column=0,
            axestype="live"
        )
        self.plotSignal_live.AddGraph(
            self.dimx,
            self.dimy,
        )

    def setFigure(self):
        self.ln = self.plotSignal_live.ax.plot([0, 1], [0, 1024], '.', linewidth=.7, color="#04c3e6", animated=True, markersize=1)[0]
        self.bm = BlitManager(self.plotSignal_live.fig.canvas, [self.ln])
        self.plotSignal_live.fig.canvas.draw()
        self.plotSignal_live.fig.canvas.flush_events()

    def update(self, queue1):
        while self.parent.serial.threadingRTD:
            y = queue1.get()
            t = np.linspace(0, y[-1]*1e-6, len(y)-1)
            #self.auto_cum = zeros(len(y)-1)

            try:
                """t0 = time.perf_counter()
                self.ln.remove()
                self.ln = self.plotSignal_live.ax.plot(t, y[:len(y)-1], linewidth=.7, color="#04c3e6")[0]
                # tell the blitting manager to do its thing
                self.plotSignal_live.fig.canvas.draw()
                self.plotSignal_live.fig.canvas.flush_events()
                print(time.perf_counter()-t0)"""

                """This method is more fast than the code above"""
                #t0 = time.perf_counter_ns()
                self.ln.set_data(t, y[:len(y)-1])
                self.bm.update()
                #print(time.perf_counter_ns()-t0)
            except Exception as e:
                print(e)
                """self.ln = self.plotSignal_live.ax.plot(t, y[:len(y)-1], linewidth=.7, color="#04c3e6")[0]
                # tell the blitting manager to do its thing
                self.plotSignal_live.fig.canvas.draw()
                self.plotSignal_live.fig.canvas.flush_events()"""

                self.ln.set_data(t, y[:len(y)-1])
                self.bm.update()
                pass

class POWER_INTENSITY_PLOT(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.dimx = 4.95
        self.dimy = 3

        self.plotPower_intensity = CHART(
            self.parent.gettingData,
            "Power intensity",
            "Frequency (Hz)",
            "Amplitude",
            row=0,
            column=0,
            axestype="spectrum"
        )
        self.plotPower_intensity.AddGraph(
            self.dimx,
            self.dimy,
        )

class G1_PLOT(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.dimx = 4.9
        self.dimy = 3

        self.plotG1 = CHART(
            self.parent.gettingData,
            "Normalized Autocorrelation",
            "Tau (s)",
            "Amplitude",
            row=0,
            column=0,
            #padx=10,
            #pady=5,
            axestype="g1"
        )
        self.plotG1.AddGraph(
            self.dimx,
            self.dimy,
        )

class DIST_PLOT(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.dimx = 4.95
        self.dimy = 3

        self.distPlot = CHART(
            self.parent.gettingData, #distFrame,
            "Size Distribution",
            "Hydrodynamic Diameter (nm)",
            "Amplitude (V)",
            row=0,
            column=1,
            axestype="live"
        )
        self.distPlot.AddGraph(
            self.dimx,
            self.dimy,
        )

class CHART(ttk.Frame):
    def __init__(self, parent, nameFrame, ejex, ejey, row, column, axestype, padx=0, pady=0):
        super().__init__()
        self.parent = parent
        self.nameFrame = nameFrame
        self.ejex = ejex
        self.ejey = ejey
        self.row = row
        self.column = column
        self.padx = padx
        self.pady = pady
        self.axestype = axestype

        self.g1 = "g1"
        self.spectrum = "spectrum"
        self.signalLive = "live"

        self.plotting = ttk.LabelFrame(
            master=self.parent,
            text=self.nameFrame,
        )

        self.plotting.grid(
            row=self.row,
            column=self.column,
            sticky=(tk.W+tk.E),
            padx=self.padx,
            pady=self.pady
        )

        self.plotting.columnconfigure(0, weight=1)


    def AddGraph(self, dimx, dimy,):
        self.fig, self.ax = plt.subplots(
            figsize=(dimx, dimy),
            dpi=100,
            constrained_layout=True,
            subplotpars=SubplotParams(left=0.1, bottom=0.1, right=0.95, top=0.95)
        )

        #self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        #self.fig.canvas.blit(self.ax.bbox)

        if self.axestype == self.g1:
            self.ax.set_xscale('log')
            #self.ax.set_xlim(1e-5, 1)

        elif self.axestype == self.spectrum:
            self.ax.set_xscale('log')
            self.ax.set_yscale('log')
            self.ax.set_xlim(1, 10000)
            pass
        else:
            pass

        self.ax.set_ylabel(rf'{self.ejey}')
        self.ax.set_xlabel(rf"{self.ejex}")
        self.ax.grid(color="#a1a1aa", alpha=1, linestyle="dotted", which='both')
        self.ax.set_facecolor("#09090b")
        self.ax.patch.set_facecolor("#27272a")
        self.fig.set_facecolor("#18181b")
        self.ax.spines['bottom'].set_color('#ffffff')
        self.ax.spines['top'].set_color('#ffffff') 
        self.ax.spines['right'].set_color('#ffffff')
        self.ax.spines['left'].set_color('#ffffff')
        self.ax.tick_params(axis='x', colors='#fff')
        self.ax.tick_params(axis='y', colors='#fff')
        self.ax.yaxis.label.set_color('#fff')
        self.ax.xaxis.label.set_color('#fff')

        self.canv = FigureCanvasTkAgg(self.fig, master=self.plotting)
        self.canv.get_tk_widget().grid(
            row=0,
            column=0,
            sticky=(tk.W+tk.E)
            #ipadx=52,
            #ipady=24
        )
        pass

    def limMaxY(self, YMax):
        self.ax.set_ylim(top=YMax)
        self.fig.canvas.flush_events()

    def limMinY(self, YMin):
        self.ax.set_ylim(bottom=YMin)
        self.fig.canvas.flush_events()

    def limMaxX(self, XMax):
        self.ax.set_xlim(right=XMax)
        self.fig.canvas.flush_events()

    def limMinX(self, XMin):
        self.ax.set_xlim(left=XMin)
        self.fig.canvas.flush_events()
 
class SliderScaleControlLim(ttk.Frame):
    def __init__(self, parent, title, vars:list, row, column):
        super().__init__()
        self.master = parent
        self.title = title
        self.vars = vars

        self.parent = ttk.Frame(
            self.master,
        )
        self.parent.grid(
            row=row,
            column=column
        )

    def setControlsY(self, YMax, YMin, increment):
#---------------------------------------------------------#
        self.Y_ = ttk.Label(
            master =self.parent,
            text=f'{self.title} Y-Limits',
        )
#########################################################
        self.YMax = ttk.Label(
            master =self.parent,
            text='Max',
            width=5,
            justify='center'
        )
        self.YMaxSB = ttk.Spinbox(
            master =self.parent,
            width=8,
            textvariable=self.vars[0],
            from_=YMin,
            to=YMax,
            increment=increment,
            justify='center'
        )
        self.YMaxScale = ttk.Scale(
            master =self.parent,
            length=200,
            from_=YMin,
            to=YMax,
            variable=self.vars[0]
        )
###########--------------------------###################
        self.YMin = ttk.Label(
            master =self.parent,
            text='Min',
            width=5,
            justify='center'
        )
        self.YMinSB = ttk.Spinbox(
            master =self.parent,
            width=8,
            textvariable=self.vars[1],
            from_=YMin,
            to=YMax,
            increment=increment,
            justify='center'
        )
        self.YMinScale = ttk.Scale(
            master =self.parent,
            length=200,
            from_=YMin,
            to=YMax,
            variable=self.vars[1]
        )
########################################################

    def setControlsX(self, XMax, XMin, increment):
#---------------------------------------------------------#
        self.X_ = ttk.Label(
            master =self.parent,
            text=f'{self.title} X-Limit',
        )
#########################################################
        self.XMax = ttk.Label(
            master =self.parent,
            text='Max',
            width=5,
            justify='center'
        )
        self.XMaxSB = ttk.Spinbox(
            master =self.parent,
            width=8,
            textvariable=self.vars[2],
            from_=XMin,
            to=XMax,
            increment=increment
        )
        self.XMaxScale = ttk.Scale(
            master =self.parent,
            length=200,
            from_=XMin,
            to=XMax,
            variable=self.vars[2]
        )
###########--------------------------###################
        self.XMin = ttk.Label(
            master =self.parent,
            text='Min',
            width=5,
            justify='center'
        )
        self.XMinSB = ttk.Spinbox(
            master =self.parent,
            width=8,
            textvariable=self.vars[3],
            from_=XMin,
            to=XMax,
            increment=increment

        )
        self.XMinScale = ttk.Scale(
            master =self.parent,
            length=200,
            from_=XMin,
            to=XMax,
            variable=self.vars[3]
        )
        ########################################################

    def showControlsY(self):
        self.Y_.grid(
            row=0,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
            columnspan=3
        )
        self.YMax.grid(
            row=1,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.YMaxSB.grid(
            row=1,
            column=1,
            sticky=(tk.W+tk.E),
        )
        self.YMaxScale.grid(
            row=1,
            column=2,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.YMin.grid(
            row=2,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.YMinSB.grid(
            row=2,
            column=1,
            sticky=(tk.W+tk.E),
        )
        self.YMinScale.grid(
            row=2,
            column=2,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )

    def showControlsX(self):
        self.X_.grid(
            row=3,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
            columnspan=3
        )
        self.XMax.grid(
            row=4,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.XMaxSB.grid(
            row=4,
            column=1,
            sticky=(tk.W+tk.E),
        )
        self.XMaxScale.grid(
            row=4,
            column=2,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.XMin.grid(
            row=5,
            column=0,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )
        self.XMinSB.grid(
            row=5,
            column=1,
            sticky=(tk.W+tk.E),
        )
        self.XMinScale.grid(
            row=5,
            column=2,
            sticky=(tk.W+tk.E+tk.N+tk.S),
        )

class BlitManager:
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for subclasses of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if (event.canvas != cv):
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
        # let the GUI event loop process anything it has to do
        cv.flush_events()

class acumm(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.values = [
                2,
                4,
                8,
                16,
                32,
                64,
                128
            ]
        self.valuesSR = tk.IntVar(value=16)
        self.timeL = tk.DoubleVar(value=1)

        self.parent.s.configure(
            'acum_counts.TLabel',
            font="Helvetica 16 bold",
        )

        self.acummlabelframe = ttk.Labelframe(
            master=self.parent.acummFrame,
            text='Accumulations'
        )
        self.acummlabelframe.grid(
            row=0,
            column=0,
            sticky=(tk.N+tk.S+tk.W+tk.E),
            #columnspan=100
        )

        self.set_widgets_ac()
        self.show_widgets_ac()
        self.setWidgets_sr()
        self.showWidgets_sr()
        self.saveWid()
        self.showSaveWid()
        self.setFigure()
        pass

    def set_widgets_ac(self):
        self.acumm_button = ttk.Button(
            master=self.acummlabelframe,
            text='Get Accumulation',
            command=self.do_getAccum 
        )
        self.acumm_entryLabel = ttk.Label(
            master=self.acummlabelframe,
            text="Nro Acummulations",
            anchor="center"
        )
        self.acumm_entry = ttk.Entry(
            master=self.acummlabelframe,
            textvariable=self.parent.Acc,
            justify='center'
        )
        self.acum_counts = ttk.Label(
            master=self.acummlabelframe,
            text="Nro Acummulations",
            anchor="s",
            textvariable=self.parent.acum_counts,
            style='acum_counts.TLabel',
            width=3
        )

    def show_widgets_ac(self):
        self.acumm_button.grid(
            row=1,
            column=0,
            sticky=(tk.N+tk.S+tk.W+tk.E),
            padx=5,
            pady=3,
        )
        self.acumm_entryLabel.grid(
            row=0,
            column=1,
            sticky=(tk.N+tk.S+tk.W+tk.E),
            padx=5,
        )
        self.acumm_entry.grid(
            row=1,
            column=1,
            sticky=(tk.N+tk.S+tk.W+tk.E),
            padx=5,
            pady=3,
        )
        self.acum_counts.grid(
            row=0,
            column=2,
            sticky=(tk.N+tk.S+tk.W+tk.E),
            rowspan=2,
            padx=5,
            pady=3,
        )

    def setWidgets_sr(self):
        self.labelSR = ttk.Label(
            master=self.acummlabelframe,
            text="Choose Scan Rate"
        )
        self.opSR = ttk.Combobox(
            master=self.acummlabelframe,
            values=self.values,
            state="readonly",
            textvariable=self.valuesSR,
            justify="center"
        )
        self.opSR.bind("<<ComboboxSelected>>", self.sendSRtoArduino)

        self.labelLiveSR = ttk.Label(
            master=self.acummlabelframe,
            text="Scan Rate (Samples/seg)"
        )
        self.liveSR = ttk.Label(
            master=self.acummlabelframe,
            textvariable=self.timeL,
            justify="center"
        )
        pass
    
    def showWidgets_sr(self):
        self.labelSR.grid(
            row=0,
            column=3,
            padx=15,
            pady=3
        )
        self.opSR.grid(
            row=1,
            column=3,
            padx=15,
            pady=3
        )

        self.labelLiveSR.grid(
            row=0,
            column=4,
            padx=15,
            pady=3
        )
        self.liveSR.grid(
            row=1,
            column=4,
            padx=15,
            pady=3
        )

    def saveWid(self):
        self.saveButton = ttk.Button(
            master=self.acummlabelframe,
            text="Save Data",
            command=self.save
        )

    def showSaveWid(self):
        self.saveButton.grid(
            row=1,
            column=5,
            padx=15,
            pady=5,
            sticky=(tk.N+tk.S+tk.W+tk.E)
        )

    def setFigure(self):
        self.ln = self.parent.G1_PLOT.plotG1.ax.plot(
            [1, 1], [1, 1],
            '.',
            color="#04c3e6",
            animated=True,
            markersize=1.5
        )[0]
        self.bm = BlitManager(self.parent.G1_PLOT.plotG1.fig.canvas, [self.ln])
        self.parent.G1_PLOT.plotG1.fig.canvas.draw()
        self.parent.G1_PLOT.plotG1.fig.canvas.flush_events()

    def do_getAccum(self):
        self.t4 = self.parent.executor.submit(
            self.get_accum
        )

    def job(self):
        try:
            data = self.parent.queueRTD.get()
            self.time = data[-1]
            del data[-1]
            #
            self.auto = self.autocorrelate(data)
            #
            self.auto_cum += self.auto
            self.x = np.linspace(
                0,
                self.time*1e-6,
                int(self.N_points/2),
            )
            self.y = self.auto_cum[:int(self.N_points/2)].reshape(-1, 1)
            self.parent.scaler.fit(self.y)
            self.y = self.parent.scaler.fit_transform(self.y)
            if self.i == 0:
                self.plot.plot(
                    self.x,
                    self.y,
                    '.',
                    color="#04c3e6",
                    animated=True,
                    markersize=3
                )[0]
                self.plot.set_xlim(right=1.5*self.time*1e-6)
                self.plot.set_ylim(-0.1, 1.1)
                self.parent.G1_PLOT.plotG1.fig.canvas.draw()
                self.parent.G1_PLOT.plotG1.fig.canvas.flush_events()
                pass
            #print(self.x)
            #print(self.auto_cum)
            #t0 = time.perf_counter_ns()
            self.ln.set_data(
                self.x,
                self.y
            )
            self.bm.update()
            #print(time.perf_counter_ns()-t0)
            self.i += 1
            self.parent.acum_counts.set(self.parent.Acc.get() - self.i)
            self.timeL.set(2500/(self.time*1e-6))
        except Exception as e:
            print(e)
            pass

    def get_accum(self):
        self.parent.acum_counts.set(self.parent.Acc.get())
        self.acumm_entry.configure(state="disabled")
        self.acumm_button['state'] = "disabled"
        self.i = 0
        self.N_points = 2500
        self.auto_cum = np.zeros(self.N_points)
        self.plot = self.parent.G1_PLOT.plotG1.ax
        #print(self.parent.Acc.get())
        while self.i<self.parent.Acc.get():
            try:
                if self.i == 0:
                    line1=self.parent.FITTING_FRAME.fittingG1_plot.pop(0)
                    line2=self.parent.FITTING_FRAME.sizeDist_plot.pop(0)
                    line1.remove()
                    line2.remove()
                self.job()
                pass
            except Exception as e:
                self.job()
                print("El error {} proviene de acumm".format(e))
                pass
        self.acumm_entry.configure(state="normal")
        self.acumm_button['state'] = "active"
        pass

    def autocorrelate(self, series):
        N = len(series)
        s_hat = rfft(series)
        return irfft(s_hat*np.conj(s_hat), N)

    def sendSRtoArduino(self, event):
        self.parent.serial.ser.write(str(self.valuesSR.get()).encode())

    def save(self):
        self.file_obj = asksaveasfilename(
            filetypes=[("CSV File", ".csv")],
            defaultextension=".csv",
            title="Save as"
        )
        try:
            fit_mask = self.parent.FITTING_FRAME.contin.fit_.copy().tolist()
            g1 = list(map(float, self.parent.acumm.y.reshape(-1).tolist()))
            diam = self.parent.FITTING_FRAME.contin.Rh.copy().tolist()
            amp = self.parent.FITTING_FRAME.contin.amp.copy().tolist()

            for i in range(len(g1)-int(self.parent.NG.get())):
                diam.append(None)
                amp.append(None)

            if len(g1) != len(fit_mask):
                for i in range(len(g1)-len(fit_mask)):
                    fit_mask.append(None)

            data = np.c_[
                ['fit', *fit_mask],
                ['g1', *g1],
                ['tau_exp', *list(self.parent.acumm.x)],
                ['Size Distribution', *diam],
                ['Amplitude Size Dist (au)', *amp]
            ]
            image = self.file_obj[:len(self.file_obj)-4]
            np.savetxt(f"{self.file_obj}", data, delimiter="\t", fmt="%s")
            self.parent.DIST_PLOT.distPlot.fig.savefig(f"{image}_dist.pdf")
            self.parent.G1_PLOT.plotG1.fig.savefig(f"{image}_g1.pdf")
        except Exception as e:
            print(e)
        
    
if __name__ == "__main__":
    data = DataMaster()
    serial = serialCtrl()
    app = root(serial, data)
    dark_title_bar(app)
    app.mainloop()
