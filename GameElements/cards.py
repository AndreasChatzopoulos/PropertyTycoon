import random


class Card:
    """
    Represents an individual action card (Pot Luck / Opportunity Knocks).
    
    Each card contains description and associated action, which is a function that 
    modifies the player or game state when executed. 
    """

    def __init__(self, description, action):
        """
        Initialise a card with description and action.

        Args: 
            description (str): Description of the card.
            action (Callable): Function that modifies player/game state.
        """
        self.description = description
        self.action = action  # Function that modifies player/game state

    def execute(self, player, game):
        """
        Executes the card's associated action and logs the effect.

        Args: 
            player (Player): The player who drew the card.
            game (Game): The current game instance.

        Returns: 
            None
        
        Side Effects:
            Calls game'es event logger.
            Modifies player state (balance, position, etc.)
            If player position changes, calls game to handle the new tile position.
        """
        initial_position = player.position
        message = f"{player.name} drew a card: {self.description}"
        print(message)
        game.log_event(message)
        self.action(player, game)  # Apply the card effect
        if player.position != initial_position:
            print(f"{player.name} moved to position {player.position}.")
            game.handle_position(player)  # Handle the new position

    


class CardDeck:
    """
    Represents a deck of action cards (Pot Luck / Opportunity Knocks) using FIFO principles.

    The deck is initialised with a list of card objects, which are shuffled once. 
    Cards are drawn from the top and placed at the bottom after execution, ensuring cycling behaviour. 
    """

    def __init__(self, cards):
        """
        Initialises the deck with a list of cards and shuffles them.

        Args: 
            cards (list): List of Card objects to be included in the deck. 
        """
        self.cards = cards
        random.shuffle(self.cards)

    def draw_card(self, player, game):
        """
         Draws a card from the top of the deck, executes its action, and places it at the bottom.
         
         Args:
            player (Player): The player who drew the card.
            game (Game): The current game instance.

        Returns: 
            Card | None: The drawn card, otherwise None. 

        Side Effects:
            Executes the card's effect (may change player or game state).
            Appends the used card to the bottom of the deck.
            Logs event in the game log
         
         """
        if not self.cards:
            print("No cards left in the deck.")
            return None

        card = self.cards.pop(0)  # FIFO removal
        card.execute(player, game)
        self.cards.append(card)  # Move to the bottom


