#!/usr/bin/python
# coding=UTF-8

import smbus
import time
import datetime
import feedparser
import sys

# OpenWeatherMap key...
weatherKey=''
import pyowm
owm = pyowm.OWM(weatherKey)

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 20   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def left(s, amount):
  return s[:amount]

def right(s, amount):
  return s[-amount:]

def scrollIt(theText,lineNum):
  # Scrolls text on the LCD display.
  while theText!="":
    lcd_string(theText, LCD_LINE_4)
    theText = theText[1:]
    time.sleep(0.1)
  lcd_string("", LCD_LINE_4)
    
def main():
  # Initialise display
  lcd_init()
  whichHeadline = 0

  while True:
    theTime = str(datetime.datetime.now().time())
    theDate = time.strftime("%d/%m/%Y")
    lcd_string(" " + theTime[0:5] + ", " + theDate,LCD_LINE_1)

    try:
      observation = owm.weather_at_place('Market Deeping,uk')
      w = observation.get_weather()
      
      weather = w.get_detailed_status()
      if len(weather) > 20:
        weather = w.get_status()
      
      weather = weather[0].upper() + weather[1:]
      wLength=len(weather)
      wLength = (20 - wLength) // 2
      weather = (' ' * wLength) + weather
    
      currTemp = w.get_temperature(unit='celsius')
      humid = w.get_humidity()
      wind = w.get_wind() 
      windspeed = int(wind['speed'])
    
      sunset = w.get_sunset_time('iso')
      sunset = right(sunset,11)
      sunset = left(sunset,8)

      cloud = w.get_clouds()

      lcd_string(weather,LCD_LINE_2)
      lcd_string("T:" + str(int(currTemp['temp'])) + "C, " + "W:" + str(windspeed) + "m/s, C:" + str(cloud) + "%",LCD_LINE_3)
      # lcd_string("Sunset: " + sunset,LCD_LINE_4)

      # Display top 5 headlines from BBC RSS feed.
      d = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=uk')
      headline= d['entries'][whichHeadline]['title']
      whichHeadline += 1
      if whichHeadline > 4:
        whichHeadline = 0
        
      scrollIt("BBC News headlines: " + headline,4)
      lcd_string("BBC News headlines:",LCD_LINE_4)
      
      time.sleep(5)
    except:
      print "Unexpected error:", sys.exc_info()[0]
      lcd_string("Weather unavailable",LCD_LINE_3)
      lcd_string("",LCD_LINE_4)      
      time.sleep(5)
      
if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
