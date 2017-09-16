#!/usr/bin/python
# coding=UTF-8

# For the AliExpress 2.4" 240x320 SPI TFT screen I used, I used this to get the display working:
# https://github.com/watterott/RPi-Display/blob/master/docs/FBTFT-Install.md#fbtft-framebuffer-installation

##  Do a sudo pip install for feedparser, pyown and psutil

########
##  Import lots of libraries.
########
import time
import datetime
import feedparser
import sys
import pygame
import os
import io
import pyowm
from urllib2 import urlopen

# ...and these ones for the system stats
import os.path # For checking if the tempData.txt file exists.
import psutil
import math

# OpenWeatherMap API key...
weatherKey='SIGN UP FOR A FREE KEY'
owm = pyowm.OWM(weatherKey)

#########
##  Set up globals
########
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
lcd = pygame.display.set_mode((320, 240))
pygame.mouse.set_visible(False)
# Dampen down the colours a bit to help limit screen burn-in.
white = (230, 230, 230)
black = (40, 40, 40)
red = (200, 0, 0)
yellow = (200, 200, 0)
green = (0, 200, 0)
grey = (175, 175, 175)

########
##  General-purpose functions.
########

def left(s, amount):
  return s[:amount]

def right(s, amount):
  return s[-amount:]

def drawText(msgText, fontSize, xLoc, yLoc, colour=black):
  fontName = pygame.font.match_font('arial')
  font = pygame.font.Font(fontName, fontSize)
  text_surface = font.render(msgText, True, colour)
  lcd.blit(text_surface, (xLoc, yLoc))

########
##  Functions for the news/weather page
########

def renderNews():
  # Display top 3 headlines from BBC RSS feed.
  d = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=uk')

  # Show BBC logo.
  image = pygame.image.load('bbc.png')
  image = pygame.transform.scale(image, [102,57]) # Original is 1024 x 576
  lcd.blit(image, (100, 5))

  yPos = 65 # y location of the first headline. 25

  for nextHeadline in range (3):
    headline= d['entries'][nextHeadline]['title'] + "."
    
    try:
      if len(headline) > 26:
        # Track down a space before starting a new line.
        spaceLoc = 26
        gotOne = False

        while gotOne == False and spaceLoc < len(headline):
          if headline[spaceLoc] == ' ':
            gotOne = True

          spaceLoc += 1

        drawText(headline[0:spaceLoc], 20, 5, yPos)
        drawText(headline[spaceLoc:], 20, 5, yPos + 25)
      else:
        drawText(headline, 20, 5, yPos + 12)

      yPos += 60
      
      pygame.display.update()
    except:
      print "News error:", sys.exc_info()[0]
      print "News error:", sys.exc_info()[1]

def renderWeather():
  # Renders the weather onto the display
  observation = owm.weather_at_place('Market Deeping,uk')
  w = observation.get_weather()

  weather = w.get_detailed_status()
  weather = weather[0].upper() + weather[1:]
  currTemp = w.get_temperature(unit='celsius')
  humid = w.get_humidity()
  wind = w.get_wind() 
  windspeed = int(wind['speed'])
  sunrise = w.get_sunrise_time('iso')
  sunrise = right(sunrise,11)
  sunrise = left(sunrise,8)
  sunset = w.get_sunset_time('iso')
  sunset = right(sunset,11)
  sunset = left(sunset,8)
  cloud = w.get_clouds()

  # Show the weather icon
  pygame.draw.rect(lcd, grey, (0, 0, 320, 93))
  icon = w.get_weather_icon_name()
  renderWeatherIcon(icon, -15, -20)
  drawText(weather, 25, 72, 13)
  drawText("Temp: " + str(int(currTemp['temp'])) + "C, " + "Wind: " + str(windspeed) + "m/s, Cloud: " + str(cloud) + "%",17, 5, 53)
  drawText("Sunrise: " + sunrise + ", Sunset: " + sunset, 17, 5, 73)

  try:
    # Do the 3-hourly forecast...
    hourlyFc = owm.three_hours_forecast('Market Deeping,uk')
    f = hourlyFc.get_forecast()
    lst = f.get_weathers()

    pygame.draw.rect(lcd, grey, (0, 95, 320, 73))
    x=15
    for weather in lst:
      if x < 300:
        icon = weather.get_weather_icon_name()
        theTemp = int(weather.get_temperature(unit='celsius')['temp'])
        forecastTime = weather.get_reference_time('iso')
        forecasthour = int(forecastTime[11:13])
        if forecasthour<12:
          suffix = "am"
        elif forecasthour == 0:
          forecasthour = 12
          suffix = "am"
        else:
          forecasthour -= 12
          suffix = "pm"
        renderWeatherIcon(icon, x, 100, 40, 40)
        drawText(str(forecasthour) + suffix, 15, x+3, 95)
        drawText(str(theTemp) + "C", 15, x + 22 - len(str(theTemp) + "C") * 5, 145)
        drawText(weather.get_status(), 10, x + 20 - len(weather.get_status()) * 3, 133)
        
        x += 50
        
    # Do the 6-day forecast...
    dailyFc = owm.daily_forecast('Market Deeping,uk', limit=6)
    f = dailyFc.get_forecast()
    lst = f.get_weathers()
    pygame.draw.rect(lcd, grey, (0, 170, 320, 85))
    x=15
    for weather in lst:
      if x < 300:
        icon = weather.get_weather_icon_name()
        theTemp = int(weather.get_temperature(unit='celsius')[u'day'])
        forecastTime = weather.get_reference_time('iso')
        forecastday = str(forecastTime[8:10])

        if forecastday.endswith('1'):
          suffix = "st"
        elif forecastday.endswith('2'):
          suffix = "nd"
        elif forecastday.endswith('3'):
          suffix = "rd"
        else:
          suffix = "th"

        renderWeatherIcon(icon, x, 177, 40, 40)
        drawText(str(forecastday) + suffix, 15, x+3, 170)
        drawText(str(theTemp) + "C", 15, x + 22 - len(str(theTemp) + "C") * 5, 220)
        drawText(weather.get_status(), 10, x + 20 - len(weather.get_status()) * 3, 210)
        
        x += 50
        
    pygame.display.update()
  except:
    # Weather trouble...
    print "Weather error:", sys.exc_info()[0]
    print "Weather error:", sys.exc_info()[1]
    drawText("Weather unavailable",20, 5, 5)
    pygame.display.update()

    
