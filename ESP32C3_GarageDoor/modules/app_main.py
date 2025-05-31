"""
MIT License

Copyright (c) 2025 Ramesh R Manubolu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is file contains the application logic and all the Network, LCD, GPIO and 
other peripherals initialization code.

Please see my website for more info on the project and more.
https://rmanubolu.com

"""

from machine import Pin, SPI
import time
import network
import logging
from arduino_iot_cloud import ArduinoCloudClient
import gc9a01
import vga1_8x16 as font
import asyncio
from secrets import SECRET_KEY
from secrets import DEVICE_ID
from secrets import WIFI_SSID
from secrets import WIFI_PASSWORD

# garage door wall control trigger pin
GD_TRIGGER_PIN = 8
garageDoor = Pin(GD_TRIGGER_PIN, Pin.OPEN_DRAIN)

networkSyncEvent = asyncio.Event()
displayUpdateEvent = asyncio.Event()
cloudVarValue = False

#LCD initialization
spi = SPI(1, baudrate=60000000, sck=Pin(6), mosi=Pin(7))
tft = gc9a01.GC9A01(
    spi,
    dc=Pin(2, Pin.OUT),
    cs=Pin(10, Pin.OUT),
    backlight=Pin(3, Pin.OUT),
    rotation=0)

# function to update the display when controlling the Garage Door from Cloud
async def updateDisplay():
    global cloudVarValue
    global displayUpdateEvent
    while True:
        await displayUpdateEvent.wait()
        displayUpdateEvent.clear()
        value = cloudVarValue
        tft.sleep_mode(False)
        tft.fill(gc9a01.BLACK)
        if value:
            tft.text(font, "Opening the Garage", 50, 100, gc9a01.WHITE)
        else:
            tft.text(font, "Closing the Garage", 50, 100, gc9a01.WHITE)
        
        for i in range(10):
            tft.sleep_mode(False)
            await asyncio.sleep(0.5)
            tft.sleep_mode(True)
            await asyncio.sleep(0.5)

        tft.text(font, " ", 50, 100, gc9a01.WHITE)
        tft.sleep_mode(True)

# Callback function for Arduino Cloud
def onChange(client, value):
    global cloudVarValue
    global displayUpdateEvent
    print("Value is: ", value)
    garageDoor.off()
    time.sleep(1)
    garageDoor.on()
    time.sleep(1)
    cloudVarValue = value
    displayUpdateEvent.set()

# Logging module init
def logging_func():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )

# Function to connect to ArduinoCloud
async def connectToArduinoCloud():
    global networkSyncEvent
    while True:
        await networkSyncEvent.wait()
        client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)
        client.register("garage", value=True, on_write=onChange)
        networkSyncEvent.clear()
        client.start()

# function to connect to WiFi
async def do_wifi_connect():
    global networkSyncEvent
    sta_if = network.WLAN(network.WLAN.IF_STA)
    while True:
        if not sta_if.isconnected():
            tft.sleep_mode(False)
            tft.fill(gc9a01.BLACK)
            tft.text(font, "Connecting to Network", 50, 100, gc9a01.WHITE)
            print("Connecting to network...")
            # try connecting to network
            sta_if.active(True)
            sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

            for _ in range(10):
                if sta_if.isconnected():
                    break
                else:
                    await asyncio.sleep(5)

            if sta_if.isconnected():
                tft.fill(gc9a01.BLACK)
                tft.text(font, "Connected", 100, 100, gc9a01.WHITE)
                print("Network Config: ", sta_if.ipconfig('addr4'))
                await asyncio.sleep(5)
                tft.sleep_mode(True)
                networkSyncEvent.set()
        else:
            networkSyncEvent.clear()
            await asyncio.sleep(60)

# App's main function, called from main.py
async def main():
    global displayUpdateEvent
    global networkSyncEvent
    garageDoor.on()
    tft.sleep_mode(False)
    tft.fill(gc9a01.WHITE)
    await asyncio.sleep(1)
    tft.sleep_mode(True)
    logging_func()

    networkSyncEvent.clear()
    displayUpdateEvent.clear()
    asyncio.create_task(do_wifi_connect())
    asyncio.create_task(connectToArduinoCloud())
    asyncio.create_task(updateDisplay())

    while True:
        await asyncio.sleep(0)
