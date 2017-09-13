#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#
# Needs psutil (+ dependencies) installing:
#    luma display lib: git clone https://github.com/rm-hull/luma.core
#    sudo apt-get install python-dev
#    sudo pip install psutil
#    copy this file into the /luma.examples/examples dir.

import os
import sys
import time
from time import gmtime, strftime
from datetime import datetime
if os.name != 'posix':
    sys.exit('{} platform not supported'.format(os.name))

import os.path # For checking if the tempData.txt file exists.
import psutil
import math

from demo_opts import device
# from oled.render import canvas
# from PIL import ImageFont

from demo_opts import device
from luma.core.render import canvas
from PIL import ImageFont

def checkRun():
    pServ = False
    pConn = False

    try:
        for pid in psutil.pids():
            p = psutil.Process(pid)

            if p.name() == "python" and len(p.cmdline()) > 1 and "PlexConnect.py" in p.cmdline()[1]:
                pConn = True            
        
            if p.name() == "Plex Media Server":
                pServ = True

        return pConn, pServ
    except:
        return False, False
    
def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

def cpu_usage():
    # load average, uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    return "CPU:%.1f %.1f %.1f Up: %s" \
        % (av1, av2, av3, str(uptime).split('.')[0])


def mem_usage():
    usage = psutil.virtual_memory()
    return bytes2human(usage.used), 100 - usage.percent
    # return "Mem: %s %.0f%%" \
        # % (bytes2human(usage.used), 100 - usage.percent)



def disk_usage(dir):
    try:
        usage = psutil.disk_usage(dir)
        return bytes2human(usage.free), usage.percent
        #return "SD:  %s %.0f%%" \
        #    % (bytes2human(usage.used), usage.percent)
    except:
        # USB HDD has crashed...
        return -1,-1


def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx%s, Rx%s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))


def firstTime(device):
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 12)

    with canvas(device) as draw:        
        draw.text((40, 30), "Loading", font=font2, fill="yellow")

def stats(device):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 12)

    with canvas(device) as draw:
        '''
        if device.height >= 64:
            draw.text((12, 26), disk_usage('/'), font=font2, fill="white")
            try:
                draw.text((12, 38), network('eth0'), font=font2, fill="white")
            except KeyError:
                # no wifi enabled/available
                pass
        '''
        
        # System uptime. Not currently used. Might come in handy...
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())

        # CPU load.
        av1, av2, av3 = os.getloadavg()
        liveLoad = int((av1 / 4)* 100)
        if liveLoad > 100:
            liveLoad = 100
            
        barHeight = int(((av1 / 4) * 38))
        if barHeight > 38:
            barHeight = 38

        x_start = 0
        if liveLoad < 10:
            x_start = 3
            
        draw.text((x_start, 0), str(liveLoad) +"%", font=font2, fill="yellow")
        draw.rectangle((3, 50, 13, 12), outline="red")
        draw.rectangle((3, 50, 13, 50 - barHeight), fill="white")
        draw.text((0, 52), "CPU", font=font2, fill="blue")

        # RAM Usage...
        mem_used, percentage = mem_usage()
        # print(percentage)
        barHeight = int(((percentage / 100)*38))
        draw.text((25, 0), str(int(percentage)) + "%", font=font2, fill="white")
        draw.rectangle((28, 50, 38, 12), outline="white")
        draw.rectangle((28, 50, 38, 50 - barHeight), fill="yellow")
        draw.text((23, 52), "RAM", font=font2, fill="blue")        

        # HDD Usage...
        hdd_used, percentage = disk_usage('/')
        barHeight = int(((percentage / 100)*38))
        draw.text((50, 0), str(int(percentage)) +"%", font=font2, fill="white")
        draw.rectangle((53, 50, 63, 12), outline="white")
        draw.rectangle((53, 50, 63, 50 - barHeight), fill="white")
        draw.text((50, 52), "HDD", font=font2, fill="blue")

        '''
        # USB HDD Usage...
        hdd_used, percentage = disk_usage('/mnt/usbhdd/')
        draw.text((75, 52), "USB", font=font2, fill="blue")

        if hdd_used != -1:
            barHeight = int(((percentage / 100)*38))
            draw.text((75, 0), str(int(percentage)) +"%", font=font2, fill="white")
            draw.rectangle((78, 50, 88, 12), outline="white")
            draw.rectangle((78, 50, 88, 50 - barHeight), fill="white")
        else:
            # USB HDD has dismounted...
            draw.rectangle((78, 50, 88, 12), outline="white")
            draw.line((78, 50, 88, 12),fill=1)
            draw.line((78, 12, 88, 50),fill=1)
            draw.text((77, 0), "--%", font=font2, fill="white")
        '''
            
        # Service status...
        pCon, pSer = checkRun()
        # draw.text((78, 5), "Conn", font=font2, fill="white")
        # draw.text((78, 15), "Server", font=font2, fill="white")
        
        if pCon == True:
            draw.text((75, 5), "Conn: On", font=font2, fill="green")
        else:
            draw.text((75, 5), "Conn: Off", font=font2, fill="red")

        if pSer == True:
            draw.text((75, 15), "Plex: On", font=font2, fill="green")
        else:
            draw.text((75, 15), "Plex: Off", font=font2, fill="red")

        draw.text((75, 25), "HDD: " + str(hdd_used), font=font2, fill="red")

        CPUtemp = getCPUtemperature()
        draw.text((75, 35), "CPU: " + CPUtemp + "C", font=font2, fill="white")

        theDate = strftime("%d-%m-%Y", gmtime())
        theTime = strftime("%H:%M:%S", gmtime())
        draw.text((75, 45), theTime, font=font2, fill="white")
        draw.text((75, 55), theDate, font=font2, fill="white")

        # Append the data file.
        CPUtempData = 'tempData.txt'

        if os.path.isfile(CPUtempData) == False:
            # File doesn't exist?
            f = open(CPUtempData, 'w')
            f.write(CPUtemp + "\n")
            f.close()
            
        f = open(CPUtempData)
        numRecs = 0
        currRecs = []

        for line in f:
            numRecs +=1
            currRecs.append(line)

        # Limit to 100 records.
        if numRecs > 100:
            f = open(CPUtempData, 'w')
            for i in range(1,101):
                f.write(currRecs[i])
        else:
            f = open(CPUtempData, 'a')

        f.write(CPUtemp + "\n")
        f.close()

        
