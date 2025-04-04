import pygame
import pandas as pd
import csv
import os

from GuiElements.spaces_gui import SpacesGUI



def load_board_data_from_csv(csv_path):
    df = pd.read_csv(csv_path, encoding="ISO-8859-1", skiprows=3)
    df = df.rename(columns={
        df.columns[0]: "Position",
        df.columns[1]: "Name",
        df.columns[3]: "Group",
        df.columns[7]: "Price",
    })

    df = df[["Position", "Name", "Group", "Price"]]
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")  # Convert to int/NaN
    df["Group"] = df["Group"].fillna(None)
    return df.to_dict(orient="records")


class BoardGUI:
    """
    Manages the layout and rendering of the Monopoly-style game board.

    This class handles the loading of board data from a CSV file, calculates the positions of all
    40 spaces (tiles), and handles drawing them onto the screen. It also handles user interaction 
    such as tile highlighting on hover and dynamic property information display.

    Args:
        board_size (int): Width and height of the square board in pixels.
        window_width (int): Width of the game window in pixels.
        window_height (int): Height of the game window in pixels.
        csv_path (str, optional): Path to the CSV file containing board space data.

    Attributes:
        tile_size (int): Calculated size of individual tiles on the board.
        board_offset_x (int): X-offset to center the board on the screen.
        board_offset_y (int): Y-offset for the board (usually 0).
        board_data (list): Parsed board space data loaded from CSV.
        spaces (list): List of `SpacesGUI` objects representing board tiles.
    """

    def __init__(self, board_size=750, window_width=1200, window_height=750, csv_path=None):
        """
        Initializes board layout configuration and loads board data.

        Args:
            board_size (int): Size (width/height) of the square board in pixels.
            window_width (int): Width of the game window.
            window_height (int): Height of the game window.
            csv_path (str, optional): Path to the CSV file containing tile definitions.
        """
        self.board_size = board_size
        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = self.board_size // 11
        self.board_offset_x = (self.window_width - self.board_size) // 2
        self.board_offset_y = 0
        self.board_data = self.load_board_data(csv_path)
        self.spaces = self.initialize_spaces()

    def load_board_data(self, csv_path):
        """
        Loads and processes board tile data from a CSV file.

        Args:
            csv_path (str): Path to the board CSV file.

        Returns:
            list[dict]: A list of dictionaries with keys "Position", "Name", "Group", and "Price".
        """
        if not csv_path:
            csv_path = os.path.join("data", "PropertyTycoonBoardData.csv")  
        return load_board_data_from_csv(csv_path)

class BoardGUI:
    def __init__(self, board_size=750, window_width=1200, window_height=750, csv_path=None):
        """
        Initializes the board layout configuration and loads board data from a CSV file.

        Args:
            board_size (int): The width and height of the square board in pixels. Default is 750.
            window_width (int): The width of the game window in pixels. Default is 1200.
            window_height (int): The height of the game window in pixels. Default is 750.
            csv_path (str, optional): Path to the CSV file containing the board space data. If not provided, default data is used.

        Returns:
            None

        Raises:
            FileNotFoundError: If the CSV file is not found at the provided path.
            ValueError: If the CSV data is malformed.
        """
        self.board_size = board_size
        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = self.board_size // 11
        self.board_offset_x = (self.window_width - self.board_size) // 2
        self.board_offset_y = 0

        self.board_data = self.load_board_data(csv_path) if csv_path else None
        self.spaces = self.initialize_spaces()

    def load_board_data(self, csv_path):
        """
        Loads and processes board tile data from a CSV file.

        Args:
            csv_path (str): The path to the board CSV file containing space data.

        Returns:
            list[dict]: A list of dictionaries containing data for each board space. Each dictionary contains:
                - "Position": Integer representing the position of the tile on the board.
                - "Name": Name of the property or space.
                - "Group": The color group to which the property belongs (if applicable).
                - "Price": Price of the property, or NaN if not a property.

        Raises:
            FileNotFoundError: If the specified CSV file does not exist at the given path.
            ValueError: If there are errors parsing the CSV file.
        """
        df = pd.read_csv(csv_path, encoding="ISO-8859-1", skiprows=3)
        df = df.rename(columns={
            df.columns[0]: "Position",
            df.columns[1]: "Name",
            df.columns[3]: "Group",
            df.columns[7]: "Price",
        })

        df = df[["Position", "Name", "Group", "Price"]]
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Group"] = df["Group"].where(pd.notnull(df["Group"]), None)
        return df.to_dict(orient="records")



    def initialize_spaces(self):
        """
        Initializes the board spaces based on the loaded board data.

        Args:
            None

        Returns:
            list: A list of `SpacesGUI` objects, each representing a space on the board with its associated properties (name, group, price, etc.).

        Raises:
            IndexError: If there is an issue with the index when iterating through the space data.
        """
        data = self.board_data
        exact_tile_size = self.board_size / 11
        spaces = []

        for i in range(40):
            info = data[i]
            name = info["Name"]
            group = info["Group"]
            price = info["Price"]
            if i <= 10:
                orientation = "bottom"
                x = self.board_offset_x + (self.board_size - (i + 1) * exact_tile_size)
                y = self.board_offset_y + self.board_size - exact_tile_size
            elif 11 <= i <= 20:
                orientation = "left"
                x = self.board_offset_x
                y = self.board_offset_y + self.board_size - ((i - 10 + 1) * exact_tile_size)
            elif 21 <= i <= 30:
                orientation = "top"
                x = self.board_offset_x + ((i - 20) * exact_tile_size)
                y = self.board_offset_y
            else:
                orientation = "right"
                x = self.board_offset_x + self.board_size - exact_tile_size
                y = self.board_offset_y + ((i - 30) * exact_tile_size)

            rect = pygame.Rect(x, y, exact_tile_size, exact_tile_size)
            spaces.append(SpacesGUI(rect, name, group, orientation, price))

        return spaces


    # change here
    def draw(self, screen, prop_data):
        """
        Draws the board and all its spaces onto the screen, including tooltips for hovered tiles.

        Args:
            screen (pygame.Surface): The main display surface where the board will be drawn.
            prop_data (list): A list of property data used to display dynamic information for each property, including rent, owner, and houses.

        Returns:
            None

        Raises:
            ValueError: If the property data is not in the expected format or contains invalid information.
        """

        # These button values should match your DiceGUI logic
        dice_button_x = self.window_width // 2 - 75
        dice_button_y = self.window_height - 100
        dice_button_width = 150

        prop_data = [p[1] for p in prop_data]
        for space in self.spaces:
            space.draw(screen)
            rent = next((prop.rent for prop in prop_data if prop.name == space.name), None)
            owner = next((prop.owner for prop in prop_data if prop.name == space.name), None)
            houses = next((prop.houses for prop in prop_data if prop.name == space.name), None)
            if rent:
                rent = rent[houses]
            if owner:
                owner = owner.name
            space.draw_popup(screen, dice_button_x, dice_button_y, dice_button_width, rent, owner)

    def handle_hover(self, mouse_pos):
        """
        Updates the highlighting of board spaces based on the current mouse position.

        Args:
            mouse_pos (tuple): A tuple representing the current (x, y) position of the mouse on the screen.

        Returns:
            None

        Raises:
            ValueError: If the mouse position is invalid or not within the bounds of the window.
        """
        for space in self.spaces:
            space.set_highlight(space.rect.collidepoint(mouse_pos))
