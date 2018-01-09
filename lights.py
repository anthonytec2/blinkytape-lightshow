"""
Code by Anthony Bisulco to control Blinky Tape lights
"""
import platform
import sys
import logging
import re
import math
from time import sleep
from subprocess import Popen, PIPE
from BlinkyTape import BlinkyTape
from color_constants import RGB
from collections import namedtuple, OrderedDict


def find_usb_dev():
    """[Function to find all USB devices on system ]

    Returns:
        [string] -- [returns list of USB devices]
    """
    if platform.system() == 'Windows':
        logging.info('Platform: Windows')
        return 'Work in Progress'
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
        return std_out
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


def color_fade(bt, col1, col2, duration=100):
    set_static_color(bt, col1)
    delta = [col2.red - col1.red, col2.green -
             col1.green, col2.blue - col1.blue]

    RGB = namedtuple('RGB', 'red, green, blue')
    red = col1.red
    green = col1.green
    blue = col1.blue
    wait_time = 100 / max(delta)
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


def gpu_color(bt):
    """[function to light strip based on gpu temperature]

    Arguments:
        bt {[BlinkyTape]} -- [light controller object]
    """
    if platform.system() == "Linux":
        process = Popen("nvidia-smi",
                        shell=True, stdout=PIPE, stderr=PIPE)
    elif platform.system() == "Windows":
        logging.debug("Working on Windows Support")
    std_out, std_err = process.communicate()
    gpu_temp = int(re.search("\d\dC",
                             std_out.decode("utf8")).group().split("C")[0])
    RGB = namedtuple('RGB', 'red, green, blue')
    set_static_color(bt, RGB(int(math.floor(1.04 * gpu_temp)),
                             int(math.floor(100 - 1.04 * gpu_temp)), 0))


def main():
    """[Main function to run custom light program]
    """
    logging.basicConfig(filename='lights.log',
                        format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.debug('Begining to Run Program')
    usb_devices = find_usb_dev()
    bt = BlinkyTape('/dev/' + usb_devices.split('\n')[0])
    color_fade(bt, RGB.BLUE, RGB.LIGHTGOLDENRODYELLOW, 5)


if __name__ == '__main__':
    main()
