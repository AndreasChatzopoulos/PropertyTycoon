import pygame
import sys
import time
import json
import os

from GuiElements.board_gui import BoardGUI
from GuiElements.pregame_screen_gui import PreGameScreen
from GuiElements.token_selection_gui import TokenSelectionScreen
from GameElements.board_elements import BoardElementsGUI
from GuiElements.dice_gui import DiceGUI
from GuiElements.jail_popup_gui import JailPopup
from GuiElements.auction_popup_gui import AuctionPopup
from GuiElements.end_game_gui import EndGamePopup

from GameElements.game_logic import Game

class PropertyTycoon:
    """
    Main controller class for the Monopoly game UI.

    This class manages the overall game state and switches between different screens
    such as the pregame setup, token selection, and the actual game board.
    It handles input, game flow, drawing of all components, and timing (for abridged mode).
    """

    def __init__(self, width=1200, height=750):
        pygame.init()
        pygame.mixer.init()

        # Background Music
        try:
            pygame.mixer.music.load("assets/game_theme.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            print("Background music playing...")
        except pygame.error as e:
            print(f"Error loading background music: {e}")

        try:
            self.jail_sound = pygame.mixer.Sound("assets/jail_sound.wav")
            self.win_sound = pygame.mixer.Sound("assets/win_sound.wav")
        except pygame.error as e:
            print(f"Failed to load sound: {e}")
            self.jail_sound = None
            self.win_sound = None


        # Screen and game state setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Monopoly Game")
        self.clock = pygame.time.Clock()

        # Game state
        self.state = "pregame" 
        self.running = True

        # UI Components
        self.pregame_screen = PreGameScreen(self.screen)
        self.token_selection_screen = None
        self.board = None
        self.elements = None

        # Game data
        self.players = {}
        self.human_players = 0
        self.ai_players = 0
        self.token_images = {}

        # Timer (for abridged mode)
        self.start_time = None
        self.time_limit_seconds = None

        self.game = None
        self.dice = DiceGUI(self.screen)
        
        self.first_turn_pending = False
        self.pending_roll = None
        self.waiting_for_dice = False

        self.jail_action_pending = False
        self.jail_action_type = None  
        self.jail_player = None

        self.player_turn_count = {}
        self.time_limit_reached = False
        self.turns_when_times_up = None



        from GuiElements.right_sidebar_gui import RightSidebar
        self.right_sidebar = RightSidebar(self.screen, self.game, self.dice)
        from GuiElements.left_sidebar_gui import LeftSidebar
        self.left_sidebar = LeftSidebar(self.screen, self.game, event_logger=self.right_sidebar.get_event_logger())

        self.jail_popup = None
        self.auction_popup = None
        self.bankruptcy_popup = None
        self.end_game_popup = None
        self.leave_game_popup = None

        self.paused = False
        self.inactivity_popup = None
        self.elapsed_time_at_pause = None



    def roll_and_play_next_turn(self):
        self.dice.start_roll_animation()
        die1, die2 = self.dice.get_dice_result()
        self.game.next_turn(self.game.players[self.game.current_player_index], die1, die2)
    
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
            self.screen.fill((200, 200, 200))

            self.board.draw(self.screen, self.game.bank.properties.items())
            self.elements.draw()

            self.left_sidebar.game = self.game
            self.right_sidebar.game = self.game
            self.left_sidebar.draw()
            self.right_sidebar.draw()

            if not self.right_sidebar.show_trade_menu:
                self.dice.draw()

            self.draw_tokens_on_board()

            if self.time_limit_seconds:
                if self.paused:
                    elapsed_time = self.elapsed_time_at_pause  # Stay frozen
                else:
                    elapsed_time = time.time() - self.start_time

                remaining_time = max(0, self.time_limit_seconds - elapsed_time)

           


                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                time_text = f"Time Left: {minutes:02}:{seconds:02}"

                timer_render = pygame.font.Font(None, 30).render(time_text, True, (255, 255, 255))
                timer_rect = timer_render.get_rect(bottomright=(self.width - 20, self.height - 20))
                self.screen.blit(timer_render, timer_rect)

                if remaining_time <= 0 and not hasattr(self, 'abridged_mode_active'):
                    self.abridged_mode_active = True
                    self.turns_target = max(p.turns_taken for p in self.game.players)
                    self.right_sidebar.log_event("Time is up! Everyone will finish this round before the winner is determined.")


            if self.jail_popup:
                self.jail_popup.draw()

            if self.auction_popup:
                self.auction_popup.draw()  

            if self.bankruptcy_popup:
                self.bankruptcy_popup.draw()

            if self.end_game_popup:
                self.end_game_popup.draw()

            if self.leave_game_popup:
                self.leave_game_popup.draw()


            if self.inactivity_popup:
                font = pygame.font.Font(None, 36)
                msg = font.render(self.inactivity_popup, True, (255, 255, 255))
                msg_rect = msg.get_rect(center=(self.width // 2, self.height // 2))
                pygame.draw.rect(self.screen, (0, 0, 0), msg_rect.inflate(20, 20))
                pygame.draw.rect(self.screen, (255, 255, 255), msg_rect.inflate(20, 20), 2)
                self.screen.blit(msg, msg_rect)



            pygame.display.flip()

    def handle_events(self):
        """
        Handle all input events like mouse clicks, movement, and key presses.
        """
        for event in pygame.event.get():
            # Detect user interaction to reset inactivity timer
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.KEYDOWN):
                self.last_input_time = time.time()
                if self.paused:
                    self.paused = False
                    self.inactivity_popup = None
                    self.pause_start_time = None


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
                if self.jail_popup and self.jail_popup.visible:
                    self.jail_popup.handle_event(event)
                    return

                if self.auction_popup and self.auction_popup.visible:
                    self.auction_popup.handle_event(event)
                    return

                if self.bankruptcy_popup and self.bankruptcy_popup.visible:
                    self.bankruptcy_popup.handle_event(event)
                    return

                if self.end_game_popup:
                    self.end_game_popup.handle_event(event)
                    return

                if self.leave_game_popup and self.leave_game_popup.visible:
                    self.leave_game_popup.handle_event(event)
                    return

                self.handle_board_events(event)

                if not self.right_sidebar.show_trade_menu:
                    self.dice.handle_event(event)

                self.left_sidebar.handle_event(event)
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
        total_players = self.human_players + self.ai_players
        self.auction_popup = None

        player_data = []

        for i in range(1, total_players + 1):
            name = self.token_selection_screen.player_names.get(i, f"Player {i}")
            token = self.players[i]
            identity = "Human" if i <= self.human_players else "Basic Bot"
            
            player_data.append({
                "name": name,
                "token": token,
                "identity": identity
            })


        self.save_players_to_json(player_data)
        player_names, player_tokens, player_identities = self.load_players_from_file("players.json")
        self.game = Game(player_names, player_tokens, player_identities)
        self.game.ui = self
        self.game.log_event = self.right_sidebar.get_event_logger()

        self.dice.start_roll_animation()
        self.waiting_for_dice = True  




        for i, player in enumerate(self.game.players, start=1):
            token_name = self.players[i]
            image_path = f"assets/{token_name}.png"
            token_image = pygame.image.load(image_path).convert_alpha()
            token_scaled = pygame.transform.scale(token_image, (40, 40))
            player.token_image = token_scaled  


        self.board = BoardGUI(
            csv_path="data/PropertyTycoonBoardData.csv",  # path to your loaded board config
            board_size=750,
            window_width=self.width,
            window_height=self.height
        )

        self.elements = BoardElementsGUI(self.screen)

        if self.pregame_screen.selected_mode == "Abridged" and self.pregame_screen.time_limit.isdigit():
            self.time_limit_seconds = int(self.pregame_screen.time_limit) * 60
            self.start_time = time.time()

        self.state = "board"

        self.last_input_time = time.time()  # Reset once players are loaded and UI is ready




        # first_player = self.game.players[0]
        # first_player.balance = 0  # 💸 Force them to start with no money
        # first_player.position = 4  # One step before Income Tax
        # die1, die2 = 1, 0  # Move 1 space to land on tile 5
        # self.game.play_turn(die1, die2)



    @staticmethod
    def load_players_from_file(filename="players.json"):
        """Loads player names and tokens from a JSON file."""
        filepath = os.path.join(os.path.dirname(__file__), filename)

        if not os.path.exists(filepath):
            print("Player file not found! Starting with default players.")
            return ["Alice", "Bob"], ["Boot", "Ship"], ["Human", "Human"]

        with open(filepath, "r") as f:
            data = json.load(f)
            player_names = [p["name"] for p in data["players"]]
            player_tokens = [p["token"] for p in data["players"]]
            player_identities = [p["identity"] for p in data["players"]]
            return player_names, player_tokens, player_identities
    
    def save_players_to_json(self, player_data, filename="players.json"):
        with open(filename, "w") as f:
            json.dump({"players": player_data}, f, indent=4)
        print("Player data saved to players.json")


    def draw_tokens_on_board(self):
        """
        Draw player tokens on the board based on their current positions.
        - Solo tokens are offset to avoid blocking tile content
        - Multiple tokens are laid out in a grid to avoid overlap
        """
        min_token_size = 24
        max_token_ratio = 0.4 
        tokens_per_tile = {}

        for player in self.game.players:
            position = player.position
            tokens_per_tile.setdefault(position, []).append(player)

        for position, players in tokens_per_tile.items():
            tile = self.board.spaces[position - 1]
            tile_rect = tile.rect
            num_tokens = len(players)

            if num_tokens == 1:
                player = players[0]
                token_image = getattr(player, 'token_image', None)
                if not token_image:
                    continue

                token_size = int(min(tile_rect.width, tile_rect.height) * max_token_ratio)
                token_size = max(min_token_size, token_size)
                token_scaled = pygame.transform.scale(token_image, (token_size, token_size))

                offset_x = -tile_rect.width // 4
                offset_y = tile_rect.height // 4
                draw_x = tile_rect.centerx + offset_x - token_size // 2
                draw_y = tile_rect.centery + offset_y - token_size // 2

                self.screen.blit(token_scaled, (draw_x, draw_y))
                continue

            max_cols = min(num_tokens, 3)
            rows = (num_tokens + max_cols - 1) // max_cols

            max_token_width = tile_rect.width / max_cols
            max_token_height = tile_rect.height / rows
            raw_token_size = int(min(max_token_width, max_token_height) * max_token_ratio)
            token_size = max(min_token_size, raw_token_size)

            total_width = max_cols * token_size
            total_height = rows * token_size
            start_x = tile_rect.centerx - total_width // 2
            start_y = tile_rect.centery - total_height // 2

            for idx, player in enumerate(players):
                token_image = getattr(player, 'token_image', None)
                if not token_image:
                    continue

                token_scaled = pygame.transform.scale(token_image, (token_size, token_size))
                col = idx % max_cols
                row = idx // max_cols
                draw_x = start_x + col * token_size
                draw_y = start_y + row * token_size

                self.screen.blit(token_scaled, (draw_x, draw_y))



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

    def create_bankruptcy_popup(self, player, amount_due, creditor):
        from GuiElements.bankruptcy_gui import BankruptcyPopup
        popup = BankruptcyPopup(self.screen, player, amount_due, creditor)
        self.bankruptcy_popup = popup
        return popup
        
    def trigger_end_game_popup(self, winner_name):
        self.end_game_popup = EndGamePopup(self.screen, winner_name)

        if self.win_sound:
            self.win_sound.play()



    def run(self):
        """Main game loop that keeps the game running and updating."""
        while self.running:
            self.handle_events()
            self.dice.update()
            self.draw()

            if not self.paused and (time.time() - self.last_input_time >= 300):
                self.paused = True
                self.pause_start_time = time.time()
                self.elapsed_time_at_pause = time.time() - self.start_time  # Freeze here
                self.inactivity_popup = "Game paused due to 5 minutes of inactivity."




            if self.state == "board":
                if self.paused:
                    self.clock.tick(30)
                    continue

                player = self.game.players[self.game.current_player_index]

                # Skip turn if flagged (after paying to leave jail)
                if getattr(player, "skip_turn", False):
                    self.game.log_event(f"⏭️ {player.name} skips this turn after paying to leave jail.")
                    player.skip_turn = False
                    self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
                    continue

                # Skip turn if waiting in jail
                if getattr(player, "turns_skipped", 0) > 0:
                    self.game.log_event(f"⏭️ {player.name} is skipping turn ({3 - player.turns_skipped}/2) due to jail wait.")
                    player.turns_skipped -= 1
                    self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
                    continue

                # Jail logic - rolling for doubles
                if getattr(player, "wants_to_roll_in_jail", False) and not self.dice.rolling:
                    self.dice.start_roll_animation()
                    player.awaiting_jail_roll_result = True
                    player.wants_to_roll_in_jail = False

                if getattr(player, "awaiting_jail_roll_result", False) and not self.dice.rolling:
                    die1, die2 = self.dice.get_dice_result()
                    is_double = die1 == die2

                    if is_double:
                        player.jail_turns = 0
                        player.in_jail = False
                        self.game.log_event(f"🎲 {player.name} rolled a double ({die1}, {die2}) and escaped jail!")
                        player.move(die1, die2, is_double)
                    else:
                        player.jail_turns += 1
                        self.game.log_event(f"{player.name} failed to roll a double ({die1}, {die2}).")

                        if player.jail_turns >= 3:
                            player.jail_turns = 0
                            player.in_jail = False
                            self.game.log_event(f"⏳ {player.name} served 3 turns in jail and is now free.")

                    player.awaiting_jail_roll_result = False

                # Deprecated - no longer using this flag (paying jail skips turn instead)
                if getattr(player, "wants_to_roll_after_paying_jail", False) and not self.dice.rolling:
                    self.dice.start_roll_animation()
                    player.awaiting_post_jail_roll = True
                    player.wants_to_roll_after_paying_jail = False

                if getattr(player, "awaiting_post_jail_roll", False) and not self.dice.rolling:
                    die1, die2 = self.dice.get_dice_result()
                    is_double = die1 == die2
                    player.move(die1, die2, is_double)
                    self.game.log_event(f"{player.name} moved {die1 + die2} steps after paying to get out of jail.")
                    player.awaiting_post_jail_roll = False

                # First turn of game (rolling to start)
                if self.waiting_for_dice and not self.dice.rolling:
                    self.pending_roll = self.dice.get_dice_result()
                    self.waiting_for_dice = False
                    self.first_turn_pending = True

                elif self.first_turn_pending:
                    pygame.time.wait(1000)
                    die1, die2 = self.pending_roll
                    self.game.play_turn(die1, die2)
                    player.turns_taken += 1
                    self.first_turn_pending = False

                # Jail popup for human players
                if player.in_jail and player.identity == "Human":
                    if not self.jail_popup or self.jail_popup.player != player:
                        self.jail_popup = JailPopup(self.screen, player, self.game)
                else:
                    self.jail_popup = None

                # Auction popup management
                if self.auction_popup:
                    if not self.auction_popup.visible:
                        self.auction_popup = None
                elif hasattr(self.game, 'start_auction_popup'):
                    prop = self.game.bank.properties.get(player.position)
                    eligible_bidders = [p for p in self.game.players if p.passed]
                    if prop and prop.owner is None and len(eligible_bidders) > 1:
                        self.auction_popup = AuctionPopup(self.screen, eligible_bidders, prop, self.game)
                    del self.game.start_auction_popup
                    if hasattr(self.game, 'auction_eligible_players'):
                        del self.game.auction_eligible_players

                # Abridged game mode end condition
                if getattr(self, 'abridged_mode_active', False) and not getattr(self, 'abridged_mode_complete', False):
                    if all(p.turns_taken >= self.turns_target for p in self.game.players):
                        winner_name = self.game.determine_winner_abridged()
                        self.trigger_end_game_popup(winner_name)
                        self.abridged_mode_complete = True

            self.clock.tick(30)

        pygame.quit()
        sys.exit()
