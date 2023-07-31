"""
Communcation with Arduino board using USB.

@author: Marc Hensel
@contact: http://www.haw-hamburg.de/marc-hensel

@copyright: 2023, Marc Hensel
@version: 2023.07.28
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""

import sys
import serial, time

class ArduinoCOM():

    # ----------------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------------

    def __init__(self, serialCOM = None, baudRate = 9600, readTimeoutSec = 60.0, terminateOnFailure=True):
        """
        Constructor.

        Parameters
        ----------
        serialCOM : int, optional
            Serial port Arduino is connected to (e.g., '3' for 'COM3').
            Tries to connect to ports 0 to 15, if argument is None. (Default: None)
        baudRate : int, optional
            Connection's baud rate. Must match rate set in Arduino. (Default: 9600)
        readTimeoutSec : float, optional
            Maximum time in [s] to wait when reading data from Arduino. (Default: 60.0)
        terminateOnFailure : bool, optional
            Shall script terminate when no connection is possible? (Default: True)

        Returns
        -------
        None.

        """
        self._serial = None
        
        # Try to connect to specific COM port
        if serialCOM != None:
            if self._connect(serialCOM, baudRate, readTimeoutSec):
                print('Connected to serial port COM{}'.format(serialCOM))
                return
            else:
                print('WARNING: Cannot connect to serial port COM{}. Trying other ports.'.format(serialCOM))
                
        # Try to connect to COM ports in [0, 15]
        for portID in range(16):
            if self._connect(portID, baudRate, readTimeoutSec):
                print('Connected to serial port COM{}'.format(portID))
                return
            
        # Could not connect
        print('WARNING: Cannot connect to serial ports COM0 to COM15')
        if terminateOnFailure:
            sys.exit()
                     
    # ----------------------------------------------------------------------
    # Serial connection
    # ----------------------------------------------------------------------

    def _connect(self, serialCOM, baudRate, readTimeoutSec):
        """
        Connect to serial port.

        Parameters
        ----------
        serialCOM : int
            Port number to connect to (e.g., '3' for 'COM3').
        baudRate : int
            Connection's baud rate. Must match rate set in Arduino.
        readTimeoutSec : float
            Maximum time in [s] to wait when reading data from Arduino.

        Returns
        -------
        bool
            True if connection established, else False.

        """
        try:
            self._serial = serial.Serial('COM{}'.format(serialCOM), baudrate=baudRate, timeout=readTimeoutSec)
            time.sleep(1.0)                     # Wait for connection established
            self._serial.reset_input_buffer()   # Clear date received during connection
        except:
            self._serial = None
        return (self._serial != None)

    # ----------------------------------------------------------------------
    
    def isConnected(self):
        return (self._serial != None)

    # ----------------------------------------------------------------------

    def close(self):
        if self._serial != None:
            print('Disconnecting from serial port')
            self._serial.close()
            self._serial = None
        else:
            print('WARNING: No serial port to disconnect from')

    # ----------------------------------------------------------------------
    # Read/write data
    # ----------------------------------------------------------------------
    
    def readLine(self):
        """
        Read line (i.e., until new line symbol included) from serial port.

        Returns
        -------
        string
            Data read from port (8-bit Unicode, without new line symbol) or None.

        """
        if self._serial != None:
            data = self._serial.readline()
            if data:
                return str(data, 'utf-8').rstrip('\n')
        return None

    def writeString(self, data):
        """
        Send string data to a connected Arduino.

        Parameters
        ----------
        data : string
            Data to send (gets encoded as 8-bit Unicode).

        Returns
        -------
        bool
            True if connection exists, else False.

        """
        if self._serial != None:
            print("Send: " + data)
            self._serial.write(data.encode('utf-8'))
            self._serial.flush()
            return True
        else:
            return False
    
# ========== Main (sample movements of Pocket cube solver) ==========

if __name__ == '__main__':
    arduino = ArduinoCOM()
    reply = arduino.readLine()              # Wait for setup() to complete
    print('Device ready: ' + reply)
    
    arduino.writeString('RRLT')
    arduino.writeString('I')
    arduino.close()
