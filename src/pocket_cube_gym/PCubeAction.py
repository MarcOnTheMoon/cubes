"""
Actions on Pocket cubes for OpenAI gym.

@authors: Finn Lanz (initial), Marc Hensel (refactoring, maintenance)
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.08.09
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""

import enum

class Action(enum.Enum):
    """
    Representation of the actions as members of the enum class.
    
    Capital letters denote clockwise rotations, small letter counter-clockwise
    rotations of the faces right, left, up, down, front, and back.
    """

    # ========== Enumerated constants in [0, 11] ==============================

    R, L, U, D, F, B, r, l, u, d, f, b = range(12)
    
    # ========== Get inverse action ===========================================
    
    def inverse_action(self):
        """
        Get inverse action.
    
        Returns
        -------
        Action
            Action turning same face in opposite direction (e.g., R and r)
            
        """
        return (Action.r, Action.l, Action.u, Action.d, Action.f, Action.b,
                Action.R, Action.L, Action.U, Action.D, Action.F, Action.B)[self.value]
