import pygame

class AuctionPopup:
    def __init__(self, screen, players, property_obj, game):
        self.screen = screen
        self.players = players
        self.property = property_obj
        self.game = game
        self.visible = True

        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36)
        self.input_text = ""
        self.active_player_index = 0
        self.highest_bid = 0
        self.highest_bidder = None
        self.exited = set()

        self.input_box = pygame.Rect(460, 400, 280, 40)
        self.place_bid_button = pygame.Rect(460, 450, 130, 40)
        self.exit_button = pygame.Rect(610, 450, 130, 40)
        self.hovered_button = None

    def current_player(self):
        return self.players[self.active_player_index]

    def draw(self):
        if not self.visible:
            return

        pygame.draw.rect(self.screen, (20, 20, 20), (400, 200, 400, 320))
        pygame.draw.rect(self.screen, (255, 255, 255), (400, 200, 400, 320), 3)

        title = self.title_font.render(f"Auction: {self.property.name}", True, (255, 255, 255))
        player_name = self.font.render(f"Current Bidder: {self.current_player().name}", True, (255, 255, 255))
        highest = self.font.render(f"Highest Bid: £{self.highest_bid}", True, (255, 255, 255))

        self.screen.blit(title, (420, 210))
        self.screen.blit(player_name, (420, 250))
        self.screen.blit(highest, (420, 280))

        pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2)
        input_surface = self.font.render(self.input_text, True, (255, 255, 255))
        self.screen.blit(input_surface, (self.input_box.x + 10, self.input_box.y + 8))

        self.draw_button(self.place_bid_button, "Place Bid", "place")
        self.draw_button(self.exit_button, "Exit Auction", "exit")

    def draw_button(self, rect, text, key):
        color = (150, 150, 150) if self.hovered_button == key else (100, 100, 100)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, (rect.x + 10, rect.y + 10))

    def handle_event(self, event):
        if not self.visible:
            return

        if self.current_player().identity != 'Human':
            self.handle_bid()

        if event.type == pygame.MOUSEMOTION:
            self.hovered_button = None
            if self.place_bid_button.collidepoint(event.pos):
                self.hovered_button = "place"
            elif self.exit_button.collidepoint(event.pos):
                self.hovered_button = "exit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.place_bid_button.collidepoint(event.pos):
                self.handle_bid()
            elif self.exit_button.collidepoint(event.pos):
                self.exited.add(self.current_player())
                self.advance_turn()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.handle_bid()
            elif event.unicode.isdigit():
                self.input_text += event.unicode


    def handle_bid(self):
        try:
            player = self.current_player()

            if player.identity == "Human":
                bid_str = self.input_text.strip()

                if bid_str.lower() == "exit":
                    self.game.log_event(f"{player.name} has exited the auction.")
                    self.exited.add(player)
                    self.advance_turn()
                    self.input_text = ""
                    return

                bid = int(bid_str)

            else:
                bid = player.bot_bid(self.highest_bid, self.property)

                if bid == "exit":
                    self.game.log_event(f"{player.name} has exited the auction.")
                    self.exited.add(player)
                    self.advance_turn()
                    return

                try:
                    bid = int(bid)
                except ValueError:
                    self.game.log_event(f"{player.name} made an invalid bid.")
                    self.exited.add(player)
                    self.advance_turn()
                    return

            if not player.passed:
                self.game.log_event(f"{player.name} cannot bid — they haven't passed GO yet.")
                self.input_text = ""
                return

            if bid > self.highest_bid and bid <= player.balance:
                self.highest_bid = bid
                self.highest_bidder = player
                self.input_text = ""
                self.advance_turn()
                self.game.log_event(f"{player.name} bids £{bid} for {self.property.name}")
            else:
                self.game.log_event(
                    f"Invalid bid by {player.name}. It must be higher than £{self.highest_bid} and within their balance (£{player.balance})."
                )
                self.input_text = ""

        except ValueError:
            self.game.log_event(" Invalid input. Please enter a valid number.")
            self.input_text = ""


    def advance_turn(self):
        active_players = [p for p in self.players if p not in self.exited and p.passed]

        if len(active_players) == 1 and self.highest_bidder:
            self.end_auction()
            return

        if len(active_players) == 0:
            self.game.log_event(f"🏦 No one bid on {self.property.name}. Property remains unsold.")
            self.visible = False
            return

        for _ in range(len(self.players)):
            self.active_player_index = (self.active_player_index + 1) % len(self.players)
            next_player = self.players[self.active_player_index]
            if next_player not in self.exited and next_player.passed:
                return  

        self.end_auction()


        while True:
            self.active_player_index = (self.active_player_index + 1) % len(self.players)
            next_player = self.players[self.active_player_index]
            if next_player not in self.exited:
                break



    def end_auction(self):
        if self.highest_bidder:
            winner = self.highest_bidder
            self.property.owner = winner
            winner.balance -= self.highest_bid
            winner.owned_properties.append(self.property)
            self.game.log_event(f"🏦 {winner.name} won {self.property.name} for £{self.highest_bid}")
        else:
            self.property.owner = None
            self.game.log_event(f"❌ No one bid on {self.property.name}. It remains unowned.")

        self.visible = False
        self.input_text = ""
        self.highest_bid = 0
        self.highest_bidder = None
        self.active_player_index = 0
        self.exited.clear()


