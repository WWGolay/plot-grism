# -*- coding: utf-8 -*-

from grismlib.imports import *
from grismlib.calibrationFrames import rotate

class Page(tk.Frame):
    def __init__(self, parent, controller, G, input_path, angle, subim_box):
        tk.Frame.__init__(self, parent)
        # Left/right centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Initialize variables and set defaults
        self.parent = parent; self.controller = controller
        labelFont = tkFont.Font(family='Segoe UI')
        self.G = G; self.input_path = input_path; self.angle = angle; self.subim_box = subim_box
        
        self.prominence = tk.DoubleVar(); self.prominence.set(0.1)
        self.width = tk.IntVar(); self.width.set(3)
        self.save = tk.BooleanVar(); self.save.set(0)
        self.Halpha = tk.BooleanVar(); self.Halpha.set(0)
        self.Hbeta = tk.BooleanVar(); self.Hbeta.set(0)
        self.Hgamma = tk.BooleanVar(); self.Hgamma.set(0)
        self.Hdelta = tk.BooleanVar(); self.Hdelta.set(0)
        self.Hepsilon = tk.BooleanVar(); self.Hepsilon.set(0)
        
        self.ref_lines = []
        
        # Wavelength Calibration Frame
        self.wavelengthFrame = tk.Frame(self)
        self.wavelengthFrame.grid(row=0, column=1, sticky='nsew')
        canvasFrame = ttk.Labelframe(self.wavelengthFrame, text='Wavelength Calibration')
        canvasFrame.grid_columnconfigure(1, weight=1)
        canvasFrame.grid(row=0, column=1, padx=5, pady=5, sticky='new')
        self.peaks, fig = self.G.find_spectral_peaks(prominence=self.prominence.get(), width=self.width.get(), do_plot=True)
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        canvas.get_tk_widget().grid(row=0, column=1, sticky='new', padx=5, pady=5)
        optionsFrame = ttk.Labelframe(self.wavelengthFrame, 
                                       text='Graph Options')
        optionsFrame.grid(row=1, column=1, padx=5, pady=5, sticky='new')
        optionsFrame.grid_columnconfigure(0, weight=1)
        optionsFrame.grid_columnconfigure(8, weight=1)
        label = ttk.Label(optionsFrame, text='Prominence:', font=labelFont)
        label.grid(row=0, column=1, sticky='w')
        prominenceEntry = ttk.Spinbox(optionsFrame, from_=0.01, to=1, increment=0.05, width=4, textvariable=self.prominence)
        prominenceEntry.grid(row=0, column=2, sticky='w')
        prominenceEntry.bind('<FocusOut>', self.prominenceListener)
        label = ttk.Label(optionsFrame, text='Width:', font=labelFont)
        label.grid(row=0, column=3, sticky='w', padx=[5,0])
        widthEntry = ttk.Spinbox(optionsFrame, from_=1, to=10, increment=1, width=4, textvariable=self.width)
        widthEntry.grid(row=0, column=4)
        widthEntry.bind('<FocusOut>', self.widthListener)
        label = ttk.Label(optionsFrame, text='Save Image: ', font=labelFont)
        label.grid(row=0, column=5, padx=[5,0], sticky='w')
        saveYes = ttk.Radiobutton(optionsFrame, text='No', variable=self.save, value=0)
        saveYes.grid(row=0, column=6, sticky='w')
        saveNo = ttk.Radiobutton(optionsFrame, text='Yes', variable=self.save, value=1)
        saveNo.grid(row=0, column=7, sticky='w')
        recalcButton = ttk.Button(optionsFrame, text='Recalculate Graph', width=15, command=lambda: 
                                  self.recalcCallback(canvasFrame))
        recalcButton.grid(row=0, column=8, sticky='e', padx=5, pady=5)
        linesFrame = ttk.Labelframe(self.wavelengthFrame, text='Lines Found:')
        linesFrame.grid(row=2, column=1, padx=5, pady=5, sticky='new')
        linesFrame.grid_columnconfigure(0, weight=1)
        linesFrame.grid_columnconfigure(6, weight=1)
        hACheck = ttk.Checkbutton(linesFrame, text='H-Alpha', variable=self.Halpha, offvalue=False, onvalue=True)
        hACheck.grid(row=0, column=5, sticky='e')
        hBCheck = ttk.Checkbutton(linesFrame, text='H-Beta', variable=self.Hbeta, offvalue=False, onvalue=True)
        hBCheck.grid(row=0, column=4, sticky='e')
        hGCheck = ttk.Checkbutton(linesFrame, text='H-Gamma', variable=self.Hgamma, offvalue=False, onvalue=True)
        hGCheck.grid(row=0, column=3)
        hDCheck = ttk.Checkbutton(linesFrame, text='H-Delta', variable=self.Hdelta, offvalue=False, onvalue=True)
        hDCheck.grid(row=0, column=2, sticky='w')
        hECheck = ttk.Checkbutton(linesFrame, text='H-Epsilon', variable=self.Hepsilon, offvalue=False, onvalue=True)
        hECheck.grid(row=0, column=1, sticky='w')
        wavelengthButtons = tk.Frame(self.wavelengthFrame)
        wavelengthButtons.grid(row=3, column=1, padx=5, pady=5, sticky='new')
        wavelengthButtons.grid_columnconfigure(0, weight=1)
        exitButton = ttk.Button(wavelengthButtons, text='Exit', width=9, command=sys.exit)
        exitButton.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        goBackButton = ttk.Button(wavelengthButtons, text='Go Back', width=9, command=self.goBackCallback)
        goBackButton.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        findCoefButton = ttk.Button(wavelengthButtons, text='Find Coefficients', style='Accent.TButton', width=15, 
                                    state = DISABLED, command=lambda: self.findCoefficientsCallback(canvasFrame))
        findCoefButton.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        
        self.Halpha.trace_add('write', lambda *args, findCoefButton = findCoefButton: 
                              self.linesListener(findCoefButton, *args))
        self.Hbeta.trace_add('write', lambda *args, findCoefButton = findCoefButton: 
                              self.linesListener(findCoefButton, *args))
        self.Hgamma.trace_add('write', lambda *args, findCoefButton = findCoefButton: 
                              self.linesListener(findCoefButton, *args))
        self.Hdelta.trace_add('write', lambda *args, findCoefButton = findCoefButton: 
                              self.linesListener(findCoefButton, *args))
        self.Hepsilon.trace_add('write', lambda *args, findCoefButton = findCoefButton: 
                              self.linesListener(findCoefButton, *args))
    
    def findCoefficientsCallback(self, canvasFrame):
        self.recalcCallback(canvasFrame)
        
        self.ref_lines = []
        if self.Hepsilon.get(): self.ref_lines.append(397.00)
        if self.Hdelta.get(): self.ref_lines.append(410.17)
        if self.Hgamma.get(): self.ref_lines.append(434.05)
        if self.Hbeta.get(): self.ref_lines.append(486.14)
        if self.Halpha.get(): self.ref_lines.append(656.28)
        f_wave,c = self.G.calc_wave(self.peaks, self.ref_lines)
        
        askYesNo = tk.messagebox.askquestion(title='Info', 
                                             message=('Coefficents found! \n \n %.2e, %.3f, %.3f' % (c[0], c[1], c[2]) + 
                                                      ' \n \n Continue?'), parent=self.parent)
        if askYesNo: self.controller.showNewCalibFrame(2, self.G, self.input_path, self.angle, self.subim_box, c)
    
    def goBackCallback(self):
        self.controller.calibFrames[Page].grid_forget()
        self.controller.calibFrames[rotate.Page].grid(row=0, column=1, sticky='nsew')
        self.controller.calibFrames[rotate.Page].tkraise()
        
    def recalcCallback(self, canvasFrame):
        self.peaks, fig = self.G.find_spectral_peaks(prominence=self.prominence.get(), width=self.width.get(), do_plot=True)
        if self.save.get(): plt.savefig(self.input_path+'-calibration_prominence.png')
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        canvas.get_tk_widget().grid(row=0, column=1, sticky='new', padx=5, pady=5)
    
    def prominenceListener(self, *args):
        try:
            float(self.prominence.get())
            if float(self.prominence.get()) > 1:
                self.prominence.set(1)
            elif float(self.prominence.get()) < 0.01:
                self.prominence.set(0.01)
        except: self.prominence.set(0.1)
    
    def widthListener(self, *args):
        try:
            int(self.width.get())
            if int(self.width.get()) > 10:
                self.width.set(10)
            elif int(self.width.get()) < 1:
                self.width.set(1)
        except: self.width.set(3)
    
    def linesListener(self, findCoefButton, *args):
        checkVars = [self.Halpha.get(), self.Hbeta.get(), self.Hgamma.get(), self.Hdelta.get(), self.Hepsilon.get()]
        count = 0
        for line in checkVars:
            if line:
                count = count + 1
        if count == len(self.peaks):
            findCoefButton.configure(state = ACTIVE)
        else:
            findCoefButton.configure(state = DISABLED)