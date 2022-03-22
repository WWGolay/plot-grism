# -*- coding: utf-8 -*-

from lib.imports import *
from lib.calibrationFrames import wavelength

class Page(tk.Frame):
    def __init__(self, parent, controller, G, input_path, angle, subim_box, c):
        tk.Frame.__init__(self, parent)
        # Left/right centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Initialize variables and set defaults
        self.parent = parent; self.controller = controller
        labelFont = tkFont.Font(family='Segoe UI')
        self.G = G; self.input_path = input_path; self.angle = angle; self.subim_box = subim_box; self.c = c
        self.image,self.star,self.utdate,self.telescope,self.instrument,self.fil = self.G.get_info()
        
        self.doPoly = tk.BooleanVar(); self.doPoly.set(0)
        self.smoothGain = tk.IntVar(); self.smoothGain.set(9)
        self.nPoly = tk.IntVar(); self.nPoly.set(9)
        self.medAvg = tk.IntVar(); self.medAvg.set(3)
        self.Balmer = tk.BooleanVar(); self.Balmer.set(1)
        self.save = tk.BooleanVar(); self.save.set(0)
        
        # Clip spectrum
        wmin = 380; wmax = 710
        self.wave,raw_spec = self.G.clip_spectrum(wmin, wmax)
        
        # Gain calibration frame
        self.gainFrame = tk.Frame(self)
        self.gainFrame.grid(row=0, column=1, sticky='nsew')
        canvasFrame = ttk.Labelframe(self.gainFrame, text='Gain Calibration')
        canvasFrame.grid_columnconfigure(0, weight=1)
        canvasFrame.grid_columnconfigure(3, weight=1)
        canvasFrame.grid(row=0, column=1, padx=5, pady=5, sticky='new')
        polynom,gain_curve,fig = self.G.calc_gain_curve(do_plot=True, do_poly=self.doPoly.get(), nsmooth=self.smoothGain.get(),
                                                  npoly=self.nPoly.get())
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        canvas.get_tk_widget().grid(row=0, column=1, sticky='nw', padx=5, pady=5)
        self.gain_curve = gain_curve
        fig = self.G.plot_spectrum(uncalibrated=False, medavg=self.medAvg.get(), plot_balmer=self.Balmer.get())
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        canvas.get_tk_widget().grid(row=0, column=2, sticky='ne', padx=5, pady=5)
        optionsFrame = ttk.Labelframe(self.gainFrame, text='Graph Options')
        optionsFrame.grid(row=1, column=1, padx=5, pady=5, sticky='new')
        optionsFrame.grid_columnconfigure(0, weight=1)
        optionsFrame.grid_columnconfigure(7, weight=1)
        label = ttk.Label(optionsFrame, text='Gain Smoothing: ', font=labelFont)
        label.grid(row=0, column=1)
        smoothEntry = ttk.Spinbox(optionsFrame, textvariable=self.smoothGain, from_=1, to=15, increment=2, width=5)
        smoothEntry.grid(row=0, column=2)
        smoothEntry.bind('<FocusOut>', self.smoothingListener)
        label = ttk.Label(optionsFrame, text='Median Average: ', font=labelFont)
        label.grid(row=0, column=3, padx=[10,0])
        medAvgEntry = ttk.Spinbox(optionsFrame, from_=1, to=11, increment=2, width=4, textvariable=self.medAvg)
        medAvgEntry.grid(row=0, column=4)
        medAvgEntry.bind('<FocusOut>', self.medAvgListener)
        label = ttk.Label(optionsFrame, text='nm', font=labelFont)
        label.grid(row=0, column=5)
        balmerCheck = ttk.Checkbutton(optionsFrame, text='Plot Balmer', variable=self.Balmer, offvalue=False, onvalue=True)
        balmerCheck.grid(row=0, column=6, padx=[5,0])
        polyFrame = tk.Frame(optionsFrame)
        polyFrame.grid(row=1, column=1, columnspan=6, pady=5)
        label = ttk.Label(polyFrame, text='Poly Degree: ', font=labelFont)
        label.grid(row=0, column=1)
        degreeEntry = ttk.Spinbox(polyFrame, textvariable=self.nPoly, from_=1, to=9, increment=1, width=5)
        degreeEntry.grid(row=0, column=2)
        degreeEntry.bind('<FocusOut>', self.polyListener)
        polyCheck = ttk.Checkbutton(polyFrame, text='Fit Polynomial', variable=self.doPoly, offvalue=False, onvalue=True)
        polyCheck.grid(row=0, column=3, padx=[5,0])
        saveFrame = tk.Frame(optionsFrame)
        saveFrame.grid(row=2, column=1, columnspan=6, pady=5)
        saveFrame.grid_columnconfigure(0, weight=1)
        saveFrame.grid_columnconfigure(4, weight=1)
        label = ttk.Label(saveFrame, text='Save Image: ', font=labelFont)
        label.grid(row=0, column=1)
        saveYes = ttk.Radiobutton(saveFrame, text='No', variable=self.save, value=0)
        saveYes.grid(row=0, column=2)
        saveNo = ttk.Radiobutton(saveFrame, text='Yes', variable=self.save, value=1)
        saveNo.grid(row=0, column=3)
        recalcFrame = tk.Frame(optionsFrame)
        recalcFrame.grid(row=0, column=7, rowspan=3, sticky='e')
        recalcButton = ttk.Button(recalcFrame, text='Recalculate Graph', width=15, command=lambda: 
                                  self.recalcCallback(canvasFrame))
        recalcButton.grid(row=0, column=0, sticky='nsew')
        
        # Buttons
        gainButtons = tk.Frame(self.gainFrame)
        gainButtons.grid(row=2, column=1, padx=5, pady=5, sticky='new')
        gainButtons.grid_columnconfigure(0, weight=1)
        exitButton = ttk.Button(gainButtons, text='Exit', width=9, command=sys.exit)
        exitButton.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        goBackButton = ttk.Button(gainButtons, text='Go Back', width=9, command=self.goBackCallback)
        goBackButton.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        writeCalibButton = ttk.Button(gainButtons, text='Write Calibration', style='Accent.TButton', width=15, 
                                    command=lambda: self.writeCalibrationCallback(canvasFrame))
        writeCalibButton.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        
    def writeCalibrationCallback(self, canvasFrame): # Write the calibration file
        self.recalcCallback(canvasFrame)
        
        date = datetime.now().strftime('%Y-%m-%d')
        
        cal_file = 'calibrations/grism_cal_%s_%s.csv' % (self.fil, date)
        c1,c2,c3 = [float(x) for x in self.c]
        xmin,xmax,ymin,ymax = [int(x) for x in self.subim_box]
        hdr_line = 'Grim calibration created %s using %s, %s, filter %s\n' % (date, self.telescope, self.instrument, 
                                                                              self.fil)
        cal_line = '%.2f, %.3e, %.3f, %.2f\n' % (float(self.angle),c1,c2,c3)
        subim_box = '%i, %i, %i, %i\n' % (xmin,xmax,ymin,ymax)
        
        with open(cal_file, 'w') as fh:
            fh.write(hdr_line)
            fh.write(cal_line)
            fh.write(subim_box)
            for j,w in enumerate(self.wave):
                fh.write('%.2f %.4f\n' % (w, self.gain_curve[j]))
        
        askYesNo = tk.messagebox.askquestion(title='Info', message=('Calibration file written! \n \n' +
                                                    os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + 
                                                    '/%s' % cal_file + '\n \n Close?'), parent=self.parent)
        if askYesNo == 'yes':
            self.controller.plotChoiceVar.set(0)
            self.controller.advancedOptions.set(0)
            self.parent.destroy()
        else: pass
    
    def goBackCallback(self): # Go back button
        self.controller.calibFrames[Page].grid_forget()
        self.controller.calibFrames[wavelength.Page].grid(row=0, column=1, sticky='nsew')
        self.controller.calibFrames[wavelength.Page].tkraise()
        
    def recalcCallback(self, canvasFrame): # Recalculate graphs
        polynom,gain_curve,fig = self.G.calc_gain_curve(do_plot=True, do_poly=self.doPoly.get(), 
                                                        nsmooth=self.smoothGain.get(), npoly=self.nPoly.get())
        if self.save.get(): plt.savefig(self.input_path+'-calibration_gain_curve.png')
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        canvas.get_tk_widget().grid(row=0, column=1, sticky='nw', padx=5, pady=5)
        fig = self.G.plot_spectrum(uncalibrated=False, medavg=self.medAvg.get(), plot_balmer=self.Balmer.get())
        if self.save.get(): plt.savefig(self.input_path+'-calibration_final_spectrum.png')
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        canvas.get_tk_widget().grid(row=0, column=2, sticky='ne', padx=5, pady=5)
    
    def smoothingListener(self, *args): # Validates smoothing entry
        try:
            int(self.smoothGain.get())
            if int(self.smoothGain.get()) > 15:
                self.smoothGain.set(15)
            elif int(self.smoothGain.get()) < 1:
                self.smoothGain.set(1)
            elif int(self.smoothGain.get()) % 2 == 0:
                self.smoothGain.set(int(self.smoothGain.get())-1)
        except: self.smoothGain.set(9)
        
    def medAvgListener(self, *args): # Validated median avg entry
        try:
            int(self.medAvg.get())
            if int(self.medAvg.get()) > 11:
                self.medAvg.set(11)
            elif int(self.medAvg.get()) < 1:
                self.medAvg.set(1)
            elif int(self.medAvg.get()) % 2 == 0:
                self.medAvg.set(int(self.medAvg.get())-1)
        except: self.medAvg.set(3)
    
    def polyListener(self, *args): # Validates polynomial degree entry
        try:
            int(self.nPoly.get())
            if int(self.nPoly.get()) > 9:
                self.nPoly.set(9)
            elif int(self.nPoly.get()) < 1:
                self.nPoly.set(1)
        except: self.nPoly.set(9)