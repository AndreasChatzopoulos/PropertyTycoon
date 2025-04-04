import pygame

class AuctionPopup:
    """
    Handles the interactive GUI-based property auction process during the game.

    This popup appears when a player declines to purchase an unowned property. 
    It allows all eligible players who have passed GO to participate in a live bidding session 
    via a graphical interface powered by Pygame.

    Attributes:
        screen (pygame.Surface): The Pygame display surface for rendering the popup.
        players (list): List of Player objects participating in the auction.
        property (Property): The property being auctioned.
        game (Game): Reference to the main game instance for logging and updates.
        visible (bool): Whether the popup is currently being shown.
        font (pygame.Font): Standard font used for rendering text.
        title_font (pygame.Font): Larger font used for the auction title.
        input_text (str): The current text in the bid input field.
        active_player_index (int): Index of the player currently bidding.
        highest_bid (int): The highest bid placed so far.
        highest_bidder (Player): The player who placed the highest bid.
        exited (set): Set of players who have exited the auction.
        input_box (pygame.Rect): Rect defining the text input box for bids.
        place_bid_button (pygame.Rect): Button rect for placing a bid.
        exit_button (pygame.Rect): Button rect for exiting the auction.
        hovered_button (str | None): Identifier of the button currently hovered (used for hover effects).
    """
    def __init__(self, screen, players, property_obj, game):
        """
        Initializes the auction popup interface for property bidding.

        Args:
            screen (pygame.Surface): The display surface where the popup will be rendered.
            players (list): A list of Player objects participating in the auction.
            property_obj (Property): The property object currently up for auction.
            game (Game): The main game instance managing state and event logging.

        Attributes Initialized:
            - visible (bool): Controls the visibility of the auction popup.
            - font (pygame.Font): Font used for regular UI text.
            - title_font (pygame.Font): Font used for the auction title.
            - input_text (str): The current bid input by the player.
            - active_player_index (int): Index of the currently active bidding player.
            - highest_bid (int): The highest bid placed during the auction.
            - highest_bidder (Player or None): The player who made the highest bid.
            - exited (set): Set of players who have exited the auction.
            - input_box (pygame.Rect): Rectangle for the bid input field.
            - place_bid_button (pygame.Rect): Button rectangle for placing a bid.
            - exit_button (pygame.Rect): Button rectangle for exiting the auction.
            - hovered_button (str or None): Identifier for the currently hovered button.
        """
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
        """
        Returns the player who is currently active in the auction.

        Returns:
            Player: The player whose turn it is to bid.
        """
        return self.players[self.active_player_index]

    def draw(self):
        """
        Draws the auction popup window on the screen with:
        - Title of the auction
        - Current bidder name
        - Current highest bid
        - Input box for entering bids
        - "Place Bid" and "Exit Auction" buttons

        Only renders if the popup is marked as visible.
        """
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
        """
        Draws a button with label and styling, including hover highlighting.

        Args:
            rect (pygame.Rect): The rectangle defining the button's area.
            text (str): The label to display on the button.
            key (str): The identifier used to track hover interaction for this button.
        """
        color = (150, 150, 150) if self.hovered_button == key else (100, 100, 100)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, (rect.x + 10, rect.y + 10))

    def handle_event(self, event):
        """
        Handles pygame events for the auction popup including mouse hover, clicks,
        and keyboard input (for placing bids or exiting).

        Args:
            event (pygame.event.Event): The event triggered by pygame's event queue.

        Side Effects:
            - Updates input text from keyboard
            - Advances auction turns
            - Places or exits bids
            - Updates visual button hover state
        """
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
        """
        Processes and validates the current player's bid, updating auction state accordingly.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If a human player enters non-numeric bid input.

        Side Effects:
            - Updates the highest bid and bidder if valid.
            - Logs auction events.
            - Advances the auction to the next player.
            - Ends the auction if conditions are met.
        """
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
        """
        Advances to the next eligible player in the auction turn order.

        Args:
            None

        Returns:
            None

        Side Effects:
            - Updates the active player index.
            - Ends the auction if only one or no eligible players remain.
        """
        active_players = [p for p in self.players if p not in self.exited and p.passed]

        if len(active_players) == 1 and self.highest_bidder:
            self.end_auction()
            return

        if len(active_players) == 0:
            self.game.log_event(f"No one bid on {self.property.name}. Property remains unsold.")
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
        """
        Finalizes the auction and handles post-auction state.

        Args:
            None

        Returns:
            None

        Side Effects:
            - Transfers ownership of the property to the highest bidder (if any).
            - Deducts the bid amount from the winner's balance.
            - Logs auction results.
            - Resets internal auction state variables.
        """
        if self.highest_bidder:
            winner = self.highest_bidder
            self.property.owner = winner
            winner.balance -= self.highest_bid
            winner.owned_properties.append(self.property)
            self.game.log_event(f"{winner.name} won {self.property.name} for £{self.highest_bid}")
        else:
            self.property.owner = None
            self.game.log_event(f"No one bid on {self.property.name}. It remains unowned.")

        self.visible = False
        self.input_text = ""
        self.highest_bid = 0
        self.highest_bidder = None
        self.active_player_index = 0
        self.exited.clear()


