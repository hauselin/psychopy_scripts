'''
Function to move newly created files to a specific folder. By default, it's the Data folder. To use this script, just run it (like how you run any other PsychoPy experiment script), and enter the participant number accordingly. The participants' files will be moved into the Data folder.

Click green runinng man icon to begin.
'''

import pandas as pd
import numpy as np
import random, os, time
from psychopy import visual, core, event, data, gui, logging, monitors


def moveFiles(outputDir = 'Data'):
    info = {}
    info['participant'] = ''
    dlg = gui.DlgFromDict(info) # create a dialogue box (function gui)
    if not dlg.OK: # if dialogue response is NOT OK, quit
        core.quit()

    # list files in current directory
    files = os.listdir(os.getcwd())

    info['participant'] = "{:03}".format(int(info['participant']))

    # create new directory (or the directory to move files to)
    dataDirectory = os.getcwd() + os.path.sep + 'Data'
    if not os.path.exists(dataDirectory):
        os.mkdir(dataDirectory)

    for filename in files:
        if filename.startswith(str(info['participant'])):
            newNameAndDir = dataDirectory + os.path.sep + filename
            print newNameAndDir
            os.rename(filename, newNameAndDir)

moveFiles(outputDir = 'Data')
