"""
Basic example how to use the Pocket cube environment for OpenAI gym.

First, sets the correct actions to solve cubes scrambles by 1 or 2 moves
deterministically. As second step, extends the policy to 3 (or more) scrambles
by scrambling a solved cube randomly 2 (or more) times and adding all next
scramble steps. Finally, the results are visualized by trying to solve randomly
scrambled cubes.

@authors: Marc Hensel
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.08.08
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
        
        # Init policy (including up to 2 scrambles)
        self.policy = Policy(self.env.action_space.n)
        self._init_policy()

    # ========== Improve policy ===============================================

    def _init_policy(self):
        """
        Set policy to solve cubes scrambled 1x or 2x.

        Returns
        -------
        None.
        """
        # Solved cubes scrambled 1x
        for action in list(Action):
            # Scramble solved cube
            self.env.reset()
            state, _, _, _, = self.env.step(action)
            
            # Solve by inverse action and add to policy
            inverse_action = action.inverse_action()
            _, reward, _, _, = self.env.step(inverse_action)
            self.policy.add(state, inverse_action, reward)

        # Solved cubes scrambled 2x
        for scramble_action in list(Action):
            # Scramble 1x
            self.env.reset()
            state, _, _, _, = self.env.step(scramble_action)
            
            # Add all states scrambled another time
            self._add_scrambles(state)

    # -------------------------------------------------------------------------

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
        
        actions = list(Action)
        
        # Proceed only if initial state knows action to solved cube
        if self.policy.max_rewards(state) <= 0:
            return

        # For each scramble add best action to policy
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
                future_rewards[action.value] = self.policy.max_rewards(new_state)

            # Add action with highest future reward to Q tables
            max_reward = future_rewards.max()
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
        # 1 to 2 scrambles already added in _init_policy()
        if number_scrambles < 3:
            return

        # Add further states randomly        
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
    # Init agend and policy for up to 2 scrambles
    agent = SampleAgent()

    # Load policy from file (to further improve it)
    if agent.policy.load_from_file():
        print('Loaded prior policy from file.')
    else:
        print('No policy file found.')
    
    # Improve policy for more scrambles and save it to file
    agent.train_policy(number_scrambles = 3, number_episodes = 10_000)
    agent.train_policy(number_scrambles = 4, number_episodes = 15_000)
    print('Saving policy to file ...')
    agent.policy.save_to_file()
    
    # Demonstrate policy with randomly scrambled cubes
    for _ in range(3):
        agent.apply_policy(number_scrambles = 3)
    for _ in range(3):
        agent.apply_policy(number_scrambles = 4)
    
    # Cleanup
    agent.env.close()

