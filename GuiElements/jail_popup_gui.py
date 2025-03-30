import pygame

class JailPopup:
    def __init__(self, screen, player, game):
        self.screen = screen
        self.player = player
        self.game = game
        self.visible = True
         

        self.font = pygame.font.SysFont(None, 28)
        self.hovered_button = None

        # Button dimensions
        self.button_width = 250
        self.button_height = 40
        self.buttons = {
            "roll": pygame.Rect(475, 250, self.button_width, self.button_height),
            "pay": pygame.Rect(475, 300, self.button_width, self.button_height),
            "card": pygame.Rect(475, 350, self.button_width, self.button_height),
            "wait": pygame.Rect(475, 400, self.button_width, self.button_height),
        }

    def draw(self):
        if not self.visible:
            return

        pygame.draw.rect(self.screen, (30, 30, 30), (400, 200, 400, 300))
        pygame.draw.rect(self.screen, (255, 255, 255), (400, 200, 400, 300), 3)

        title = self.font.render(f"{self.player.name} is in Jail!", True, (255, 255, 255))
        self.screen.blit(title, (460, 210))

        options = [
            ("Roll for Doubles", "roll"),
            ("Pay £50 to Get Out", "pay"),
            ("Use Jail Free Card", "card"),
            ("Wait Turn (Skip)", "wait"),
        ]

        for label, key in options:
            btn_rect = self.buttons[key]
            
            # Highlight if hovered
            if self.hovered_button == key:
                color = (150, 150, 150)  # lighter gray on hover
            else:
                color = (100, 100, 100)  # default button color

            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 2)

            text = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

            
    def update_hover(self, mouse_pos):
        self.hovered_button = None
        for key, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                self.hovered_button = key
                break

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEMOTION:
            self.update_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for key, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.handle_choice(key)
                    self.visible = False  # Close the popup after selection
                    return


    def handle_choice(self, choice):
        if choice == "roll":
            die1, die2, is_double = self.player.roll_dice()
            if is_double:
                self.player.jail_turns = 0
                self.player.in_jail = False
                self.game.log_event(f"🎲 {self.player.name} rolled a double and escaped jail!")
                self.player.move(die1, die2, is_double)
                self.visible = False
            else:
                self.player.jail_turns += 1
                self.game.log_event(f"{self.player.name} did not roll a double (Rolled {die1} + {die2}).")
                if self.player.jail_turns >= 2:
                    self.player.in_jail = False
                    self.player.jail_turns = 0
                    self.player.position = 11  # Just Visiting
                    self.game.log_event(f"{self.player.name} has served their time and is now Just Visiting.")
                self.visible = False

        elif choice == "pay":
            if self.player.balance >= 50:
                self.player.balance -= 50
                self.game.fines += 50
                self.player.jail_turns = 0
                self.player.in_jail = False
                self.player.position = 11  # Just Visiting
                self.game.log_event(f"💸 {self.player.name} paid £50 to get out of jail.")
                self.visible = False
            else:
                self.game.log_event(f"❌ {self.player.name} doesn't have enough money to pay.")
                # Let them pick again

        elif choice == "card":
            if self.player.get_out_of_jail_cards > 0:
                self.player.get_out_of_jail_cards -= 1
                self.player.jail_turns = 0
                self.player.in_jail = False
                self.player.position = 11  # Just Visiting
                if hasattr(self.game.cards, "return_jail_card_to_bottom"):
                    self.game.cards.return_jail_card_to_bottom()
                self.game.log_event(f"🎟️ {self.player.name} used a Get Out of Jail Free card.")
                self.visible = False
            else:
                self.game.log_event(f"❌ {self.player.name} has no Get Out of Jail Free cards.")
                # ❌ Don't close popup — let them try another option

        elif choice == "wait":
            self.player.jail_turns += 1
            self.game.log_event(f"{self.player.name} chose to wait in jail (Turn {self.player.jail_turns}/2).")
            if self.player.jail_turns >= 2:
                self.player.jail_turns = 0
                self.player.in_jail = False
                self.player.position = 11  # Just Visiting
                self.game.log_event(f"{self.player.name} has served their sentence and is now Just Visiting.")
            self.visible = False
