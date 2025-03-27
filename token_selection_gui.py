import pygame
import os
import random

class TokenSelectionScreen:
    """
    Provides an interactive interface for human players to select their tokens.
    Automatically assigns tokens to AI players once human selections are confirmed.
    """

    def __init__(self, screen, human_players, ai_players):
        """
        Initialize the selection screen.

        Args:
            screen (pygame.Surface): The main game screen to render UI on.
            human_players (int): Number of human players.
            ai_players (int): Number of AI players.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, 36)

        # Allowed token names (must match filenames in assets folder)
        self.allowed_tokens = ["boot", "cat", "hatstand", "iron", "smartphone"]

        self.assets_folder = "assets"
        self.token_images = self.load_token_images()
        self.available_tokens = [t for t in self.allowed_tokens if t in self.token_images]

        self.human_players = human_players
        self.ai_players = ai_players
        self.total_players = human_players + ai_players

        # Tracks selected tokens and which players have confirmed
        self.selected_tokens = {}
        self.confirmed_players = set()

        self.current_player = 1
        self.selected_token = None

        # Confirm/start button rectangle
        self.confirm_button_rect = pygame.Rect(self.width // 2 - 75, self.height - 100, 150, 50)

        # Sound effects
        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("assets/click.wav")

        # Background
        self.background = pygame.image.load("assets/background.png")
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

    def load_token_images(self):
        """
        Load token images from the assets folder.

        Returns:
            dict: token_name -> pygame.Surface
        """
        token_images = {}
        for file in os.listdir(self.assets_folder):
            if file.endswith(".png"):
                token_name = file.split(".")[0].lower()
                if token_name in self.allowed_tokens:
                    img = pygame.image.load(os.path.join(self.assets_folder, file))
                    img = pygame.transform.scale(img, (80, 80))
                    token_images[token_name] = img
        return token_images

    def draw(self):
        """
        Render the token selection interface, including available tokens,
        current player, and confirm/start button.
        """
        self.screen.blit(self.background, (0, 0))

        # Semi-transparent overlay for better contrast
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font.render(f"Player {self.current_player}, select your token:", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Token buttons
        x_start, y_start = 100, 150
        x_offset = 120
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for index, token in enumerate(self.allowed_tokens):
            x = x_start + index * x_offset
            token_rect = pygame.Rect(x, y_start, 80, 80)

            # Highlight if hovering and not already selected
            if token_rect.collidepoint(mouse_x, mouse_y) and token not in self.selected_tokens.values():
                pygame.draw.rect(self.screen, (255, 255, 0), token_rect, 4)

            self.screen.blit(self.token_images[token], (x, y_start))
            pygame.draw.rect(self.screen, (255, 255, 255), token_rect, 2)

            # Show if selected
            if self.selected_tokens.get(self.current_player) == token:
                pygame.draw.rect(self.screen, (255, 0, 0), token_rect, 3)

        # Display selected tokens
        y_selected = 300
        label = self.font.render("Selected Tokens:", True, (255, 255, 255))
        self.screen.blit(label, (100, y_selected))

        for player, token in self.selected_tokens.items():
            confirmed = "✔" if player in self.confirmed_players else ""
            text = self.font.render(f"Player {player}: {token} {confirmed}", True, (255, 255, 255))
            self.screen.blit(text, (100, y_selected + player * 30))

        # Confirm or Start button
        if self.current_player not in self.confirmed_players and self.selected_tokens.get(self.current_player):
            self.highlight_button(self.confirm_button_rect, (200, 0, 0), "Confirm")
        elif len(self.confirmed_players) == self.total_players:
            self.highlight_button(self.confirm_button_rect, (0, 200, 0), "Start Game")

        pygame.display.flip()

    def handle_event(self, event):
        """
        Handle mouse clicks on tokens and buttons.

        Args:
            event (pygame.Event): Event to handle.

        Returns:
            str or None: "confirmed" if all players selected, else None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            self.click_sound.play()

            # Check for token selection
            for i, token in enumerate(self.allowed_tokens):
                token_rect = pygame.Rect(100 + i * 120, 150, 80, 80)
                if token_rect.collidepoint(x, y):
                    self.select_token(token)
                    return

            # Confirm or start game
            if self.confirm_button_rect.collidepoint(x, y):
                if self.current_player not in self.confirmed_players:
                    self.confirm_selection()
                    return "confirmed"

        return None

    def select_token(self, token):
        """
        Assign the selected token to the current player.

        Args:
            token (str): The token name selected.
        """
        if token in self.allowed_tokens and token not in self.selected_tokens.values():
            self.selected_tokens[self.current_player] = token

    def confirm_selection(self):
        """
        Confirm the selected token for current player,
        then either move to next human or assign AI tokens.
        """
        if self.current_player in self.confirmed_players:
            return

        if self.selected_tokens.get(self.current_player):
            self.confirmed_players.add(self.current_player)

            # Move to next player or assign AI tokens
            if self.current_player < self.human_players:
                self.current_player += 1
            else:
                self.assign_ai_tokens()

    def assign_ai_tokens(self):
        """
        Randomly assigns remaining tokens to AI players.
        """
        ai_start = self.human_players + 1
        for ai_player in range(ai_start, self.total_players + 1):
            remaining = set(self.allowed_tokens) - set(self.selected_tokens.values())
            if remaining:
                token = random.choice(list(remaining))
                self.selected_tokens[ai_player] = token
                self.confirmed_players.add(ai_player)

    def get_selected_tokens(self):
        """
        Returns:
            dict: player_number -> token_name
        """
        return self.selected_tokens

    def highlight_button(self, button_rect, color, text):
        """
        Draw a button with hover effect.

        Args:
            button_rect (pygame.Rect): Rect of the button.
            color (tuple): Base color of button.
            text (str): Button label.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_x, mouse_y)

        # Lighten color on hover
        hover_color = (255, 100, 100) if is_hovered else color

        pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=10)

        text_surf = pygame.font.Font(None, 28).render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
