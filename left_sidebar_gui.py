import pygame

class LeftSidebar:
    """
    This class creates and manages the left sidebar in the Monopoly game UI.
    It includes the bank section, player info, and interactive buttons for
    viewing properties, selling properties, and selling houses.
    """

    def __init__(self, screen):
        """
        Initialize the sidebar layout, sizes, and placeholders for player and bank info.

        Parameters:
        screen (pygame.Surface): The main screen surface where the sidebar will be drawn.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()

        # Sidebar dimensions and position
        self.sidebar_width = 200
        self.sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, self.height)

        # Layout areas (sections and buttons)
        self.bank_section = pygame.Rect(10, 10, self.sidebar_width - 20, 80)
        self.sell_property_button = pygame.Rect(10, self.bank_section.bottom + 10, self.sidebar_width - 20, 40)
        self.sell_house_button = pygame.Rect(10, self.sell_property_button.bottom + 10, self.sidebar_width - 20, 40)
        self.player_info_section = pygame.Rect(10, self.height // 2 - 70, self.sidebar_width - 20, 100)
        self.view_properties_button = pygame.Rect(10, self.player_info_section.bottom + 10, self.sidebar_width - 20, 40)

        # Placeholder bank balance
        self.bank_balance = 50000

        # Mock player data
        self.selected_player = 1
        self.players = {
            1: ("Hatstand", 1500),
            2: ("Boot", 1400)
        }

        # Popup system for showing additional UI panels
        self.active_popup = None
        self.popup_titles = {
            "view_properties": "Owned Properties",
            "sell_property": "Sell Property",
            "sell_house": "Sell House"
        }

        # Rectangle used for popup and its close button
        self.popup_rect = pygame.Rect(10, self.view_properties_button.bottom + 10,
                                      self.sidebar_width - 20,
                                      self.height - (self.view_properties_button.bottom + 30))
        self.close_button_rect = None
        self.close_button_hovered = False

    def draw(self):
        """
        Draws the entire sidebar, including sections, buttons, and popups if active.
        """
        # Draw sidebar background and border
        pygame.draw.rect(self.screen, (50, 50, 50), self.sidebar_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.sidebar_rect, 2)

        # Bank Section
        pygame.draw.rect(self.screen, (0, 100, 0), self.bank_section)
        pygame.draw.rect(self.screen, (0, 0, 0), self.bank_section, 2)
        bank_title = pygame.font.Font(None, 28).render("Bank", True, (255, 255, 255))
        self.screen.blit(bank_title, (self.bank_section.x + 10, self.bank_section.y + 10))
        bank_balance_text = pygame.font.Font(None, 24).render(f"Balance: £{self.bank_balance}", True, (255, 255, 255))
        self.screen.blit(bank_balance_text, (self.bank_section.x + 10, self.bank_section.y + 40))

        # Buttons
        self.highlight_button(self.sell_property_button, (0, 0, 255), "Sell Property")
        self.highlight_button(self.sell_house_button, (0, 0, 255), "Sell House")

        # Player Info
        pygame.draw.rect(self.screen, (0, 0, 128), self.player_info_section)
        pygame.draw.rect(self.screen, (0, 0, 0), self.player_info_section, 2)

        if self.selected_player:
            player_token, player_balance = self.players[self.selected_player]

            player_text = pygame.font.Font(None, 26).render(f"Player {self.selected_player}", True, (255, 255, 255))
            token_text = pygame.font.Font(None, 22).render(f"Token: {player_token}", True, (255, 255, 255))
            balance_text = pygame.font.Font(None, 22).render(f"Balance: £{player_balance}", True, (255, 255, 255))

            self.screen.blit(player_text, (self.player_info_section.x + 10, self.player_info_section.y + 10))
            self.screen.blit(token_text, (self.player_info_section.x + 10, self.player_info_section.y + 40))
            self.screen.blit(balance_text, (self.player_info_section.x + 10, self.player_info_section.y + 65))

        # View Properties Button
        self.highlight_button(self.view_properties_button, (204, 204, 0), "View Properties")

        # Draw popup if active
        if self.active_popup:
            self.draw_property_popup()

    def highlight_button(self, button_rect, color, text):
        """
        Draws a button with hover effect.

        Parameters:
        button_rect (pygame.Rect): The rectangle area of the button.
        color (tuple): RGB color to use when hovered.
        text (str): Text to display on the button.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if button_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(self.screen, color, button_rect)
            button_text = pygame.font.Font(None, 26).render(text, True, (255, 255, 255))
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), button_rect)  # Default gray
            button_text = pygame.font.Font(None, 26).render(text, True, (0, 0, 0))

        self.screen.blit(button_text, (button_rect.x + 10, button_rect.y + 10))

    def draw_property_popup(self):
        """
        Draws the active popup with title and a close button.
        """
        pygame.draw.rect(self.screen, (200, 200, 200), self.popup_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.popup_rect, 2)

        title = pygame.font.Font(None, 22).render(self.popup_titles[self.active_popup], True, (0, 0, 0))
        self.screen.blit(title, (self.popup_rect.x + 10, self.popup_rect.y + 10))

        # Draw "Close" button
        self.close_button_rect = pygame.Rect(
            self.popup_rect.x + 50,
            self.popup_rect.y + self.popup_rect.height - 40,
            100, 30
        )
        self.highlight_close_button()

    def highlight_close_button(self):
        """
        Handles hover effect for the Close button in the popup.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.close_button_rect.collidepoint(mouse_x, mouse_y):
            self.close_button_hovered = True
            button_color = (180, 0, 0)
        else:
            self.close_button_hovered = False
            button_color = (255, 0, 0)

        pygame.draw.rect(self.screen, button_color, self.close_button_rect)
        close_text = pygame.font.Font(None, 20).render("Close", True, (255, 255, 255))
        self.screen.blit(close_text, (self.close_button_rect.x + 30, self.close_button_rect.y + 5))

    def handle_event(self, event):
        """
        Handles mouse clicks on buttons and the popup's close button.

        Parameters:
        event (pygame.Event): A single event from Pygame's event loop.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Main buttons
            if self.view_properties_button.collidepoint(x, y):
                self.toggle_popup("view_properties")
            elif self.sell_property_button.collidepoint(x, y):
                self.toggle_popup("sell_property")
            elif self.sell_house_button.collidepoint(x, y):
                self.toggle_popup("sell_house")

            # Popup close button
            if self.active_popup and self.close_button_rect and self.close_button_rect.collidepoint(x, y):
                self.active_popup = None

    def toggle_popup(self, popup_type):
        """
        Shows the specified popup or closes it if it's already open.

        Parameters:
        popup_type (str): The key representing which popup to toggle.
        """
        self.active_popup = popup_type if self.active_popup != popup_type else None
