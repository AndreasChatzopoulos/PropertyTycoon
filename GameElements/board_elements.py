import pygame

class BoardElementsGUI:
    """
    Manages and renders static visual elements on the Monopoly game board.

    This includes:
    - The "Pot Luck" and "Opportunity Knocks" icons, which are placed at fixed positions.
    - A stylized two-line title ("Property Tycoon") with a shadow effect for visual appeal.

    Designed to be used with a Pygame screen surface passed during initialization.

    Args:
        screen (pygame.Surface): The Pygame display surface where the board elements will be drawn.

    Attributes:
        pot_luck_img (pygame.Surface): Scaled image representing the Pot Luck card icon.
        opportunity_knocks_img (pygame.Surface): Scaled image representing the Opportunity Knocks card icon.
        pot_luck_pos (tuple): Fixed (x, y) position for the Pot Luck icon.
        opportunity_knocks_pos (tuple): Fixed (x, y) position for the Opportunity Knocks icon.
        title_font (pygame.Font): Font used for the board's title text.
        title_color (tuple): RGB color for the main title text.
        shadow_color (tuple): RGB color used to create a shadow effect under the title.
    """

    def __init__(self, screen):
        """
        Initialize the baord GUI elements, including special icons and title configuration. 

        Loads and scales the Pot Luck and Opportunity Knocks images, sets their positions on the board,
        and prepares the font and colour settings for the game title. 

        Args:
        - screen (pygame.surface) the main pygame display surface where elements will be rendered.
        """
        self.screen = screen

        # Load and scale special card images
        self.pot_luck_img = pygame.image.load("assets/potofgold.png")
        self.opportunity_knocks_img = pygame.image.load("assets/opportunityknocks.png")

        self.pot_luck_img = pygame.transform.scale(self.pot_luck_img, (100, 100))
        self.opportunity_knocks_img = pygame.transform.scale(self.opportunity_knocks_img, (100, 100))

        # Define fixed positions
        self.pot_luck_pos = (325, 100)
        self.opportunity_knocks_pos = (775, 550)

        # Title configuration
        self.title_font = pygame.font.Font(None, 64)  
        self.title_color = (255, 255, 255)            
        self.shadow_color = (0, 0, 0)                 

    def draw(self):
        """
        Draw all board elements, including:
        - Pot Luck and Opportunity Knocks icons positioned at predefined co-ordinates.
        - A two-line, centered stylized title "Property Tycoon" with shadow effect.
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

            text_rect = rendered_text.get_rect(center=(center_x, start_y + i * 50))
            self.screen.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2)) 
            self.screen.blit(rendered_text, text_rect)  