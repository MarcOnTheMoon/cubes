# Add Pocket cube env to path
import sys
sys.path.append('../../pocket_cube_gym')

# Other imports
import numpy as np
from PocketCubeEnv import PocketCubeEnv
from PCubeAction import Action
from PCubeState import State

import collections
import random
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
import torch.optim.lr_scheduler as scheduler
from torch import optim
from tensorboardX import SummaryWriter

from LinearNet import LinearNet

def make_scramble_buffer(cube, size, depth, include_initial = False, return_inverse = False):
    """
    Create data buffer with scramble states and explored substates.

    Parameters
    ----------
    cube : Cube_2x2() -> Defined in cube_2x2x2.py (Pocketcube environment)
            Object of the Pocketcube environment.
    size : int
        how many states to generate.
    depth : int
        how deep to scramble.
    include_initial : bool
        If initial cube state should be included in the buffer.
    return_inverse:
        If True the reverse action is added to the return values.

    Returns
    -------
    result : tuple
        tuple which contains depth, encoded state, encoded explored states and if any of the explored states is the goal state.

    """
    # Calculate number of necessary iterations
    rounds = size // depth
    # Create List of actions to prevent applying to moves that aer invertibles of each other
    actions = list(Action)
    # Create List for return values
    result = []
    for _ in range(rounds):
        # Append initial state
        cube_state = State()    # Initial state
        if include_initial:
            explored_states, goals = cube.explore_state(cube_state, encoded=True)
            res = (1, (encode_inplace(np.zeros((8,24)), cube_state)), explored_states, goals)
            result.append(res)
        # Apply random actions
        for d in range(depth):
            action = random.choice(actions)
            inv_move = action.inverse_action()
            actions = list(Action)
            # Prevent that two invertible moves follow each other
            actions.remove(inv_move)
            cube_state,_,_,_ = cube.step(action, cube_state) 
            explored_states, goals = cube.explore_state(cube_state, encoded=True)
            # Append values
            if return_inverse: # With inverse action of applied move
                inv_action = action.inverse_action()
                res = (d+1, encode_inplace(np.zeros((8,24)), cube_state), inv_action, explored_states, goals)
            else: # Without inverse move
                res = (d+1, encode_inplace(np.zeros((8,24)), cube_state), explored_states, goals)
            result.append(res)  
    return result

def sample_batch(scramble_buffer, batch_size, net, zero_goal = True):
    """
    Sample batch of given size from scramble buffer produced by make_scramble_buffer.

    Parameters
    ----------
    scramble_buffer : tuple
        Contains necessary values for ADI.
    batch_size : int
        Size of batch to generate.
    net : LinearNet -> defined in LinearNet.py
        Network to use to calculate targets.
    zero_goal : bool
        If zero_goal method should be used or the original one in the paper of McAleer et al (2018).
    
    Returns
    -------
    Tensors for states, weights, policy and value

    """
    
    # Get data from buffer
    data = random.sample(scramble_buffer, batch_size)
    depths, states, explored_states, goals = zip(*data)
    
    # Handle explored states
    explored_states = np.stack(explored_states)
    shape = explored_states.shape
    explored_states_t = torch.tensor(explored_states, dtype= torch.float32).to(device) # Error if its float 64
    explored_states_t = explored_states_t.view(shape[0]*shape[1], *shape[2:])          # Shape: (states*actions, encoded_shape), combining states with actions for net input
    value_t = net(explored_states_t, value_only=True)
    value_t = value_t.squeeze(-1).view(shape[0], shape[1])                             # Shape: (states, actions), seperate actions after net output
    
    # Add reward to the values
    goals_mask_t = torch.tensor(goals, dtype=torch.int8).to(device)
    goals_mask_t += goals_mask_t - 1   # has 1 at final states and -1 elsewhere
    value_t += goals_mask_t.type(dtype=torch.float32)

    # Mask to set final goal states to 0 instead oft outputted value of network 
    if zero_goal is True: 
        goals_mask_t_inv = np.logical_not(goals).astype(int)
        goals_mask_t_inv = torch.tensor(goals_mask_t_inv, dtype=torch.int8).to(device)
        value_t *= goals_mask_t_inv

    # Find target value and target policy
    max_val_t, max_act_t = value_t.max(dim=1)

    # Create Tensors
    enc_input = np.stack(states)
    enc_input_t = torch.tensor(enc_input, dtype=torch.float32).to(device)
    depths_t = torch.tensor(depths, dtype=torch.float32).to(device)
    weights_t = 1/depths_t
    return enc_input_t.detach(), weights_t.detach(), max_act_t.detach(), max_val_t.detach()

def load(path, net, opt):
    """
    Load model and optimizer parameters.

    Parameters
    ----------
    path : string
        Where model parameters file can be found.
    net : LinearNet -> defined in LinearNet.py
        Network to use to calculate targets.
    opt : defined in torch.optim
        Which optimizer has been used.

    Returns
    -------
    None.

    """
    checkpoint = torch.load(path, map_location = 0)
    net.load_state_dict(checkpoint['model_state_dict'])
    opt.load_state_dict(checkpoint['optimizer_state_dict'])
    net.eval()
    print('loaded', path)

def save(path, net, opt):
    """
    Save model and optimizer parameters.

    Parameters
    ----------
    path : string
        Where model parameters file can be found.
    net : LinearNet -> defined in LinearNet.py
        Network to use to calculate targets.
    opt : defined in torch.optim
        Which optimizer has been used.

    Returns
    -------
    None.

    """
    torch.save({
        'model_state_dict': net.state_dict(),
        'optimizer_state_dict': opt.state_dict()
    }, path)

