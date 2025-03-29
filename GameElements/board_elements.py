import pygame

class BoardElementsGUI:
    """
    A class to manage static visual elements on the game board, including special card icons
    and the main game title. Designed for use with a pygame screen.
    """

    def __init__(self, screen):
        """
        Initialize the GUI elements.

        Parameters:
        - screen: the main pygame display surface where elements will be drawn.
        """
        self.screen = screen

        # Load and scale special card images
        self.pot_luck_img = pygame.image.load("assets/potofgold.png")
        self.opportunity_knocks_img = pygame.image.load("assets/opportunityknocks.png")

        self.pot_luck_img = pygame.transform.scale(self.pot_luck_img, (100, 100))
        self.opportunity_knocks_img = pygame.transform.scale(self.opportunity_knocks_img, (100, 100))

        # Define fixed positions for the card images on the board
        self.pot_luck_pos = (325, 100)
        self.opportunity_knocks_pos = (775, 550)

        # Title configuration
        self.title_font = pygame.font.Font(None, 64)  # Large font for title
        self.title_color = (255, 255, 255)            # White text
        self.shadow_color = (0, 0, 0)                 # Black shadow for contrast

    def draw(self):
        """
        Draw all board elements, including:
        - Pot Luck and Opportunity Knocks icons.
        - A stylized title "Property Tycoon" with shadow effect.
        """
        # Draw special card icons at their defined positions
        self.screen.blit(self.pot_luck_img, self.pot_luck_pos)
        self.screen.blit(self.opportunity_knocks_img, self.opportunity_knocks_pos)

        # Draw the game title centered on screen with a drop shadow
        center_x = self.screen.get_width() // 2
        start_y = 180  # Vertical position of the first title line

        title_lines = ["Property", "Tycoon"]  # Split title into two lines for visual balance

        for i, line in enumerate(title_lines):
            rendered_text = self.title_font.render(line, True, self.title_color)
            shadow_text = self.title_font.render(line, True, self.shadow_color)

            # Center text and apply a slight shadow offset for 3D look
            text_rect = rendered_text.get_rect(center=(center_x, start_y + i * 50))
            self.screen.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))  # Shadow
            self.screen.blit(rendered_text, text_rect)  # Main text