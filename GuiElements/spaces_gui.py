import pygame
import pandas as pd

class SpacesGUI:
    """
    Represents a single space (tile) on the board with visual rendering,
    highlighting, and optional pop-up info like name, price, rent, and owner.

    Args:
        rect (pygame.Rect): Position and size of the tile on the board.
        name (str): Name of the space (e.g., "Old Kent Road").
        color (str): Property group color (e.g., "Brown", "Red").
        orientation (str): Edge of board where the tile sits ("top", "bottom", "left", "right").
        price (int, optional): Purchase price for property-type spaces.

    Attributes:
        rect (pygame.Rect): Rectangle representing the tile's position and size.
        name (str): Name of the space.
        color (str): The color group of the property (e.g., "Brown", "Red").
        orientation (str): Edge of the board where the tile sits.
        price (int, optional): Purchase price for the property space.
        owner (str): The name of the owner of the property or "Unowned".
        highlighted (bool): Whether the space is highlighted or not.
        rent (int, optional): Rent value calculated as 10% of the price.
        property_colors (dict): A dictionary mapping property group names to color values.
    """

    def __init__(self, rect, name, color, orientation, price=None):
        """
        Initializes a board space with display properties.

        Args:
            rect (pygame.Rect): Position and size of the tile.
            name (str): Name of the space (e.g., "Old Kent Road").
            color (str): Property group color (e.g., "Brown", "Red").
            orientation (str): Edge of board where the tile sits ("top", "bottom", "left", "right").
            price (int, optional): Purchase price for property-type spaces.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Sets initial properties for the space such as position, name, color, rent, and owner.
        """
        self.rect = rect
        self.name = name
        self.color = color
        self.orientation = orientation
        self.price = price
        self.owner = "Unowned"  
        self.highlighted = False  

        self.rent = int(self.price * 0.1) if isinstance(self.price, (int, float)) and not pd.isna(self.price) else None


        self.property_colors = {
            "Brown": (139, 69, 19), "Blue": (135, 206, 250), "Purple": (128, 0, 128),
            "Orange": (255, 165, 0), "Red": (255, 0, 0), "Yellow": (255, 255, 0),
            "Green": (0, 255, 0), "Deep blue": (0, 0, 139),
            "Station": (255, 255, 255), "Utilities": (255, 255, 255),
            "Take card": (255, 255, 255)
        }

    def draw(self, screen):
        """
        Renders the board space, name, and color band.

        Args:
            screen (pygame.Surface): The main game screen to render to.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Draws the space with its background, borders, and color bar depending on the orientation.
            - Renders the space's name (split across lines if necessary).
            - Highlights the space if `highlighted` is `True`.
        """
        # Draw background and border
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        color_bar_size = self.rect.height // 7
        if self.color and self.color in self.property_colors:
            color_value = self.property_colors[self.color]
            if self.orientation == "top":
                pygame.draw.rect(screen, color_value, (self.rect.x, self.rect.y + self.rect.height - color_bar_size, self.rect.width, color_bar_size))
            elif self.orientation == "bottom":
                pygame.draw.rect(screen, color_value, (self.rect.x, self.rect.y, self.rect.width, color_bar_size))
            elif self.orientation == "left":
                pygame.draw.rect(screen, color_value, (self.rect.x + self.rect.width - color_bar_size, self.rect.y, color_bar_size, self.rect.height))
            elif self.orientation == "right":
                pygame.draw.rect(screen, color_value, (self.rect.x, self.rect.y, color_bar_size, self.rect.height))

        font_size = int(self.rect.height * 0.22)
        font = pygame.font.Font(None, font_size)

        words = self.name.split()
        line1, line2, line3 = (words + ["", ""])[:3] 

        text_surface1 = font.render(line1, True, (0, 0, 0))
        text_surface2 = font.render(line2, True, (0, 0, 0))
        text_surface3 = font.render(line3, True, (0, 0, 0)) if line3 else None

        text_rect1 = text_surface1.get_rect(center=(self.rect.centerx, self.rect.centery - font_size))
        text_rect2 = text_surface2.get_rect(center=(self.rect.centerx, self.rect.centery))
        text_rect3 = text_surface3.get_rect(center=(self.rect.centerx, self.rect.centery + font_size)) if text_surface3 else None

        screen.blit(text_surface1, text_rect1)
        screen.blit(text_surface2, text_rect2)
        if text_surface3:
            screen.blit(text_surface3, text_rect3)

        if self.highlighted:
            pygame.draw.rect(screen, (255, 255, 0), self.rect, 4)

    def set_highlight(self, highlight=True):
        """
        Enables or disables a visual highlight on the space.

        Args:
            highlight (bool): True to highlight, False to remove highlight.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Sets the `highlighted` attribute of the space to True or False.
            - Modifies the visual appearance of the space by highlighting or unhighlighting it.
        """
        self.highlighted = highlight

    def draw_popup(self, screen, dice_button_x, dice_button_y, dice_button_width, rent, owner):
        """
        Renders a pop-up box with property details when highlighted.

        Args:
            screen (pygame.Surface): Pygame screen to draw to.
            dice_button_x (int): X-coordinate of the dice button (used for popup alignment).
            dice_button_y (int): Y-coordinate of the dice button.
            dice_button_width (int): Width of the dice button.
            rent (int, optional): Rent value of the property.
            owner (str): Name of the property owner.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Renders a pop-up displaying the name, price, rent, and owner of the property if it is highlighted.
        """
        if self.highlighted and self.is_property:
            popup_width, popup_height = 250, 140
            popup_x = dice_button_x + (dice_button_width // 2) - (popup_width // 2)
            popup_y = dice_button_y - popup_height - 10

            popup_x = max(10, min(popup_x, screen.get_width() - popup_width - 10))

            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
            pygame.draw.rect(screen, (240, 240, 240), popup_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)

            font = pygame.font.Font(None, 28)
            text_name = font.render(self.name, True, (0, 0, 0))
            text_price = font.render(f"Price: ${self.price}", True, (0, 0, 0))
            text_rent = font.render(f"Rent: ${rent}", True, (0, 0, 0)) if self.rent else None
            text_owner = font.render(f"Owner: {owner}", True, (0, 0, 0))

            screen.blit(text_name, (popup_x + 10, popup_y + 10))
            screen.blit(text_price, (popup_x + 10, popup_y + 40))
            if text_rent:
                screen.blit(text_rent, (popup_x + 10, popup_y + 65))
            screen.blit(text_owner, (popup_x + 10, popup_y + 90))

     
    @property
    def is_property(self):
        """
        Checks if the space is a property space.

        Args:
            None

        Returns:
            bool: True if the space has a price (indicating it is a property space), False otherwise.

        Raises:
            None

        Side Effects:
            - Returns whether the space qualifies as a property space based on the presence of a price value.
        """
        return isinstance(self.price, (int, float)) and not pd.isna(self.price)