def renderWeatherIcon(icon, xPos, yPos, xSize=90, ySize=90):
  # Renders a weather icon onto the display
  image_url = "http://openweathermap.org/img/w/" + icon + ".png"
  image_str = urlopen(image_url).read()
  image_file = io.BytesIO(image_str)
  image = pygame.image.load(image_file)
  image = pygame.transform.scale(image, [xSize,ySize])
  lcd.blit(image, (xPos, yPos))

def paintTime(numSecs = 5):
  # Show the time / date at the bottom for 5s, then update everything else.
  for x in range(numSecs * 2):
    theTime = str(datetime.datetime.now().time())
    theDate = time.strftime("%d/%m/%Y")
    pygame.draw.rect(lcd, white, (0, 185, 320, 225))
    drawText(theTime[0:8] + ", " + theDate,32,5,205)
    pygame.display.update()
    time.sleep(0.5)

########
## System stats functions
########

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
    uptime = datetime.datetime.now() - datetime.fromtimestamp(psutil.boot_time())
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

def updateCPUTempLog():
  # Append the data file.
  CPUtempData = 'tempData.txt'

  if os.path.isfile(CPUtempData) == False:
      # File doesn't exist?
      f = open(CPUtempData, 'w')
      f.write(getCPUtemperature() + "\n")
      f.close()

  f = open(CPUtempData)
  numRecs = 0
  currRecs = []

  for line in f:
      numRecs +=1
      currRecs.append(line)

  # Limit to 100 records.
  if numRecs > 130:
      f = open(CPUtempData, 'w')
      for i in range(1,131):
          f.write(currRecs[i])
  else:
      f = open(CPUtempData, 'a')

  f.write(getCPUtemperature() + "\n")
  f.close()  

