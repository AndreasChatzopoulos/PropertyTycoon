import pygame
from property_tycoon import PropertyTycoon

class RightSidebar(PropertyTycoon):
    """
    Handles the UI for the right-hand sidebar in the game.
    This includes:
    - A scrolling event log panel
    - Functional buttons (Buy Property, Trade, End Turn, Save Game, Leave Game)
    - A modal-style Trade Menu window
    """
    

    def __init__(self, screen, game, dice):
        """
        Initialize the sidebar layout, buttons, and event log.

        Args:
            screen: The main Pygame surface to render onto.
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
        visible_lines = self.event_log[-(max_lines + self.scroll_offset):-self.scroll_offset if self.scroll_offset > 0 else None]
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
            text: The original string.
            font: Font used to render text.
            max_width: Maximum width in pixels allowed for each line.

        Returns:
            List of rendered surfaces for each wrapped line.
        """
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
            button_rect: Button position/size (pygame.Rect)
            color: Button background color on hover
            text: Label to display
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
            event: Pygame event object.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.show_trade_menu:
                # Close trade menu
                if self.close_trade_button.collidepoint(x, y):
                    self.show_trade_menu = False
                return

            if self.buy_property_button.collidepoint(x, y):
                self.log_event("Buy Property Clicked")
                message = self.game.prompt_property_purchase(self.game.players[self.game.current_player_index])
                self.log_event(message)
            elif self.trade_button.collidepoint(x, y):
                self.show_trade_menu = True
                self.log_event("Trade Menu Opened")
            elif self.end_turn_button.collidepoint(x, y):
                self.log_event("End Turn Clicked")

                # check for auction
                if self.game.eligible_to_buy(self.game.players[self.game.current_player_index]):
                    print(f"{self.game.players[self.game.current_player_index].name} declined to buy the property. Starting auction!")
                    self.game.start_auction(self.game.players[self.game.current_player_index])

                super().roll_and_play_next_turn() 
            elif self.save_game_button.collidepoint(x, y):
                self.log_event("Game Saved")
            elif self.leave_game_button.collidepoint(x, y):
                self.log_event("Left Game")  

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
            message: String to display in the log panel.
        """
        self.event_log.append(message)

    def get_event_logger(self):
        """
        Returns a function that can be passed around for logging events.

        Returns:
            Callable log_event function
        """
        return self.log_event 
