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


def set_static_color(col, bt):
    """[sets a static color on the led strip]

    Arguments:
        col {[type]} -- [color from RGB class]
        bt {[BlinkyTape]} -- [light controller object]
    """
    bt.displayColor(col.red, col.green, col.blue)
    logging.debug("Set Color to (%s,%s,%s)" % (col.red, col.green, col.blue))


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
    set_static_color(RGB(math.floor(1.04 * gpu_temp),
                         math.floor(100 - 1.04 * gpu_temp), 0), bt)


def main():
    """[Main function to run custom light program]
    """
    logging.basicConfig(filename='lights.log',
                        format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.debug('Begining to Run Program')
    usb_devices = find_usb_dev()
    bt = BlinkyTape('/dev/' + usb_devices.split('\n')[0])


if __name__ == '__main__':
    main()