def stats():
  try:
    # System uptime. Not currently used. Might come in handy...
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())

    # CPU load.
    av1, av2, av3 = os.getloadavg()
    liveLoad = int((av1 / 4)* 100)
    if liveLoad > 100:
        liveLoad = 100

    barHeight = int(((av1 / 4) * 100))
    if barHeight > 100:
        barHeight = 100

    if barHeight > 90:
      barColour = red
    elif barHeight >50:
      barColour = yellow
    else:
      barColour = green

    '''
    x_start = 0
    if liveLoad < 10:
        x_start = 3
    '''
    
    # drawText(str, size, x, y)
    drawText("System Statistics", 25, 5, 5)
    drawText(str(liveLoad) + "%", 15, 6, 55)
    pygame.draw.rect(lcd, barColour, (5, 170 - barHeight, 25, barHeight))
    pygame.draw.rect(lcd, black, (5, 70, 25, 100), 2)
    drawText("CPU", 15, 2, 170)
    
    # RAM Usage...
    mem_used, percentage = mem_usage()
    # print(percentage)
    barHeight = int(((percentage / 100)*100))
    drawText(str(int(percentage)) + "%", 15, 45, 55)

    if barHeight > 90:
      barColour = red
    elif barHeight >80:
      barColour = yellow
    else:
      barColour = green
    
    pygame.draw.rect(lcd, barColour, (45, 170 - barHeight, 25, barHeight))
    pygame.draw.rect(lcd, black, (45, 70, 25, 100), 2)
    drawText("RAM", 15, 41, 170)
    
    # HDD Usage...
    hdd_used, percentage = disk_usage('/')
    barHeight = int(((percentage / 100)*100))

    if barHeight > 93:
      barColour = red
    elif barHeight >75:
      barColour = yellow
    else:
      barColour = green
    
    drawText(str(int(percentage)) +"%", 15, 84, 55)
    pygame.draw.rect(lcd, barColour, (85, 170 - barHeight, 25, barHeight))
    pygame.draw.rect(lcd,black, (85, 70, 25, 100), 2)
    drawText("HDD", 15, 83, 170)

    # Service status...
    pCon, pSer = checkRun()

    drawText("PlexConnect:", 17, 130, 80, black)
    if pCon == True:
      drawText("Running", 17, 230, 80, green)
    else:
      drawText("Stopped", 17, 230, 80, red)

    drawText("Plex Server:", 17, 130, 100, black)
    if pSer == True:
      drawText("Running", 17, 230, 100, green)
    else:
      drawText("Stopped", 17, 230, 100, red)

    drawText("Free HDD: " + str(hdd_used), 17, 130, 120)
    
    CPUtemp = getCPUtemperature()
    drawText("CPU temperature: " + CPUtemp + "C", 17, 130, 140)

    theTime = str(datetime.datetime.now().time())
    theDate = time.strftime("%d/%m/%Y")
    # pygame.draw.rect(lcd, white, (0, 185, 320, 225))
    drawText(theTime[0:8] + ", " + theDate,32,5,205)
    pygame.display.update()
  except:
    print "Unexpected error:", sys.exc_info()[0]          
    print "Unexpected error:", sys.exc_info()[1]
  
def graph():
    # Render the CPU temperature graph
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

    howThick = 3
    drawText("CPU Temperature", 25, 65, 5)
    pygame.draw.line(lcd, black, (25, 25), (25, 200), howThick)
    pygame.draw.line(lcd, black, (25, 25), (10, 40), howThick)
    pygame.draw.line(lcd, black, (25, 25), (40, 40), howThick)
    pygame.draw.line(lcd, black, (25, 200), (300, 200), howThick)
    pygame.draw.line(lcd, black, (300, 200), (285, 185), howThick)
    pygame.draw.line(lcd, black, (300, 200), (285, 215), howThick)

    # Label up the Y axis
    labelYloc = 200
    for temp in range(30, 100, 10):
      drawText(str(temp), 12, 6, int(labelYloc) - 5)
      pygame.draw.line(lcd, black, (22, int(labelYloc)), (28, int(labelYloc)), 2)
      labelYloc -= 29.1

    # Plotting points...
    # y = 200 is the location of the origin on the y axis.
    # y = 25 is the highest point we probably want to draw up to.
    # Range of 175 pixels to be used to show values.
    highest = 25
    lowest = 200
    # There are 175 pixels of Y axis, and a range of 60C (30C-90C)
    # Each degree is 2.91 pixels.
    perPixel = 2.91
    currX = 28
    lastY = 200 - ((values[0] - 30) * perPixel)

    for nextVal in values:
        # print nextVal. Pretty colours...
        if nextVal > 80:
          whatColour = red
        elif nextVal > 60:
          whatColour = yellow
        else:
          whatColour = green

        nextVal = 200 - ((nextVal - 30) * perPixel)
        pygame.draw.line(lcd, whatColour, (currX - 2, lastY), (currX, nextVal), 3)
        currX += 2
        lastY = nextVal

    theTime = str(datetime.datetime.now().time())
    theDate = time.strftime("%d/%m/%Y")
    drawText(theTime[0:8] + ", " + theDate,32,5,205)        
    drawText("CPU: " + str(lastVal) + "C", 14, 210, 30)
    pygame.display.update()

########
## System stats function ends.
########

########
## Multi-day forecast code starts
########

def multiDay():
  # Grab forecast
  fc = owm.daily_forecast('London,uk', limit=6)
  # Render it

########
## Multi-day forecast code starts
########



########
## Main program loop
########

def main():
  whichHeadline = 0
  lcd.fill(white)
  
  while True:
    # Show system stats
    lcd.fill(white)
    for n in range(10):
      stats()
      time.sleep(0.5)
      lcd.fill(white)
      
    # Show weather
    lcd.fill(white)
    renderWeather()
    time.sleep(5)

    # Append the CPU log file
    updateCPUTempLog()

    # Show temperature graph
    lcd.fill(white)
    for n in range(10):
      graph()
      time.sleep(0.5)
      lcd.fill(white)    
    
    # Show the news...
    lcd.fill(white)
    renderNews()
    time.sleep(5)

    # Append the CPU log file
    updateCPUTempLog()

main()

'''
if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    pygame.quit()   # stops the PyGame engine
    sys.exit()
'''
