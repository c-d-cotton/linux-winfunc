#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/')

import pickle

# GENERAL WINDOW FUNCTIONS:{{{1
def getactiveid():
    import subprocess
    import sys

    output = subprocess.check_output(['/usr/bin/xprop', '-root', '_NET_ACTIVE_WINDOW'])

    if sys.version_info >= (3, 0):
        output = output.decode('utf-8')

    id = output.strip('_NET_ACTIVE_WINDOW(WINDOW): window id # ')

    return(format(int(id, 16), "#010x"))


def getcurdim(curid):
    import subprocess

    output = subprocess.check_output(['wmctrl', '-G', '-l'])

    lines = output.split('\n')[:-1]

    for line in lines:
        if line.split(None, 1)[0] == curid:
            break


    partline = line.split(None)
    winx = partline[2]
    winy = partline[3]
    winwidth = partline[4]
    winheight = partline[5]

    return([winx, winy, winwidth, winheight])


def getcurdesktop():
    import subprocess

    desktop = subprocess.check_output(['/usr/bin/xprop', '-root', '_NET_CURRENT_DESKTOP'])
    desktop = desktop.decode('utf-8')
    desktop = desktop.replace('_NET_CURRENT_DESKTOP(CARDINAL) = ', '')
    desktop = desktop.replace('\n', '')
    desktop = int(desktop)
    return(desktop)


def addmaxvert(winid):
    import subprocess

    subprocess.call(['wmctrl', '-i', '-r', str(winid), '-b', 'add,maximized_vert'])


def addmaxhorz(winid):
    import subprocess

    subprocess.call(['wmctrl', '-i', '-r', str(winid), '-b', 'add,maximized_horz'])


def winmvpos(x, y, width, height, winid = None, active = False): 
    """
    Need to specify winid or set active to be true.
    """

    import subprocess

    if active is True:
        winid = ':ACTIVE:'
    else:
        winid = str(winid)

    newpos = '0,' + str(x) + ',' + str(y) + ',' + str(width) + ',' + str(height)
    subprocess.call(['wmctrl', '-i', '-r', winid, '-b', 'remove,maximized_horz'])
    subprocess.call(['wmctrl', '-i', '-r', winid, '-b', 'remove,maximized_vert'])
    subprocess.call(['wmctrl', '-i', '-r', winid, '-e', newpos])


def winmvdesktop(desktop, winid = None, active = False):
    """
    Need to specify winid or set active to be true.
    """

    import subprocess

    if active is True:
        winid = ':ACTIVE:'
    else:
        winid = str(winid)

    subprocess.call(['wmctrl', '-i', '-r', winid, '-t', str(desktop)])


def changedesktop(desktop):
    import subprocess

    desktop = str(desktop)
    subprocess.call(['wmctrl', '-s', desktop])


def visualpidfrompid(pid):
    import subprocess

    output = subprocess.check_output(['wmctrl', '-lp'])
    output = output.decode('latin-1')
    output = str(output) # for python2
    outputsplit = [line.split() for line in output.splitlines()]

    visualpid = None
    for line in outputsplit:
        if line[2] == str(pid):
            visualpid = line[0]

    return(visualpid)


