import pygame
from property_tycoon import PropertyTycoon
from GuiElements.leave_game_popup_gui import LeaveGamePopup


class RightSidebar(PropertyTycoon):
    """
    Handles the UI for the right-hand sidebar in the game.
    This includes:
    - A scrolling event log panel
    - Functional buttons (Buy Property, Trade, End Turn, Save Game, Leave Game)
    - A modal-style Trade Menu window

    Args:
        screen (pygame.Surface): The main Pygame surface to render onto.
        game (PropertyTycoon): The game object that holds the current game state and logic.
        dice (DiceGUI): The DiceGUI object used for rolling dice.

    Attributes:
        screen (pygame.Surface): The Pygame screen surface to render the sidebar UI.
        width (int): Width of the screen.
        height (int): Height of the screen.
        sidebar_rect (pygame.Rect): The rectangle defining the sidebar dimensions.
        game_events_panel (pygame.Rect): The panel to display game events.
        event_log (list): The list of event log messages.
        font (pygame.font.Font): The font used for rendering text.
        scroll_offset (int): The offset used for scrolling the event log.
        buy_property_button (pygame.Rect): The button to buy property.
        trade_button (pygame.Rect): The button to open the trade menu.
        end_turn_button (pygame.Rect): The button to end the current player's turn.
        save_game_button (pygame.Rect): The button to save the game.
        leave_game_button (pygame.Rect): The button to leave the game.
        show_trade_menu (bool): Whether the trade menu is currently visible.
        trade_menu_rect (pygame.Rect): The rectangle defining the trade menu's dimensions.
        close_trade_button (pygame.Rect): The button to close the trade menu.
        game (PropertyTycoon): The game object.
        dice (DiceGUI): The DiceGUI object.
    """

    def __init__(self, screen, game, dice):
        """
        Initialize the sidebar layout, buttons, and event log.

        Args:
            screen (pygame.Surface): The Pygame surface to render onto.
            game (PropertyTycoon): The game object that holds the current game state and logic.
            dice (DiceGUI): The DiceGUI object used for rolling dice.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Initializes the sidebar layout, buttons, and event log.
            - Sets up the UI for the sidebar panel, buttons, and trade menu.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()

        # Sidebar panel
        self.sidebar_width = 200
        self.sidebar_rect = pygame.Rect(self.width - self.sidebar_width, 0, self.sidebar_width, self.height)

        # Game events display panel (top half of sidebar)
        self.game_events_panel = pygame.Rect(self.sidebar_rect.x + 10, 10, self.sidebar_width - 20, self.height // 2)
        self.event_log = ["Game started"]  # Keeps all log messages
        self.font = pygame.font.Font(None, 20)
        self.scroll_offset = 0  # For scrolling event log

        # Button layout
        self.buy_property_button = pygame.Rect(self.sidebar_rect.x + 10, self.game_events_panel.bottom + 10, self.sidebar_width - 20, 40)
        self.trade_button = pygame.Rect(self.sidebar_rect.x + 10, self.buy_property_button.bottom + 10, self.sidebar_width - 20, 40)
        self.end_turn_button = pygame.Rect(self.sidebar_rect.x + 10, self.trade_button.bottom + 10, self.sidebar_width - 20, 40)
        self.save_game_button = pygame.Rect(self.sidebar_rect.x + 10, self.end_turn_button.bottom + 10, self.sidebar_width - 20, 40)
        self.leave_game_button = pygame.Rect(self.sidebar_rect.x + 10, self.save_game_button.bottom + 10, self.sidebar_width - 20, 40)

        # Trade menu popup
        self.show_trade_menu = False
        self.trade_menu_rect = pygame.Rect(self.width // 4, self.height // 4, self.width // 2, self.height // 2)
        self.close_trade_button = pygame.Rect(self.trade_menu_rect.x + self.trade_menu_rect.width - 60, self.trade_menu_rect.y + 10, 50, 30)
        self.game = game
        self.dice = dice

    def draw(self):
        """
        Renders the sidebar UI, including event log, buttons, and the trade menu if active.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Renders the sidebar background, event log, buttons, and trade menu.
            - Updates the visual state of the sidebar UI based on the current game state.
        """
        # Draw sidebar background
        pygame.draw.rect(self.screen, (50, 50, 50), self.sidebar_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.sidebar_rect, 2)

        # Game Events Panel (Red border with white interior)
        pygame.draw.rect(self.screen, (180, 0, 0), self.game_events_panel)
        inner_rect = self.game_events_panel.inflate(-6, -6)
        pygame.draw.rect(self.screen, (255, 255, 255), inner_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), inner_rect, 2)
        self.screen.blit(pygame.font.Font(None, 24).render("Game Events", True, (0, 0, 0)), (inner_rect.x + 10, inner_rect.y + 5))

        # Render visible portion of event log (with line wrapping and scroll support)
        visible_height = inner_rect.height - 30
        line_height = 20
        max_lines = visible_height // line_height
        visible_lines = self.event_log[::-1][self.scroll_offset:self.scroll_offset + max_lines]

        log_y = inner_rect.y + 30

        for line in visible_lines:
            wrapped = self.wrap_text(line, self.font, inner_rect.width - 20)
            for wline in wrapped:
                if log_y + line_height > inner_rect.bottom:
                    break
                self.screen.blit(wline, (inner_rect.x + 10, log_y))
                log_y += line_height

        # Render buttons below event panel
        self.highlight_button(self.buy_property_button, (0, 153, 0), "Buy Property")
        self.highlight_button(self.trade_button, (255, 153, 255), "Trade")
        self.highlight_button(self.end_turn_button, (255, 0, 0), "End Turn")
        self.highlight_button(self.save_game_button, (0, 153, 255), "Save Game")
        self.highlight_button(self.leave_game_button, (153, 0, 0), "Leave Game")

        # Draw trade menu if open
        if self.show_trade_menu:
            self.draw_trade_menu()

    def wrap_text(self, text, font, max_width):
        """
        Helper function to wrap text into multiple lines to fit in a defined width.

        Args:
            text (str): The original string.
            font (pygame.font.Font): Font used to render text.
            max_width (int): Maximum width in pixels allowed for each line.

        Returns:
            list: List of rendered surfaces for each wrapped line.

        Raises:
            None

        Side Effects:
            - Breaks the text into multiple lines to ensure it fits within the specified width.
            - Returns a list of text surfaces ready to be rendered.
        """
        if not text:
            return []
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = f"{current_line} {word}" if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(font.render(current_line, True, (0, 0, 0)))
                current_line = word
        if current_line:
            lines.append(font.render(current_line, True, (0, 0, 0)))
        return lines

    def highlight_button(self, button_rect, color, text):
        """
        Draws a button with hover effect and label.

        Args:
            button_rect (pygame.Rect): Button position/size (pygame.Rect).
            color (tuple): Button background color on hover.
            text (str): Label to display inside the button.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Renders the button with hover effects.
            - Updates the visual state of the button based on mouse hover status.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_x, mouse_y)

        if is_hovered:
            pygame.draw.rect(self.screen, color, button_rect)
            label = pygame.font.Font(None, 26).render(text, True, (255, 255, 255))
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), button_rect)
            label = pygame.font.Font(None, 26).render(text, True, (0, 0, 0))

        self.screen.blit(label, (button_rect.x + 10, button_rect.y + 10))

    def draw_trade_menu(self):
        """
        Renders a centered trade menu window with a close button.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Renders the trade menu window with a close button in the center.
        """
        pygame.draw.rect(self.screen, (220, 220, 220), self.trade_menu_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.trade_menu_rect, 2)

        title = pygame.font.Font(None, 30).render("Trade Menu", True, (0, 0, 0))
        self.screen.blit(title, (self.trade_menu_rect.x + 20, self.trade_menu_rect.y + 10))

        self.highlight_button(self.close_trade_button, (255, 0, 0), "X")

    def handle_event(self, event):
        """
        Handles interaction with sidebar buttons and scrolling the event log.

        Args:
            event (pygame.event): The Pygame event object.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Responds to mouse clicks on buttons (Buy Property, Trade, End Turn, etc.).
            - Handles scroll actions for the event log panel using the mouse wheel.
            - Opens or closes the trade menu based on user interaction.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.show_trade_menu:
                # Close trade menu
                if self.close_trade_button.collidepoint(x, y):
                    self.show_trade_menu = False
                return

            if self.buy_property_button.collidepoint(x, y):
                if (self.game.players[self.game.current_player_index].identity != "Human"):
                    return
                self.log_event("Buy Property Clicked")
                message = self.game.prompt_property_purchase(self.game.players[self.game.current_player_index])
                if (message != "bought" and message != "declined") :
                    self.log_event(message)
            elif self.trade_button.collidepoint(x, y):
                self.show_trade_menu = True
                self.log_event("Trade Menu Opened")
            elif self.end_turn_button.collidepoint(x, y):
                self.log_event("End Turn Clicked")
                current_player = self.game.players[self.game.current_player_index]

                # Check if the player can buy the property
                if self.game.eligible_to_buy(current_player):
                    prop = self.game.bank.properties.get(current_player.position, None)

                    if prop and not prop.already_auctioned:
                        eligible_bidders = self.game.get_eligible_auction_players()
                        if len(eligible_bidders) > 1:
                            self.log_event(f"{current_player.name} declined to buy {prop.name}. Starting auction!")
                            self.game.start_auction(current_player)
                        else:
                            self.log_event("Not enough eligible bidders to start an auction. Property remains unowned.")
                            prop.already_auctioned = False
                            super().roll_and_play_next_turn()
                    else:
                        self.log_event(f"{prop.name if prop else 'Property'} already auctioned this turn. Skipping auction.")
                        prop.already_auctioned = False
                        super().roll_and_play_next_turn()
                else:
                    # Check if an auction is still in progress
                    auction = self.game.ui.auction_popup
                    if auction and (auction.visible or not auction.finished):
                        self.log_event("Auction in progress. Cannot end turn.")
                    else:
                        super().roll_and_play_next_turn()
            elif self.save_game_button.collidepoint(x, y):
                self.log_event("Game Saved")
            elif self.leave_game_button.collidepoint(x, y):
                self.log_event("Left Game")
                leaving_player = self.game.players[self.game.current_player_index]
                self.game.ui.leave_game_popup = LeaveGamePopup(self.screen, leaving_player, self.game.players, self.game)

                self.game.check_end_game()

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll the game events panel when hovered
            if self.game_events_panel.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset -= event.y
                max_scroll = max(0, len(self.event_log) - ((self.game_events_panel.height - 30) // 20))
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def log_event(self, message):
        """
        Adds a message to the event log.

        Args:
            message (str): The message to be added to the event log.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Adds the specified message to the event log for display in the game UI.
        """
        self.event_log.append(message)

    def get_event_logger(self):
        """
        Returns a function that can be passed around for logging events.

        Args:
            None

        Returns:
            Callable: The `log_event` function that logs events to the event log.

        Raises:
            None

        Side Effects:
            - Provides access to the `log_event` function for external use (e.g., in other parts of the game).
        """
        return self.log_event 
