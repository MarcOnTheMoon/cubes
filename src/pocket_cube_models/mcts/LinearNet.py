import numpy as np
import torch.nn as nn
import torch.nn.functional as F

class LinearNet(nn.Module):
    """
    A feedforward neural network used for value and policy iteration.
    """
    def __init__(self, input_shape, action_size, device):

        super(LinearNet, self).__init__()

        self.device = device
        self.size = int(np.prod(input_shape))
        self.action_size = action_size

        self.fc1 = nn.Linear(in_features=self.size, out_features=4096)
        self.bn1 = nn.BatchNorm1d(4096)
        self.fc2 = nn.Linear(in_features=4096, out_features=2048)
        self.bn2 = nn.BatchNorm1d(2048)
        self.fc_v = nn.Linear(in_features=2048, out_features=512)
        self.fc_p = nn.Linear(in_features=2048, out_features=512)
        self.bn3 = nn.BatchNorm1d(512)

        # Two heads on our network
        self.action_head = nn.Linear(in_features=512, out_features=self.action_size)
        self.value_head = nn.Linear(in_features=512, out_features=1)
    
        self.to(device)

        # Initialize all weights with Glorot initialization
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.xavier_uniform_(self.fc_v.weight)
        nn.init.xavier_uniform_(self.fc_p.weight)
        nn.init.xavier_uniform_(self.action_head.weight)
        nn.init.xavier_uniform_(self.value_head.weight)

    def forward(self, x, value_only = False):
        """
        Foward pass of network.

        Parameters
        ----------
        x : Tennsor
            Input that shall be forward propagated through network.
        value_only : bool
            If True only value part will be returned, otherwise policy will be returned too.
        
        Returns
        -------
        If value_only == True:
            Tensor
                Value output of network
        Else:
            Tuple of Tensors (value, policy)
        """
        x = x.view((-1, self.size))
        x = F.leaky_relu(self.bn1(self.fc1(x)))
        x = F.leaky_relu(self.bn2(self.fc2(x)))

        # value branch
        x_v = F.leaky_relu(self.bn3(self.fc_v(x)))
        out_v = self.value_head(x_v)

        # policy branch
        x_p = F.leaky_relu(self.bn3(self.fc_p(x)))
        out_p = self.action_head(x_p)

        if value_only is True:
            return out_v
        else:
            return (out_p, out_v)

        