# GENERAL MONITOR FUNCTIONS:{{{1
def getmondim():
    """
    Requires xrandr.
    Get monitor dimensions as a pickle object saved in temporary directory.
    """
    import globaldef
    import pickle
    import subprocess
    import tempfile

    width=[]
    height=[]
    offwidth=[]
    offheight=[]

    mondict={}

    xrandroutput = subprocess.check_output(['xrandr']).decode("utf-8")

    for line in xrandroutput.splitlines():
        # print(type(line))
        if not line != line.replace(' connected ', ''):
            continue
        temp = ' '.join(line.split(' ')[2: ]) #remove "eDP1 connected ", "HDMI1 connected " etc.
        temp = temp.replace('primary ', '')
        dimensions = temp.split(' ')[0]
        try:
            width.append(int(dimensions.split('x')[0]))
        except:
            continue
        temp = dimensions.split('x')[1]
        height.append(int(temp.split('+')[0]))
        offwidth.append(int(temp.split('+')[1]))
        offheight.append(int(temp.split('+')[2]))

    for monnum in range(1, len(width) + 1):
        minoffheight = min(offheight)
        minoffheightindex = []
        for i in range(0, len(width)):
            if offheight[i] == minoffheight:
                minoffheightindex.append(i)
        minoffwidth = min([offwidth[i] for i in minoffheightindex])
        for j in minoffheightindex:
            if offwidth[j] == minoffwidth:
                mondict[monnum] = {'width': width[j],'height': height[j],'offwidth': offwidth[j],'offheight': offheight[j]}
                
                width.pop(j)
                height.pop(j)
                offwidth.pop(j)
                offheight.pop(j)
                break

    from globaldef import monitorsfile
    with open(monitorsfile, 'wb') as handle:
        pickle.dump(mondict, handle, protocol = 2) #change to protocol 3 when change other script to python3


def nummonitors():
    import pickle

    from globaldef import monitorsfile
    with open(monitorsfile, 'rb') as handle:
        mondict = pickle.load(handle)

    return(len(mondict.values()))


# FUNCTIONS REQUIRING WINDOW DETAILS:{{{1
def getwindet():
    import os
    import pickle
    import subprocess
    import sys

    output = subprocess.check_output(['wmctrl', '-l', '-x'])

    if sys.version_info >= (3, 0):
        output = output.decode('utf-8')
    splitthis = str(output).split('\n')[:-1]

    newdict = {}
    for line in splitthis:
        elements = line.split(None, 3)
        pid = elements[0]
        desktop = int(elements[1])
        theclass = elements[2]
        title = elements[3]

        pos = ''
        index = 0

        # if not desktop<0:
        newdict[pid] = {'desktop': desktop, 'theclass': theclass, 'title': title, 'pos': pos, 'index': index}


    from globaldef import windowsfile
    if os.path.exists(windowsfile):
        from globaldef import windowsfile
        with open(windowsfile, 'rb') as handle:
            olddict = pickle.load(handle)

            for pid in newdict:
                try:
                    newdict[pid]['pos'] = olddict[pid]['pos']
                    newdict[pid]['index'] = olddict[pid]['index']
                except:
                    None
    from globaldef import windowsfile
    with open(windowsfile, 'wb') as handle:
        pickle.dump(newdict, handle)


def winresizegen(winid, winpos = None, windesk = None):
    import math
    import pickle
    import time

    from globaldef import monitorsfile
    with open(monitorsfile, 'rb') as handle:
        mondict = pickle.load(handle)

    if winpos is not None:
        #I allowed both options but I should input winpos as a string
        winpossimp = int(str(winpos).strip('f'))
        if str(winpossimp) != str(winpos):
            fullscreen = 1
            monitor = int(winpossimp)
        else:
            fullscreen = 0
            monitor = int(math.ceil(float(winpossimp)/2))

        winx = mondict[monitor]['offwidth']
        winy = mondict[monitor]['offheight']
        winwidth = mondict[monitor]['width']
        winheight = mondict[monitor]['height']

        if fullscreen == 1:
            x = winx
            y = winy
            width = winwidth
            height = winheight
            winmvpos(x, y, width, height, winid = winid)
            addmaxvert(winid)
            time.sleep(0.1) #seems necessary for spotify to work correctly
            addmaxhorz(winid)
        else:
            if math.ceil(float(winpos)/2) == float(winpos)/2: #so it's even and thus on the RHS
                x = int(winx + winwidth/2)
                y = winy
                width = int(winwidth/2)
                height = winheight
                winmvpos(x, y, width, height, winid = winid)
                addmaxvert(winid)
            else:
                x = winx
                y = winy
                width = int(winwidth/2)
                height = winheight
                winmvpos(x, y, width, height, winid = winid)
                addmaxvert(winid)

    if windesk is not None:
        winmvdesktop(windesk, winid = winid)

    from globaldef import windowsfile
    if not os.path.exists(windowsfile):
        getwindet()


