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
    A class responsible for initializing and drawing the main board layout in the game.
    This includes all 40 spaces (tiles) arranged around the square board, each with its label,
    color group, and cost.
    """

    def __init__(self, board_size=750, window_width=1200, window_height=750, csv_path=None):
        """
        Initialize the board's dimensions, position, tile size, and the list of space objects.

        Parameters:
        - board_size (int): The width and height of the board square.
        - window_width (int): Width of the full game window.
        - window_height (int): Height of the full game window.
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
        if not csv_path:
            csv_path = os.path.join("data", "PropertyTycoonBoardData.csv")  
        return load_board_data_from_csv(csv_path)

from GuiElements.spaces_gui import SpacesGUI
import csv
import os

import pandas as pd

class BoardGUI:
    def __init__(self, board_size=750, window_width=1200, window_height=750, csv_path=None):
        self.board_size = board_size
        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = self.board_size // 11
        self.board_offset_x = (self.window_width - self.board_size) // 2
        self.board_offset_y = 0

        self.board_data = self.load_board_data(csv_path) if csv_path else None
        self.spaces = self.initialize_spaces()

    def load_board_data(self, csv_path):
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
        Draw the board and all its spaces, including tooltips for hovered tiles.

        Parameters:
        - screen: The main pygame display surface.
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
        Update highlighting on board spaces based on current mouse position.

        Parameters:
        - mouse_pos: Tuple representing the current (x, y) position of the mouse.
        """
        for space in self.spaces:
            space.set_highlight(space.rect.collidepoint(mouse_pos))
