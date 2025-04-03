import pygame

class PreGameScreen:
    """
    Displays the pre-game setup screen where players can:
    - Choose game mode (Normal or Abridged)
    - Set a time limit (for Abridged mode)
    - Select the number of human and AI players
    - Start the game when valid settings are chosen
    """

    def __init__(self, screen):
        """
        Initialize all UI elements and settings for the pre-game screen.

        Args:
            screen: The Pygame display surface to draw the interface on.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()

        # 🎨 Load and scale background image to fill the screen
        self.background = pygame.image.load("assets/background.png")
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        # 🖋️ Fonts for general and button text
        self.font = pygame.font.Font(None, 38)
        self.button_font = pygame.font.Font(None, 32)

        # Game state options
        self.selected_mode = "Normal"
        self.time_limit = ""  # in minutes
        self.num_human_players = 1
        self.num_ai_players = 0
        self.max_players = 5  # Combined human + AI

        # 🎵 Load button click sound
        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("assets/click.wav")

        # Button placements
        self.start_button_rect = pygame.Rect(self.width // 2 - 75, self.height - 100, 150, 50)
        self.normal_button_rect = pygame.Rect(100, 150, 200, 50)
        self.abridged_button_rect = pygame.Rect(400, 150, 200, 50)
        self.minus_human_button = pygame.Rect(340, 300, 40, 40)
        self.plus_human_button = pygame.Rect(390, 300, 40, 40)
        self.minus_ai_button = pygame.Rect(340, 380, 40, 40)
        self.plus_ai_button = pygame.Rect(390, 380, 40, 40)

        # Input box for time (only shown in Abridged mode)
        self.input_box = pygame.Rect(340, 220, 100, 40)
        self.input_active = False

        self.start_disabled = True  # Start disabled until enough players are selected

    def draw(self):
        """
        Render the full pre-game UI including:
        - Mode buttons
        - Player selection
        - Time limit input
        - Start button
        """
        self.screen.blit(self.background, (0, 0))

        # Overlay for better text readability
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Dark transparent layer
        self.screen.blit(overlay, (0, 0))

        # Game title
        title_text = self.font.render("Welcome to Property Tycoon: Select Your Game Options", True, (255, 255, 255))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 50))

        # Game mode buttons
        self.draw_hover_button(self.normal_button_rect, "Normal", selected=self.selected_mode == "Normal")
        self.draw_hover_button(self.abridged_button_rect, "Abridged", selected=self.selected_mode == "Abridged")

        # Show time input for abridged mode
        if self.selected_mode == "Abridged":
            time_label = self.font.render("Time Limit (mins):", True, (255, 255, 255))
            self.screen.blit(time_label, (100, 230))

            pygame.draw.rect(self.screen, (200, 200, 200), self.input_box, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2, border_radius=5)

            # Show typed numbers inside input box
            time_text = self.font.render(self.time_limit, True, (0, 0, 0))
            text_rect = time_text.get_rect(midleft=(self.input_box.x + 10, self.input_box.centery))
            self.screen.blit(time_text, text_rect)

            # Draw (Max: 180 mins) note
            note_font = pygame.font.Font(None, 24)
            note_text = note_font.render("(Max: 180 mins)", True, (220, 220, 220))
            self.screen.blit(note_text, (self.input_box.right + 15, self.input_box.y + 10))

        # Player count controls
        human_text = self.font.render(f"Human Players: {self.num_human_players}", True, (255, 255, 255))
        self.screen.blit(human_text, (100, 300))

        ai_text = self.font.render(f"AI Players: {self.num_ai_players}", True, (255, 255, 255))
        self.screen.blit(ai_text, (100, 380))

        # Draw + / - buttons for players
        self.draw_hover_button(self.minus_human_button, "−")
        self.draw_hover_button(self.plus_human_button, "+")
        self.draw_hover_button(self.minus_ai_button, "−")
        self.draw_hover_button(self.plus_ai_button, "+")

        # Draw Start button (enabled/disabled)
        self.draw_hover_button(self.start_button_rect, "Start", disabled=self.start_disabled)

        pygame.display.flip()


    def handle_event(self, event):
        """
        Respond to mouse clicks and keyboard input.

        Returns:
            "start" if the Start button is clicked and valid.
            None otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            self.click_sound.play()

            # Switch modes
            if self.normal_button_rect.collidepoint(x, y):
                self.selected_mode = "Normal"
                self.input_active = False
                self.time_limit = ""

            elif self.abridged_button_rect.collidepoint(x, y):
                self.selected_mode = "Abridged"
                self.input_active = True

            # Adjust human players
            if self.minus_human_button.collidepoint(x, y) and self.num_human_players > 1:
                self.num_human_players -= 1
            elif self.plus_human_button.collidepoint(x, y) and self.num_human_players + self.num_ai_players < self.max_players:
                self.num_human_players += 1

            # Adjust AI players
            if self.minus_ai_button.collidepoint(x, y) and self.num_ai_players > 0:
                self.num_ai_players -= 1
            elif self.plus_ai_button.collidepoint(x, y) and self.num_human_players + self.num_ai_players < self.max_players:
                self.num_ai_players += 1

            self.check_start_condition()

            # Activate time input
            if self.input_box.collidepoint(x, y) and self.selected_mode == "Abridged":
                self.input_active = True

            # Start game if conditions met
            if self.start_button_rect.collidepoint(x, y) and not self.start_disabled:
                return "start"

        # Handle typing in time box
        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.time_limit = self.time_limit[:-1]
            elif event.unicode.isdigit():
                combined = self.time_limit + event.unicode
                if combined.isdigit() and int(combined) <= 180:
                    self.time_limit = combined

        return None


    def check_start_condition(self):
        """
        Validate that there are enough players to start the game.
        Enables or disables the Start button accordingly.
        """
        self.start_disabled = not (
            self.num_human_players >= 2 or
            (self.num_human_players >= 1 and self.num_ai_players >= 1)
        )

    def draw_hover_button(self, button_rect, text, selected=False, disabled=False):
        """
        Draws a button with hover effects and highlight state.

        Args:
            button_rect: pygame.Rect defining button size/position.
            text: Label displayed inside the button.
            selected: Whether this button is actively selected.
            disabled: Whether this button should be dimmed and non-interactive.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_x, mouse_y)

        if disabled:
            color = (80, 80, 80)
        elif selected:
            color = (255, 0, 0)
        elif is_hovered:
            color = (255, 50, 50)
        else:
            color = (200, 0, 0)

        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
        text_surface = self.button_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