def winresizeactive(winpos = None, windesk = None):
    getwindet()

    curid = getactiveid()
    winresizegen(curid, winpos = winpos, windesk = windesk)


def winassignposgen(winid, winpos = None, windesk = None):
    import pickle

    from globaldef import windowsfile
    with open(windowsfile, 'rb') as handle:
        windict = pickle.load(handle)
    if winpos is not None:
        windict[winid]['pos'] = str(winpos) #just in case, make sure assign string
    if windesk is not None:
        windict[winid]['desktop'] = str(desktop)

    from globaldef import windowsfile
    with open(windowsfile, 'wb') as handle:
        pickle.dump(windict, handle)


def winassignposactive(winpos = None, windesk = None):
    curid = getactiveid()
    winassignposgen(curid, winpos = winpos, windesk = windesk)


def winresizeandassignposgen(winid, winpos = None, windesk = None):
    winresizegen(winid, winpos = winpos, windesk = windesk)
    winassignposgen(winid, winpos = winpos, windesk = windesk)


def winresizeandassignposactive(winpos = None, windesk = None):
    curid = getactiveid()
    winresizeandassignposgen(curid, winpos = winpos, windesk = windesk)


def savecurdesktop():
    from globaldef import savedir
    with open(savedir + 'curdesktop', 'w') as f:
        f.write(str(getcurdesktop()))


def getnewwinid(classarray = None):
    import pickle

    #Run getwindet() before opening new window (otherwise may pick up old windows)
    try: #windowsfile may not exist
        from globaldef import windowsfile
        with open(windowsfile, 'rb') as handle:
            olddict = pickle.load(handle)
    except:
        olddict = {}
    getwindet()
    from globaldef import windowsfile
    with open(windowsfile, 'rb') as handle:
        newdict = pickle.load(handle)
    newpid = None
    for pid in newdict:
        if not pid in olddict:
            # newpid == pid when either I don't care about the class of the array or it is the correct class
            if classarray is None or newdict[pid]['theclass'] in classarray:
                newpid = pid
    if newpid != None:
        return(newpid)
    else:
        raise('None')
    

def getnewwinid_rep(classarray = None, secsstop = 2):
    import time

    secs = 0
    interval = 0.1
    while secs< secsstop:
        try:
            return(getnewwinid(classarray))
        except:
            secs = secs + interval
            time.sleep(interval)
    return(False)
    

def testnewactive(classarray = None):
    import os
    import pickle

    #Run getwindet() before opening new window (otherwise may pick up old windows)
    try:
        curid = getactiveid() #don't put this in try since use later
    except:
        return(False)
    #Windowsfile may not exists:
    from globaldef import windowsfile
    if os.path.isfile(windowsfile):
        from globaldef import windowsfile
        with open(windowsfile, 'rb') as handle:
            windict = pickle.load(handle)
        #False if now window opened:
        if curid in windict:
            return(False)
    if classarray is None:
        return(True)
    else:
        #Check of correct class:
        getwindet()
        from globaldef import windowsfile
        with open(windowsfile, 'rb') as handle:
            windict = pickle.load(handle)
        if curid in windict:
            if windict[curid]['theclass'] in classarray:
                return(True)
            else:
                print('different class')
                return(False)
        else:
            return(False)
            

def testnewactive_rep(classarray):
    import time

    secs = 0
    interval = 0.1
    while secs<2:
        pid = testnewactive(classarray)
        if pid is not False:
            return(pid)
        secs = secs + interval
        time.sleep(interval)
    raise NameError('test')


def selectbyid(winid):
    import subprocess

    subprocess.call(['wmctrl', '-i', '-a', str(winid)])


def selectbymyid(theid):
    getwindet()
    savecurdesktop()

    from globaldef import savedir
    with open(savedir + 'id_' + theid, 'r') as f:
        pid = f.read()
    selectbyid(pid)


