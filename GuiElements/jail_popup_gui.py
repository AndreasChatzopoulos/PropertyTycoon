import pygame

class JailPopup:
    def __init__(self, screen, player, game):
        self.screen = screen
        self.player = player
        self.game = game
        self.visible = True
         

        self.font = pygame.font.SysFont(None, 28)
        self.hovered_button = None

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
            
            if self.hovered_button == key:
                color = (150, 150, 150)  
            else:
                color = (100, 100, 100)  

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
                    self.visible = False  
                    return


    def handle_choice(self, choice):
        player = self.player
        game = self.game

        if choice == "roll":
            #  Flag player to roll animated dice in main loop
            player.wants_to_roll_in_jail = True
            self.visible = False

        elif choice == "pay":
            if player.balance >= 50:
                player.balance -= 50
                game.fines += 50
                player.jail_turns = 0
                player.in_jail = False
                player.wants_to_roll_after_paying_jail = True  #  New flag
                game.log_event(f"💸 {player.name} paid £50 to get out of jail.")
                self.visible = False
            else:
                game.log_event(f" {player.name} doesn't have enough money to pay.")

        elif choice == "card":
            if player.get_out_of_jail_cards > 0:
                player.get_out_of_jail_cards -= 1
                player.jail_turns = 0
                player.in_jail = False
                player.position = 11  # Just Visiting
                if hasattr(game.cards, "return_jail_card_to_bottom"):
                    game.cards.return_jail_card_to_bottom()
                game.log_event(f" {player.name} used a Get Out of Jail Free card.")
                self.visible = False
            else:
                game.log_event(f" {player.name} has no Get Out of Jail Free cards.")

        elif choice == "wait":
            player.jail_turns += 1
            game.log_event(f"{player.name} chose to wait in jail (Turn {player.jail_turns}/3).")
            if player.jail_turns >= 3:
                player.jail_turns = 0
                player.in_jail = False
                game.log_event(f"{player.name} has served their sentence and is now Just Visiting.")
            self.visible = False
