#!/usr/bin/env python

from Tkinter import *
from tkMessageBox import *
import tkFileDialog
import bdeprocessor

def notdone():
    showerror('Not implemented', 'Not yet available')

def askopenfilename():
    filename = tkFileDialog.askopenfilename(
        title='Select the XML setting file',
        filetypes=[('XML Files','*.xml'),('All files', '*')])
    if not filename:
        return
    else:
        print 'working on %s' % filename

    config = bdeprocessor.ProcessorConfig()
    config.readXMLConfig(filename)
    bdeprocessor.bdeprocessor(config)
    

def makemenu(parent):
    menubar = Frame(parent)
    menubar.pack(side=TOP, fill=X)
    fbutton = Menubutton(menubar, text='File', underline=0)
    fbutton.pack(side=LEFT)
    fileb = Menu(fbutton)
    fileb.add_command(label='Open...', command=askopenfilename, underline=0)
    fileb.add_command(label='Close', command=notdone, underline=0)
    fbutton.config(menu=fileb)

    return menubar



if __name__ == '__main__':
    root = Tk()
    root.title('OEE Reporting Tool')
    makemenu(root)
    msg = Label(root, text='OEE Reporting Tool')
    msg.pack(expand=YES, fill=BOTH)
    msg.config(relief=SUNKEN, width=40, height=8)
    root.mainloop()


