# -*- coding: utf-8 -*-

from grismlib.imports import *

class Page(tk.Frame):
    def __init__(self, parent, controller, G, input_path):
        tk.Frame.__init__(self, parent)
        # Left/right centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Initialize variables and set defaults
        self.parent = parent; self.controller = controller
        labelFont = tkFont.Font(family='Segoe UI')
        self.G = G; self.input_path = input_path
        self.image,self.star,self.utdate,self.telescope,self.instrument,self.fil = self.G.get_info()
        
        self.xoff = tk.IntVar(); self.xoff.set(0)
        self.yoff = tk.IntVar(); self.yoff.set(0)
        self.xwidth = tk.IntVar(); self.xwidth.set(1000)
        self.ywidth = tk.IntVar(); self.ywidth.set(100)
        self.medAvg = tk.IntVar(); self.medAvg.set(3)
        self.save = tk.BooleanVar(); self.save.set(0)
        
        self.canvases = {}
        
        # Rotation Correction Frame
        self.rotationFrame = tk.Frame(self)
        self.rotationFrame.grid(row=0, column=1, sticky='nsew')
        canvasFrame = ttk.Labelframe(self.rotationFrame, text='Rotational Correction')
        canvasFrame.grid_columnconfigure(0, weight=1)
        canvasFrame.grid_columnconfigure(3, weight=1)
        canvasFrame.grid(row=0, column=0, padx=5, pady=5, sticky='new')
        fig = self.G.plot_image()
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        self.canvases['image'] = canvas.get_tk_widget()
        canvas.get_tk_widget().grid(row=0, column=1, sticky='new', padx=5, pady=5)
        subimageFrame = ttk.Labelframe(self.rotationFrame, 
                                       text='Create a subimage near the center to calculate the rotation angle:')
        subimageFrame.grid(row=1, column=0, padx=5, pady=5, sticky='new')
        subimageFrame.grid_columnconfigure(0, weight=1)
        subimageFrame.grid_columnconfigure(5, weight=1)
        label = ttk.Label(subimageFrame, text='x-offset: ', font=labelFont)
        label.grid(row=0, column=1, sticky='e')
        xoffEntry = ttk.Entry(subimageFrame, textvariable=self.xoff)
        xoffEntry.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        xoffEntry.bind('<FocusOut>', lambda *args, var = self.xoff: self.rotationEntryListener(var, *args))
        label = ttk.Label(subimageFrame, text='y-offset: ', font=labelFont)
        label.grid(row=0, column=3, sticky='w')
        yoffEntry = ttk.Entry(subimageFrame, textvariable=self.yoff)
        yoffEntry.grid(row=0, column=4, padx=5, pady=5, sticky='w')
        yoffEntry.bind('<FocusOut>', lambda *args, var = self.yoff: self.rotationEntryListener(var, *args))
        label = ttk.Label(subimageFrame, text='x-width: ', font=labelFont)
        label.grid(row=1, column=1, sticky='e')
        xwidthEntry = ttk.Entry(subimageFrame, textvariable=self.xwidth)
        xwidthEntry.grid(row=1, column=2, padx=5, pady=5, sticky='e')
        xwidthEntry.bind('<FocusOut>', lambda *args, var = self.xwidth: self.rotationEntryListener(var, *args))
        label = ttk.Label(subimageFrame, text='y-width: ', font=labelFont)
        label.grid(row=1, column=3, sticky='w')
        ywidthEntry = ttk.Entry(subimageFrame, textvariable=self.ywidth)
        ywidthEntry.grid(row=1, column=4, padx=5, pady=5, sticky='w')
        ywidthEntry.bind('<FocusOut>', lambda *args, var = self.ywidth: self.rotationEntryListener(var, *args))
        specFrame = ttk.LabelFrame(self.rotationFrame, text='Uncalibrated Spectrum Options')
        specFrame.grid(row=2, column=0, padx=5, pady=5, sticky='new')
        medAvgFrame = ttk.Frame(specFrame)
        medAvgFrame.grid(row=0, column=0)
        medAvgFrame.grid_columnconfigure(0, weight=1)
        medAvgFrame.grid_columnconfigure(4, weight=1)
        label = ttk.Label(medAvgFrame, text='Median Average: ', font=labelFont)
        label.grid(row=0, column=1)
        medAvgEntry = ttk.Spinbox(medAvgFrame, from_=1, to=11, increment=2, width=4, textvariable=self.medAvg)
        medAvgEntry.grid(row=0, column=2)
        medAvgEntry.bind('<FocusOut>', self.medAvgListener)
        label = ttk.Label(medAvgFrame, text='nm', font=labelFont)
        label.grid(row=0, column=3)
        saveFrame = tk.Frame(specFrame)
        saveFrame.grid(row=1, column=0)
        label = ttk.Label(saveFrame, text='Save Images: ', font=labelFont)
        label.grid(row=1, column=1)
        calibratedYes = ttk.Radiobutton(saveFrame, text='No', variable=self.save, value=0)
        calibratedYes.grid(row=1, column=2, sticky='w')
        calibratedNo = ttk.Radiobutton(saveFrame, text='Yes', variable=self.save, value=1)
        calibratedNo.grid(row=1, column=3, sticky='w')
        rotationButtons = tk.Frame(self.rotationFrame)
        rotationButtons.grid(row=3, column=0, sticky='new')
        rotationButtons.grid_columnconfigure(0, weight=1)
        exitButton = ttk.Button(rotationButtons, text='Exit', width=9, command=sys.exit)
        exitButton.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        findAngleButton = ttk.Button(rotationButtons, text='Find Angle', style='Accent.TButton', width=13, command=lambda:
                                     self.findAngleCallback(canvasFrame))
        findAngleButton.grid(row=0, column=1, padx=5, pady=5, sticky='e')
    
    def findAngleCallback(self, canvasFrame): # Finds angle and continues to next page 
        ys,xs = self.image.shape
        xc = int(xs/2) + self.xoff.get(); yc = int(ys/2) + self.yoff.get()
        ymin = yc - self.ywidth.get(); ymax = yc + self.ywidth.get()
        xmin = xc - self.xwidth.get(); xmax = xc + self.xwidth.get()
        box = [xmin,xmax,ymin,ymax]
        
        fig = self.G.plot_image()
        if self.save.get(): plt.savefig(self.input_path+'-calibration_image.png')
        
        angle,subim = self.G.rotate_image(box, self.ywidth.get())
        fig = self.G.plot_image(image=subim,figsize=(6,4),cmap='gray')
        if self.save.get(): plt.savefig(self.input_path+'-calibration_subimage.png')
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        self.canvases['subimage'] = canvas.get_tk_widget()
        canvas.get_tk_widget().grid(row=0, column=2, sticky='new', padx=5, pady=5)
        
        fig = self.G.plot_strip()
        if self.save.get(): plt.savefig(self.input_path+'-calibration_strip_image.png')
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        self.canvases['strip'] = canvas.get_tk_widget()
        canvas.get_tk_widget().grid(row=1, column=1, sticky='new', padx=5, pady=5)
        
        self.G.calc_spectrum()
        fig = self.G.plot_spectrum(uncalibrated=True, medavg=self.medAvg.get())
        if self.save.get(): plt.savefig(self.input_path+'-calibration_uncalibrated_spectrum.png')
        canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
        self.canvases['spectrum'] = canvas.get_tk_widget()
        canvas.get_tk_widget().grid(row=1, column=2, sticky='new', padx=5, pady=5)
        
        askYesNo = tk.messagebox.askquestion(title='Info', message=('Rotation angle found! \n \n Rotation = %.2f deg' % angle +
                                                                    '\n \n Continue?' % angle), parent=self.parent)
        if askYesNo: self.controller.showNewCalibFrame(1, self.G, self.input_path, subim_box=box, angle=angle)
    
    def rotationEntryListener(self, var, *args): # Validates offset and width entries
        try:
            ys,xs = self.image.shape
            xc = int(xs/2) + self.xoff.get(); yc = int(ys/2) + self.yoff.get()
            ymin = yc - self.ywidth.get(); ymax = yc + self.ywidth.get()
            xmin = xc - self.xwidth.get(); xmax = xc + self.xwidth.get()
            if ymin <= 0 or ymax > ys:
                self.yoff.set(0)
                self.ywidth.set(100)
            elif xmin <= 0 or xmax > xs:
                self.xoff.set(0)
                self.xwidth.set(1000)
        except:
            if var == self.xwidth: var.set(1000)
            elif var == self.xoff: var.set(0)
            elif var == self.ywidth: var.set(100)
            elif var == self.yoff: var.set(0)
            
    def medAvgListener(self, *args): # Validates median average entry
        try:
            int(self.medAvg.get())
            if int(self.medAvg.get()) > 11:
                self.medAvg.set(11)
            elif int(self.medAvg.get()) < 1:
                self.medAvg.set(1)
            elif int(self.medAvg.get()) % 2 == 0:
                self.medAvg.set(int(self.medAvg.get())-1)
        except: self.medAvg.set(3)