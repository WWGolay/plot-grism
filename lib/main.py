# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import sys,os,matplotlib; import matplotlib.pyplot as plt; import tkinter as tk

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from lib.application import Application

    matplotlib.use('TkAgg')
    plt.ioff()

    root = tk.Tk()
    root.tk.call('source', 'bin/themeSetup.tcl')
    root.tk.call('set_theme', 'dark')
    icon_photo = tk.PhotoImage(file='images/UILogo.png')
    root.iconphoto(False, icon_photo)
    application = Application(root)
    application.mainloop()