def log_gradients_in_model(net, writer, step):
    """
    Save gradient values of network.

    Parameters
    ----------
    net : LinearNet -> defined in LinearNet.py
        Network to use to calculate targets.
    writer : SummaryWriter of TensorboardX
        Which writer shall be used to save gradients.
    step : int
        Number of iteration that the ADI is in.

    Returns
    -------
    None.

    """
    for tag, value in net.named_parameters():
        if value.grad is not None:
            writer.add_histogram(tag + "/grad", value.grad.cpu(), step)

if __name__ == '__main__':

    # Create writer to log data
    writer = SummaryWriter()
    # Device that shall be used for network computations; 0 = gpu or cpu
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Neural Network
    net = LinearNet((8,24), 12, device)
    # Optimzer
    opt = optim.Adam(net.parameters(), lr=1e-5)
    # Learn rate scheduler
    sched = scheduler.CyclicLR(opt, base_lr=1e-6, max_lr=5e-5, step_size_up=100, cycle_momentum=False)
    # Environment
    env = PocketCubeEnv()
    # Lists to save losses
    buf_policy_loss, buf_value_loss, buf_loss = [], [], []
    buf_mean_values = []
    best_loss = None
    
    # Batch size
    train_batch_size = 1000
    # Batches to keep in scramble buffer
    scramble_buffer_batches = 10
    # After how many iterations push fresh batch into the scramble buffer
    push_scramble_buffer_iters=100
    # Scramble depth of cubes
    train_scramble_depth = 200
    # Weighted loss 
    weight_samples= False
    # Max number of batches
    train_max_batches = 15000
    # Save models
    save_models = True
    # Keep track of iterations
    step_idx = 0

    # Create scramble buffer
    scramble_buf = collections.deque(maxlen=scramble_buffer_batches * train_batch_size)
    # Fill scramble buffer 
    scramble_buf.extend(make_scramble_buffer(env, train_batch_size * 2, train_scramble_depth))
    

    while True:
        
        # Get data from buffer
        x_t, weights_t, y_policy_t, y_value_t = sample_batch(scramble_buf, train_batch_size, net)
        
        # Reset optimizer 
        opt.zero_grad()
        # Evaluate states
        policy_out_t, value_out_t  = net(x_t)
        value_out_t = value_out_t.squeeze(-1)
        value_loss_t = (value_out_t - y_value_t)**2
        value_loss_raw_t = value_loss_t.mean()

        # Calculate losses
        if weight_samples:  # If distance weighting shall be used
            value_loss_t *= weights_t
        value_loss_t = value_loss_t.mean()
        policy_loss_t = F.cross_entropy(policy_out_t, y_policy_t, reduction='none')
        policy_loss_raw_t = policy_loss_t.mean()
        if weight_samples:  # If distance weighting shall be used
            policy_loss_t *= weights_t
        policy_loss_t = policy_loss_t.mean()
        loss_raw_t = policy_loss_raw_t + value_loss_raw_t

        # Entropy loss
        entropy_loss = -(F.softmax(policy_out_t, dim=1) * F.log_softmax(policy_out_t, dim=1)).sum(dim=1).mean() * 0.05

        # Loss overall
        loss_t = value_loss_t + (policy_loss_t - entropy_loss)

        # Backpropagation
        loss_t.backward()

        # Save results in respective lists
        buf_mean_values.append(value_out_t.mean().item())
        buf_policy_loss.append(policy_loss_t.item())
        buf_value_loss.append(value_loss_t.item())
        buf_loss.append(loss_t.item())
        m_loss = np.mean(buf_loss)

        # Update model parameters
        opt.step()

        # Update learning rate
        sched.step()

        # Save if new model is the best model so far
        if best_loss is None:
                best_loss = m_loss
        elif best_loss > m_loss:
            if save_models is True:
                save('best_model.pth', net, opt)
            
        # Save gradients and scalar values for the losses
        if step_idx % 100 == 0:
            # Print step number to keep track of progress
            print(step_idx)
            log_gradients_in_model(net, writer, step_idx)
            m_policy_loss = np.mean(buf_policy_loss)
            m_value_loss = np.mean(buf_value_loss)
            m_loss = np.mean(buf_loss)
            buf_value_loss.clear()
            buf_policy_loss.clear()
            buf_loss.clear()
            m_values = np.mean(buf_mean_values)
            buf_mean_values.clear()
            writer.add_scalar("loss_policy", m_policy_loss, step_idx)
            writer.add_scalar("loss_value", m_value_loss, step_idx)
            writer.add_scalar("loss", m_loss, step_idx)
            writer.add_scalar("values", m_values, step_idx)

            # Save latest version of model 
            if save_models is True:
                save('latest.pth', net, opt)

        # Once a bounded length deque is full, when new items are added, a corresponding number of items are discarded from the opposite end.
        if step_idx % push_scramble_buffer_iters == 0:
            scramble_buf.extend(make_scramble_buffer(env, train_batch_size, train_scramble_depth))
            print("Pushed new data in scramble buffer, new size = ", len(scramble_buf))
            
        # If abort condition is met stop 
        if train_max_batches is not None and train_max_batches <= step_idx:
            print("Limit of train batches reached, exiting")
            break

        # Increase counter for iterations
        step_idx += 1

            

 

    
    