import pygame
import os
import random

class TokenSelectionScreen:
    """
    Provides an interactive interface for human players to select their tokens.
    Automatically assigns tokens to AI players once human selections are confirmed.

    Args:
        screen (pygame.Surface): The main game screen to render UI on.
        human_players (int): Number of human players.
        ai_players (int): Number of AI players.

    Attributes:
        screen (pygame.Surface): The main game screen to render the UI.
        width (int): Width of the screen.
        height (int): Height of the screen.
        font (pygame.font.Font): Font used for text rendering.
        allowed_tokens (list): List of token names allowed in the game.
        assets_folder (str): Folder path where token images are stored.
        token_images (dict): A dictionary of token names mapped to their respective images.
        available_tokens (list): List of tokens that are available for selection.
        human_players (int): Number of human players.
        ai_players (int): Number of AI players.
        total_players (int): Total number of players (human + AI).
        selected_tokens (dict): A dictionary mapping players to selected tokens.
        confirmed_players (set): A set tracking which players have confirmed their selection.
        current_player (int): The number of the current player selecting a token.
        selected_token (str, optional): The token currently selected by the player.
        confirm_button_rect (pygame.Rect): Rectangle for the confirm/start button.
        click_sound (pygame.mixer.Sound): Sound played when a button is clicked.
        background (pygame.Surface): The background image for the screen.
        player_names (dict): A dictionary mapping player numbers to player names.
        name_input_active (bool): Flag indicating if the name input field is active.
        name_input_text (str): Text entered by the player in the name input field.
        name_input_rect (pygame.Rect): Rectangle for the name input field.
    """

    def __init__(self, screen, human_players, ai_players):
        """
        Initializes the selection screen.

        Args:
            screen (pygame.Surface): The main game screen to render UI on.
            human_players (int): Number of human players.
            ai_players (int): Number of AI players.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Loads the token images from the assets folder.
            - Initializes player names based on the number of human and AI players.
            - Sets up initial UI elements such as the background, font, and button positions.
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

        self.player_names = {}  
        self.name_input_active = False
        self.name_input_text = ""
        self.name_input_rect = pygame.Rect(self.width // 2 - 100, 250, 200, 40)
        for i in range(1, self.human_players + 1):
            self.player_names[i] = f"Player {i}"
        for i in range(self.human_players + 1, self.total_players + 1):
            self.player_names[i] = f"AI Player {i}"


    def load_token_images(self):
        """
        Loads token images from the assets folder.

        Returns:
            dict: A dictionary mapping token names (str) to their corresponding Pygame surfaces (pygame.Surface).

        Raises:
            None

        Side Effects:
            - Loads image files for each token from the assets folder.
            - Scales the images to 80x80 pixels.
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
        Render the token selection interface, including:
        - Available tokens
        - Name input field
        - Confirm/start button
        - List of selected players

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Draws the background, overlay, and UI components on the screen.
            - Renders each available token with hover and selection effects.
            - Updates the display for player name input and selected tokens.
        """

        self.screen.blit(self.background, (0, 0))

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render(f"Player {self.current_player}, select your token and enter your name:", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        x_start, y_start = 100, 150
        x_offset = 120
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for index, token in enumerate(self.allowed_tokens):
            x = x_start + index * x_offset
            token_rect = pygame.Rect(x, y_start, 80, 80)

            if token_rect.collidepoint(mouse_x, mouse_y) and token not in self.selected_tokens.values():
                pygame.draw.rect(self.screen, (255, 255, 0), token_rect, 4)

            self.screen.blit(self.token_images[token], (x, y_start))
            pygame.draw.rect(self.screen, (255, 255, 255), token_rect, 2)

            if self.selected_tokens.get(self.current_player) == token:
                pygame.draw.rect(self.screen, (255, 0, 0), token_rect, 3)

        input_label = self.font.render("Enter name:", True, (255, 255, 255))
        self.screen.blit(input_label, (100, 270))

        name_text = self.player_names.get(self.current_player, f"Player {self.current_player}")
        box_border_color = (255, 255, 255) if self.name_input_active else (200, 200, 200)
        box_fill_color = (240, 240, 240)  
        text_color = (0, 0, 0) 

        pygame.draw.rect(self.screen, box_fill_color, self.name_input_rect, border_radius=8)
        pygame.draw.rect(self.screen, box_border_color, self.name_input_rect, 2, border_radius=8)

        name_surface = self.font.render(name_text, True, text_color)
        self.screen.blit(name_surface, (self.name_input_rect.x + 8, self.name_input_rect.y + 8))


        y_selected = 350
        self.screen.blit(self.font.render("Selected Players:", True, (255, 255, 255)), (100, y_selected))

        for player, token in self.selected_tokens.items():
            name = self.player_names.get(player, "Unknown")
            confirmed = "✔" if player in self.confirmed_players else ""
            info = f"Player {player}: {name} ({token}) {confirmed}"
            self.screen.blit(self.font.render(info, True, (255, 255, 255)), (100, y_selected + player * 30))

        if self.current_player not in self.confirmed_players and self.selected_tokens.get(self.current_player):
            self.highlight_button(self.confirm_button_rect, (200, 0, 0), "Confirm")
        elif len(self.confirmed_players) == self.total_players:
            self.highlight_button(self.confirm_button_rect, (0, 200, 0), "Start Game")

        pygame.display.flip()


    def handle_event(self, event):
        """
        Handle mouse clicks and keyboard input for token selection and name entry.

        Args:
            event (pygame.event.Event): A Pygame event object.

        Returns:
            str or None: "confirmed" if all players selected, else None.

        Raises:
            None

        Side Effects:
            - Detects player clicks on tokens or buttons to select tokens or confirm selection.
            - Handles keyboard input for entering player names.
            - Updates the selection state based on user input.
        """

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            self.click_sound.play()

            if self.name_input_rect.collidepoint(x, y):
                self.name_input_active = True
            else:
                self.name_input_active = False

            for i, token in enumerate(self.allowed_tokens):
                token_rect = pygame.Rect(100 + i * 120, 150, 80, 80)
                if token_rect.collidepoint(x, y):
                    if token not in self.selected_tokens.values():
                        self.select_token(token)
                    return
                
            if self.confirm_button_rect.collidepoint(x, y):
                if self.current_player not in self.confirmed_players and self.selected_tokens.get(self.current_player):
                    self.confirm_selection()
                    return "confirmed"

        elif event.type == pygame.KEYDOWN:
            if self.name_input_active:
                if self.current_player not in self.player_names:
                    self.player_names[self.current_player] = ""

                if event.key == pygame.K_RETURN:
                    self.name_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.player_names[self.current_player] = self.player_names[self.current_player][:-1]
                else:
                    if len(self.player_names[self.current_player]) < 12: 
                        self.player_names[self.current_player] += event.unicode

        return None



    def select_token(self, token):
        """
        Select a token for the current player.

        Args:
            token (str): The name of the token being selected.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Adds the selected token to the `selected_tokens` dictionary for the current player.
            - Activates the name input field for the player.
        """

        if token in self.allowed_tokens and token not in self.selected_tokens.values():
            self.selected_tokens[self.current_player] = token
            self.selected_token = token
            self.name_input_active = True
            if self.current_player not in self.player_names:
                self.player_names[self.current_player] = ""  


    def confirm_selection(self):
        """
        Confirm the selected token and name for the current player.
        Moves to the next player or assigns AI tokens once all human players are done.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Marks the current player as confirmed.
            - Updates the name of the player if it is not provided.
            - If all human players are confirmed, AI players' tokens are assigned automatically.
        """

        if self.current_player in self.confirmed_players:
            return

        selected_token = self.selected_tokens.get(self.current_player)

        if not selected_token:
            print("Player must select a token before confirming.")
            return

        # Use default name if name is empty
        name_entered = self.player_names.get(self.current_player, "").strip()
        if not name_entered:
            self.player_names[self.current_player] = f"Player {self.current_player}"

        self.confirmed_players.add(self.current_player)

        self.name_input_active = False
        self.name_input_text = ""

        if self.current_player < self.human_players:
            self.current_player += 1
            self.selected_token = None
        else:
            self.assign_ai_tokens()



    def assign_ai_tokens(self):
        """
        Randomly assigns remaining tokens to AI players.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Assigns a random token to each AI player.
            - Marks each AI player's token selection as confirmed.
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
        Returns the selected tokens for all players.

        Args:
            None

        Returns:
            dict: A dictionary mapping player numbers (int) to selected token names (str).

        Raises:
            None

        Side Effects:
            - None
        """
        return self.selected_tokens

    def highlight_button(self, button_rect, color, text):
        """
        Draw a button with hover effect.

        Args:
            button_rect (pygame.Rect): Rect of the button.
            color (tuple): Base color of the button.
            text (str): Button label.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Renders the button with a color change on hover.
            - Displays the label text centered inside the button.
        """

        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_x, mouse_y)

        hover_color = (255, 100, 100) if is_hovered else color

        pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=10)

        text_surf = pygame.font.Font(None, 28).render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
