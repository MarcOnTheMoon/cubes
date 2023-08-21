"""
States of Pocket cubes for OpenAI gym.

@authors: Finn Lanz (initial), Marc Hensel (refactoring, maintenance)
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.08.21
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""

import numpy as np
from PCubeAction import Action

class State:
    """
    Representation of a cubes states and related operations.
    
    Each state contains of two lists with 8 items, representing the 8 corner stones.
    List self.positions stores the location of each stone.
    List self.orientation stores the angle of each stone at its location.
    
    A solved cube in 'standard orientation' has positions (0, 1, 2, 3, 4, 5, 6, 7)
    and orientations (0, 0, 0, 0, 0, 0, 0, 0). 'Standard orientation' corresponds
    to face 'up' being white and face 'front' being red.
    """

    # ========== Constructor ==================================================

    def __init__(self, positions=tuple(range(8)), orientations=tuple([0]*8)):
        """
        Constructor.

        Parameters
        ----------
        positions : tupel(int), optional
            Positions of the 8 corner stones.
            Default: (0, 1, 2, 3, 4, 5, 6, 7) representing solved cube.
        orientations : tupel(int), optional
            Orientations of the 8 corner stones.
            Default: (0, 0, 0, 0, 0, 0, 0, 0) representing solved cube.

        Returns
        -------
        None.
        
        """
        self.positions = positions
        self.orientations = orientations

    # ========== Getter =======================================================

    # Solved states (key: orientation, value: valid positions for the orientation)
    __solved_states = {
        (0, 0, 0, 0, 0, 0, 0, 0): (
            (0, 1, 2, 3, 4, 5, 6, 7),       # White 0
            (1, 2, 3, 0, 5, 6, 7, 4),       # White 270
            (2, 3, 0, 1, 6, 7, 4, 5),       # White 180
            (3, 0, 1, 2, 7, 4, 5, 6),       # White 90
            (4, 7, 6, 5, 0, 3, 2, 1),       # Yellow 90
            (5, 4, 7, 6, 1, 0, 3, 2),       # Yellow 180
            (6, 5, 4, 7, 2, 1, 0, 3),       # Yellow 270
            (7, 6, 5, 4, 3, 2, 1, 0)),      # Yellow 0
        (1, 2, 1, 2, 2, 1, 2, 1): (
            (0, 3, 7, 4, 1, 2, 6, 5),       # Green 270
            (1, 0, 4, 5, 2, 3, 7, 6),       # Red 180
            (2, 1, 5, 6, 3, 0, 4, 7),       # Blue 90
            (3, 2, 6, 7, 0, 1, 5, 4),       # Orange 0
            (4, 5, 1, 0, 7, 6, 2, 3),       # Red 0
            (5, 6, 2, 1, 4, 7, 3, 0),       # Blue 270
            (6, 7, 3, 2, 5, 4, 0, 1),       # Orange 180
            (7, 4, 0, 3, 6, 5, 1, 2)),      # Green 90
        (2, 1, 2, 1, 1, 2, 1, 2): (
            (0, 4, 5, 1, 3, 7, 6, 2),       # Red 90
            (1, 5, 6, 2, 0, 4, 7, 3),       # Blue 0
            (2, 6, 7, 3, 1, 5, 4, 0),       # Orange 270
            (3, 7, 4, 0, 2, 6, 5, 1),       # Green 180
            (4, 0, 3, 7, 5, 1, 2, 6),       # Green 0
            (5, 1, 0, 4, 6, 2, 3, 7),       # Red 270
            (6, 2, 1, 5, 7, 3, 0, 4),       # Blue 180
            (7, 3, 2, 6, 4, 0, 1, 5))       # Orange 90
        }
    __solved_state_keys = __solved_states.keys()

    def is_cube_solved(self):
        """
        Check whether the state represents a solved cube (i.e., faces not scrambled).

        Returns
        -------
        bool
            True if state represents solved cube, else False.
            
        """
        is_orientation = self.orientations in State.__solved_state_keys
        return is_orientation and (self.positions in State.__solved_states[self.orientations])
    
    # ========== Apply action =================================================

    __next_state_index_map = {
        Action.R: ((1, 2), (2, 6), (6, 5), (5, 1)),
        Action.r: ((2, 1), (6, 2), (5, 6), (1, 5)),
        Action.L: ((3, 0), (7, 3), (0, 4), (4, 7)),
        Action.l: ((0, 3), (3, 7), (4, 0), (7, 4)),
        Action.U: ((0, 3), (1, 0), (2, 1), (3, 2)),
        Action.u: ((3, 0), (0, 1), (1, 2), (2, 3)),
        Action.D: ((4, 5), (5, 6), (6, 7), (7, 4)),
        Action.d: ((5, 4), (6, 5), (7, 6), (4, 7)),
        Action.F: ((0, 1), (1, 5), (5, 4), (4, 0)),
        Action.f: ((1, 0), (5, 1), (4, 5), (0, 4)),
        Action.B: ((2, 3), (3, 7), (7, 6), (6, 2)),
        Action.b: ((3, 2), (7, 3), (6, 7), (2, 6))
    }

    def next_state(self, action):
        """
        Get state when a specific action is taken (i.e., a face rotated).
    
        Parameters
        ----------
        action : Action
            Action to take
    
        Returns
        -------
        state  : State
            Resulting state when the action is applied to the current state.
            
        """
        assert isinstance(action, Action)
        
        # Move corners to their new positions within in tupels positions and orientations
        index_map = State.__next_state_index_map[action]
        new_positions, new_orientations = self._permuted_corners(index_map)
        
        # Adapt corner orientations (angles)
        new_orientations = State._rotate_corners(new_orientations, action)
    
        return State(positions=tuple(new_positions), orientations=tuple(new_orientations))
    
    # -------------------------------------------------------------------------

    def _permuted_corners(self, index_map):
        """
        Lists of positions and orientations after an action is applied.
    
        Parameters
        ----------
        index_map : list of int tuples
            Mappings (source, destination) of corner indices in positions and orientations
        
        Returns
        -------
        dst_positions : list(int)
            Positions with correct order after the action has been applied
        dst_orientations : list(int)
            Orientations with correct order (possibly wrong angle) after the action has been applied
            
        """
        dst_positions = list(self.positions)
        dst_orientations = list(self.orientations)
        
        for (src, dst) in index_map:
            dst_positions[dst] = self.positions[src]
            dst_orientations[dst] = self.orientations[src]
                    
        return dst_positions, dst_orientations

    # -------------------------------------------------------------------------

    def _rotate_corners(orientations, action):
        """
        Rotate corners to correct angle 0, 120, or 240 degrees when an action is applied.
        
        Parameters
        ----------
        orientations : list of int
            Orientations already shifted to the correct ordern when the action is applied
        action : Action
            Action to take
        
        Returns
        -------
        list(int) :
            Orientations with correct angle after the action has been applied
            
        """
        if action in [Action.R, Action.r]:
            corners = ((1, 2), (2, 1), (5, 1), (6, 2))
        elif action in [Action.L, Action.l]:
            corners = ((0, 1), (3, 2), (4, 2), (7, 1))
        elif action in [Action.U, Action.u, Action.D, Action.d]:
            corners = ()
        elif action in [Action.F, Action.f]:
            corners = ((0, 2), (1, 1), (4, 1), (5, 2))
        elif action in [Action.B, Action.b]:
            corners = ((2, 2), (3, 1), (6, 1), (7, 2))
        
        new_orientations = list(orientations)
        for index, delta_angle in corners:
            new_orientations[index] = (new_orientations[index] + delta_angle) % 3
        return new_orientations

    # ========== Plane representation =========================================
        
    # Map 3-sided cubelets to their projection on the cube's faces.
    # Faces are indexed in the order the presentation returned by get_plane_representation().
    __corner_maps = (
        # Top layer
        ((0, 2), (3, 0), (1, 1)),
        ((0, 3), (4, 0), (3, 1)),
        ((0, 1), (2, 0), (4, 1)),
        ((0, 0), (1, 0), (2, 1)),
        # Bottom layer
        ((5, 0), (1, 3), (3, 2)),
        ((5, 1), (3, 3), (4, 2)),
        ((5, 3), (4, 3), (2, 2)),
        ((5, 2), (2, 3), (1, 2))
    )

    # Cubie colors of solved state
    __corner_colors = (
        ('W', 'R', 'G'),    # Cubie 0
        ('W', 'B', 'R'),    # Cubie 1
        ('W', 'O', 'B'),    # Cubie 2
        ('W', 'G', 'O'),    # Cubie 3
        ('Y', 'G', 'R'),    # Cubie 4
        ('Y', 'R', 'B'),    # Cubie 5
        ('Y', 'B', 'O'),    # Cubie 6
        ('Y', 'O', 'G')     # Cubie 7
    )

    def get_plane_representation(self):
        """
        Get a plane representation of the state.
        
        The plane representation is defined as follows:
            
                  +-----+
                  | U U |
                  | U U |
            +-----+-----+-----+-----+
            | L L | F F | R R | B B |
            | L L | F F | R R | B B |
            +-----+-----+-----+-----+
                  | D D |
                  | D D |
                  +-----+
        
        Data structure stores the cube's faces in following order:
            
            [[U, U, U, U        White for solved cube
             [L, L, L, L],      Green
             [B, B, B, B],      Orange
             [F, F, F, F],      Red
             [R, R, R, R],      Blue
             [D, D, D, D]]      Yellow
            
        Returns
        -------
        list(list(char)) :
            Plane representation with colors denoted by chard, e.g. solved cube:
            [['W', 'W', 'W', 'W'], ['G', 'G', 'G', 'G'], ['O', 'O', 'O', 'O'],
             ['R', 'R', 'R', 'R'], ['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y', 'Y']]
            
        """
        plane_faces = [
            [None, None, None, None],       # Up
            [None, None, None, None],       # Left
            [None, None, None, None],       # Back
            [None, None, None, None],       # Front
            [None, None, None, None],       # Right
            [None, None, None, None]]       # Down
    
        for corner, orientation, mapping in zip(self.positions, self.orientations, State.__corner_maps):
            colors = State.__corner_colors[corner]
            colors = State._map_colors_orientation(colors, orientation)
            
            for (face_index, location_index), color in zip(mapping, colors):
                plane_faces[face_index][location_index] = color
    
        return plane_faces

    # -------------------------------------------------------------------------
    
    def _map_colors_orientation(colors, orientation):
        """
        Reorder colors in a 3-tuple with a cubie's colors depending on its orientation.
        
        The method is used to generate plane representations by get_plane_representation().
        
        Parameters
        ----------
        colors : tuple
            The three colors of a cubie represented by chars.
        orientation : int
            Orientation of the cubie (0: 0 degrees, 1: 120 degrees, 2: 240 and -120 degrees).
            
        Returns
        -------
        tuple :
            Color tuple of the cubie with reordered colors.
            
        """
        if orientation == 0:
            return colors
        elif orientation == 1:
            return colors[2], colors[0], colors[1]
        else:
            return colors[1], colors[2], colors[0]

    # ========== One-hot encoding =============================================

    def one_hot_encoding(self, dst=None):
        """
        Encode as one-hot encoding of the cube's state as 8x24 tensor.
        
        The encoding is used for the training of neural networks.
        Each of the 8 corner stones of the cube is encoded as 24 numbers,
        where only one has the value 1 and all others 0. The index [0..23] of
        the value 1 is determined by:
            
            3 * <index within self.positions> + <value in self.orientation>
        
        Parameters
        ----------
        dst : numpy.ndarray of shape (8,24) or None
            Numpy array to store encoding in or None to create an array.
            (Default: None)
            
        Returns
        -------
        numpy.ndarray
            Encoded state
            
        """
        assert (dst is None) or (isinstance(dst, np.ndarray) and (dst.shape == (8, 24)))

        # Create data structure
        if dst is None:
            dst = np.zeros((8,24))
            
        # Create one-hot encoded vector for each corner stone
        for corner_index in range(8):
            permutated_index = self.positions.index(corner_index)
            ortientation = self.orientations[permutated_index]
            dst[corner_index, permutated_index * 3 + ortientation] = 1
    
        return dst

    # -------------------------------------------------------------------------

    # TODO Added: Check and refactor
    def one_hot_encode_states(states):
        """
        Encode multiple cube states as 8x24 one-hot tensors.
        
        Refer to one_hot_encoding() for further information on the encoding.
        
        Parameters
        ----------
        states: list(State)
            List of cube states from type State
           
        Returns
        -------
        numpy.ndarray
            Array of encoded states
        """
        encoded_shape = (8, 24)
    
        # states could be list of lists or just list of states
        if isinstance(states[0], list):
            encoded = np.zeros((len(states), len(states[0])) + encoded_shape, dtype=np.float32)
    
            for i, st_list in enumerate(states):
                for j, state in enumerate(st_list):
                    state.one_hot_encoding(dst = encoded[i, j])
        else:
            encoded = np.zeros((len(states), ) + encoded_shape, dtype=np.float32)
            for i, state in enumerate(states):
                state.one_hot_encoding(dst = encoded[i])
    
        return encoded
