import pygame
from spaces_gui import SpacesGUI  # Import the SpacesGUI class that manages individual tiles on the board

class BoardGUI:
    """
    This class handles the layout, creation, and rendering of the board and its spaces.
    It creates a Monopoly-style square board using rectangles for each space, assigns 
    properties to each space, and manages how they're drawn and interacted with.
    """

    def __init__(self, board_size=750, window_width=1200, window_height=750):
        """
        Initializes the board layout and spacing.

        Parameters:
        board_size (int): The width and height (in pixels) of the square board area.
        window_width (int): The width of the game window.
        window_height (int): The height of the game window.
        """
        self.board_size = board_size
        self.window_width = window_width
        self.window_height = window_height

        # Each side of the board has 11 tiles, so we divide to find tile size
        self.tile_size = self.board_size // 11

        # X and Y offsets position the board in the window (centered horizontally)
        self.board_offset_x = (self.window_width - self.board_size) // 2
        self.board_offset_y = 0  # The board sits at the top

        # Create and store all board space objects
        self.spaces = self.initialize_spaces()

    def initialize_spaces(self):
        """
        Creates all 40 spaces on the board with their names, types, and optional prices.
        These are arranged in order around a square board.

        Returns:
        list: A list of SpacesGUI objects, each representing a space on the board.
        """
        # Define the board layout: (name, color/type, price)
        board_layout = [
            # Bottom row (left to right)
            ("Go", None, None), ("The Old Creek", "Brown", 60), ("Pot Luck", None, None),
            ("Gangsters Paradise", "Brown", 60), ("Income Tax", None, None), ("Brighton Station", "Station", 200),
            ("The Angels Delight", "Blue", 100), ("Opportunity Knocks", None, None),
            ("Potter Avenue", "Blue", 100), ("Granger Drive", "Blue", 120), ("Jail/Just visiting", None, None),
            # Left column (bottom to top)
            ("Skywalker Drive", "Purple", 140), ("Tesla Power Co", "Utilities", 150),
            ("Wookie Hole", "Purple", 140), ("Rey Lane", "Purple", 160), ("Hove Station", "Station", 200),
            ("Bishop Drive", "Orange", 180), ("Pot Luck", None, None),
            ("Dunham Street", "Orange", 180), ("Broyles Lane", "Orange", 200), ("Free Parking", None, None),
            # Top row (right to left)
            ("Yue Fei Square", "Red", 220), ("Opportunity Knocks", None, None),
            ("Mulan Rouge", "Red", 220), ("Han Xin Gardens", "Red", 240), ("Falmer Station", "Station", 200),
            ("Shatner Close", "Yellow", 260), ("Picard Avenue", "Yellow", 260),
            ("Edison Water", "Utilities", 150), ("Crusher Creek", "Yellow", 280), ("Go to Jail", None, None),
            # Right column (top to bottom)
            ("Sirat Mews", "Green", 300), ("Ghengis Crescent", "Green", 300),
            ("Pot Luck", None, None), ("Ibis Close", "Green", 320), ("Portslade Station", "Station", 200),
            ("Opportunity Knocks", None, None), ("James Webb Way", "Deep blue", 350),
            ("Super Tax", None, None), ("Turing Heights", "Deep blue", 400)
        ]

        spaces = []
        exact_tile_size = self.board_size / 11  # tile sizes

        # Bottom row (left to right)
        for i in range(11):
            spaces.append(SpacesGUI(
                pygame.Rect(
                    self.board_offset_x + (self.board_size - (i + 1) * exact_tile_size),  # X position
                    self.board_offset_y + self.board_size - exact_tile_size,              # Y position
                    exact_tile_size, exact_tile_size),
                board_layout[i][0], board_layout[i][1], "bottom", board_layout[i][2]))

        # Left column (bottom to top)
        for i in range(1, 10):
            spaces.append(SpacesGUI(
                pygame.Rect(
                    self.board_offset_x,  # Fixed X position (left edge)
                    self.board_offset_y + self.board_size - ((i + 1) * exact_tile_size),  # Increasing Y
                    exact_tile_size, exact_tile_size),
                board_layout[i + 10][0], board_layout[i + 10][1], "left", board_layout[i + 10][2]))

        # Top row (right to left)
        for i in range(11):
            spaces.append(SpacesGUI(
                pygame.Rect(
                    self.board_offset_x + (i * exact_tile_size),  # X increases left to right
                    self.board_offset_y,  # Top edge
                    exact_tile_size, exact_tile_size),
                board_layout[i + 20][0], board_layout[i + 20][1], "top", board_layout[i + 20][2]))

        # Right column (top to bottom)
        for i in range(1, 10):
            spaces.append(SpacesGUI(
                pygame.Rect(
                    self.board_offset_x + self.board_size - exact_tile_size,  # Right edge
                    self.board_offset_y + (i * exact_tile_size),              # Y increases downward
                    exact_tile_size, exact_tile_size),
                board_layout[i + 30][0], board_layout[i + 30][1], "right", board_layout[i + 30][2]))

        return spaces

    def draw(self, screen):
        """
        Draws all the board spaces on the screen, and shows popups if the mouse hovers
        over a space.

        Parameters:
        screen (pygame.Surface): The game window or surface where board elements will be drawn.
        """
        # Coordinates and size for a dice roll button (used by popup)
        dice_button_x = self.window_width // 2 - 75  
        dice_button_y = self.window_height - 100  
        dice_button_width = 150

        # Draw each space and its popup (if hovered)
        for space in self.spaces:
            space.draw(screen)
            space.draw_popup(screen, dice_button_x, dice_button_y, dice_button_width)

    def handle_hover(self, mouse_pos):
        """
        Checks if the mouse is hovering over any space and highlights it.

        Parameters:
        mouse_pos (tuple): The current position of the mouse (x, y).
        """
        for space in self.spaces:
            # If the mouse is over the space, highlight it
            if space.rect.collidepoint(mouse_pos):
                space.set_highlight(True)
            else:
                space.set_highlight(False)
