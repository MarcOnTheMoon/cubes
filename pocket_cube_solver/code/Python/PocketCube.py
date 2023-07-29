"""
Control mechanical movements of 2x2x2 Pocket Cube by Arduino board using USB.

@author: Marc Hensel
@contact: http://www.haw-hamburg.de/marc-hensel

@copyright: 2023, Marc Hensel
@version: 2023.07.29
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""

import time
from ArduinoCOM import ArduinoCOM

class PocketCube():
    
    # ----------------------------------------------------------------------
    # Class constants
    # ----------------------------------------------------------------------

    # Map orientation identifiers to faces in standard orientation
    _orientation2Face = {
        '+x': 'F',
        '-x': 'B',
        '+y': 'R',
        '-y': 'L',
        '+z': 'U',
        '-z': 'D'
    }

    # For a given face, get the face on the opposite side of the cube
    _oppositeFace = {
        'U': 'D',
        'D': 'U',
        'F': 'B',
        'B': 'F',
        'L': 'R',
        'R': 'L',
    }

    # Change of orientation in 'SpiCor' mode
    # Usage: newOrientation = PocketCube._nextOrientation[currentOrientation][cubeRotation]
    _nextOrientation = {
        '+x': {
            'U': '+y', 'u': '-y', 'U2': '-x',
            'D': '+x', 'd': '+x', 'D2': '+x',
            'F': '-z', 'f': '-z', 'F2': '-z',
            'B': '-z', 'b': '-z', 'B2': '-z',
            'L': '+x', 'l': '+x', 'L2': '+x',
            'R': '+x', 'r': '+x', 'R2': '+x',
            'tl': '+x', 'tr': '+x'
        },
        '-x': {
            'U': '-y', 'u': '+y', 'U2': '+x',
            'D': '-x', 'd': '-x', 'D2': '-x',
            'F': '+z', 'f': '+z', 'F2': '+z',
            'B': '+z', 'b': '+z', 'B2': '+z',
            'L': '-x', 'l': '-x', 'L2': '-x',
            'R': '-x', 'r': '-x', 'R2': '-x',
            'tl': '-x', 'tr': '-x'
        },
        '+y': {
            'U': '-x', 'u': '+x', 'U2': '-y',
            'D': '+y', 'd': '+y', 'D2': '+y',
            'F': '+y', 'f': '+y', 'F2': '+y',
            'B': '+y', 'b': '+y', 'B2': '+y',
            'L': '+z', 'l': '+z', 'L2': '+z',
            'R': '-z', 'r': '-z', 'R2': '-z',
            'tl': '+z', 'tr': '-z'
        },
        '-y': {
            'U': '+x', 'u': '-x', 'U2': '+y',
            'D': '-y', 'd': '-y', 'D2': '-y',
            'F': '-y', 'f': '-y', 'F2': '-y',
            'B': '-y', 'b': '-y', 'B2': '-y',
            'L': '-z', 'l': '-z', 'L2': '-z',
            'R': '+z', 'r': '+z', 'R2': '+z',
            'tl': '-z', 'tr': '+z'
        },
        '+z': {
            'U': '+z', 'u': '+z', 'U2': '+z',
            'D': '+z', 'd': '+z', 'D2': '+z',
            'F': '+x', 'f': '+x', 'F2': '+x',
            'B': '+y', 'b': '-y', 'B2': '-x',
            'L': '-y', 'l': '-y', 'L2': '-y',
            'R': '+y', 'r': '+y', 'R2': '+y',
            'tl': '-y', 'tr': '+y'
        },
        '-z': {
            'U': '-z', 'u': '-z', 'U2': '-z',
            'D': '-z', 'd': '-z', 'D2': '-z',
            'F': '-x', 'f': '-x', 'F2': '-x',
            'B': '-y', 'b': '+y', 'B2': '+x',
            'L': '+y', 'l': '+y', 'L2': '+y',
            'R': '-y', 'r': '-y', 'R2': '-y',
            'tl': '+y', 'tr': '-y'
        }
    }

    # Face rotation to servo commands:
    # Usage: servoCommands = PocketCube._rotation2servoCmd[cubeRotation][mode]
    _rotation2servoCmd = {
        # Up
        'U'  : { 'ReCor': 'TTRTT', 'SpiCor': 'R'},          # 90° left
        'u'  : { 'ReCor': 'TTLTT', 'SpiCor': 'L'},          # 90° right
        'U2' : { 'ReCor': 'TTRRTT', 'SpiCor': 'RR'},        # 180°
        # Down
        'D'  : { 'ReCor': 'R',      'SpiCor': 'R'},         # 90° right
        'd'  : { 'ReCor': 'L',      'SpiCor': 'L'},         # 90° left
        'D2' : { 'ReCor': 'RR',     'SpiCor': 'RR'},        # 180°
        # Front
        'F'  : { 'ReCor': 'TRTTT',  'SpiCor': 'TR'},        # 90° right
        'f'  : { 'ReCor': 'TLTTT',  'SpiCor': 'TL'},        # 90° left
        'F2' : { 'ReCor': 'TRRTTT', 'SpiCor': 'TRR'},       # 180°
        # Back
        'B'  : { 'ReCor': 'TTTRT',  'SpiCor': 'TTTR'},      # 90° left
        'b'  : { 'ReCor': 'TTTLT',  'SpiCor': 'TTTL'},      # 90° right
        'B2' : { 'ReCor': 'TTTRRT', 'SpiCor': 'TTTRR'},     # 180°
        # Left
        'L'  : { 'ReCor': '(TLTTRT) R (TRTTLT)',  'SpiCor': '(TLTTRT) R'},  # 90° to front (tl R tr)
        'l'  : { 'ReCor': '(TLTTRT) L (TRTTLT)',  'SpiCor': '(TLTTRT) L'},  # 90° to back (tl L tr)
        'L2' : { 'ReCor': '(TLTTRT) RR (TRTTLT)', 'SpiCor': '(TLTTRT) RR'}, # 180° (tl RR tr)
        # Right
        'R'  : { 'ReCor': '(TRTTLT) R (TLTTRT)',  'SpiCor': '(TRTTLT) R'},  # 90° to back (tr R tl)
        'r'  : { 'ReCor': '(TRTTLT) L (TLTTRT)',  'SpiCor': '(TRTTLT) L'},  # 90° to front (tr L tl)
        'R2' : { 'ReCor': '(TRTTLT) RR (TLTTRT)', 'SpiCor': '(TRTTLT) RR'}, # 180° (tr RR tl)
        # Tilt to left and right
        'tl' : { 'ReCor': 'TLTTRT', 'SpiCor': 'TLTTRT'},    # 90° left
        'tr' : { 'ReCor': 'TRTTLT', 'SpiCor': 'TRTTLT'},    # 90° right
        # Scan cube for colors
        'Scan colors' : { 'ReCor': 'RRRRTT RRRRTT', 'SpiCor': 'RRRRTT RRRRTT'}
    }
    
    # ----------------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------------

    def __init__(self, mode = 'SpiCor', serialCOM = None):
        """
        Constructor, tries to connects to Arduino using serial COM ports.
        
        On connection, the Arduino runs setup() and sends "ok" when ready.
        Hence, this method waits for the Arduino's reply using the read
        timeout set in the constructor of class ArduinoCOM.
        
        Parameters
        ----------
        mode : string, optional
            'ReCor' brings cube back into standard orientation after each move,
            'SpiCor' doesn't, why it needs less servo movements. (Default: 'SpiCor')
        serialCOM : int, optional
            Serial port Arduino is connected to (e.g., '3' for 'COM3').
            Tries to connect to ports 0 to 15, if argument is None. (Default: None)

        Returns
        -------
        None.

        """
        # Connect to Arduino (will reset Arduino => Runs setup())
        self._arduino = ArduinoCOM(serialCOM=serialCOM)
        reply = self._arduino.readLine()
        print('Device ready: ' + reply)
        
        # Mode and cube orientation
        self._mode = mode
        if mode == 'SpiCor':
            self._orientationFront = '+x'
            self._orientationRight = '+y'
            self._orientationUp = '+z'

    # ----------------------------------------------------------------------
    # Serial connection
    # ----------------------------------------------------------------------

    def close(self, waitTimeSec=5.0):
        """
        Requests Arduino to set servo angles in starting position and closes
        serial connection.

        Parameters
        ----------
        waitTimeSec : float
            Delay before moving servo motor back in default position [s] (Default: 5.0)

        Returns
        -------
        None.

        """
        time.sleep(waitTimeSec)
        cube._arduino.writeString('I')
        time.sleep(1.0)             # Wait for Arduino to read buffer
        self._arduino.close()

    # ----------------------------------------------------------------------
    # Cube logic
    # ----------------------------------------------------------------------

    def rotateCube(self, rotation):
        """
        Performs Pocket cube rotation.
        
        Valid rotations are defined in PocketCube._rotation2servoCmd and
        include, amongst others, 90 degree turns of the cube faces 'up' (U, u),
        'down' (D, d), 'front' (F, f), 'back' (B, b), 'left'(L, l), and
        'right' (R, r).

        Parameters
        ----------
        rotation : string
            A single rotation string as defined in PocketCube._rotation2servoCmd

        Returns
        -------
        None.

        """
        # Determine relative rotation (i.e., rotation in standard orientation)
        if self._mode == 'SpiCor':
            logicalRotation = rotation
            rotation = self._relativeRotation(rotation)
            print('Relative rotation {} -> {}'.format(logicalRotation, rotation))
            
        # Move servos
        commands = PocketCube._rotation2servoCmd[rotation][self._mode]
        print('Rotation commands {} -> {}'.format(rotation, commands))
        self._arduino.writeString(commands + '>')
        reply = self._arduino.readLine()
        print('Reply: ' + str(reply))

        # SpiCor: update location of cube's logical faces
        if self._mode == 'SpiCor':
            self._orientationFront = PocketCube._nextOrientation[self._orientationFront][rotation]
            self._orientationUp = PocketCube._nextOrientation[self._orientationUp][rotation]
            self._orientationRight = PocketCube._nextOrientation[self._orientationRight][rotation]
            
    def _relativeRotation(self, rotation):
        """
        Determine rotation to perform for cube not in standard orientation.

        Parameters
        ----------
        rotation : string
            Logical rotation to perform (i.e., if the cube were in standard
            orientation.

        Returns
        -------
        string
            Rotation corresponding to logical rotation when applied to cube
            in its current orientation.

        """
        # Determine face to rotate
        if rotation in ['U', 'u', 'U2']:
            face = PocketCube._orientation2Face[self._orientationUp]
        elif rotation in ['D', 'd', 'D2']:
            face = PocketCube._orientation2Face[self._orientationUp]
            face = PocketCube._oppositeFace[face]
        elif rotation in ['F', 'f', 'F2']:
            face = PocketCube._orientation2Face[self._orientationFront]
        elif rotation in ['B', 'b', 'B2']:
            face = PocketCube._orientation2Face[self._orientationFront]
            face = PocketCube._oppositeFace[face]
        elif rotation in ['R', 'r', 'R2']:
            face = PocketCube._orientation2Face[self._orientationRight]
        elif rotation in ['L', 'l', 'L2']:
            face = PocketCube._orientation2Face[self._orientationRight]
            face = PocketCube._oppositeFace[face]
                  
        # Return 90 degree rotation (X, x)
        if len(rotation) == 1:
            return face if rotation.isupper() else face.lower()
        # Return 180 degree rotation (X2)
        elif len(rotation) == 2:
            return face + '2'
            
# ========== Main (sample movements of Pocket cube solver) ==========

if __name__ == '__main__':
    cube = PocketCube(mode='SpiCor', serialCOM=None)
    cube.rotateCube('F')
    cube.rotateCube('f')
    cube.close()

