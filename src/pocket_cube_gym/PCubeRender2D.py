"""
2D rendering of Pocket cubes for OpenAI gym.

The 'match' syntax in chooseColor requires Python 3.10 or higher.

The graphical user interface is based on PyGame. Install PyGame in Anaconda
by the command 'pip install pygame'.

@authors: Finn Lanz (initial), Marc Hensel (refactoring, maintenance)
@contact: http://www.haw-hamburg.de/marc-hensel
@copyright: 2023
@version: 2023.08.20
@license: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
"""
import os
import pygame 
import ctypes
from ctypes import wintypes
from time import sleep
from PCubeState import State

class Render2D:
    
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
        
        # Cube and window dimensions
        self.__facelet_size = 60
        self.__width = 9 * self.__facelet_size
        self.__height = 7 * self.__facelet_size
        self.__x_center = self.__width / 2
        self.__y_center = self.__height / 2

        # Init pygame
        pygame.init()
        pygame.display.init()        
        
        # Set window properties and get canvas
        pygame.display.set_caption('Pocket cube gym')
        self.font = pygame.font.SysFont('Consolas', 24)
        self.screen = pygame.display.set_mode((self.__width, self.__height), pygame.HIDDEN)
        self.canvas = pygame.Surface((self.__width, self.__height))
        self._set_always_on_top()

    # -------------------------------------------------------------------------
        
    def _set_always_on_top(self):
        """
        Make window stay on top of other windows.
        
        Reference:
        https://learn.microsoft.com/de-de/windows/win32/api/winuser/nf-winuser-setwindowpos?redirectedfrom=MSDN

        Returns
        -------
        None.
        
        """
        HWND_TOPMOST = -1
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        
        window_handle = pygame.display.get_wm_info()['window'] # handle to the window
        win_dll = ctypes.WinDLL("user32")
        win_dll.SetWindowPos.restype = wintypes.HWND
        win_dll.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.UINT]
        win_dll.SetWindowPos(window_handle, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE)
        
    # ========== Show, hide, and close window =================================

    def show_window(self, is_show):
        """
        Show or hide window.

        Parameters
        ----------
        is_show : bool
            Shows window if True, else hides window

        Returns
        -------
        None.
        
        """
        if is_show is True:
            self.screen = pygame.display.set_mode((self.__width, self.__height))
        else:
            self.screen = pygame.display.set_mode((self.__width, self.__height), pygame.HIDDEN)

    # -------------------------------------------------------------------------

    def close(self):
        """
        Closed the window and free resources.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        
        """
        pygame.display.quit()
        pygame.quit()

    # ========== Colors =======================================================

    # Define colors for rendering
    __colors = {
       'red' : (255, 0, 0),
       'green' : (0, 255, 0),
       'blue' : (0, 0, 255),
       'white' : (255, 255, 255),
       'yellow' : (255, 255, 0),
       'orange' : (255, 128, 0),
       'black': (0, 0, 0)
    }

    # -------------------------------------------------------------------------

    def _char2color(color_char):
        """
        Get color RGB values in [0,255] corresponding to a color char.
    
        Parameters
        ----------
        color_char : char
            Color as defined in Render2D._colors
    
        Returns
        -------
        tuple(int)
            RGB values corresponding to the color.
            
        """
        match color_char:
            case 'W': color = Render2D.__colors['white']
            case 'Y': color = Render2D.__colors['yellow']
            case 'O': color = Render2D.__colors['orange']
            case 'R': color = Render2D.__colors['red']
            case 'G': color = Render2D.__colors['green']
            case 'B': color = Render2D.__colors['blue']
        return color

    # ========== Render cube ==================================================
        
    def render(self, state):
        """
        Draw the cube (colored plane representation) and annotated text.
        
        Displays a congratulations image, if the state represents a solved cube
        and there have been moves in self._env.

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

        # Show window and draw cube
        self.show_window(True)
        self.canvas.fill(Render2D.__colors['white'])
        self._draw_cube(state)
        self._draw_text()
        
        # Process event queue (mandatory for each frame when not working with events!)
        pygame.event.pump()
        
        # Update the displayed content and delay (=> fps)
        pygame.display.update()
        sleep(1.0 / self.__fps)

        # Display special image when the cube is solved
        if (self.__env.number_actions > 0) and state.is_cube_solved():
            # Clear screen
            self.screen.fill(Render2D.__colors['white'])

            # Show image
            file_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(file_dir, 'assets')
            img = pygame.image.load(assets_dir + '\CubySolved.png')
            factor = (self.__height - 50) / img.get_rect().height    # Top and bottom margin of 25 pixel
            img = pygame.transform.scale(img, (factor * img.get_rect().width, factor * img.get_rect().height))
            self.screen.blit(img, (self.__x_center - img.get_rect().width/2, 25))

            # Process event queue
            pygame.event.pump()
            
            # Update displayed content and delay (twice the standard delay)
            pygame.display.update()
            sleep(1.0)

    # -------------------------------------------------------------------------

    def _draw_text(self):
        """
        Draw annotation strings (last move, number moves, and number scrambles).
        
        The values are given by elf._env.
        
        In PyGame, strings are rendered as images, first.
        
        Parameters
        ----------
        None.

        Returns
        -------
        None.
        
        """
        text_color = Render2D.__colors['black']
        if self.__env.last_action is not None:
            image_last_action = self.font.render(f'Last move : {self.__env.last_action.name}', True, text_color)
        else:
            image_last_action = self.font.render('Last move :', True, text_color)
        image_actions = self.font.render(f'Moves     : {self.__env.number_actions}', True, text_color)
        image_scrambles = self.font.render(f'Scrambles : {self.__env.number_scrambles}', True, text_color)
        
        self.screen.blit(image_last_action, (self.__x_center + self.__facelet_size , 40))
        self.screen.blit(image_actions, (self.__x_center + self.__facelet_size , 65))
        self.screen.blit(image_scrambles, (self.__x_center + self.__facelet_size , 90))
    
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
        # Get plane representation and reorder
        # TODO Change get_plane_representation() to return correct order?
        plane_representation = state.get_plane_representation()
        order = [0, 1, 3, 4 ,2, 5]
        plane_representation = [plane_representation[i] for i in order]

        # Draw faces on Top (U, 'up') and bottom (D, 'down')
        frame_color = Render2D.__colors['black']
        for row in range(2):
            for col in range(2):
                # Up
                color = Render2D._char2color(plane_representation[0][2 * row + col])
                x0 = self.__x_center - ((2 - col) * self.__facelet_size)
                y0 = self.__y_center - ((3 - row) * self.__facelet_size)
                rectangle = pygame.Rect(x0, y0, self.__facelet_size + 1, self.__facelet_size + 1)
                pygame.draw.rect(self.canvas, color, rectangle)             # Filled square
                pygame.draw.rect(self.canvas, frame_color, rectangle, 1)    # Black frame
                
                # Down
                color = Render2D._char2color(plane_representation[5][2 * row + col])
                x0 = self.__x_center - ((2 - col) * self.__facelet_size)
                y0 = self.__y_center + ((1 + row) * self.__facelet_size)
                rectangle = pygame.Rect(x0, y0, self.__facelet_size + 1, self.__facelet_size + 1)
                pygame.draw.rect(self.canvas, color, rectangle)
                pygame.draw.rect(self.canvas, frame_color, rectangle, 1)
        
        # Draw 4 faces in vertical center from left to right
        for face_idx in range(4):
            for row in range(2):
                for col in range(2):
                    color = Render2D._char2color(plane_representation[face_idx + 1][2 * row + col])
                    x0 = self.__x_center - ((4 - col) * self.__facelet_size) + (2 * face_idx * self.__facelet_size)
                    y0 = self.__y_center - ((1 - row) * self.__facelet_size)
                    rectangle = pygame.Rect(x0, y0, self.__facelet_size + 1, self.__facelet_size + 1)
                    pygame.draw.rect(self.canvas, color, rectangle)
                    pygame.draw.rect(self.canvas, frame_color, rectangle, 1)
                    
        self.screen.blit(self.canvas, self.canvas.get_rect())
