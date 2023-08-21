"""
3D rendering of Pocket cubes for OpenAI gym.

The 'match' syntax in chooseColor requires Python 3.10 or higher.

The graphical user interface is based on VPython. The library uses the default
browser to display images and animations. Install VPython in Anaconda by the
command 'conda install -c conda-forge vpython'.

@authors: Marc Hensel
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.08.21
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""
from vpython import scene, vector, pyramid, box, arrow
import itertools
from time import sleep
from PCubeState import State

class Render3D:
    
    # ========== Constructor ==================================================

    def __init__(self, env, fps):
        """
        Constructor.

        Parameters
        ----------
        env : PocketCubeEnv
            Gym environment containing the cube to be rendered.
        fps : float
            Speed of the rendering in frames per seconds.
            Determines how long a state will shown before proceeding.

        Returns
        -------
        None.
        
        """
        assert isinstance(fps, float) and (fps > 0.0)
        
        # Set parent environment and render speed
        self.__env = env
        self.__fps = fps

        # Set VPython scene
        self.__scene = scene
        
        # Cube and scene dimensions
        self.__cubicle_center_shift = 0.52
        self.__scene.width = 600
        self.__scene.height = 600
        self.__scene.range = 2.5
        self.__scene.center = vector(0, 0, 0)

        # Set scene properties
        self.__scene.title = 'Pocket cube gym (right-click to rotate, mouse wheel to zoom)'
        self.__scene.caption = "\n"
        self.__scene.autoscale = False
        self.__scene.background = Render3D.__colors['background']
        
        # Create render objects
        self._init_render_objects()
        
    # ========== Colors =======================================================

    # Define colors for rendering
    __colors = {
        'background': vector(0.8, 0.8, 0.8),
        'arrow': vector(0.5, 0.5, 0.5),
        'red' : vector(1, 0, 0),
        'green' : vector(0, 1, 0),
        'blue' : vector(0, 0, 1),
        'white' : vector(1, 1, 1),
        'yellow' : vector(1, 1, 0),
        'orange' : vector(1, 0.5, 0),
        'black': vector(0, 0, 0)
    }

    # -------------------------------------------------------------------------

    def _char2color(color_char):
        """
        Get color RGB values in [0,1] corresponding to a color char.
    
        Parameters
        ----------
        color_char : char
            Color as defined in Render3D._colors
    
        Returns
        -------
        tuple(int)
            RGB values corresponding to the color.
            
        """
        match color_char:
            case 'W': color = Render3D.__colors['white']
            case 'Y': color = Render3D.__colors['yellow']
            case 'O': color = Render3D.__colors['orange']
            case 'R': color = Render3D.__colors['red']
            case 'G': color = Render3D.__colors['green']
            case 'B': color = Render3D.__colors['blue']
        return color

    # ========== Render cube ==================================================
        
    def render(self, state):
        """
        Draw the cube (colored plane representation).

        Parameters
        ----------
        state : State
            State to visualize.
            By default (None) the observation space of self._env is used.
    
        Returns
        -------
        None.
        
        """
        assert isinstance(state, State)

        # Draw cube
        self._draw_cube(state)
        
        # Update texts
        caption = '\nLast move :'
        if self.__env.last_action is not None:
            caption += f' {self.__env.last_action.name}'
        caption += f'\nMoves      : {self.__env.number_actions}'
        caption += f'\nScrambles : {self.__env.number_scrambles}'
        self.__scene.caption = caption
        
        
        # Delay (=> fps)
        sleep(1.0 / self.__fps)
   
    # -------------------------------------------------------------------------
    
    def _init_render_objects(self):
        """
        Create all objects of the rendered scene.
        
        Gray boxes make sure the cubicles have surfaces at all sides.
        The colored faces are represented by pyramids.
        Arrows indicate the "up" axis (large arrow) and "front" (small arrow).

        Returns
        -------
        None.

        """
        # Cubicles (so that interior is drawn)
        center = self.__cubicle_center_shift - 0.0001      # Do not mix box color with face colors
        for dx, dy, dz in itertools.product([-center, center], [-center, center], [-center, center]):
            box(pos=vector(dx, dy, dz), size=vector(1, 1, 1), color=Render3D.__colors['background'])

        # Arrows marking the faces "up" and "front"
        arrow(pos=vector(0, -2, 0), axis=vector(0, 4, 0), shaftwidth=0.1, color=Render3D.__colors['arrow'])
        arrow(pos=vector(0, 0, 0), axis=vector(0, 0, 1.75), shaftwidth=0.05, color=Render3D.__colors['arrow'])
        
        # Colored faces (initially in gray)
        c = self.__cubicle_center_shift
        dist = 1.02
        size = vector(0.5,1,1)
        color = Render3D.__colors['background']
        
        self.__faces = {
            'U': [
                pyramid(pos=vector(-c, dist, -c), axis=vector(0,-1,0), size=size, color=color),
                pyramid(pos=vector(+c, dist, -c), axis=vector(0,-1,0), size=size, color=color),
                pyramid(pos=vector(-c, dist, +c), axis=vector(0,-1,0), size=size, color=color),
                pyramid(pos=vector(+c, dist, +c), axis=vector(0,-1,0), size=size, color=color)],
            'D': [
                pyramid(pos=vector(-c, -dist, +c), axis=vector(0,1,0), size=size, color=color),
                pyramid(pos=vector(+c, -dist, +c), axis=vector(0,1,0), size=size, color=color),
                pyramid(pos=vector(-c, -dist, -c), axis=vector(0,1,0), size=size, color=color),
                pyramid(pos=vector(+c, -dist, -c), axis=vector(0,1,0), size=size, color=color)],
            'F': [
                pyramid(pos=vector(-c, +c, dist), axis=vector(0,0,-1), size=size, color=color),
                pyramid(pos=vector(+c, +c, dist), axis=vector(0,0,-1), size=size, color=color),
                pyramid(pos=vector(-c, -c, dist), axis=vector(0,0,-1), size=size, color=color),
                pyramid(pos=vector(+c, -c, dist), axis=vector(0,0,-1), size=size, color=color)],
            'B': [
                pyramid(pos=vector(+c, +c, -dist), axis=vector(0,0,1), size=size, color=color),
                pyramid(pos=vector(-c, +c, -dist), axis=vector(0,0,1), size=size, color=color),
                pyramid(pos=vector(+c, -c, -dist), axis=vector(0,0,1), size=size, color=color),
                pyramid(pos=vector(-c, -c, -dist), axis=vector(0,0,1), size=size, color=color)],
            'L': [
                pyramid(pos=vector(-dist, +c, -c), axis=vector(1,0,0), size=size, color=color),
                pyramid(pos=vector(-dist, +c, +c), axis=vector(1,0,0), size=size, color=color),
                pyramid(pos=vector(-dist, -c, -c), axis=vector(1,0,0), size=size, color=color),
                pyramid(pos=vector(-dist, -c, +c), axis=vector(1,0,0), size=size, color=color)],
            'R': [
                pyramid(pos=vector(dist, +c, +c), axis=vector(-1,0,0), size=size, color=color),
                pyramid(pos=vector(dist, +c, -c), axis=vector(-1,0,0), size=size, color=color),
                pyramid(pos=vector(dist, -c, +c), axis=vector(-1,0,0), size=size, color=color),
                pyramid(pos=vector(dist, -c, -c), axis=vector(-1,0,0), size=size, color=color)]
            }
        
    # -------------------------------------------------------------------------

    def _draw_cube(self, state):
        """
        Draw the colored facelets as plane representation.

        Parameters
        ----------
        state : State
            State to visualize.

        Returns
        -------
        None.
        
        """
        # Get plane representation
        plane_representation = state.get_plane_representation()
        
        # Set colors
        for i in range(4):
            self.__faces['U'][i].color = Render3D._char2color(plane_representation[0][i])
            self.__faces['L'][i].color = Render3D._char2color(plane_representation[1][i])
            self.__faces['B'][i].color = Render3D._char2color(plane_representation[2][i])
            self.__faces['F'][i].color = Render3D._char2color(plane_representation[3][i])
            self.__faces['R'][i].color = Render3D._char2color(plane_representation[4][i])
            self.__faces['D'][i].color = Render3D._char2color(plane_representation[5][i])
