import pygame  # Import the Pygame library, which is used for making games and multimedia applications

class BoardElementsGUI:
    """
    This class is responsible for displaying static board elements (images)
    on the game screen using Pygame.
    It displays:
    - A 'Pot Luck' image
    - An 'Opportunity Knocks' image

    These images are displayed at fixed positions on the screen and can be updated or extended later.
    """

    def __init__(self, screen):
        """
        Initializes the board elements and prepares them for drawing.

        Parameters:
        screen (pygame.Surface): The game window or surface where elements will be drawn.
        """
        self.screen = screen  # Store the reference to the screen so we can draw images on it

        # Load the 'Pot Luck' image from the file system.
        # Make sure the file path is correct and that the image is in the 'assets' folder.
        self.pot_luck_img = pygame.image.load("assets/potofgold.png")

        # Load the 'Opportunity Knocks' image from the file system.
        self.opportunity_knocks_img = pygame.image.load("assets/opportunityknocks.png")

        # Resize both images to 100x100 pixels to fit nicely on the board.
        self.pot_luck_img = pygame.transform.scale(self.pot_luck_img, (100, 100))
        self.opportunity_knocks_img = pygame.transform.scale(self.opportunity_knocks_img, (100, 100))

        # Define fixed positions (in pixels) where these images will appear on the screen.
        # These are (x, y) coordinates from the top-left of the screen.
        self.pot_luck_pos = (325, 100)  # Position for 'Pot Luck'
        self.opportunity_knocks_pos = (775, 550)  # Position for 'Opportunity Knocks'

    def draw(self):
        """
        Draws the board elements (images) onto the screen.
        This should be called every frame in the main game loop after screen.fill().
        """
        # Blit (draw) the 'Pot Luck' image at its specified position
        self.screen.blit(self.pot_luck_img, self.pot_luck_pos)

        # Blit (draw) the 'Opportunity Knocks' image at its specified position
        self.screen.blit(self.opportunity_knocks_img, self.opportunity_knocks_pos)
