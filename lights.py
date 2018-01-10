"""
Code by Anthony Bisulco to control Blinky Tape lights
"""
import platform
import sys
import logging
import re
import math
import time
import numpy as np
from time import sleep
from subprocess import Popen, PIPE
from BlinkyTape import BlinkyTape
from color_constants import RGB
from collections import namedtuple, OrderedDict
import colorsys


def find_usb_dev():
    """[Function to return usb device on system ]

    Returns:
        [string] -- [returns list of USB devices]
    """
    if platform.system() == 'Windows':
        logging.info('Platform: Windows')
        process = Popen("mode",
                        shell=True, stdout=PIPE, stderr=PIPE)
        std_out, std_err = process.communicate()
        usb_dev = re.search("COM\d",
                            std_out.decode("utf8")).group()
        logging.debug(std_err)
        if not std_out:
            logging.debug("No USB Devices")
            sys.exit(-1)
        logging.debug(usb_dev)
        return usb_dev
    elif platform.system() == 'Linux':
        logging.info('Platform: Linux')
        process = Popen("ls /dev/ | grep -E '(ttyACM*|ttyUSB*)'",
                        shell=True, stdout=PIPE, stderr=PIPE)
        std_out, std_err = process.communicate()
        std_out = std_out.decode("utf8")
        logging.debug(std_err)
        if not std_out:
            logging.debug("No USB Devices")
            sys.exit(-1)
        logging.debug(std_out)

        return '/dev/' + std_out.split('\n')[0]
    else:
        logging.debug('Platform: Unknown exiting')
        sys.exit(-1)
        return -1


def set_static_color(bt, col):
    """[sets a static color on the led strip]

    Arguments:
        col {[type]} -- [color from RGB class]
        bt {[BlinkyTape]} -- [light controller object]
    """
    ret = bt.displayColor(col.red, col.green, col.blue)
    if ret == 1:
        logging.debug("Set Color to (%s,%s,%s)" %
                      (col.red, col.green, col.blue))
    else:
        logging.debug("Shutting off lights, off hours")


def two_color_swap(bt, col1, col2, freq=10, duration=10):
    for a in range(0, freq * duration):
        for i in range(0, bt.get_led_count()):
            if i % 2 == 0:
                bt.sendPixel(col1.red, col1.green, col1.blue)
            else:
                bt.sendPixel(col2.red, col2.green, col2.blue)
        bt.show()
        time.sleep(1 / freq)
        for i in range(0, bt.get_led_count()):
            if i % 2 == 1:
                bt.sendPixel(col1.red, col1.green, col1.blue)
            else:
                bt.sendPixel(col2.red, col2.green, col2.blue)
        bt.show()
        time.sleep(1 / freq)


def color_fade(bt, col1, col2, duration=100):
    set_static_color(bt, col1)
    delta = [col2.red - col1.red, col2.green -
             col1.green, col2.blue - col1.blue]

    RGB = namedtuple('RGB', 'red, green, blue')
    red = col1.red
    green = col1.green
    blue = col1.blue
    wait_time = duration / max(delta)
    for i in range(0, max(delta)):
        if delta[0] > 0:
            red += 1
            delta[0] += 1
        elif delta[0] < 0:
            red -= 1
            delta[0] -= 1
        if delta[1] > 0:
            green += 1
            delta[1] += 1
        elif delta[1] < 0:
            green -= 1
            delta[1] -= 1
        if delta[2] > 0:
            blue += 1
            delta[2] += 1
        elif delta[2] < 0:
            blue -= 1
            delta[2] -= 1
        set_static_color(bt, RGB(red, green, blue))
        sleep(wait_time)


def color_phase(bt, freq=10, duration=10):
    colors = np.linspace(0, 360, bt.get_led_count())
    for a in range(0, duration * freq):
        for i in range(0, bt.get_led_count()):
            color_vals = colorsys.hsv_to_rgb(colors[i] / 360, 0.9, 0.9)
            bt.sendPixel(
                int(255 * color_vals[0]), int(255 * color_vals[1]), int(255 * color_vals[2]))
        bt.show()
        colors = colors + 5
        colors[colors > 360] = colors[colors > 360] - 360
        time.sleep(1 / freq)


def gpu_color(bt):
    """[function to light strip based on gpu temperature]

    Arguments:
        bt {[BlinkyTape]} -- [light controller object]
    """
    if platform.system() == "Linux":
        process = Popen("nvidia-smi",
                        shell=True, stdout=PIPE, stderr=PIPE)
    elif platform.system() == "Windows":
        process = Popen("C:\\Program Files\\NVIDIA Corporation\\NVSMI\\nvidia-smi.exe",
                        shell=True, stdout=PIPE, stderr=PIPE)
    else:
        return
        logging.debug("Unknown OS")
    std_out, std_err = process.communicate()
    gpu_temp = int(re.search("\d\dC",
                             std_out.decode("utf8")).group().split("C")[0])
    logging.info('GPU TEMP: ' + str(gpu_temp) + "C")
    RGB = namedtuple('RGB', 'red, green, blue')
    set_static_color(bt, RGB(int(math.floor(1.04 * gpu_temp)),
                             int(math.floor(100 - 1.04 * gpu_temp)), 0))


def game_running():
    if platform.system() == 'Windows':
        process = Popen("tasklist",
                        shell=True, stdout=PIPE, stderr=PIPE)
        std_out, std_err = process.communicate()
        games = ['TslGame.exe', 'starwarsbattlefrontii.exe',
                 'FortniteClient-Win64-Ship', 'RocketLeague.exe', 'Shogun2.exe']
        std_out = std_out.decode('utf8')
        if any(game in std_out for game in games):
            return True
    elif platform.system() == 'Linux':
        return False
    else:
        return False

def travel_up(bt, col1,col2, block_size=0, exp=False, time_delay=0.1):
    set_static_color(bt, col1)
    for i in range(0,bt.get_led_count()):
        for j in range(0, bt.get_led_count()):
            if i <= j <= i+block_size:
                bt.sendPixel(col2.red,col2.green,col2.blue)
            else:
                bt.sendPixel(col1.red,col1.green,col1.blue)
        bt.show()
        if exp:
            time_delay=time_delay/1.1
            time.sleep(time_delay)
        else:
            time.sleep(time_delay)


def main():
    """[Main function to run custom light program]
    """
    logging.basicConfig(filename='lights.log',
                        format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.debug('Begining to Run Program')
    usb_devices = find_usb_dev()
    bt = BlinkyTape(usb_devices)
    travel_up(bt, RGB.AQUA, RGB.PINK, block_size=3, exp=True, time_delay=3)


if __name__ == '__main__':
    main()
