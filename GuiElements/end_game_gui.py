import pygame
import sys

class EndGamePopup:
    """
    Handles the display of the end game popup, showing the winner and providing an option to quit the game.

    This class is responsible for rendering the end game popup window on the screen when the game is over.
    It displays the winner's name, a message indicating the game is over, and provides a "Quit" button to close the game.

    Args:
        screen (pygame.Surface): The Pygame surface where the popup will be drawn.
        winner_name (str): The name of the player who won the game.

    Attributes:
        width (int): Width of the game window.
        height (int): Height of the game window.
        popup_width (int): Width of the popup window.
        popup_height (int): Height of the popup window.
        popup_rect (pygame.Rect): The rectangle defining the position and size of the popup.
        font_title (pygame.font.Font): The font used for the title text.
        font_body (pygame.font.Font): The font used for the body text (winner's name).
        font_button (pygame.font.Font): The font used for the button text.
        quit_button (pygame.Rect): The rectangle defining the "Quit" button's position and size.

    Methods:
        draw():
            Renders the popup on the screen with the winner's name and a "Quit" button.

        handle_event(event):
            Handles events such as mouse clicks. If the "Quit" button is clicked, the game is exited.
    """
    def __init__(self, screen, winner_name):
        """
        Initializes the end game popup with the winner's name and necessary parameters for drawing.

        Args:
            screen (pygame.Surface): The Pygame surface where the popup will be drawn.
            winner_name (str): The name of the player who won the game.

        Returns:
            None

        Raises:
            None

        Side Effects:
            Initializes the popup's position, size, and fonts. Creates a button for quitting the game.
        """    
        self.screen = screen
        self.winner_name = winner_name
        self.visible = True

        self.width, self.height = self.screen.get_size()
        self.popup_width = 400
        self.popup_height = 220
        self.popup_rect = pygame.Rect(
            self.width // 2 - self.popup_width // 2,
            self.height // 2 - self.popup_height // 2,
            self.popup_width,
            self.popup_height
        )

        self.font_title = pygame.font.Font(None, 48)
        self.font_body = pygame.font.Font(None, 32)
        self.font_button = pygame.font.Font(None, 30)

        self.quit_button = pygame.Rect(self.popup_rect.centerx - 60, self.popup_rect.y + 150, 120, 40)

    def draw(self):
        """
        Draws the end game popup with the winner's message and a "Quit" button.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            Renders the popup window on the screen, including the title, winner's name, and the "Quit" button.
            The appearance of the popup is determined by the screen dimensions and the winner's name.
        """
        if not self.visible:
            return

        pygame.draw.rect(self.screen, (40, 40, 40), self.popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.popup_rect, 3, border_radius=10)

        title_surf = self.font_title.render("🎉 Game Over!", True, (255, 255, 255))
        self.screen.blit(title_surf, (self.popup_rect.centerx - title_surf.get_width() // 2, self.popup_rect.y + 20))

        winner_msg = f"{self.winner_name} Wins!"
        winner_surf = self.font_body.render(winner_msg, True, (255, 215, 0))
        self.screen.blit(winner_surf, (self.popup_rect.centerx - winner_surf.get_width() // 2, self.popup_rect.y + 80))

        pygame.draw.rect(self.screen, (200, 0, 0), self.quit_button, border_radius=6)
        quit_surf = self.font_button.render("Quit", True, (255, 255, 255))
        self.screen.blit(quit_surf, (self.quit_button.centerx - quit_surf.get_width() // 2, self.quit_button.y + 8))

    def handle_event(self, event):
        """
        Handles user input events for the end game popup.

        Args:
            event (pygame.event): The Pygame event to process (e.g., mouse click).

        Returns:
            None

        Raises:
            None

        Side Effects:
            If the "Quit" button is clicked, the game will exit by calling `pygame.quit()` and `sys.exit()`.
        """
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()


        

        
        