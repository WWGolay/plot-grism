# -*- coding: utf-8 -*-

from grismlib.imports import *
from grismlib.calibrationFrames import rotate,gain,wavelength

class Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Left/right centering
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(6, weight=2)
        
        # Initialize variables and set defaults
        labelFont = tkFont.Font(family='Segoe UI')
        
        self.fitsPath = tk.StringVar(); self.fitsPath.set('Enter or browse to FITS image path')
        self.calibPath = tk.StringVar(); self.calibPath.set('Enter or browse to calibration .csv path')
        self.referencePath = tk.StringVar(); self.referencePath.set('Enter or browse to reference spectrum .csv path')
        
        self.plotChoiceVar = tk.IntVar(); self.plotChoiceVar.set(0)
        self.plotFileVar = tk.IntVar(); self.plotFileVar.set(0)
        self.titleVar = tk.StringVar()
        
        self.calibratedVar = tk.BooleanVar(); self.calibratedVar.set(1)
        self.Balmer = tk.BooleanVar(); self.Balmer.set(0)
        self.Carbon = tk.BooleanVar(); self.Carbon.set(0)
        self.Nitrogen = tk.BooleanVar(); self.Nitrogen.set(0)
        self.Oxygen = tk.BooleanVar(); self.Oxygen.set(0)
        self.Helium = tk.BooleanVar(); self.Helium.set(0)
        self.medAvg = tk.IntVar(); self.medAvg.set(3)
        self.fromWv = tk.IntVar(); self.fromWv.set(400)
        self.toWv = tk.IntVar(); self.toWv.set(700)
        self.yWidth = tk.IntVar(); self.yWidth.set(30)
        
        self.colorMap = tk.StringVar(); self.colorMap.set('gray')
        self.temp = tk.IntVar(); self.temp.set(15000)
        self.emission = tk.BooleanVar(); self.emission.set(0)
        self.customCenterWv = tk.DoubleVar(); self.customCenterWv.set(550)
        
        self.objName = tk.StringVar()
        self.objRA = tk.StringVar()
        self.objDec = tk.StringVar()
        self.dateTime = tk.StringVar()
        self.exposure = tk.StringVar()
        self.filter = tk.StringVar()
        
        self.advancedOptions = tk.BooleanVar(); self.advancedOptions.set(False)
        
        # FITS file path frame
        fitsFrame = tk.LabelFrame(self, text='FITS Path:', bd=0)
        fitsFrame.grid(row=0, column=1, columnspan=3, padx=5, pady=2, sticky='nsew')
        fitsFrame.grid_columnconfigure(0, weight=1)
        fitsEntry = ttk.Entry(fitsFrame, width=140, textvariable=self.fitsPath)
        fitsEntry.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        fitsEntry.bind('<FocusOut>', self.fitsPathListener) # Register listener for changes in value
        browseButton = ttk.Button(fitsFrame, text='Browse', width=9, command=lambda: self.browseButtonCallback('fits'))
        browseButton.grid(row=0, column=2, sticky='w', padx=5, pady=5)
        
        # Calibration csv file path frame
        calibFrame = tk.LabelFrame(self, text='Calibration CSV Path:', bd=0)
        calibFrame.grid_columnconfigure(0, weight=1)
        calibEntry = ttk.Entry(calibFrame, textvariable=self.calibPath)
        calibEntry.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        calibEntry.bind('<FocusOut>', self.calibPathListener) # Register listener for changes in value
        browseButton = ttk.Button(calibFrame, text='Browse', width=9, command=lambda: self.browseButtonCallback('calib'))
        browseButton.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Reference spectrum csv file path frame
        referenceFrame = tk.LabelFrame(self, text='Reference Spectrum CSV Path:', bd=0)
        referenceFrame.grid_columnconfigure(0, weight=1)
        referenceEntry = ttk.Entry(referenceFrame, textvariable=self.referencePath)
        referenceEntry.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        referenceEntry.bind('<FocusOut>', self.referencePathListener) # Register listener for changes in value
        browseButton = ttk.Button(referenceFrame, text='Browse', width=9, command=lambda: self.browseButtonCallback('ref'))
        browseButton.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Output type frame
        outputFrame = tk.LabelFrame(self, text='Output Type')
        outputFrame.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky='nsew')
        outputChoices = tk.Frame(outputFrame)
        outputChoices.grid(row=0, column=0, sticky='w')
        label = ttk.Label(outputChoices, text='Output: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        standardOutput = ttk.Radiobutton(outputChoices, text='Standard', variable=self.plotChoiceVar, value=0)
        standardOutput.grid(row=0, column=1, sticky='w')
        imageOutput = ttk.Radiobutton(outputChoices, text='Image', variable=self.plotChoiceVar, value=1)
        imageOutput.grid(row=0, column=2, sticky='w')
        stripOutput = ttk.Radiobutton(outputChoices, text='Strip Image', variable=self.plotChoiceVar, value=2)
        stripOutput.grid(row=0, column=3, sticky='w')
        
        # Advanced output type frames
        advancedOutputChoices = tk.Frame(outputFrame)
        twoOutput = ttk.Radiobutton(advancedOutputChoices, text='2x2', variable=self.plotChoiceVar, value=3)
        twoOutput.grid(row=0, column=0, sticky='w')
        rectifiedOutput = ttk.Radiobutton(advancedOutputChoices, text='Rectified Spectrum', variable=self.plotChoiceVar, 
            value=4)
        rectifiedOutput.grid(row=0, column=1, sticky='w')
        gaussianOutput = ttk.Radiobutton(advancedOutputChoices, text='Gaussian Fit', variable=self.plotChoiceVar, value=5)
        gaussianOutput.grid(row=0, column=2, sticky='w')
        calibrationOutput = ttk.Radiobutton(advancedOutputChoices, text='Calibration', variable=self.plotChoiceVar, value=6)
        calibrationOutput.grid(row=0, column=3, sticky='w')
        
        # Output filetype options frame
        fileFrame = tk.Frame(outputFrame)
        fileFrame.grid(row=1, column=0, sticky='w')
        label = ttk.Label(fileFrame, text='File Type: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        pngOutput = ttk.Radiobutton(fileFrame, text='PNG', variable=self.plotFileVar, value=0)
        pngOutput.grid(row=0, column=1, sticky='w')
        pdfOutput = ttk.Radiobutton(fileFrame, text='PDF', variable=self.plotFileVar, value=1)
        pdfOutput.grid(row=0, column=2, sticky='w')
        csvOutput = ttk.Radiobutton(fileFrame, text='CSV', variable=self.plotFileVar, value=2, state=DISABLED)
        
        # Title frame
        titleFrame = tk.Frame(outputFrame)
        label = ttk.Label(titleFrame, text='Plot Title: ', font = labelFont)
        label.grid(row=0, column=0, sticky='w')
        titleEntry = ttk.Entry(titleFrame, textvariable=self.titleVar, width=25)
        titleEntry.grid(row=0, column=1, sticky='w')
        
        # Standard options frame
        standardOptionsFrame = tk.LabelFrame(self, text='Output Options')
        standardOptionsFrame.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky='nsew')
        calibratedFrame = tk.Frame(standardOptionsFrame)
        calibratedFrame.grid(row=0, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(calibratedFrame, text='Calibrated: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        calibratedYes = ttk.Radiobutton(calibratedFrame, text='Yes', variable=self.calibratedVar, value=1)
        calibratedYes.grid(row=0, column=1, sticky='w')
        calibratedNo = ttk.Radiobutton(calibratedFrame, text='No', variable=self.calibratedVar, value=0)
        calibratedNo.grid(row=0, column=2, sticky='w')
        checkFrame = tk.Frame(standardOptionsFrame)
        checkFrame.grid(row=1, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(checkFrame, text='Plot Lines: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        balmerCheck = ttk.Checkbutton(checkFrame, text='Balmer', variable=self.Balmer, offvalue=False, onvalue=True)
        balmerCheck.grid(row=0, column=1, sticky='w')
        carbonCheck = ttk.Checkbutton(checkFrame, text='Carbon', variable=self.Carbon, offvalue=False, onvalue=True)
        nitrogenCheck = ttk.Checkbutton(checkFrame, text='Nitrogen', variable=self.Nitrogen, offvalue=False, onvalue=True)
        oxygenCheck = ttk.Checkbutton(checkFrame, text='Oxygen', variable=self.Oxygen, offvalue=False, onvalue=True)
        heliumCheck = ttk.Checkbutton(checkFrame, text='Helium', variable=self.Helium, offvalue=False, onvalue=True)
        medAvgFrame = tk.Frame(standardOptionsFrame)
        medAvgFrame.grid(row=2, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(medAvgFrame, text='Median Avg Width: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        medAvgEntry = ttk.Spinbox(medAvgFrame, from_=1, to=11, increment=2, width=4, textvariable=self.medAvg)
        medAvgEntry.grid(row=0, column=1, sticky='w')
        medAvgEntry.bind('<FocusOut>', self.medAvgListener)
        label = ttk.Label(medAvgFrame, text='nm', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        wvRangeFrame = tk.Frame(standardOptionsFrame)
        wvRangeFrame.grid(row=3, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(wvRangeFrame, text='Wavelength from ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        fromWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.fromWv)
        fromWvEntry.grid(row=0, column=1, sticky='w')
        fromWvEntry.bind('<FocusOut>', self.fromWvListener)
        label = ttk.Label(wvRangeFrame, text='to ', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        toWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.toWv)
        toWvEntry.grid(row=0, column=3, sticky='w')
        toWvEntry.bind('<FocusOut>', self.toWvListener)
        label = ttk.Label(wvRangeFrame, text='nm', font=labelFont)
        label.grid(row=0, column=4, sticky='w')
        yWidthFrame = tk.Frame(standardOptionsFrame)
        yWidthFrame.grid(row=4, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(yWidthFrame, text='Vertical Width: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        yWidthEntry = ttk.Spinbox(yWidthFrame, from_=5, to=50, increment=1, width=4, textvariable=self.yWidth)
        yWidthEntry.grid(row=0, column=1, sticky='w')
        yWidthEntry.bind('<FocusOut>', self.yWidthListener)
        label = ttk.Label(yWidthFrame, text='pixels', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        
        # Image options frame
        imageOptionsFrame = tk.LabelFrame(self, text='Output Options')
        label = ttk.Label(imageOptionsFrame, text='Colormap: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        colorOptions = ['gray', 'hot', 'jet', 'Reds', 'Greens', 'Blues']
        colorDrop = ttk.OptionMenu(imageOptionsFrame, self.colorMap, None, *colorOptions)
        colorDrop.grid(row=0, column=1, sticky='w')
        
        # Strip image options frame
        stripOptionsFrame = tk.LabelFrame(self, text='Output Options')
        label = ttk.Label(stripOptionsFrame, text='Colormap: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        colorDrop = ttk.OptionMenu(stripOptionsFrame, self.colorMap, None, *colorOptions)
        colorDrop.grid(row=0, column=1, sticky='w')
        
        # 2x2 options frame
        twoOptionsFrame = tk.LabelFrame(self, text='Output Options')
        medAvgFrame = tk.Frame(twoOptionsFrame)
        medAvgFrame.grid(row=0, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(medAvgFrame, text='Median Avg Width: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        medAvgEntry = ttk.Spinbox(medAvgFrame, from_=1, to=11, increment=2, width=4, textvariable=self.medAvg)
        medAvgEntry.grid(row=0, column=1, sticky='w')
        medAvgEntry.bind('<FocusOut>', self.medAvgListener)
        label = ttk.Label(medAvgFrame, text='nm', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        wvRangeFrame = tk.Frame(twoOptionsFrame)
        wvRangeFrame.grid(row=1, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(wvRangeFrame, text='Wavelength from ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        fromWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.fromWv)
        fromWvEntry.grid(row=0, column=1, sticky='w')
        fromWvEntry.bind('<FocusOut>', self.fromWvListener)
        label = ttk.Label(wvRangeFrame, text='to ', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        toWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.toWv)
        toWvEntry.grid(row=0, column=3, sticky='w')
        toWvEntry.bind('<FocusOut>', self.toWvListener)
        label = ttk.Label(wvRangeFrame, text='nm', font=labelFont)
        label.grid(row=0, column=4, sticky='w')
        
        # Rectified options frame
        rectifiedOptionsFrame = tk.LabelFrame(self, text='Output Options')
        tempFrame = tk.Frame(rectifiedOptionsFrame)
        tempFrame.grid(row=0, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(tempFrame, text='Temperature: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        tempEntry = ttk.Entry(tempFrame, width=7, textvariable=self.temp)
        tempEntry.grid(row=0, column=1, sticky='w')
        label = ttk.Label(tempFrame, text='K', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        wvRangeFrame = tk.Frame(rectifiedOptionsFrame)
        wvRangeFrame.grid(row=1, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(wvRangeFrame, text='Wavelength from ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        fromWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.fromWv)
        fromWvEntry.grid(row=0, column=1, sticky='w')
        fromWvEntry.bind('<FocusOut>', self.fromWvListener)
        label = ttk.Label(wvRangeFrame, text='to ', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        toWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.toWv)
        toWvEntry.grid(row=0, column=3, sticky='w')
        toWvEntry.bind('<FocusOut>', self.toWvListener)
        label = ttk.Label(wvRangeFrame, text='nm', font=labelFont)
        label.grid(row=0, column=4, sticky='w')
        
        # Gaussian options frame
        gaussianOptionsFrame = tk.LabelFrame(self, text='Output Options')
        centerFrame = tk.Frame(gaussianOptionsFrame)
        centerFrame.grid(row=0, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(centerFrame, text='Center On: ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        hAlphaButton = ttk.Button(centerFrame, text='H-α', style='Accent.TButton', width=3, command=lambda: 
                                  self.CenterCallback('H-α'))
        hAlphaButton.grid(row=0, column=1, sticky='w', padx=5)
        hBetaButton = ttk.Button(centerFrame, text='H-β', style='Accent.TButton', width=3, command=lambda: 
                                 self.CenterCallback('H-β'))
        hBetaButton.grid(row=0, column=2, sticky='w', padx=5)
        hGammaButton = ttk.Button(centerFrame, text='H-γ', style='Accent.TButton', width=3, command=lambda: 
                                  self.CenterCallback('H-γ'))
        hGammaButton.grid(row=0, column=3, sticky='w', padx=5)
        customEntry = ttk.Spinbox(centerFrame, from_=380, to=750, increment=0.1, width=6, textvariable=self.customCenterWv)
        customEntry.grid(row=0, column=5, sticky='w', padx=(25,0))
        customEntry.bind('<FocusOut>', self.customWvListener)
        label = ttk.Label(centerFrame, text='nm', font=labelFont)
        label.grid(row=0, column=6, sticky='w')
        customButton = ttk.Button(centerFrame, text='Go', style='Accent.TButton', width=3, command=lambda: 
                                  self.CenterCallback('Go'))
        customButton.grid(row=0, column=7, sticky='w', padx=2)
        wvRangeFrame = tk.Frame(gaussianOptionsFrame)
        wvRangeFrame.grid(row=1, column=0, sticky='w', padx=2, pady=2)
        label = ttk.Label(wvRangeFrame, text='Wavelength from ', font=labelFont)
        label.grid(row=0, column=0, sticky='w')
        fromWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.fromWv)
        fromWvEntry.grid(row=0, column=1, sticky='w')
        fromWvEntry.bind('<FocusOut>', self.fromWvListener)
        label = ttk.Label(wvRangeFrame, text='to ', font=labelFont)
        label.grid(row=0, column=2, sticky='w')
        toWvEntry = ttk.Spinbox(wvRangeFrame, from_=380, to=750, increment=10, width=6, textvariable=self.toWv)
        toWvEntry.grid(row=0, column=3, sticky='w')
        toWvEntry.bind('<FocusOut>', self.toWvListener)
        label = ttk.Label(wvRangeFrame, text='nm', font=labelFont)
        label.grid(row=0, column=4, sticky='w')
        emissionFrame = tk.Frame(gaussianOptionsFrame)
        emissionFrame.grid(row=2, column=0, sticky='w', padx=2, pady=2)
        absorptionChoice = ttk.Radiobutton(emissionFrame, text='Absorption Line', variable=self.emission, value=0)
        absorptionChoice.grid(row=0, column=0, sticky='w')
        emissionChoice = ttk.Radiobutton(emissionFrame, text='Emission Line', variable=self.emission, value=1)
        emissionChoice.grid(row=0, column=1, sticky='w')
        
        # Calibration options frame
        calibrationOptionsFrame = tk.LabelFrame(self, text='Output Options')
        calibrationOptionsFrame.grid_rowconfigure(1, weight=1)
        calibrationOptionsFrame.grid_columnconfigure(1, weight=1)
        calibGoButton = ttk.Button(calibrationOptionsFrame, text='Begin Calibration', style='Accent.TButton',
                                  command=self.beginCalibration)
        calibGoButton.grid(row=1, column=1)
        
        # Options frame selection tracer 
        self.plotChoiceVar.trace_add('write', lambda *args, optionFrames = 
                [standardOptionsFrame, imageOptionsFrame, stripOptionsFrame, twoOptionsFrame, rectifiedOptionsFrame, 
                 gaussianOptionsFrame, calibrationOptionsFrame], fileWidgets = [pngOutput, pdfOutput], csvWidget=csvOutput: 
                self.plotChoiceCallback(optionFrames, fileWidgets, csvWidget, *args))
        
        # FITS details frame
        self.detailsFrame = tk.LabelFrame(self, text='FITS Details')
        self.detailsFrame.grid(row=3, column=3, rowspan=2, padx=5, pady=5, sticky='nsew')
        self.detailsFrame.grid_columnconfigure(1, weight=1)
        label = ttk.Label(self.detailsFrame, text='Object:', font=labelFont)
        label.grid(row=0, column=0, sticky='e')
        objNameLabel = ttk.Label(self.detailsFrame, textvariable=self.objName, font=labelFont)
        objNameLabel.grid(row=0, column=1, sticky='w')
        label = ttk.Label(self.detailsFrame, text='RA:', font=labelFont)
        label.grid(row=1, column=0, sticky='e')
        objRALabel = ttk.Label(self.detailsFrame, textvariable=self.objRA, font=labelFont)
        objRALabel.grid(row=1, column=1, sticky='w')
        label = ttk.Label(self.detailsFrame, text='Dec:', font=labelFont)
        label.grid(row=2, column=0, sticky='e')
        objDecLabel = ttk.Label(self.detailsFrame, textvariable=self.objDec, font=labelFont)
        objDecLabel.grid(row=2, column=1, sticky='w')
        label = ttk.Label(self.detailsFrame, text='Date/Time:', font=labelFont)
        label.grid(row=3, column=0, sticky='e')
        dateTimeLabel = ttk.Label(self.detailsFrame, textvariable=self.dateTime, font=labelFont)
        dateTimeLabel.grid(row=3, column=1, sticky='w')
        label = ttk.Label(self.detailsFrame, text='Exposure:', font=labelFont)
        label.grid(row=4, column=0, sticky='e')
        exposureLabel = ttk.Label(self.detailsFrame, textvariable=self.exposure, font=labelFont)
        exposureLabel.grid(row=4, column=1, sticky='w')
        label = ttk.Label(self.detailsFrame, text='Filter:', font=labelFont)
        label.grid(row=5, column=0, sticky='e')
        filterLabel = ttk.Label(self.detailsFrame, textvariable=self.filter, font=labelFont)
        filterLabel.grid(row=5, column=1, sticky='w')
        photo = ImageTk.PhotoImage(Image.open('images/UILogo.png'))
        label = ttk.Label(self.detailsFrame, image=photo, anchor='center')
        label.image = photo
        label.grid(row=6, column=0, columnspan=2, sticky='ws')
        
        # Advanced checkbox and buttons frame
        bottomFrame = tk.Frame(self)
        bottomFrame.grid(row=5, column=1, columnspan=3, padx=5, pady=2, sticky='nsew')
        bottomFrame.grid_columnconfigure(1, weight=1)
        
        advancedFrames = [calibFrame, referenceFrame, advancedOutputChoices, csvOutput, titleFrame, carbonCheck, nitrogenCheck,
                          oxygenCheck, heliumCheck]
        advancedCheck = ttk.Checkbutton(bottomFrame, text='Advanced Options', variable=self.advancedOptions, 
            offvalue=False, onvalue=True)
        self.advancedOptions.trace_add('write', lambda *args, advancedFrames=advancedFrames:
                                       self.toggleAdvancedOptions(advancedFrames))
        advancedCheck.grid(row=0, column=0, sticky='w')
        exitButton = ttk.Button(bottomFrame, text='Exit', width=9, command=sys.exit)
        exitButton.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        aboutButton = ttk.Button(bottomFrame, text='About', width=9, command=self.aboutButtonCallback)
        aboutButton.grid(row=0, column=3, padx=5, pady=5, sticky='e')
        startButton = ttk.Button(bottomFrame, text='Start', style='Accent.TButton', width=9, command=self.startButtonCallback)
        startButton.grid(row=0, column=4, padx=5, pady=5, sticky='e')
            
    def browseButtonCallback(self, call):
        if call == 'fits':
            filename = tk.filedialog.askopenfilename(filetypes = [('FITS','.fts .fit .fits')])
            if not filename:
                return
            self.fitsPath.set(filename)
            self.fitsPathListener()
        else:
            filename = tk.filedialog.askopenfilename(filetypes = [('CSV','.csv')])
            if not filename:
                return
            if call == 'calib':
                self.calibPath.set(filename)
                self.calibPathListener
            else:
                self.referencePath.set(filename)
                self.referencePathListener
    
    def plotChoiceCallback(self, optionFrames, fileWidgets, csvWidget, *args):
        choice = self.plotChoiceVar.get()
        for i in range(len(optionFrames)):
            optionFrames[i].grid_forget()
        optionFrames[choice].grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky='nsew')
        for i in range(len(fileWidgets)):
            fileWidgets[i].configure(state = ACTIVE)
        if choice == 6:
            self.plotFileVar.set(2)
            csvWidget.configure(state = ACTIVE)
            for i in range(len(fileWidgets)):
                fileWidgets[i].configure(state = DISABLED)
        else:
            if self.plotFileVar.get() == 2:
                self.plotFileVar.set(0)
            csvWidget.configure(state = DISABLED)
            
    def toggleAdvancedOptions(self, advancedFrames, *args):
        if self.advancedOptions.get():
            advancedFrames[0].grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='nsew')
            advancedFrames[1].grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='nsew')
            advancedFrames[2].grid(row=0, column=1, sticky='w')
            advancedFrames[3].grid(row=0, column=3, sticky='w')
            advancedFrames[4].grid(row=2, column=0, sticky='w')
            advancedFrames[5].grid(row=0, column=2, sticky='w')
            advancedFrames[6].grid(row=0, column=3, sticky='w')
            advancedFrames[7].grid(row=0, column=4, sticky='w')
            advancedFrames[8].grid(row=0, column=5, sticky='w')
        else:
            for i in range(len(advancedFrames)):
                advancedFrames[i].grid_forget()
            self.plotChoiceVar.set(0)
            self.plotFileVar.set(0)
            self.Carbon.set(0)
            self.Nitrogen.set(0)
            self.Oxygen.set(0)
            self.Helium.set(0)
    
    def aboutButtonCallback(self):
        webbrowser.open('http://astro.physics.uiowa.edu/software/spectroscopy-tools/', new=1, autoraise=True)
    
    def startButtonCallback(self):
        if self.plotChoiceVar.get() == 6: # If calibration selection
            self.beginCalibration()
            return
        
        input_file = self.fitsPath.get()
        if not os.path.isfile(input_file):
            tk.messagebox.showerror(title='Error', message='Please select a valid FITS image')
            return
        
        im, hdr = getdata(input_file, 0, header=True)
        
        calibFile = self.findCalibFile(hdr['FILTER'], hdr['DATE-OBS'])
        if calibFile == None: 
            tk.messagebox.showerror(title='Error', message='No recent calibration files exist in the default '+
                'directory, please open Advanced Options and choose a calibration file or perform a calibration.' +
                '\n \n Calibrations must be no older than 6 months.')
            return
        
        self.G = grism_analysis(input_file, calibFile, ywidth=self.yWidth.get()) # Initialize grism tools
        input_path = input_file.rsplit('.', 1)[0]
            
        if self.plotChoiceVar.get() == 0: # If standard selection
            self.G.plot_spectrum(calibrated = self.calibratedVar.get(), plot_balmer=self.Balmer.get(), 
                    title=self.titleVar.get(), medavg=self.medAvg.get(), xlims=[self.fromWv.get(), self.toWv.get()])
            if self.plotFileVar.get() == 0:
                output_file = input_path + '-standard.png'
            else:
                output_file = input_path + '-standard.pdf'
        elif self.plotChoiceVar.get() == 1: # If image selection
            self.G.plot_image(title=self.titleVar.get(), cmap=self.colorMap.get())
            if self.plotFileVar.get() == 0:
                output_file = input_path + '-image.png'
            else:
                output_file = input_path + '-image.pdf'
        elif self.plotChoiceVar.get() == 2: # If strip image selection
            self.G.plot_strip(title=self.titleVar.get(), cmap=self.colorMap.get())
            if self.plotFileVar.get() == 0:
                output_file = input_path + '-strip_image.png'
            else:
                output_file = input_path + '-strip_image.pdf'
        elif self.plotChoiceVar.get() == 3: # If 2x2 selection
            if not os.path.isfile(self.referencePath.get()): # If no reference spectrum is entered
                if self.referencePath.get() == 'Enter or browse to reference spectrum .csv path':
                    self.referencePath.set('')
                else:
                    tk.messagebox.showerror(title='Error', message='Please select a valid CSV reference spectrum path')
                    return
                
            self.G.plot_2x2(ref_file=self.referencePath.get(), medavg=self.medAvg.get(), xlims=[self.fromWv.get(), self.toWv.get()])
            if self.plotFileVar.get() == 0:
                output_file = input_path + '-2x2.png'
            else:
                output_file = input_path + '-2x2.pdf'
        elif self.plotChoiceVar.get() == 4: # If rectified selection
            self.G.plot_rectified_spectrum(T=self.temp.get(), wavemin=self.fromWv.get(), wavemax=self.toWv.get())
            if self.plotFileVar.get() == 0:
                output_file = input_path + '-rectified_spectrum.png'
            else:
                output_file = input_path + '-rectified_spectrum.pdf'
        elif self.plotChoiceVar.get() == 5: # If Gaussian selection
            self.G.fit_gaussian(wave_min=self.fromWv.get(), wave_max=self.toWv.get(), emission=self.emission.get())
            if self.plotFileVar.get() == 0:
                output_file = input_path + '-Gaussian_fit.png'
            else:
                output_file = input_path + '-Gaussian_fit.pdf'
            
        plt.savefig(output_file)
        if self.plotFileVar.get() == 0:
            Image.open(output_file).show()
        else:
            subprocess.Popen(output_file,shell=True)
    
    def beginCalibration(self):
        raw_image = self.fitsPath.get(); reference_spectrum = self.referencePath.get()
        if not os.path.isfile(raw_image):
            tk.messagebox.showerror(title='Error', message='Please select a valid FITS image')
            return
        
        im, hdr = getdata(raw_image, 0, header=True)
        
        if not os.path.isfile(reference_spectrum): # If a custom reference spectrum file is not entered, then try to find one
            defaultDir = 'jacoby_spectra/' 
            star = str(hdr['OBJECT'])
            
            # Check if any calibration files exist for that star
            if os.path.isfile(defaultDir+star+'-Jacoby-spec.csv'): 
                referenceFile = defaultDir+star+'-Jacoby-spec.csv'
            else:
                tk.messagebox.showerror(title='Error', message='No reference spectra exist for this object in the default  '+
                        'directory, please choose an image with a different object or a different reference spectrum file.')
                return
        else:
            referenceFile = self.referencePath.get()
        
        G = grism_calibrate(raw_image, referenceFile) # Initialize grism calibration
        input_path = raw_image.rsplit('.', 1)[0]
    
        self.calibWindow = tk.Toplevel(self)
        self.calibWindow.grid_columnconfigure(1, weight=1)
        self.calibWindow.title('Grism Calibration')
        icon_photo = tk.PhotoImage(file='UILogo.png')
        self.calibWindow.iconphoto(False, icon_photo)
        self.calibWindow.grab_set()
        
        self.calibFrames = {}
        frame = rotate.Page(self.calibWindow, self, G, input_path)
        self.calibFrames[rotate.Page] = frame
        self.calibFrames[rotate.Page].grid(row=0, column=1, sticky='nsew')
        
        self.calibFrames[rotate.Page].tkraise()
        self.calibFrames[rotate.Page].update_idletasks()
        
    def showNewCalibFrame(self, pageNum, G, input_path, angle=0, subim_box=[], c=[]):
        if pageNum == 1:
            self.calibFrames[rotate.Page].grid_forget()
            frame = wavelength.Page(self.calibWindow, self, G, input_path, angle=angle, subim_box=subim_box)
            self.calibFrames[wavelength.Page] = frame
            self.calibFrames[wavelength.Page].grid(row=0, column=1, sticky='nsew')
        
            self.calibWindow.geometry('')
            self.calibFrames[wavelength.Page].tkraise()
            self.calibFrames[wavelength.Page].update_idletasks()
        elif pageNum == 2:
            self.calibFrames[wavelength.Page].grid_forget()
            frame = gain.Page(self.calibWindow, self, G, input_path, angle=angle, subim_box=subim_box, c=c)
            self.calibFrames[gain.Page] = frame
            self.calibFrames[gain.Page].grid(row=0, column=1, sticky='nsew')
            
            self.calibWindow.geometry('')
            self.calibFrames[gain.Page].tkraise()
            self.calibFrames[gain.Page].update_idletasks()
    
    def findCalibFile(self, fitsFilter, fitsDate):
        if not os.path.isfile(self.calibPath.get()): # If a custom calibration file is not entered, then try to find one
            defaultDir = 'calibrations/'
            
            # Check if any calibration files exist for that filter
            if not len(glob.glob(defaultDir+'grism_cal_'+fitsFilter+'*.csv')) > 0: 
                return
            
            # Get date of image to iterate back to latest calibration file
            startDate = date(int(fitsDate[0:4]), int(fitsDate[5:7]), int(fitsDate[8:10]))
            
            for testDate in (startDate - timedelta(n) for n in range(180)): # Iterate to find latest calib file
                if os.path.isfile(defaultDir+'grism_cal_'+fitsFilter+'_'+testDate.strftime('%Y_%m_%d')+'.csv'):
                    calibFile = defaultDir+'grism_cal_'+fitsFilter+'_'+testDate.strftime('%Y_%m_%d')+'.csv'
                    break
                elif testDate == startDate - timedelta(179):
                    return
                else: continue
                
        else:
            calibFile = self.calibPath.get()
        return calibFile
    
    def refreshImages(self):
        input_file = self.fitsPath.get()
        im, hdr = getdata(input_file, 0, header=True)
        
        calibFile = self.findCalibFile(hdr['FILTER'], hdr['DATE-OBS'])
        if calibFile == None: return
        self.G = grism_analysis(input_file, calibFile, ywidth=self.yWidth.get())

        fig = self.G.plot_image(figsize=(3,3))
        canvas = FigureCanvasTkAgg(fig, master=self.detailsFrame)
        canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, sticky='ws')

        fig = self.G.plot_strip(figsize=(3,1))
        canvas = FigureCanvasTkAgg(fig, master=self.detailsFrame)
        canvas.get_tk_widget().grid(row=7, column=0, columnspan=2, sticky='ws')
        
    def fitsPathListener(self, *args): # Validates entry of fits file path
        input_file = self.fitsPath.get()
        if input_file == 'Enter or browse to FITS image path': return
        descriptors = [self.objName, self.objRA, self.objDec, self.dateTime, self.exposure, self.filter]
        if (input_file.rsplit('.')[-1] != 'fts' and input_file.rsplit('.')[-1] != 'fits' 
        and input_file.rsplit('.')[-1] != 'fit'):
            self.fitsPath.set('Enter or browse to FITS image path')
            for i in range(len(descriptors)):
                descriptors[i].set('')
            tk.messagebox.showerror(title='Error', message='Filename must end in ".fts", ".fits", or ".fit"')
            return
        try: 
            im, hdr = getdata(input_file, 0, header=True)
            self.objName.set(hdr['OBJECT'])
            try: self.objRA.set(hdr['RA'])
            except: self.objRA.set(hdr['OBJCTRA'])
            try: self.objDec.set(hdr['DEC'])
            except: self.objDec.set(hdr['OBJCTDEC'])
            self.dateTime.set(hdr['DATE-OBS'].replace('T',' '))
            self.exposure.set(str(hdr['EXPTIME']))
            self.filter.set(str(hdr['FILTER']))
        except:
            self.fitsPath.set('Enter or browse to FITS image path')
            for i in range(len(descriptors)):
                descriptors[i].set('')
            tk.messagebox.showerror(title='Error', message='Error reading file: "{}"'.format(input_file))
            return

        self.refreshImages()

    def calibPathListener(self, *args): # Validates entry of calibration csv path
        if self.calibPath.get() == 'Enter or browse to calibration .csv path': return
        if self.calibPath.get().rsplit('.')[-1] != 'csv':
            self.calibPath.set('Enter or browse to calibration .csv path')
            tk.messagebox.showerror(title='Error', message='Filename must end in ".csv"')
            return
    
    def referencePathListener(self, *args): # Validates entry of reference spectrum csv path
        if self.referencePath.get() == 'Enter or browse to reference spectrum .csv path': return
        if self.referencePath.get().rsplit('.')[-1] != 'csv':
            self.referencePath.set('Enter or browse to reference spectrum .csv path')
            tk.messagebox.showerror(title='Error', message='Filename must end in ".csv"')
            return
    
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
    
    def fromWvListener(self, *args): # Validates lower wv bound entry
        try:
            int(self.fromWv.get())
            if int(self.fromWv.get()) > int(self.toWv.get()):
                self.fromWv.set(int(self.toWv.get())-1)
            elif int(self.fromWv.get()) < 380:
                self.fromWv.set(380)
        except: self.fromWv.set(400)
        
    def toWvListener(self, *args): # Validates upper wv bound entry
        try:
            int(self.toWv.get())
            if int(self.toWv.get()) > 750:
                self.toWv.set(750)
            elif int(self.toWv.get()) < int(self.fromWv.get()):
                self.toWv.set(int(self.fromWv.get())+1)
        except: self.toWv.set(700)
    
    def customWvListener(self, *args): # Validates custom wv entry
        try:
            float(self.customCenterWv.get())
            if self.customCenterWv.get() > 750:
                self.customCenterWv.set(750)
            elif self.customCenterWv.get() < 380:
                self.customCenterWv.set(380)
        except: self.customCenterWv.set(550)
    
    def yWidthListener(self, *args):
        try:
            int(self.yWidth.get())
            if int(self.yWidth.get()) > 50:
                self.yWidth.set(50)
                self.refreshImages()
            elif int(self.yWidth.get()) < 5:
                self.yWidth.set(5)
                self.refreshImages()
            else:
                self.refreshImages()
        except:
            self.yWidth.set(30)
            self.refreshImages()
    
    def CenterCallback(self, call): # Center on buttons function
        if call == 'H-α':
            self.fromWv.set(651.3)
            self.customCenterWv.set(656.3)
            self.toWv.set(661.3)
        elif call == 'H-β':
            self.fromWv.set(481.1)
            self.customCenterWv.set(486.1)
            self.toWv.set(491.1)
        elif call == 'H-γ':
            self.fromWv.set(429.0)
            self.customCenterWv.set(434.0)
            self.toWv.set(439.0)
        elif call == 'Go':
            self.fromWv.set(self.customCenterWv.get()-5)
            self.toWv.set(self.customCenterWv.get()+5)