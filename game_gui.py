import pygame
import sys
import time

# Import all GUI components for different parts of the game
from board_gui import BoardGUI
from pregame_screen_gui import PreGameScreen
from token_selection_gui import TokenSelectionScreen
from left_sidebar_gui import LeftSidebar
from board_elements import BoardElementsGUI
from dice_gui import DiceGUI
from right_sidebar_gui import RightSidebar

class GameGUI:
    """
    Main controller class for the Monopoly game UI.

    This class manages the overall game state and switches between different screens
    such as the pregame setup, token selection, and the actual game board.
    It handles input, game flow, drawing of all components, and timing (for abridged mode).
    """

    def __init__(self, width=1200, height=750):
        pygame.init()
        pygame.mixer.init()

        # 🎵 Background Music
        try:
            pygame.mixer.music.load("assets/game_theme.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            print("🎶 Background music playing...")
        except pygame.error as e:
            print(f"⚠️ Error loading background music: {e}")

        # Screen and game state setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Monopoly Game")
        self.clock = pygame.time.Clock()

        # Game state
        self.state = "pregame"  # Options: pregame, token_selection, board
        self.running = True

        # UI Components
        self.pregame_screen = PreGameScreen(self.screen)
        self.token_selection_screen = None
        self.board = None
        self.right_sidebar = RightSidebar(self.screen)
        self.sidebar = LeftSidebar(self.screen, event_logger=self.right_sidebar.get_event_logger())
        self.elements = None
        self.dice = DiceGUI(self.screen, event_logger=self.right_sidebar.get_event_logger())

        # Game data
        self.players = {}
        self.human_players = 0
        self.ai_players = 0
        self.token_images = {}

        # Timer (for abridged mode)
        self.start_time = None
        self.time_limit_seconds = None

    def draw(self):
        """
        Draw the appropriate screen depending on the current game state.
        This method is called every frame.
        """
        if self.state == "pregame":
            self.pregame_screen.draw()

        elif self.state == "token_selection":
            self.token_selection_screen.draw()

        elif self.state == "board":
            self.screen.fill((200, 200, 200))  # Background color

            self.board.draw(self.screen)
            self.elements.draw()
            self.sidebar.draw()
            self.right_sidebar.draw()

            # Hide dice when trade menu is visible
            if not self.right_sidebar.show_trade_menu:
                self.dice.draw()

            self.draw_tokens_on_board()

            # Handle timer countdown if abridged mode is active
            if self.time_limit_seconds:
                elapsed_time = time.time() - self.start_time
                remaining_time = max(0, self.time_limit_seconds - elapsed_time)

                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                time_text = f"Time Left: {minutes:02}:{seconds:02}"

                timer_render = pygame.font.Font(None, 30).render(time_text, True, (255, 255, 255))
                timer_rect = timer_render.get_rect(bottomright=(self.width - 20, self.height - 20))
                self.screen.blit(timer_render, timer_rect)

                if remaining_time <= 0:
                    print("Game Over: Time is up!")
                    self.running = False

            pygame.display.flip()

    def handle_events(self):
        """
        Handle all input events like mouse clicks, movement, and key presses.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "pregame":
                result = self.pregame_screen.handle_event(event)
                if result == "start":
                    self.start_token_selection()

            elif self.state == "token_selection":
                result = self.token_selection_screen.handle_event(event)
                if result == "confirmed":
                    if len(self.token_selection_screen.confirmed_players) == self.human_players + self.ai_players:
                        self.start_board_game()

            elif self.state == "board":
                self.handle_board_events(event)

                if not self.right_sidebar.show_trade_menu:
                    self.dice.handle_event(event)

                self.sidebar.handle_event(event)
                self.right_sidebar.handle_event(event)

    def start_token_selection(self):
        """
        Transition from pregame setup to the token selection screen.
        """
        self.human_players = self.pregame_screen.num_human_players
        self.ai_players = self.pregame_screen.num_ai_players

        self.token_selection_screen = TokenSelectionScreen(self.screen, self.human_players, self.ai_players)
        self.state = "token_selection"

    def start_board_game(self):
        """
        Start the main game after token selection is confirmed.
        Initializes the board and game elements.
        """
        self.players = self.token_selection_screen.get_selected_tokens()

        # Load and scale player token images
        for player, token_name in self.players.items():
            image_path = f"assets/{token_name}.png"
            self.token_images[player] = pygame.image.load(image_path)
            self.token_images[player] = pygame.transform.scale(self.token_images[player], (40, 40))

        self.board = BoardGUI(board_size=750, window_width=self.width, window_height=self.height)
        self.elements = BoardElementsGUI(self.screen)

        # If in abridged mode, start countdown
        if self.pregame_screen.selected_mode == "Abridged" and self.pregame_screen.time_limit.isdigit():
            self.time_limit_seconds = int(self.pregame_screen.time_limit) * 60
            self.start_time = time.time()

        self.state = "board"

    def draw_tokens_on_board(self):
        """
        Draw player tokens on the board (initially placed at "GO").
        Automatically positions tokens in groups to avoid overlap.
        """
        base_position = self.board.spaces[0].rect.center
        horizontal_offset = 25
        vertical_offset = 35
        total_players = self.human_players + self.ai_players
        mid_point = total_players // 2

        for i, (player, token_name) in enumerate(self.players.items()):
            token_image = self.token_images.get(player)
            if token_image:
                if i < mid_point:
                    x_offset = base_position[0] - (mid_point * horizontal_offset // 2) + (i * horizontal_offset)
                    y_offset = base_position[1] - vertical_offset // 2
                else:
                    x_offset = base_position[0] - (mid_point * horizontal_offset // 2) + (
                        (i - mid_point) * horizontal_offset)
                    y_offset = base_position[1] + vertical_offset // 2

                tile_rect = self.board.spaces[0].rect
                token_w = tile_rect.width * 0.35
                token_h = tile_rect.height * 0.35
                token_image = pygame.transform.scale(token_image, (int(token_w), int(token_h)))

                self.screen.blit(token_image, (x_offset - token_image.get_width() // 2,
                                               y_offset - token_image.get_height() // 2))

    def handle_board_events(self, event):
        """Handle hover highlighting for board spaces."""
        if event.type == pygame.MOUSEMOTION:
            self.update_hover(event.pos)

    def update_hover(self, pos):
        """Update hover state based on current mouse position."""
        hovered_space = self.get_hovered_space(pos)
        self.reset_highlights()
        if hovered_space is not None:
            self.board.spaces[hovered_space].set_highlight(True)

    def get_hovered_space(self, pos):
        """Return index of hovered space if any, else None."""
        for index, space in enumerate(self.board.spaces):
            if space.rect.collidepoint(pos):
                return index
        return None

    def reset_highlights(self):
        """Remove all highlights from board spaces."""
        for space in self.board.spaces:
            space.set_highlight(False)

    def run(self):
        """Main game loop that keeps the game running and updating."""
        while self.running:
            self.handle_events()
            self.dice.update()
            self.draw()
            self.clock.tick(30)  # 30 FPS

        pygame.quit()
        sys.exit()
