import platform
import sys
import logging
from subprocess import Popen, PIPE
from BlinkyTape import BlinkyTape


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


def main():
    """[Main function to run custom light program]
    """
    logging.basicConfig(filename='lights.log',
                        format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.debug('Begining to Run Program')
    usb_devices = find_usb_dev()


if __name__ == '__main__':
    main()
