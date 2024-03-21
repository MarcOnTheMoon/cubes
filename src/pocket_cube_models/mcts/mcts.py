"""
Reinforcement learning for the Pocket cube environment based on ADI and MCTS.

The code is based on the publication on DeepCube (see below) and uses Autodidactic
Iteration (ADI) and Monte Carlo Tree Search (MCTS).

S. McAleer et al.:
Solving the Rubik's Cube with Approximate Policy Iteration', ICLR 2019.

@authors: Finn Lanz (initial), Marc Hensel (refactoring, maintenance)
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.09.27
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""

# Add Pocket cube env to path
import sys
sys.path.append('../../pocket_cube_gym')

# Other imports
import numpy as np
from PocketCubeEnv import PocketCubeEnv
from PCubeAction import Action
from PCubeState import State


import random
import numpy as np
import collections
import torch
import torch.nn.functional as F

from LinearNet import LinearNet

class MCTS:

    def __init__(self, cube_env, state, net, exploration_c=100, virt_loss_nu=100.0, device=0):

        assert isinstance(state, State)

        # Pocketcube environment
        self.cube_env = cube_env
        # Starting state
        self.root_state = state
        # Neural network
        self.net = net
        # Exploration/Exploitation parameter
        self.exploration_c = exploration_c
        # Virtual loss -> prevents the tree search from visiting the same stat
        self.virt_loss_nu = virt_loss_nu
        # Used device for neural network calculation -> gpu or cpu 
        self.device = device

        # Tree state
        shape = ((12), )
        # correspond to N_s(a) in the paper
        self.act_counts = collections.defaultdict(lambda: np.zeros(shape, dtype=np.uint32))
        # correspond to W_s(a)
        self.val_maxes = collections.defaultdict(lambda: np.zeros(shape, dtype=np.float32))
        # correspond to P_s(a)
        self.prob_actions = {}
        # correspond to L_s(a)
        self.virt_loss = collections.defaultdict(lambda: np.zeros(shape, dtype=np.float32))
        # Edges which connect the nodes
        self.edges = {}

    def __len__(self):
        """
        Number of edges.
        
        Parameters
        ----------
        None

        Returns
        -------
        int
            Number of created edges.

        """
        return len(self.edges)

    def search(self):
        """
        One iteration of the mcts search algorithm.
        
        Parameters
        ----------
        None

        Returns
        -------
        If goal has been found:

        list   
            Return list of actions that led to the goal state.

        Otherwise:
        None.
            
        """
        s, path_actions, path_states = self._search_leaf()
       
        child_states, child_goal = self.cube_env.explore_state(s, encoded = False)
        self.edges[s] = child_states

        value = self._expand_leaves([s])[0]
        
        self._backup_leaf(path_states, path_actions, value)

        if np.any(child_goal):
            path_actions.append(np.argmax(child_goal))
            return path_actions
        return None

    def _search_leaf(self):
        """
        Starting the root state, find path to the leaf node
        
        Parameters
        ----------
        None

        Returns
        -------
        tuple: 
            Returns the leaf node state, the actions that led to that state and the states that have been visited -> (state, path_actions, path_states).

        """
        # Always starts at state s until a leaf node has been found, no rollout phase
        s = self.root_state
        path_actions = []
        path_states = []

        # Walking down the tree
        while True:
            next_states = self.edges.get(s)
    
            # If leaf node has been found break
            if next_states is None:
                break

            # Counter how often state has been vistied
            act_counts = self.act_counts[s]
            N_sqrt = np.sqrt(np.sum(act_counts))
    
            # If state hasnt been seen before do random action
            if N_sqrt < 1e-6:
                act = random.randrange(12)
            else: # Else pick the one with the highest sum of (u+q)
                u = self.exploration_c * N_sqrt / (act_counts + 1)
                u *= self.prob_actions[s]
                q = self.val_maxes[s] - self.virt_loss[s]
                act = np.argmax(u + q)
            # Update virtual loss
            self.virt_loss[s][act] += self.virt_loss_nu
            path_actions.append(act)
            path_states.append(s)
            s = next_states[act]
        return s, path_actions, path_states

    def _expand_leaves(self, leaf_states):
        """
        From list of states expand them using the network.

        Parameters
        ----------
        leaf_states : list 
            List of states.

        Returns
        ----------
        list 
            List of state values.
        """
        policies, values = self.evaluate_states(leaf_states)
        self.prob_actions[leaf_states[0]] = policies[0]
        return values

    def _backup_leaf(self, states, actions, value):
        """
        Update tree state after reaching and expanding the leaf node.

        Parameters
        ----------
        states : list of States (State  -> Defined in cube_utils. Describes cube state with its cubies (position and orientation))
            Path of states (without final leaf state):
        actions : List of nubers. Numbers corresponding to actions.
            Path of actions.
        value : List of values of the states.
            Value of leaf nodes.
        Returns
        ----------
        None.

        """
        
        for path_s, path_a in zip(states, actions):
            self.act_counts[path_s][path_a] += 1
            w = self.val_maxes[path_s]
            w[path_a] = max(w[path_a], value)
            self.virt_loss[path_s][path_a] -= self.virt_loss_nu

    def evaluate_states(self, states):
        """
        Ask network to return policy and values.

        Parameters
        ----------
        net : LinearNet -> defined in LinearNet.py 
            Neural network that is used for the computations
        states: List of States (State  -> Defined in cube_utils. Describes cube state with its cubies (position and orientation))
            States that shall be evaluated by the network.
        
        Returns
        ----------   
        policy : NDArray
            Array which contains corresponding policy values for the presented states.
        value : NDArray
            Array which contains corresponding values for the presented states.
        """
        enc_states = State.one_hot_encode_states(states)
        enc_states_t = torch.tensor(enc_states).to(self.device)
        policy_t, value_t = self.net(enc_states_t)
        policy_t = F.softmax(policy_t, dim=1)
        return policy_t.detach().cpu().numpy(), value_t.squeeze(-1).detach().cpu().numpy()
    
    def complete_search(self):
        """
        One complete mcts search for the solution path.

        Parameters
        ----------
        None. 

        Returns
        ----------
        solution_path : list
            Solution path in Action format. -> Action.D, Action.R ..
        solution_path_nr : list
            Solution path as numbers. -> 3, 0 ..
        """
        while True:
            print('Search')
            solution = self.search()
            print('Search ended')
            
            # When the goal state has been reached
            if solution:
                print('Is solution')
                solution_path = []
                solution_path_nr = []
                # Append actions to a list that led to goal state
                for action in solution:
                    solution_path.append(Action(action))
                    solution_path_nr.append(action)
                # Reverse actions
                solution_path.reverse()
                solution_path_nr.reverse()
                return solution_path, solution_path_nr

    def find_solution(self):
        """
        Perform a full breath-ﬁrst search to ﬁnd the shortest predicted path 
        from the starting state to solution.

        Parameters
        ----------
        None. 

        Returns
        ----------
        p: list
            List with action that lead to solved state.
        """

        # Batch size
        batch_size = 1000
        # Create queue for seach
        queue = collections.deque([(self.root_state, [])])
        # Create list to note which states have already been visited
        seen = set()
        # As long as the queue is not empty
        while queue:
            # Create batch
            batch = []  
            for _ in range(min(batch_size, len(queue))):
                # Remove first entry of the queue 
                s, path = queue.popleft()
                # Add state to seen set
                seen.add(s)
                # Add state and patch to batch 
                batch.append((s, path))
            # Iterate through batch
            for s, path in batch:
                # Explore child states of current state s
                c_states, c_goals = self.cube_env.explore_state(s, encoded = False)
                # Enumerate over children
                for a_idx, (c_state, c_goal) in enumerate(zip(c_states, c_goals)):
                    # Add action to path
                    p = path + [a_idx]
                    # If solved state has been found return path
                    if c_goal:
                        return p
                    # If state is in seen set or isnt already in the edges of the tree continue the loop
                    if c_state in seen or c_state not in self.edges:
                        continue
                    # Otherwise add state and path to the queue 
                    queue.append((c_state, p))
        # If no solution has been found
        return None


if __name__ == '__main__':
    env = PocketCubeEnv()
    state = env.scramble(25)


    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    print('Create model')
    model = LinearNet((8,24), 12, device)
    checkpoint = torch.load('./LinearNetParameters.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    print('Eval model')
    model.eval()
    print('Create MCTS')
    tree = MCTS(env, state, model, device=device)
    print('MCTS complete search')
    tree.complete_search()
