"""
Policy for basic example how to use the Pocket cube environment for OpenAI gym.

The policy stores the 'quality' Q(s,a) being the maximum future rewards for
action a applied to state s.

@authors: Marc Hensel
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.08.09
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""
# Add Pocket cube env to path
import sys
sys.path.append('../../pocket_cube_gym')

# Other imports
import numpy as np
import os.path
from collections import defaultdict
from PCubeAction import Action
from PCubeState import State

class Policy():

    # ========== Constructor ==================================================

    def __init__(self, number_actions):
        """
        Constructor.

        Returns
        -------
        None.
        
        """
        self.Q = defaultdict(lambda: np.zeros(number_actions))
        self.file_name = 'PCube_SampleQuality.npy'

    # ========== Objects to table indices =====================================
    
    def to_index_s(self, state):
        """
        Get the index 's' to the table Q[s][a].

        Parameters
        ----------
        state : State
            State s for which to generate the index

        Returns
        -------
        int
            index, being the joined tuples state.positions and state.orientations
            
        """
        return state.positions + state.orientations

    # -------------------------------------------------------------------------
    
    def to_index_a(self, action):
        """
        Get the index 'a' to the table Q[s][a].

        Parameters
        ----------
        action : Action
            Action a for which to generate the index

        Returns
        -------
        int
            index, being the enumeration value within class Action
            
        """
        return action.value

    # ========== Getter =======================================================
    
    def max_rewards(self, state):
        """
        Get maximum rewards (including future rewards) for a state.

        Parameters
        ----------
        state : State
            State s to get maximum rewards for.

        Returns
        -------
        int
            Maximum rewards (including future rewards) known for state s.
            
        """
        s = self.to_index_s(state)
        return self.Q[s].max()

    # -------------------------------------------------------------------------
    
    def best_action(self, state):
        """
        Get action with highest future rewards for a state.

        Parameters
        ----------
        state : State
            State s to get the best action for.

        Returns
        -------
        Action
            Action applied to state s with highest future rewards.
            
        """
        s = self.to_index_s(state)
        return Action(self.Q[s].argmax())
        
    # ========== Add (state, action) pair to table ============================

    def add(self, state, action, future_rewards):
        """
        Add a state/action pair to the table.

        Parameters
        ----------
        state : State
            State s on which the action is replied.
        action : Action
            Action a which is applied to the state.
        future_rewards : int
            Reward and maximum future rewards when applying a to s.

        Returns
        -------
        None.
        
        """
        assert isinstance(state, State)
        assert isinstance(action, Action)
        
        s = self.to_index_s(state)
        a = self.to_index_a(action)        
        self.Q[s][a] = future_rewards

    # ========== File I/O =====================================================

    def save_to_file(self):
        """
        Save the table data to file 'PCube_SampleQuality.npy'.

        Returns
        -------
        None.
        
        """
        np.save(self.file_name, np.array(dict(self.Q)))

    # -------------------------------------------------------------------------

    def load_from_file(self):
        """
        Load the table data from file 'PCube_SampleQuality.npy'.

        Returns
        -------
        bool
            True if the file exists, else False.
            
        """
        if os.path.exists(self.file_name):
            q = np.load(self.file_name, allow_pickle = True)
            self.Q.update(q.item())
            return True
        else:
            return False
