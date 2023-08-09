"""
Basic example how to use the Pocket cube environment for OpenAI gym.

Learns how to solve randomly scrambled cubes starting with cubes being
scrambled by 1 move, then 2 moves, 3 moves, and so on. Finally, the results
are visualized by trying to solve randomly scrambled cubes.

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
import time
import numpy as np
from PocketCubeEnv import PocketCubeEnv
from PCubeAction import Action
from PCubeState import State
from SamplePolicy import Policy

# -----------------------------------------------------------------------------
# Agent
# -----------------------------------------------------------------------------

class SampleAgent():
    
    # ========== Constructor ==================================================

    def __init__(self, render_fps=1.0):
        """
        Constructor.

        Returns
        -------
        None.
        
        """
        # Init gym environment
        assert isinstance(render_fps, float)
        self.env = PocketCubeEnv(render_fps=render_fps)
        
        # Init policy
        self.policy = Policy(self.env.action_space.n)

    # ========== Improve policy ===============================================

    def _add_scrambles(self, state):
        """
        Adds all states to the policy that result by applying an action to the
        state passed as argument.

        Parameters
        ----------
        state : State
            State to scramble and add with all valid actions.

        Returns
        -------
        None.
        
        """
        assert isinstance(state, State)
        
        # Skip if there is no known way to the solved cube from the state
        if (self.policy.max_rewards(state) <= 0) and (state.is_cube_solved() is False):
            return
        
        # For each scramble add best action to policy
        actions = list(Action)
        for scramble_action in actions:
            # Scramble initial state
            self.env.observation_space = state
            scrambled_state, _, _, _, = self.env.step(scramble_action)
            
            # Determine future rewards of all actions
            future_rewards = np.zeros(len(Action))
            for action in actions:
                # Apply action to scrambled state
                self.env.observation_space = scrambled_state
                new_state, reward, _, _, = self.env.step(action)
                future_rewards[action.value] = reward + self.policy.max_rewards(new_state)

            # Add action with highest future reward to Q tables
            max_reward = future_rewards.max()
            if max_reward > 0:
                max_action = Action(future_rewards.argmax())
                self.policy.add(scrambled_state, max_action, reward + max_reward)

    # -------------------------------------------------------------------------

    def train_policy(self, number_scrambles, number_episodes):
        """
        Add state/action pairs for random states to the table.
        
        When training for N scrambles, the policy should already know how to
        solve a cube for (N - 1) scrambles. Example: Do not train with
        number_scrambles == 4 before having trained sufficiently with
        number_scrambles == 3.

        Parameters
        ----------
        number_scrambles : int
            Number of times the cube shall be rotated randomly.
        number_episodes : int
            Number of times trying to add a random state.

        Returns
        -------
        None.
        
        """
        print(f'Training cube with {number_scrambles:_} scrambles:', flush=True)
        start_time_ns = time.time_ns()
        
        for current_episode in range(1, number_episodes + 1):
            # Scramble cube
            self.env.reset()
            self.env.scramble(number_scrambles - 1)     # For last scramble all actions are added below
            
            # Add last scramble (all actions)
            self._add_scrambles(self.env.observation_space)

            # Print progress to the console
            if (current_episode % 1_000 == 0) or (current_episode == number_episodes):
                time_per_episode_ns = (time.time_ns() - start_time_ns) / current_episode
                print(f'\rRunning episode {current_episode:_} / {number_episodes:_} ({time_per_episode_ns / 1_000_000:.2f} ms/episode) ... ', flush=True, end = '')
            if current_episode == number_episodes:
                print('ok')

    # ========== Apply policy =================================================
    
    def apply_policy(self, number_scrambles, is_render=True):
        """
        Scramble cube and apply policy to solve it.

        Parameters
        ----------
        number_scrambles : int
            Number of times the cube is randomly scrambled.
        is_render : bool, optional
            The cube is rendered if True. (Default: True)

        Returns
        -------
        None.
        
        """
        # Create the scrambled cube
        self.env.reset()
        self.env.scramble(number_scrambles)
        
        if is_render:
            self.env.render()
        
        # Determine and apply actions
        for _ in range(number_scrambles):
            if self.env.observation_space.is_cube_solved():
                break
            
            # Get and apply action with of maximum future rewards
            action = self.policy.best_action(self.env.observation_space)
            next_state, reward, done, _ = self.env.step(action)
            
            if is_render:
                self.env.render()

# -----------------------------------------------------------------------------
# Main (sample)
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    agent = SampleAgent()

    # Load policy from file (to further improve it)
    if agent.policy.load_from_file():
        print('Loaded prior policy from file.')
    else:
        print('No policy file found.')
    
    # Improve policy for more scrambles and save it to file
    agent.train_policy(number_scrambles = 1, number_episodes = 5_000)
    agent.train_policy(number_scrambles = 2, number_episodes = 15_000)
    agent.train_policy(number_scrambles = 3, number_episodes = 25_000)
    print('Saving policy to file ...')
    agent.policy.save_to_file()
    
    # Demonstrate policy with randomly scrambled cubes
    for _ in range(3):
        agent.apply_policy(number_scrambles = 1)
    for _ in range(3):
        agent.apply_policy(number_scrambles = 2)
    for _ in range(3):
        agent.apply_policy(number_scrambles = 3)
    
    # Cleanup
    agent.env.close()

