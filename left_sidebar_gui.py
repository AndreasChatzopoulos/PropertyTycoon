import pygame

class LeftSidebar:
    """
    Represents the left sidebar of the Monopoly game GUI.

    Displays:
    - Bank balance
    - Selected player information
    - A 'Manage Property' button
    - A scrollable property list with property action buttons

    Includes support for mouse interaction, property selection, and event logging.
    """

    def __init__(self, screen, event_logger=None):
        """
        Initialize the LeftSidebar layout and data.

        Args:
            screen: The main Pygame surface to draw onto.
            event_logger: Optional function to log actions (e.g., to a sidebar log).
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.just_scrolled = False  # Used to prevent mis-clicks after scrolling

        self.sidebar_width = 200
        self.sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, self.height)

        # Sections layout
        self.bank_section = pygame.Rect(10, 10, self.sidebar_width - 20, 80)
        self.player_info_section = pygame.Rect(10, self.bank_section.bottom + 10, self.sidebar_width - 20, 100)
        self.manage_property_button = pygame.Rect(10, self.player_info_section.bottom + 10, self.sidebar_width - 20, 40)

        # Example bank/player data
        self.bank_balance = 50000
        self.selected_player = 1
        self.players = {
            1: ("Hatstand", 1500),
            2: ("Boot", 1400)
        }

        # Property management state
        self.owned_properties = [  # Example list of owned properties
            "Old Kent Road", "Whitechapel Road", "King's Cross Station", "Euston Road", "Pentonville Road",
            "Pall Mall", "Whitehall", "Northumberland Avenue", "Bow Street", "Marlborough Street",
            "Vine Street", "Strand"
        ]
        self.selected_property_name = None
        self.property_buttons = []
        self.scroll_offset = 0

        self.active_popup = None
        self.popup_rect = pygame.Rect(
            10, self.manage_property_button.bottom + 10,
            self.sidebar_width - 20,
            self.height - (self.manage_property_button.bottom + 30)
        )

        # Action buttons in the popup
        self.popup_buttons = {
            "build_house": pygame.Rect(0, 0, self.sidebar_width - 20, 30),
            "build_hotel": pygame.Rect(0, 0, self.sidebar_width - 20, 30),
            "mortgage": pygame.Rect(0, 0, self.sidebar_width - 20, 30),
            "sell_house": pygame.Rect(0, 0, self.sidebar_width - 20, 30),
        }

        self.log_event = event_logger if event_logger else print  # Logger fallback

    def draw(self):
        """Draw the entire left sidebar and its components."""
        pygame.draw.rect(self.screen, (50, 50, 50), self.sidebar_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.sidebar_rect, 2)

        # Bank section
        pygame.draw.rect(self.screen, (0, 100, 0), self.bank_section)
        pygame.draw.rect(self.screen, (0, 0, 0), self.bank_section, 2)
        font = pygame.font.Font(None, 24)
        self.screen.blit(font.render("Bank", True, (255, 255, 255)), (self.bank_section.x + 10, self.bank_section.y + 10))
        self.screen.blit(font.render(f"\u00a3{self.bank_balance}", True, (255, 255, 255)), (self.bank_section.x + 10, self.bank_section.y + 40))

        # Player section
        pygame.draw.rect(self.screen, (0, 0, 128), self.player_info_section)
        pygame.draw.rect(self.screen, (0, 0, 0), self.player_info_section, 2)
        token, balance = self.players[self.selected_player]
        self.screen.blit(font.render(f"Player {self.selected_player}", True, (255, 255, 255)), (self.player_info_section.x + 10, self.player_info_section.y + 10))
        self.screen.blit(font.render(f"Token: {token}", True, (255, 255, 255)), (self.player_info_section.x + 10, self.player_info_section.y + 40))
        self.screen.blit(font.render(f"\u00a3{balance}", True, (255, 255, 255)), (self.player_info_section.x + 10, self.player_info_section.y + 65))

        self.highlight_button(self.manage_property_button, (204, 204, 0), "Manage Property")

        if self.active_popup == "manage_properties":
            self.draw_manage_properties_popup()

    def draw_manage_properties_popup(self):
        """Render the scrollable list of properties and action buttons."""
        pygame.draw.rect(self.screen, (200, 200, 200), self.popup_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.popup_rect, 2)

        self.property_buttons = []
        prop_font = pygame.font.Font(None, 18)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        visible_count = 8
        item_height = 26
        start_y = self.popup_rect.y + 10
        max_offset = max(0, len(self.owned_properties) - visible_count)
        scroll_area_height = visible_count * item_height

        # Render visible property buttons
        for i, prop in enumerate(self.owned_properties):
            display_index = i - self.scroll_offset
            if 0 <= display_index < visible_count:
                y = start_y + display_index * item_height
                prop_rect = pygame.Rect(self.popup_rect.x + 10, y, self.popup_rect.width - 30, 22)
                is_hovered = prop_rect.collidepoint(mouse_x, mouse_y)
                is_selected = (prop == self.selected_property_name)

                bg_color = (0, 100, 255) if is_selected else (240, 240, 240) if is_hovered else (220, 220, 220)
                text_color = (255, 255, 255) if is_selected else (0, 0, 0)

                pygame.draw.rect(self.screen, bg_color, prop_rect, border_radius=3)
                pygame.draw.rect(self.screen, (0, 0, 0), prop_rect, 1, border_radius=3)
                label = prop_font.render(prop, True, text_color)
                self.screen.blit(label, (prop_rect.x + 5, prop_rect.y + 3))
                self.property_buttons.append((prop_rect, prop))

        # Draw scrollbar if needed
        if len(self.owned_properties) > visible_count:
            scrollbar_x = self.popup_rect.right - 15
            scrollbar_y = start_y
            bar_height = max(20, int(scroll_area_height * (visible_count / len(self.owned_properties))))
            scroll_ratio = self.scroll_offset / max_offset if max_offset > 0 else 0
            bar_y = scrollbar_y + int((scroll_area_height - bar_height) * scroll_ratio)

            pygame.draw.rect(self.screen, (180, 180, 180), (scrollbar_x, scrollbar_y, 8, scroll_area_height), border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 100), (scrollbar_x, bar_y, 8, bar_height), border_radius=4)

        # Action buttons (build, mortgage, etc.)
        font = pygame.font.Font(None, 20)
        start_y = self.popup_rect.bottom - 150
        spacing = 35

        for i, (key, rect) in enumerate(self.popup_buttons.items()):
            rect.x = self.popup_rect.x + 10
            rect.y = start_y + i * spacing
            rect.width = self.popup_rect.width - 20

            is_hovered = rect.collidepoint(pygame.mouse.get_pos())
            base_color = (0, 180, 0) if key in ["build_house", "build_hotel"] else (0, 120, 255)
            base_color = base_color if not is_hovered else [min(c + 30, 255) for c in base_color]

            pygame.draw.rect(self.screen, base_color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1, border_radius=5)
            label = font.render(key.replace("_", " ").title(), True, (255, 255, 255))
            self.screen.blit(label, (rect.x + 10, rect.y + 5))

    def highlight_button(self, button_rect, color, text):
        """Render a button with hover effect."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = button_rect.collidepoint(mouse_x, mouse_y)
        bg = color if hovered else (100, 100, 100)
        fg = (255, 255, 255) if hovered else (0, 0, 0)

        pygame.draw.rect(self.screen, bg, button_rect)
        label = pygame.font.Font(None, 26).render(text, True, fg)
        self.screen.blit(label, (button_rect.x + 10, button_rect.y + 10))

    def handle_event(self, event):
        """Handle mouse interaction for sidebar and property popup."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.manage_property_button.collidepoint(x, y):
                self.toggle_popup("manage_properties")

            elif self.active_popup == "manage_properties" and not self.just_scrolled:
                for rect, prop_name in self.property_buttons:
                    if rect.collidepoint(x, y):
                        self.selected_property_name = prop_name

                for key, rect in self.popup_buttons.items():
                    if rect.collidepoint(x, y):
                        if self.selected_property_name:
                            self.log_event(f"{key.replace('_', ' ').title()} clicked for {self.selected_property_name}")
                        else:
                            self.log_event(f"{key.replace('_', ' ').title()} clicked (no property selected)")

            self.just_scrolled = False  # Reset flag

        elif event.type == pygame.MOUSEWHEEL and self.active_popup == "manage_properties":
            self.scroll_offset -= event.y
            self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(self.owned_properties) - 8)))
            self.just_scrolled = True

    def toggle_popup(self, popup_type):
        """Show or hide a popup menu in the sidebar."""
        self.active_popup = popup_type if self.active_popup != popup_type else None