def selectbyclass(classtype): 
    import pickle
    import subprocess

    if not isinstance(classtype, list): #true if list, false if not
        classtype = [classtype]
        
    getwindet()
    curid = getactiveid()
    from globaldef import windowsfile
    with open(windowsfile, 'rb') as handle:
        windict = pickle.load(handle)

    #Doesn't seem to work if on desktop so added try, except
    try:
        if windict[curid]['theclass'] in classtype:
            windict[curid]['index'] = 999
    except:
        None

    minindex = 999
    minpid = None
    for pid in windict:
        if windict[pid]['theclass'] in classtype and windict[pid]['desktop'] == getcurdesktop() and windict[pid]['index']<=minindex:
            minindex = windict[pid]['index']
            minpid = pid
    windict[minpid]['index'] = -1
    subprocess.call(['wmctrl', '-i', '-a', minpid])
    listpidindex = []
    def getKey(item):
        return(item[0])
    listpidindex = []
    for pid in windict:
        listpidindex.append([windict[pid]['index'], pid])
    listpidindex = sorted(listpidindex, key = getKey)
    for i in range(0, len(listpidindex)):
        pid = listpidindex[i][1]
        windict[pid]['index'] = i + 1
    from globaldef import windowsfile
    with open(windowsfile, 'wb') as handle:
        pickle.dump(windict, handle)


def selectbyposition(pos): 
    import pickle
    import subprocess

    if isinstance(pos, list): #true if list, false if not
        pos = [str(p) for p in pos]
    else:
        pos = [str(pos)]
        
    getwindet()
    curid = getactiveid()

    from globaldef import windowsfile
    with open(windowsfile, 'rb') as handle:
        windict = pickle.load(handle)

    try:
        if windict[curid]['pos'] in pos:
            windict[curid]['index'] = 999
    except:
        None

    minindex = 999
    minpid = None
    for pid in windict:
        if windict[pid]['pos'] in pos and windict[pid]['desktop'] == getcurdesktop() and windict[pid]['index']<=minindex:
            minindex = windict[pid]['index']
            minpid = pid
    try:
        windict[minpid]['index'] = -1
        subprocess.call(['wmctrl', '-i', '-a', minpid])
        listpidindex = []
        def getKey(item):
            return(item[0])
        listpidindex = []
        for pid in windict:
            listpidindex.append([windict[pid]['index'], pid])
        listpidindex = sorted(listpidindex, key = getKey)
        for i in range(0, len(listpidindex)):
            pid = listpidindex[i][1]
            windict[pid]['index'] = i + 1
        from globaldef import windowsfile
        with open(windowsfile, 'wb') as handle:
            pickle.dump(windict, handle)
    except:
        None


def resizenewclass(getdefaultposdict, theclass):
    dicts = getdefaultposdict()
    byclassdict = dicts['classdict']
    
    if testnewactive_rep([theclass]):
        winresizeactive(winpos = byclassdict[theclass])
        winassignposactive(winpos = byclassdict[theclass])


def newwinclassandresize(getdefaultposdict, newwincommand, theclass):
    import subprocess

    getwindet()
    print(newwincommand[theclass]) #DME
    subprocess.call(newwincommand[theclass] + ' & exit', shell = True)

    resizenewclass(getdefaultposdict, theclass)


def assignidgen(pid, theid):
    from globaldef import savedir
    with open(savedir + 'id_' + theid, 'w') as f:
        f.write(pid)


def assignidactive(theid):
    pid = getactiveid()
    assignidgen(pid, theid)


def assignandmoveidgen(getdefaultposdict, idworkspace, pid, theid):
    dicts = getdefaultposdict()
    byiddict = dicts['iddict']

    winresizegen(pid, winpos = byiddict[theid])
    winassignposgen(pid, winpos = byiddict[theid])
    if idworkspace[theid] != 99:
        winmvdesktop(idworkspace[theid], winid = pid)

    assignidgen(pid, theid)


def assignandmoveidactive(getdefaultposdict, idworkspace, theid):
    pid = getactiveid()

    dicts = getdefaultposdict()
    byiddict = dicts['iddict']

    winresizegen(pid, winpos = byiddict[theid])
    winassignposgen(pid, winpos = byiddict[theid])
    if idworkspace[theid] != 99:
        winmvdesktop(idworkspace[theid], winid = pid)
        changedesktop(idworkspace[theid])

    assignidgen(pid, theid)