class Cards:
    """
    Manages Pot Luck and Opportunity Knocks decks, including drawing and applying their effects. 

    This encapsulates card generation, drawing, reward / charge logic , and the handling of special 
    "Get out of jail free" cards. It serves as main interface for triggering card-related events during the game. 
    """

    def __init__(self):
        """
        Initialises the card system by creating and shuffling both decks. 
        """
        self.pot_luck_deck = self.create_pot_luck_deck()
        self.opportunity_knocks_deck = self.create_opportunity_knocks_deck()

    def charge_player(self, player, game, amount, reason):
        """
        Charges the player a specific amount. If the player cannot afford it, triggers bankruptcy. 

        Args: 
            player (Player): The player to charge.
            game (Game): The current game instance.
            amount (int): The amount to charge the player.
            reason (str): Reason for the charge.
        
        Side Effects:
            Deducts amount from player's balance.
            Logs event in the game log.
            Triggers bankruptcy if player cannot afford the charge.
        """

        if player.balance >= amount:
            player.balance -= amount
            game.log_event(f"{player.name} paid £{amount} for {reason}.")
        else:
            game.log_event(f"{player.name} cannot afford £{amount} for {reason}.")
            player.avoid_bankruptcy(amount, None)

    def reward_player(self, player, game, amount, reason):
        """
        Gives the player a reward (adds money to their balance).

        Args: 
            player (Player): The player to reward.
            game (Game): The current game instance.
            amount (int): The amount to reward the player.
            reason (str): Reason for the reward.
        
        Side Effects: 
            Adds amount to player's balance.
            Logs event in the game log.
        """

        player.balance += amount
        game.log_event(f"{player.name} received £{amount} for {reason}.")

    def create_pot_luck_deck(self):
        """
        Creates and returns a CardDeck object containing Pot Luck cards.

        Returns: 
            CardDeck: Initialised deck of Pot Luck cards with effects.
        """

        return CardDeck([
            Card("You inherit £200", lambda p, g: self.reward_player(p, g, 200, "inheritance")),
            Card("You have won 2nd prize in a beauty contest, collect £50",
                 lambda p, g: self.reward_player(p, g, 50, "beauty contest")),
            Card("Go back to the Old Creek", lambda p, g: p.move_player_to(2)),
            Card("Student loan refund. Collect £20", lambda p, g: self.reward_player(p, g, 20, "student loan refund")),
            Card("Bank error in your favour. Collect £200", lambda p, g: self.reward_player(p, g, 200, "bank error")),
            Card("Pay bill for textbooks of £100", lambda p, g: self.charge_player(p, g, 100, "textbooks")),
            Card("Advance to GO", lambda p, g: p.move_player_to(1)),
            Card("Get out of jail free", lambda p, g: setattr(p, 'get_out_of_jail_cards', p.get_out_of_jail_cards + 1)),
            Card("Go to jail. Do not pass GO, do not collect £200", lambda p, g: p.go_to_jail())
        ])

    def create_opportunity_knocks_deck(self):
        """
        Creates and returns a CardDeck object containing the Opportunity Knocks deck.
        
        Returns: 
            CardDeck: Initialised deck of Opportunity Knocks cards with effects.
        """
        return CardDeck([
            Card("Bank pays you a dividend of £50", lambda p, g: self.reward_player(p, g, 50, "dividend")),
            Card("Advance to Turing Heights", lambda p, g: p.move_player_to(40)),
            Card("Advance to Han Xin Gardens. If you pass GO, collect £200",
                 lambda p, g: p.move_player_to(25)),
            Card("Fined £15 for speeding", lambda p, g: self.charge_player(p, g, 15, "speeding")),
            Card("Pay university fees of £150", lambda p, g: self.charge_player(p, g, 150, "university fees")),
            Card("Take a trip to Hove station. If you pass GO collect £200", lambda p, g: p.move_player_to(16)),
            Card("You are assessed for repairs, £40/house, £115/hotel",
                 lambda p, g: p.assess_property_repair(g, 40, 115)),  # this is handled safely in Player
            Card("Go back 3 spaces", lambda p, g: setattr(p, 'position', max(1, p.position - 3))),
            Card("Drunk in charge of a hoverboard. Fine £30", lambda p, g: self.charge_player(p, g, 30, "hoverboard fine")),
            Card("Get out of jail free", lambda p, g: setattr(p, 'get_out_of_jail_cards', p.get_out_of_jail_cards + 1)),
            Card("Go to jail. Do not pass GO, do not collect £200", lambda p, g: p.go_to_jail())
        ])

    def draw_pot_luck_card(self, player, game):
        """
        Draws and applies a Pot Luck card for the player. 

        Args: 
            player (Player): The player who drew the card.
            game (Game): The current game instance.
        
        Side Effects:
            Executes the card's effect (may change player or game state).
            Logs event in the game log.
        """
        self.pot_luck_deck.draw_card(player, game)

    def draw_opportunity_knocks_card(self, player, game):
        """
        Draws and applies an Opportunity Knocks card for the player.

        Args: 
            player (Player): The player who drew the card.
            game (Game): The current game instance.
        
        Side Effects:   
            Executes the card's effect (may change player or game state).
            Logs event in the game log.
        """
        self.opportunity_knocks_deck.draw_card(player, game)

    def return_jail_card_to_bottom(self, deck="pot_luck"):
        """
        Returns a 'Get Out of Jail Free' card to the bottom of the specified deck.
        
        Args: 
            deck (str): The deck to return the card to ('pot_luck' or 'opportunity_knocks').

        Side Effects: 
            Appends a 'Get Out of Jail Free' card to the specified deck.
            Prints a confirmation message. 
        """
        
        card = Card("Get out of jail free", lambda p, g: setattr(p, 'get_out_of_jail_cards', p.get_out_of_jail_cards + 1))
        if deck == "pot_luck":
            self.pot_luck_deck.cards.append(card)
        elif deck == "opportunity_knocks":
            self.opportunity_knocks_deck.cards.append(card)
        print(f"'Get Out of Jail Free' card returned to {deck.replace('_', ' ').title()} deck.")
