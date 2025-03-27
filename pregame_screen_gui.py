import pygame

class PreGameScreen:
    """
    This class manages the Pre-Game screen where players select game mode,
    time limit (if applicable), and number of human/AI players before starting.
    """

    def __init__(self, screen):
        """
        Initialize the UI elements and layout for the pregame configuration screen.

        Parameters:
        screen (pygame.Surface): The Pygame surface where the screen is drawn.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()

        # Load and scale background image
        self.background = pygame.image.load("assets/background.png")
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        # Fonts for UI elements
        self.font = pygame.font.Font(None, 38)
        self.button_font = pygame.font.Font(None, 32)

        # Default selections
        self.selected_mode = "Normal"       # Game mode: "Normal" or "Abridged"
        self.time_limit = ""                # Time input (only if Abridged selected)
        self.num_human_players = 1          # Starting human players
        self.num_ai_players = 0             # Starting AI players
        self.max_players = 5                # Game limit

        # Sound for clicking buttons
        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("assets/click.wav")

        # UI element rectangles (positions and sizes)
        self.start_button_rect = pygame.Rect(self.width // 2 - 75, self.height - 100, 150, 50)
        self.normal_button_rect = pygame.Rect(100, 150, 200, 50)
        self.abridged_button_rect = pygame.Rect(400, 150, 200, 50)
        self.minus_human_button = pygame.Rect(340, 300, 40, 40)
        self.plus_human_button = pygame.Rect(390, 300, 40, 40)
        self.minus_ai_button = pygame.Rect(340, 380, 40, 40)
        self.plus_ai_button = pygame.Rect(390, 380, 40, 40)

        self.input_box = pygame.Rect(340, 220, 100, 40)
        self.input_active = False  # Whether the time limit input box is selected

        self.start_disabled = True  # Prevent starting until valid player count

    def draw(self):
        """
        Draw the full pre-game screen with all buttons, labels, inputs, and overlays.
        """
        # Draw background and dark overlay for readability
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        # Title
        title_text = self.font.render("Welcome to Property Tycoon: Select Your Game Options", True, (255, 255, 255))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 50))

        # Game mode buttons
        self.draw_hover_button(self.normal_button_rect, "Normal", selected=self.selected_mode == "Normal")
        self.draw_hover_button(self.abridged_button_rect, "Abridged", selected=self.selected_mode == "Abridged")

        # Time limit input (only if Abridged is selected)
        if self.selected_mode == "Abridged":
            time_label = self.font.render("Time Limit (mins):", True, (255, 255, 255))
            self.screen.blit(time_label, (100, 230))

            pygame.draw.rect(self.screen, (200, 200, 200), self.input_box, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2, border_radius=5)

            time_text = self.font.render(self.time_limit, True, (0, 0, 0))
            text_rect = time_text.get_rect(midleft=(self.input_box.x + 10, self.input_box.centery))
            self.screen.blit(time_text, text_rect)

        # Player count display
        human_text = self.font.render(f"Human Players: {self.num_human_players}", True, (255, 255, 255))
        self.screen.blit(human_text, (100, 300))
        ai_text = self.font.render(f"AI Players: {self.num_ai_players}", True, (255, 255, 255))
        self.screen.blit(ai_text, (100, 380))

        # + and - buttons for adjusting player counts
        self.draw_hover_button(self.minus_human_button, "−")
        self.draw_hover_button(self.plus_human_button, "+")
        self.draw_hover_button(self.minus_ai_button, "−")
        self.draw_hover_button(self.plus_ai_button, "+")

        # Start button (only enabled if player count is valid)
        self.draw_hover_button(self.start_button_rect, "Start", disabled=self.start_disabled)

        pygame.display.flip()

    def handle_event(self, event):
        """
        Handles mouse clicks and keyboard input (for text fields).

        Parameters:
        event (pygame.event.Event): A single event from the Pygame event loop.

        Returns:
        str or None: Returns "start" if the user clicks the start button, otherwise None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            self.click_sound.play()

            # Game mode selection
            if self.normal_button_rect.collidepoint(x, y):
                self.selected_mode = "Normal"
                self.input_active = False
            elif self.abridged_button_rect.collidepoint(x, y):
                self.selected_mode = "Abridged"
                self.input_active = True

            # Human player count
            if self.minus_human_button.collidepoint(x, y) and self.num_human_players > 1:
                self.num_human_players -= 1
            elif self.plus_human_button.collidepoint(x, y) and (self.num_human_players + self.num_ai_players < self.max_players):
                self.num_human_players += 1

            # AI player count
            if self.minus_ai_button.collidepoint(x, y) and self.num_ai_players > 0:
                self.num_ai_players -= 1
            elif self.plus_ai_button.collidepoint(x, y) and (self.num_human_players + self.num_ai_players < self.max_players):
                self.num_ai_players += 1

            # Enable or disable start button based on selection
            self.check_start_condition()

            # Activate text input box if clicked
            if self.input_box.collidepoint(x, y) and self.selected_mode == "Abridged":
                self.input_active = True

            # Start game
            if self.start_button_rect.collidepoint(x, y) and not self.start_disabled:
                return "start"

        # Text input for time limit (when Abridged mode is selected)
        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.time_limit = self.time_limit[:-1]
            elif event.unicode.isdigit():
                self.time_limit += event.unicode

        return None

    def check_start_condition(self):
        """
        Validates player count and enables/disables the Start button.
        Game requires either:
        - 2+ human players, OR
        - 1+ human AND 1+ AI player
        """
        self.start_disabled = not (
            self.num_human_players >= 2 or
            (self.num_human_players >= 1 and self.num_ai_players >= 1)
        )

    def draw_hover_button(self, button_rect, text, selected=False, disabled=False):
        """
        Draws a button with color changes for hover, selected, or disabled states.

        Parameters:
        button_rect (pygame.Rect): Position and size of the button.
        text (str): Button label.
        selected (bool): If True, shows the button as selected.
        disabled (bool): If True, dims the button and disables click.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_x, mouse_y)

        # Color logic for different states
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