def newwinidandresize(getdefaultposdict, idwmclass, idworkspace, newwincommand, theid):
    import subprocess

    getwindet()
    savecurdesktop()

    dicts = getdefaultposdict()
    byiddict = dicts['iddict']
    theclass = idwmclass[theid]
    thecommand = newwincommand[theclass]

    #byiddict[theid] returns the right dictionary. Then select mon and pos of this dictionary.

    subprocess.call(thecommand + ' & exit', shell = True)
    if testnewactive_rep([theclass]):
        assignandmoveidactive(getdefaultposdict, idworkspace, theid)


def selectornewwinid(getdefaultposdict, idwmclass, idworkspace, newwincommand, theid):
    import pickle

    pidexists = 0
    try:
        from globaldef import savedir
        with open(savedir + 'id_' + theid, 'r') as f:
            pid = f.read()
        getwindet()
        from globaldef import windowsfile
        with open(windowsfile, 'rb') as handle:
            windict = pickle.load(handle)
        if pid in windict:
            pidexists = 1
    except:
        None
    if pidexists == 1:
        selectbymyid(theid)
    else:
        newwinidandresize(getdefaultposdict, idwmclass, idworkspace, newwincommand, theid)


def windefaults(getdefaultposdict, idworkspace):
    import os
    import pickle
    import subprocess

    from globaldef import windowsfile
    if os.path.isfile(windowsfile):
        from globaldef import windowsfile
        subprocess.call(['rm', windowsfile])
    getwindet()
    from globaldef import windowsfile
    with open(windowsfile, 'rb') as handle:
        windict = pickle.load(handle)
    from globaldef import monitorsfile
    with open(monitorsfile, 'rb') as handle:
        mondict = pickle.load(handle)

    dicts = getdefaultposdict()
    byclassdict = dicts['classdict']
    byiddict = dicts['iddict']

    for pid in windict:
        try:
            pos = byclassdict[windict[pid]['theclass']]
            winresizegen(pid, winpos = pos)
            windict[pid]['pos'] = str(pos)
        except:
            continue
    for theid in byiddict:
        try:
            from globaldef import savedir
            with open(savedir + 'id_' + theid, 'r') as f:
                pid = f.read()

            pos = byiddict[theid]
            winresizegen(pid, winpos = pos)
            if idworkspace[theid] != 99:
                winmvdesktop(idworkspace[theid], winid = pid)
            windict[pid]['pos'] = str(pos)
        except:
            continue
    from globaldef import windowsfile
    with open(windowsfile, 'wb') as handle:
        pickle.dump(windict, handle)


#EXTENSIONS:{{{1
def golastdesktop():
    import subprocess

    from globaldef import savedir
    with open(savedir + 'curdesktop', 'r') as f:
        curdesk = f.read()
    subprocess.call(['wmctrl', '-s', curdesk])


def movenewwintocurdesk():
    """
    Get the winid of the libreoffice thing and move it
    """
    newwinid = getnewwinid_rep(secsstop = 5)

    if newwinid is False:
        # no newwinid
        return(0)

    # desktop I am currently on
    activedesk = getcurdesktop()

    # get desktop of libreoffice window
    from globaldef import windowsfile
    with open(windowsfile, 'rb') as handle:
        windict = pickle.load(handle)
    curwindesk = windict[newwinid]['desktop']
    
    if activedesk != curwindesk:
        winmvdesktop(activedesk, winid = newwinid)


def movetocurwindesk():
    """
    Get the winid of the libreoffice thing and move it
    """
    newwinid = getnewwinid_rep(secsstop = 5)

    if newwinid is False:
        # no newwinid
        return(0)

    # desktop I am currently on
    activedesk = getcurdesktop()

    # get desktop of libreoffice window
    from globaldef import windowsfile
    with open(windowsfile, 'rb') as handle:
        windict = pickle.load(handle)
    curwindesk = windict[newwinid]['desktop']
    
    if activedesk != curwindesk:
        # winmvdesktop(activedesk, winid = newwinid)
        changedesktop(curwindesk)


