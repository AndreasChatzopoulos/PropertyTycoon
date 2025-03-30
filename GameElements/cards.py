import random


class Card:
    """Represents an action card (Pot Luck / Opportunity Knocks)."""

    def __init__(self, description, action):
        self.description = description
        self.action = action  # Function that modifies player/game state

    def execute(self, player, game):
        """Executes the action associated with the card."""
        initial_position = player.position
        message = f"🃏 {player.name} drew a card: {self.description}"
        print(message)
        game.log_event(message)
        self.action(player, game)  # Apply the card effect
        if player.position != initial_position:
            print(f"🎲 {player.name} moved to position {player.position}.")
            game.handle_position(player)  # Handle the new position

    


class CardDeck:
    """Represents a deck of shuffled cards using FIFO behavior."""

    def __init__(self, cards):
        self.cards = cards
        random.shuffle(self.cards)

    def draw_card(self, player, game):
        """Draws a card, executes its action, and places it at the bottom."""
        if not self.cards:
            print("❌ No cards left in the deck.")
            return None

        card = self.cards.pop(0)  # FIFO removal
        card.execute(player, game)
        self.cards.append(card)  # Move to the bottom


class Cards:
    """Manages Pot Luck and Opportunity Knocks card decks."""

    def __init__(self):
        self.pot_luck_deck = self.create_pot_luck_deck()
        self.opportunity_knocks_deck = self.create_opportunity_knocks_deck()

    def create_pot_luck_deck(self):
        """Creates the Pot Luck deck."""
        pot_luck_cards = [
            Card("You inherit £200", lambda p, g: setattr(p, 'balance', p.balance + 200)),
            Card("You have won 2nd prize in a beauty contest, collect £50",
                 lambda p, g: setattr(p, 'balance', p.balance + 50)),
            Card("Go back to the Old Creek",
                 lambda p, g: p.move_player_to(2)),  # Fix: Use board position
            Card("Student loan refund. Collect £20",
                 lambda p, g: setattr(p, 'balance', p.balance + 20)),
            Card("Bank error in your favour. Collect £200",
                 lambda p, g: setattr(p, 'balance', p.balance + 200)),
            Card("Pay bill for textbooks of £100",
                 lambda p, g: setattr(p, 'balance', p.balance - 100)),
            Card("Advance to GO", lambda p, g: p.move_player_to(1)),  # GO position
            Card("Get out of jail free", lambda p, g: setattr(p, 'get_out_of_jail_cards', p.get_out_of_jail_cards + 1)),
            Card("Go to jail. Do not pass GO, do not collect £200", lambda p, g: p.go_to_jail())
        ]
        return CardDeck(pot_luck_cards)

    def create_opportunity_knocks_deck(self):
        """Creates the Opportunity Knocks deck."""
        opportunity_knocks_cards = [
            Card("Bank pays you a dividend of £50", lambda p, g: setattr(p, 'balance', p.balance + 50)),
            Card("Advance to Turing Heights", lambda p, g: p.move_player_to(40)),  # Fix: Uses board position
            Card("Advance to Han Xin Gardens. If you pass GO, collect £200",
                 lambda p, g: p.move_player_to(25)),  # Fix: Uses method to check GO
            Card("Fined £15 for speeding", lambda p, g: setattr(p, 'balance', p.balance - 15)),
            Card("Pay university fees of £150", lambda p, g: setattr(p, 'balance', p.balance - 150)),
            Card("Take a trip to Hove station. If you pass GO collect £200",
                 lambda p, g: p.move_player_to(16)),  # Fix: Uses method to check GO
            Card("You are assessed for repairs, £40/house, £115/hotel",
                 lambda p, g: p.assess_property_repair(g, 40, 115)),
            Card("Go back 3 spaces", lambda p, g: setattr(p, 'position', max(1, p.position - 3))),
            Card("Drunk in charge of a hoverboard. Fine £30", lambda p, g: setattr(p, 'balance', p.balance - 30)),
            Card("Get out of jail free", lambda p, g: setattr(p, 'get_out_of_jail_cards', p.get_out_of_jail_cards + 1)),
            Card("Go to jail. Do not pass GO, do not collect £200", lambda p, g: p.go_to_jail())
        ]
        return CardDeck(opportunity_knocks_cards)

    def draw_pot_luck_card(self, player, game):
        """Draws a Pot Luck card for the player."""
        self.pot_luck_deck.draw_card(player, game)

    def draw_opportunity_knocks_card(self, player, game):
        """Draws an Opportunity Knocks card for the player."""
        self.opportunity_knocks_deck.draw_card(player, game)

    def return_jail_card_to_bottom(self, deck="pot_luck"):
        """Returns a 'Get Out of Jail Free' card to the bottom of the specified deck."""
        card = Card("Get out of jail free", lambda p, g: setattr(p, 'get_out_of_jail_cards', p.get_out_of_jail_cards + 1))

        if deck == "pot_luck":
            self.pot_luck_deck.cards.append(card)
        elif deck == "opportunity_knocks":
            self.opportunity_knocks_deck.cards.append(card)

        print(f"🔁 'Get Out of Jail Free' card returned to {deck.replace('_', ' ').title()} deck.")

