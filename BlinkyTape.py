"""
The MIT License(MIT)

Copyright(c) 2013 Blinkinlabs, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
BlinkyTape Python communication library.

  This code assumes stock serialLoop() in the firmware.

  Commands are issued in 3-byte blocks, with pixel data
  encoded in RGB triplets in range 0-254, sent sequentially
  and a triplet ending with a 255 causes the accumulated pixel
  data to display (a show command).

  Note that with the stock firmware changing the maximum brightness
  over serial communication is impossible.
"""
import serial
import datetime
# For Python3 support- always run strings through a bytes converter
import sys
if sys.version_info < (3,):
    def encode(x):
        return x
else:
    import codecs

    def encode(x):
        return codecs.latin_1_encode(x)[0]


class BlinkyTape(object):
    def __init__(self, port, ledCount=60, buffered=True):
        """Creates a BlinkyTape object and opens the port.

        Parameters:
          port
            Required, port name as accepted by PySerial library:
            http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial
            It is the same port name that is used in Arduino IDE.
            Ex.: COM5 (Windows), /dev/ttyACM0 (Linux).
          ledCount
            Optional, total number of LEDs to work with,
            defaults to 60 LEDs. The limit is enforced and an
            attempt to send more pixel data will throw an exception.
          buffered
            Optional, enabled by default. If enabled, will buffer
            pixel data until a show command is issued. If disabled,
            the data will be sent in byte triplets as expected by firmware,
            with immediate flush of the serial buffers (slower).

        """
        self.port = port
        self.ledCount = ledCount
        self.position = 0
        self.buffered = buffered
        self.buf = ""
        self.serial = serial.Serial(port, 115200)
        self.show()  # Flush any incomplete data
        self.override = False
        self.timeoutval = datetime.datetime.now()
        self.displayColor(0, 0, 0)

    def get_led_count(self):
        return self.ledCount

    def set_override(self, val, timeout=30):
        self.override = val
        if val:
            self.timeoutval = datetime.datetime.now() + datetime.timedelta(minutes=timeout)

    def send_list(self, colors):
        if len(colors) > self.ledCount:
            raise RuntimeError("Attempting to set pixel outside range!")
        for r, g, b in colors:
            self.sendPixel(r, g, b)
        self.show()

    def send_list(self, colors):
        data = ""
        for r, g, b in colors:
            data += chr(r) + chr(g) + chr(b)

        data = data.replace(chr(255), chr(254))

        self.serial.write(encode(data))
        self.show()

    def sendData(self, data):
        data = data.replace(chr(255), chr(254))
        self.serial.write(encode(data))
        self.show()

    def sendPixel(self, r, g, b):
        if r > 255:
            r = 255
        if g > 255:
            g = 255
        if b > 255:
            b = 255

        """Sends the next pixel data triplet in RGB format.

        Values are clamped to 0-254 automatically.

        Added in timer for shutting fof lights

        Throws a RuntimeException if [ledCount] pixels are already set.
        """
        if self.timeoutval < datetime.datetime.now():
            self.set_override(False)

        if not(datetime.datetime.now().hour < 23 and datetime.datetime.now().hour > 15 or self.override) and not r == 0 and not g == 0 and b == 0:
            return
        data = ""
        data = chr(r) + chr(g) + chr(b)
        data = data.replace(chr(255), chr(254))

        if self.position < self.ledCount:
            if self.buffered:
                self.buf += data
            else:
                self.serial.write(encode(data))
                self.serial.flush()
            self.position += 1
        else:
            raise RuntimeError("Attempting to set pixel outside range!")

    def show(self):
        """Sends the command(s) to display all accumulated pixel data.

        Resets the next pixel position to 0, flushes the serial buffer,
        and discards any accumulated responses from BlinkyTape.
        """
        control = chr(255)
        if self.buffered:
            # Fix an OS X specific bug where sending more than 383 bytes of data at once
            # hangs the BlinkyTape controller. Why this is???
            # TODO: Test me on other platforms
            CHUNK_SIZE = 300

            self.buf += control
            for i in range(0, len(self.buf), CHUNK_SIZE):
                self.serial.write(encode(self.buf[i:i + CHUNK_SIZE]))
                self.serial.flush()

            self.buf = ""
        else:
            self.serial.write(encode(control))
        self.serial.flush()
        self.serial.flushInput()  # Clear responses from BlinkyTape, if any
        self.position = 0

    def displayColor(self, r, g, b):
        """Fills [ledCount] pixels with RGB color and shows it."""
        if self.timeoutval < datetime.datetime.now():
            self.set_override(False)

        if datetime.datetime.now().hour < 23 and datetime.datetime.now().hour > 15 or self.override:
            for i in range(0, self.ledCount):
                self.sendPixel(r, g, b)
            self.show()
            return 1

        else:
            for i in range(0, self.ledCount):
                self.sendPixel(0, 0, 0)
            self.show()
            return -1

    def resetToBootloader(self):
        """Initiates a reset on BlinkyTape.

        Note that it will be disconnected.
        """
        self.serial.setBaudrate(1200)
        self.close()

    def close(self):
        """Safely closes the serial port."""
        self.serial.close()


# Example code

if __name__ == "__main__":

    import glob
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-p", "--port", dest="portname",
                      help="serial port (ex: /dev/ttyUSB0)", default=None)
    parser.add_option("-c", "--ledcount", dest="ledcount",
                      help="number of LEDs attached", type="int", default=60)
    parser.add_option("-b", action="store_true",
                      default="True", dest="buffered")
    parser.add_option("-u", action="store_false", dest="buffered")

    (options, args) = parser.parse_args()

    if options.portname is not None:
        port = options.portname
    else:
        serialPorts = glob.glob("/dev/cu.usbmodem*")
        port = serialPorts[0]

    bt = BlinkyTape(port, options.ledcount, options.buffered)

    while True:
        bt.displayColor(255, 0, 0)
        bt.displayColor(0, 255, 0)
        bt.displayColor(0, 0, 255)
        bt.displayColor(255, 255, 255)
        bt.displayColor(0, 0, 0)
