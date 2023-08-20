"""
OpenAI gym environment for Pocket cubes.

The environment follows the gym documentation (last visited: 03.08.2023):
https://www.gymlibrary.dev/content/environment_creation/

@authors: Finn Lanz (initial), Marc Hensel (refactoring, maintenance)
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.08.20
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""

import gym
from gym import spaces
import random

from PCubeAction import Action
from PCubeState import State
from PCubeRender2D import Render2D

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

class PocketCubeEnv(gym.Env):
    # Define render modes ('None' included by default) and speed
    metadata = {'render_modes': ['2D'], 'render_fps': 1.0}

    # ========== Constructor ==================================================

    def __init__(self, render_mode='2D', render_fps=None):
        """
        Constructor.

        Parameters
        ----------
        render_mode : string, optional
            '2D', '3D', or None. (Default: '2D')
        render_fps : float
            Speed of the rendering in frames per seconds. (Default: metadata['render_fps'])

        Returns
        -------
        None.
        
        """
        # Init action space (6 faces rotated clockwise or counter-clockwise)
        self.action_space = spaces.Discrete(12)
        
        # Observation space (will be initialized as solved cube: 8 corners with positions with orientation)
        self.observation_space = None
        
        # Init rendering
        assert render_mode is None or render_mode in self.metadata['render_modes']
        assert render_fps is None or isinstance(render_fps, float)

        self.render_mode = render_mode
        if render_fps is None:
            render_fps = self.metadata['render_fps']

        if render_mode == '2D':
            self.render_window = Render2D(self, render_fps)
        
        # Set initial state
        self.observation_space, _ = self.reset()

    # ========== Override gym.Env: Reset environment ==========================
    
    def _random_orientation(self):
        """
        Rotates cube as a whole randomly. This makes sure that the initial
        solved cube does not always have the color white at its face 'up'
        and red at its face 'front'.

        Returns
        -------
        None.
        
        """
        # Actions to bring a color to the face 'up'
        face_up = {
            'white': [],
            'blue': [Action.B, Action.f],
            'green': [Action.b, Action.F],
            'red': [Action.R, Action.l],
            'orange': [Action.r, Action.L],
            'yellow': [Action.R, Action.R, Action.l, Action.l] }

        # Actions to rotate the cube as a whole horizontally
        horizontal_rotations = {
            '0': [],
            '90': [Action.D, Action.u],
            '180': [Action.D, Action.D, Action.u, Action.u],
            '270': [Action.d, Action.U] }

        # Rotate the cube as a whole randomly
        up_actions = random.choice(list(face_up.values()))
        rotate_actions = random.choice(list(horizontal_rotations.values()))
        for action in (up_actions + rotate_actions):
            self.step(action)
    
        # Do not count moves
        self.last_action = None
        self.number_actions = 0
    
    # -------------------------------------------------------------------------

    def reset(self, is_random_orientation=True):
        """
        Sets the environment to its initial state.

        Parameters
        ----------
        is_random_orientation : bool
            Resets cube to standard orientation (white up, red front) if False,
            else with the cube randomly rotated.

        Returns
        -------
        state: State
            Initial state (observation space) of the cube
        info:
            Empty, but required by Gym API
            
        """
        self.last_action = None
        self.number_actions = 0
        self.number_scrambles = 0

        self.observation_space = State()
        if is_random_orientation:
            self._random_orientation()
        
        return self.observation_space, {}

    # ========== Override gym.Env: Do action (time step) ======================
        
    def step(self, action):
        """
        Do an action resulting in new state and reward.

        Parameters
        ----------
        action : Action
            Action to take.

        Returns
        -------
        next_state : State
            New state after the action was taken
        reward : int
            Reward of the action in the current state (1 if cube is solved, else -1)
        done : bool
            True if the cube is in the solved state, else False
        info:
            Empty, but required by Gym API
            
        """
        assert isinstance(action, Action)
        
        # Apply action to current state
        next_state = self.observation_space.next_state(action)
        self.observation_space = next_state

        # Check for end state and determine reward
        done = next_state.is_cube_solved()
        reward = 50 if done else -1

        # Store last and overall number of actions (i.e., rotations)
        self.last_action = action
        self.number_actions += 1
            
        return next_state, reward, done, {}

    # ========== Override gym.Env: Render =====================================
    
    def render(self, state=None):
        """
        Display a cube state.

        Parameters
        ----------
        state  : State
            State to be displayed.
            By default (None), this is the internal state in self.observation_space.
            However, can be passed explicitely when exploring states in explore_states().

        Returns
        -------
        None.
        
        """
        # Set state
        if state is None:
            state = self.observation_space
        
        # Render        
        if self.render_mode == '2D':
            self.render_window.render(state)

    # ========== Close resources ==============================================

    def close(self):
        """
        Closes PyGame resources (opened for rendering).
        
        Parameters
        ----------
        None.

        Returns
        -------
        None.
        
        """
        if self.render_window is not None:
            self.render_window.close()

    # ========== Scramble cube (i.e., apply random rotations) =================
    
    def scramble(self, number_moves):
        """
        Applay random sequence of actions to cube state.
        
        Parameters
        ----------
        number_moves : int
            Number of rotations to apply

        Returns
        -------
        State
            State after scrambling
            
        """
        # Create list of all actions
        valid_actions = list(Action)

        # Apply random actions (excluding inverse sequences like Rr or uU)
        for _ in range(number_moves):
            # Apply radom action
            action = random.choice(valid_actions)
            self.step(action)

            # Create list without inverse action for next run            
            valid_actions = list(Action)
            valid_actions.remove(action.inverse_action())
            
        # Store number of scrambles (displayed in rendering)
        self.number_scrambles = number_moves
        
        # Don't count moves
        self.number_actions = 0
        self.last_action = None
            
        return self.observation_space

    # ========== Explore all next states of a given state =====================

    def explore_state(self, state=None, encoded=True):
        """
        Expand cube state by applying every action to it.

        Parameters
        ----------
        state : State
            State to explore.
            By default (None) the current state is explored.
        encoded : bool
            Return state in encoded format (8x24 Tensor in one-hot-encoding)

        Returns
        -------
        new_states : list(State)
            List of states that can be reached from the original state.
        is_solved_states : list(bool)
            Corresponding flag, if a state in the list is the solved cube.
            
        """
        assert (state is None) or isinstance(state, State)

        # Create empty lists
        new_states, is_solved_states = [], []

        # Remember initial state and move count of environment object
        env_state = self.observation_space
        env_number_moves = self.number_actions

        # Apply all defined rotations
        explored_state = self.observation_space if (state is None) else state
        actions = list(Action)
        for action in actions:
            # Get new state
            self.observation_space = explored_state
            new_state, _, _, _ = self.step(action)

            # Check if cube solved and add flag to list
            is_cube_solved = new_state.is_cube_solved()
            is_solved_states.append(is_cube_solved)

            # Add new state to list (Modifies new_state => After checking flag!)
            if encoded is True:
                new_states.append(new_state.one_hot_encoding())
            else:
                new_states.append(new_state)

        # Restore initial state and move count in environment object
        self.observation_space = env_state
        self.number_actions = env_number_moves

        return new_states, is_solved_states
 
# -----------------------------------------------------------------------------
# Main (sample)
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Create environment and render initial state
    env = PocketCubeEnv(render_fps = 1.5)
    env.render()    

    # Aplly sample actions and render
    for action in [Action.F, Action.L, Action.u, Action.U, Action.l, Action.f]:
        env.step(action)
        env.render()
    
    # Free resources
    env.close()
 