def graph(device):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 12)

    f = open('tempData.txt')
    lowest = 1000000
    highest = -1000000
    values = []
    lastVal = 0
    
    for line in f:
        line = line.rstrip()
        line = int(float(line))
        if line > highest:
            highest = line
        if line < lowest:
            lowest = line
        values.append(line)
        lastVal = line
    
    f.close()
    
    with canvas(device) as draw:
        draw.text((0, 25), "(C)", font=font2, fill="white")
        draw.line((25, 0, 25, 58), fill="white")
        draw.line((25, 0, 20, 5), fill="white")
        draw.line((25, 0, 30, 5), fill="white")
        draw.line((25, 58, 127, 58), fill="white")
        draw.line((127, 58, 123, 53), fill="white")
        draw.line((127, 58, 123, 63), fill="white")
        # draw.line((30, 30, 128, 30), fill="white")

        # Plotting points...
        # y = 58 is the location of the origin on the y axis.
        # y = 8 is the highest point we probably want to draw up to.
        # Range of 50 pixels to be used to show values.
        highest += 5
        lowest -= 5
        dataRange = highest - lowest

        if dataRange >= 50:
            perPixel = dataRange/50.0
        
            currX = 26
            lastY = 58 - (math.ceil(values[0] * perPixel))
            draw.text((12, 53), str(lowest), font=font2, fill="white")
            draw.text((12, 6), str(highest), font=font2, fill="white")
        
            for nextVal in values:
                nextVal = 58 - (math.ceil(nextVal * perPixel))
                # print nextVal
                draw.line((currX - 1, lastY, currX, nextVal), fill="white")
                # draw.point((currX, nextVal), fill="white")
                currX += 1
                lastY = nextVal

        else:
            perPixel = 50.0 / dataRange
            currX = 26
            lastY = 58 - ((values[0] - lowest) * perPixel)
            draw.text((12, 53), str(lowest), font=font2, fill="white")
            draw.text((12, 6), str(highest), font=font2, fill="white")
        
            for nextVal in values:
                nextVal = 58 - ((nextVal - lowest) * perPixel)
                # print nextVal
                draw.line((currX - 1, lastY, currX, nextVal), fill="white")
                # draw.point((currX, nextVal), fill="white")
                currX += 1
                lastY = nextVal

        draw.text((30, 45), "CPU: " + str(lastVal) + "C", font=font2, fill="white")
                
def main():    
    time.sleep(3)
    firstTime(device)
    
    while True:
        stats(device)
        time.sleep(2)
        graph(device)
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
