# -*- coding: utf-8 -*-

import tkinter as tk
from lib.analysisFrames import analysis

class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master = self.master
        
        master.grid_columnconfigure(1, weight=1)
        master.title('Grism Analysis & Calibration')
        
        self.analysisPage = analysis.Page(master, self)
        self.analysisPage.grid(row=0, column=1, sticky='nsew')
        
        self.analysisPage.tkraise()
        self.analysisPage.update_idletasks()