import pygame
import os
import random

class TokenSelectionScreen:
    """
    This class manages the token selection screen where players choose their game pieces (tokens).
    It handles rendering the available tokens, confirming selections, and assigning random tokens to AI players.
    """

    def __init__(self, screen, human_players, ai_players):
        """
        Initializes the screen layout, available tokens, and player data.

        Parameters:
        screen (pygame.Surface): The main game display surface.
        human_players (int): Number of human players.
        ai_players (int): Number of AI players.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, 36)

        self.allowed_tokens = ["boot", "cat", "hatstand", "iron", "smartphone"]  # Allowed token names

        self.assets_folder = "assets"
        self.token_images = self.load_token_images()  # Load images from folder
        self.available_tokens = [token for token in self.allowed_tokens if token in self.token_images]

        self.human_players = human_players
        self.ai_players = ai_players
        self.total_players = human_players + ai_players

        self.selected_tokens = {}       # Maps player number → token name
        self.confirmed_players = set()  # Players who have locked in their choice
        self.current_player = 1         # Start with Player 1
        self.selected_token = None      # Currently hovered or selected token

        # Confirm/Start button
        self.confirm_button_rect = pygame.Rect(self.width // 2 - 75, self.height - 100, 150, 50)

        # Sound effect for interaction
        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("assets/click.wav")

        # Background image
        self.background = pygame.image.load("assets/background.png")
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

    def load_token_images(self):
        """
        Loads and scales token images from the assets folder.

        Returns:
        dict: token_name → pygame.Surface (image)
        """
        token_images = {}
        for file in os.listdir(self.assets_folder):
            if file.endswith(".png"):
                token_name = file.split(".")[0].lower()
                if token_name in self.allowed_tokens:
                    img = pygame.image.load(os.path.join(self.assets_folder, file))
                    img = pygame.transform.scale(img, (80, 80))  # Resize for uniform display
                    token_images[token_name] = img
        return token_images

    def draw(self):
        """
        Renders the token selection screen: background, title, token choices, selected list, and buttons.
        """
        self.screen.blit(self.background, (0, 0))

        # Dark overlay for better text readability
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Title prompt for current player
        title_text = self.font.render(f"Player {self.current_player}, select your token:", True, (255, 255, 255))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 50))

        # Display all token images
        x_start, y_start = 100, 150
        x_offset, y_offset = 120, 120
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for index, token in enumerate(self.allowed_tokens):
            x = x_start + (index * x_offset)
            y = y_start
            token_rect = pygame.Rect(x, y, 80, 80)

            # Highlight if hovered and not taken
            if token_rect.collidepoint(mouse_x, mouse_y) and token not in self.selected_tokens.values():
                pygame.draw.rect(self.screen, (255, 255, 0), token_rect, 4)

            # Draw image and border
            self.screen.blit(self.token_images[token], (x, y))
            pygame.draw.rect(self.screen, (255, 255, 255), token_rect, 2)

            # Red border if selected by current player
            if self.selected_tokens.get(self.current_player) == token:
                pygame.draw.rect(self.screen, (255, 0, 0), token_rect, 3)

        # List of selected tokens (with confirmation checkmarks)
        y_selected_start = 300
        selected_text = self.font.render("Selected Tokens:", True, (255, 255, 255))
        self.screen.blit(selected_text, (100, y_selected_start))

        for player, token in self.selected_tokens.items():
            confirmed_status = "✔" if player in self.confirmed_players else ""
            token_text = self.font.render(f"Player {player}: {token} {confirmed_status}", True, (255, 255, 255))
            self.screen.blit(token_text, (100, y_selected_start + player * 30))

        # Show confirm or start button based on selection status
        if self.selected_tokens.get(self.current_player) and self.current_player not in self.confirmed_players:
            self.highlight_button(self.confirm_button_rect, (200, 0, 0), "Confirm")

        if len(self.confirmed_players) == self.total_players:
            self.highlight_button(self.confirm_button_rect, (0, 200, 0), "Start Game")

        pygame.display.flip()

    def handle_event(self, event):
        """
        Handles mouse events to select tokens or confirm/start the game.

        Parameters:
        event (pygame.event.Event): Event from Pygame's event loop.

        Returns:
        str or None: Returns "confirmed" if player confirms selection, else None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            self.click_sound.play()

            # Check for token selection
            x_start, y_start = 100, 150
            x_offset = 120

            for index, token in enumerate(self.allowed_tokens):
                token_x = x_start + (index * x_offset)
                token_y = y_start
                token_rect = pygame.Rect(token_x, token_y, 80, 80)

                if token_rect.collidepoint(x, y):
                    self.select_token(token)
                    return

            # Confirm or start
            if self.confirm_button_rect.collidepoint(x, y):
                if self.current_player not in self.confirmed_players:
                    self.confirm_selection()
                    return "confirmed"

        return None

    def select_token(self, token):
        """
        Selects a token for the current player (if available).

        Parameters:
        token (str): Token name to assign.
        """
        if token in self.allowed_tokens and token not in self.selected_tokens.values():
            self.selected_tokens[self.current_player] = token

    def confirm_selection(self):
        """
        Confirms current player's selection and advances to next player or assigns AI tokens.
        """
        if self.current_player in self.confirmed_players:
            return  # Skip if already confirmed

        if self.selected_tokens.get(self.current_player):
            self.confirmed_players.add(self.current_player)

            if self.current_player < self.human_players:
                self.current_player += 1
            else:
                self.assign_ai_tokens()  # All human players confirmed

    def assign_ai_tokens(self):
        """
        Randomly assigns tokens to AI players from remaining available options.
        """
        ai_start = self.human_players + 1
        for ai_player in range(ai_start, self.total_players + 1):
            remaining_tokens = set(self.allowed_tokens) - set(self.selected_tokens.values())
            if remaining_tokens:
                random_token = random.choice(list(remaining_tokens))
                self.selected_tokens[ai_player] = random_token
                self.confirmed_players.add(ai_player)

    def get_selected_tokens(self):
        """
        Returns:
        dict: A mapping of player number → selected token name.
        """
        return self.selected_tokens

    def highlight_button(self, button_rect, color, text):
        """
        Draws a button with hover effect and centered text.

        Parameters:
        button_rect (pygame.Rect): Button area.
        color (tuple): Default background color.
        text (str): Label to display on the button.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_x, mouse_y)

        button_color = (255, 100, 100) if is_hovered else color

        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
        button_text = pygame.font.Font(None, 28).render(text, True, (255, 255, 255))
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)
