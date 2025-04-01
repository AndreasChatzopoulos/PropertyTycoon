import pygame

class BankruptcyPopup:
    def __init__(self, screen, player, amount_due, creditor=None):
        self.screen = screen
        self.player = player
        self.amount_due = amount_due
        self.creditor = creditor
        self.visible = True

        self.font = pygame.font.Font(None, 30) # Standard font
        self.small_font = pygame.font.Font(None, 24) # Smaller font for mortgaged properties
        self.selected_property = None
        self.property_rects = []

        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 20

        self.buttons = {}

        self.colors = {
            "popup_bg": (30, 30, 30),
            "border": (255, 255, 255),
            "text_light": (255, 255, 255),
            "text_error": (255, 0, 0),
            "text_warning": (255, 255, 0),
            "prop_default_bg": (80, 80, 80),
            "prop_selected_bg": (110, 110, 70),
            "button_default": (100, 100, 100),
            "button_hover": (130, 130, 130),
            "button_pay_default": (0, 200, 0),
            "button_pay_hover": (0, 230, 0),
            "button_bankrupt_default": (200, 0, 0),
            "button_bankrupt_hover": (220, 0, 0),
        }

    def draw(self):
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()

        popup_rect = pygame.Rect(200, 100, 800, 550)
        pygame.draw.rect(self.screen, self.colors["popup_bg"], popup_rect)
        pygame.draw.rect(self.screen, self.colors["border"], popup_rect, 3)

        title = self.font.render("Bankruptcy: Raise Funds", True, self.colors["text_light"])
        self.screen.blit(title, (popup_rect.x + 20, popup_rect.y + 10))

        self.screen.blit(self.font.render(f"Amount Due: £{self.amount_due}", True, self.colors["text_error"]), (popup_rect.x + 20, popup_rect.y + 50))
        self.screen.blit(self.font.render(f"Current Balance: £{self.player.balance}", True, self.colors["text_light"]), (popup_rect.x + 20, popup_rect.y + 80))
        still_needed = max(0, self.amount_due - self.player.balance)
        self.screen.blit(self.font.render(f"Still Needed: £{still_needed}", True, self.colors["text_warning"]), (popup_rect.x + 20, popup_rect.y + 110))

        self.property_rects.clear()
        list_area_rect = pygame.Rect(popup_rect.x + 10, popup_rect.y + 150, 420, 380)
        start_y = list_area_rect.y + 10 - self.scroll_offset
        max_y_in_list = start_y

        original_clip = self.screen.get_clip()

        for prop in self.player.owned_properties:
            prop_rect = pygame.Rect(list_area_rect.x + 10, start_y, 400, 40)
            self.property_rects.append((prop_rect, prop))

            if prop == self.selected_property:
                bg_color = self.colors["prop_selected_bg"]
            else:
                bg_color = self.colors["prop_default_bg"]

            visible_rect = prop_rect.clip(list_area_rect)
            if visible_rect.height > 0:

                pygame.draw.rect(self.screen, bg_color, visible_rect)
                pygame.draw.rect(self.screen, self.colors["border"], prop_rect, 2)

                info = f"{prop.name} | {'MORTGAGED' if prop.mortgaged else 'Active'} | Houses: {prop.houses}"

                # Choose font based on mortgaged status
                current_font = self.small_font if prop.mortgaged else self.font

                text_surface = current_font.render(info, True, self.colors["text_light"])
                text_pos_rect = text_surface.get_rect(midleft = (prop_rect.x + 10, prop_rect.centery))

                clip_rect_for_text = prop_rect.clip(list_area_rect)
                self.screen.set_clip(clip_rect_for_text)

                self.screen.blit(text_surface, text_pos_rect)

                self.screen.set_clip(original_clip)

            start_y += 50
            max_y_in_list = max(max_y_in_list, prop_rect.bottom)

        self.screen.set_clip(original_clip)

        content_height = max_y_in_list - (list_area_rect.y + 10 - self.scroll_offset)
        self.max_scroll = max(0, content_height - list_area_rect.height)

        self.buttons.clear()
        button_font = pygame.font.Font(None, 24) # Keep button font consistent
        actions_x = popup_rect.x + 450
        actions_y = popup_rect.y + 160

        if self.selected_property:
             mortgage_rect = pygame.Rect(actions_x, actions_y, 200, 40)
             self.buttons["mortgage"] = mortgage_rect
             is_hovered_mort = mortgage_rect.collidepoint(mouse_pos)
             color_mort = self.colors["button_hover"] if is_hovered_mort else self.colors["button_default"]
             pygame.draw.rect(self.screen, color_mort, mortgage_rect)
             pygame.draw.rect(self.screen, self.colors["border"], mortgage_rect, 2)
             label_mort = button_font.render("Mortgage", True, self.colors["text_light"])
             label_rect_mort = label_mort.get_rect(center=mortgage_rect.center)
             self.screen.blit(label_mort, label_rect_mort)

             can_sell_houses = (hasattr(self.selected_property, 'group') and
                                self.selected_property.group not in ["Station", "Utilities"] and
                                hasattr(self.selected_property, 'house_cost') and
                                self.selected_property.house_cost > 0 and
                                hasattr(self.selected_property, 'houses') and
                                self.selected_property.houses > 0)

             if can_sell_houses:
                 sell_house_rect = pygame.Rect(actions_x, actions_y + 60, 200, 40)
                 self.buttons["sell_house"] = sell_house_rect
                 is_hovered_sh = sell_house_rect.collidepoint(mouse_pos)
                 color_sh = self.colors["button_hover"] if is_hovered_sh else self.colors["button_default"]
                 pygame.draw.rect(self.screen, color_sh, sell_house_rect)
                 pygame.draw.rect(self.screen, self.colors["border"], sell_house_rect, 2)
                 label_sh = button_font.render("Sell House", True, self.colors["text_light"])
                 label_rect_sh = label_sh.get_rect(center=sell_house_rect.center)
                 self.screen.blit(label_sh, label_rect_sh)

             sell_prop_rect = pygame.Rect(actions_x, actions_y + 120, 200, 40)
             self.buttons["sell_property"] = sell_prop_rect
             is_hovered_sp = sell_prop_rect.collidepoint(mouse_pos)
             color_sp = self.colors["button_hover"] if is_hovered_sp else self.colors["button_default"]
             pygame.draw.rect(self.screen, color_sp, sell_prop_rect)
             pygame.draw.rect(self.screen, self.colors["border"], sell_prop_rect, 2)
             label_sp = button_font.render("Sell Property", True, self.colors["text_light"])
             label_rect_sp = label_sp.get_rect(center=sell_prop_rect.center)
             self.screen.blit(label_sp, label_rect_sp)


        if self.player.balance >= self.amount_due:
            pay_rect = pygame.Rect(actions_x, popup_rect.bottom - 140, 200, 50)
            self.buttons["pay"] = pay_rect
            is_hovered = pay_rect.collidepoint(mouse_pos)
            color = self.colors["button_pay_hover"] if is_hovered else self.colors["button_pay_default"]
            pygame.draw.rect(self.screen, color, pay_rect)
            pygame.draw.rect(self.screen, self.colors["border"], pay_rect, 2)
            label = button_font.render("✅ Pay & Continue", True, self.colors["text_light"])
            label_rect = label.get_rect(center=pay_rect.center)
            self.screen.blit(label, label_rect)

        bankrupt_rect = pygame.Rect(actions_x, popup_rect.bottom - 70, 200, 50)
        self.buttons["declare_bankruptcy"] = bankrupt_rect
        is_hovered = bankrupt_rect.collidepoint(mouse_pos)
        color = self.colors["button_bankrupt_hover"] if is_hovered else self.colors["button_bankrupt_default"]
        pygame.draw.rect(self.screen, color, bankrupt_rect)
        pygame.draw.rect(self.screen, self.colors["border"], bankrupt_rect, 2)
        label = button_font.render("Declare Bankruptcy", True, self.colors["text_light"])
        label_rect = label.get_rect(center=bankrupt_rect.center)
        self.screen.blit(label, label_rect)

        if not hasattr(self, "tip_logged"):
            if hasattr(self.player, 'game') and hasattr(self.player.game, 'log_event'):
                 self.player.game.log_event("TIP: Select a property from the list to see actions like Sell House/Mortgage.")
            self.tip_logged = True


    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                return
            elif event.button == 5:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
                return

            elif event.button == 1:
                mx, my = event.pos

                clicked_on_property = False
                for rect, prop in self.property_rects:
                    if rect.collidepoint(mx, my):
                        self.selected_property = prop
                        clicked_on_property = True
                        return

                if not clicked_on_property:
                    for key, rect in list(self.buttons.items()):
                        if rect.collidepoint(mx, my):
                            self.handle_button_click(key)
                            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)

    def handle_button_click(self, key):
        if key in ["mortgage", "sell_house", "sell_property"] and not self.selected_property:
             print("Error: No property selected for action.")
             return

        prop = self.selected_property
        game = self.player.game
        ui = game.ui if hasattr(game, 'ui') else None
        log_event = game.log_event if hasattr(game, "log_event") else print

        if key == "mortgage" and prop:
            if prop.mortgaged:
                log_event(f"ℹ️ {prop.name} is already mortgaged.")
                return
            if hasattr(prop, 'houses') and prop.houses > 0:
                 log_event(f"❌ Cannot mortgage {prop.name}. Sell houses first.")
                 return
            game.bank.mortgage_property(self.player, prop)

        elif key == "sell_house" and prop:
            if not hasattr(prop, 'houses') or prop.houses == 0:
                log_event(f"ℹ️ No houses to sell on {prop.name}.")
                return
            game.bank.sell_houses_to_the_bank(self.player, prop)

        elif key == "sell_property" and prop:
            if hasattr(prop, 'houses') and prop.houses > 0:
                log_event(f"❌ Cannot sell {prop.name} — sell houses first.")
                return
            game.bank.sell_property_to_the_bank(self.player, prop)
            self.selected_property = None

        elif key == "pay":
            if self.player.balance < self.amount_due:
                log_event(f"❌ {self.player.name} attempted to pay but doesn't have enough funds.")
                return

            self.player.balance -= self.amount_due
            debt_paid_to = "the Bank"
            if self.creditor:
                if hasattr(self.creditor, 'balance'):
                     self.creditor.balance += self.amount_due
                     debt_paid_to = self.creditor.name if hasattr(self.creditor, 'name') else 'Creditor'
                else:
                    log_event(f"⚠️ Creditor object invalid or missing 'balance' attribute.")


            log_event(f"✅ {self.player.name} paid £{self.amount_due} to {debt_paid_to}.")
            self.visible = False
            if ui: ui.bankruptcy_popup = None

        elif key == "declare_bankruptcy":
            if self.player not in game.players:
                log_event(f"ℹ️ {self.player.name} is already out of the game.")
                return

            log_event(f"☠️ {self.player.name} declared bankruptcy and is removed from the game.")
            self.player.declare_bankruptcy(self.creditor, self.amount_due)
            self.visible = False
            if ui: ui.bankruptcy_popup = None


    def player_has_options(self):
        for prop in self.player.owned_properties:
            if hasattr(prop, 'houses') and prop.houses > 0:
                return True
            if hasattr(prop, 'mortgaged') and not prop.mortgaged and hasattr(prop, 'houses') and prop.houses == 0:
                 if hasattr(prop, 'group') and prop.group not in ["Station", "Utilities"]:
                     return True
                 elif hasattr(prop, 'group') and prop.group in ["Station", "Utilities"]:
                     return True

        return False