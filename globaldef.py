#!/usr/bin/env python3
import os
import tempfile


#Paths:{{{1
savedir = tempfile.gettempdir() +  '/' + 'linux-winfunc/'
if not savedir[-1]:
    savedir = savedir+'/'
if not os.path.isdir(savedir):
    os.mkdir(savedir)

monitorsfile = savedir + 'monitors.pickle'
windowsfile = savedir + 'windows.pd'


    
