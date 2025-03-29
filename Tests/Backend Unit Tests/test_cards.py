import unittest
from unittest.mock import MagicMock, patch
from GameElements.cards import Card, Cards, CardDeck

class TestCard(unittest.TestCase):

    def setUp(self):
        self.mock_player = MagicMock()
        self.mock_game = MagicMock()

    # __init__(self, description, action)
    def test_card_initialization(self):
        card_description = "You inherit £200"
        action = lambda p, g: setattr(p, 'balance', p.balance + 200)

        card = Card(card_description, action)

        self.assertEqual(card.description, card_description)
        self.assertEqual(card.action, action)

    # execute(self, player, game)
    def test_card_execute_balance_change(self):
        initial_balance = 100
        self.mock_player.balance = initial_balance
        card_description = "You inherit £200"
        action = lambda p, g: setattr(p, 'balance', p.balance + 200)

        card = Card(card_description, action)
        card.execute(self.mock_player, self.mock_game)

        self.assertEqual(self.mock_player.balance, initial_balance + 200)

    def test_card_execute_does_not_move_player(self):
        initial_position = 5
        self.mock_player.position = initial_position
        card_description = "No position change"
        action = lambda p, g: None
        card = Card(card_description, action)
        card.execute(self.mock_player, self.mock_game)

        self.mock_game.handle_position.assert_not_called()

    def test_card_execute_moves_player(self):
        initial_position = 5
        self.mock_player.position = initial_position
        card_description = "Go to jail"
        action = lambda p, g: setattr(p, 'position', 10) 
        card = Card(card_description, action)
        card.execute(self.mock_player, self.mock_game)

        self.mock_game.handle_position.assert_called_once_with(self.mock_player)

class TestCardDeck(unittest.TestCase):

    def setUp(self):
        self.mock_player = MagicMock()
        self.mock_game = MagicMock()

        # Create mock cards with dummy descriptions and actions
        self.card1 = MagicMock()
        self.card2 = MagicMock()
        self.card3 = MagicMock()
        self.card4 = MagicMock()

        self.card1.description = "Move 1 space"
        self.card1.action = lambda p, g: setattr(p, 'position', p.position + 1)
        self.card2.description = "Move 2 spaces"
        self.card2.action = lambda p, g: setattr(p, 'position', p.position + 2)
        self.card3.description = "Move 3 spaces"
        self.card3.action = lambda p, g: setattr(p, 'position', p.position + 3)
        self.card4.description = "Move 4 spaces"
        self.card4.action = lambda p, g: setattr(p, 'position', p.position + 4)
        
        # Initialize the card deck with 4 cards
        self.deck = CardDeck([self.card1, self.card2, self.card3, self.card4])

    # __init__
    def test_deck_initialization(self):
        self.assertEqual(len(self.deck.cards), 4)
        self.assertNotEqual(self.deck.cards, [self.card1, self.card2, self.card3, self.card4])

    # draw_card(self, player, game)
    @patch("builtins.print")
    def test_deck_empty(self, mock_print):
        self.deck.cards = []
        card = self.deck.draw_card(self.mock_player, self.mock_game)

        self.assertIsNone(card)
        mock_print.assert_called_once_with("❌ No cards left in the deck.")
    
    @patch("builtins.print")
    def test_draw_card_places_card_at_bottom(self, mock_print):
        initial_cards = self.deck.cards.copy()
        self.deck.draw_card(self.mock_player, self.mock_game)

        self.assertEqual(self.deck.cards[0], initial_cards[1]) 
        self.assertEqual(self.deck.cards[-1], initial_cards[0]) 


class TestCards(unittest.TestCase):

    def setUp(self):
        self.cards = Cards()
        self.mock_player = MagicMock()
        self.mock_game = MagicMock()
        self.cards.pot_luck_deck.draw_card = MagicMock()
        self.cards.opportunity_knocks_deck.draw_card = MagicMock()

    # create_pot_luck_deck(self)
    def test_create_pot_luck_deck(self):
        self.assertEqual(len(self.cards.pot_luck_deck.cards), 9)  # 9 Pot Luck cards
        self.assertIsInstance(self.cards.pot_luck_deck.cards[0], Card)

    # create_opportunity_knocks_deck(self)
    def test_create_opportunity_knocks_deck(self):
        self.assertEqual(len(self.cards.opportunity_knocks_deck.cards), 11)  # 11 Opportunity Knocks cards
        self.assertIsInstance(self.cards.opportunity_knocks_deck.cards[0], Card)

    #  draw_pot_luck_card(self, player, game)
    def test_draw_pot_luck_card(self):
        self.cards.draw_pot_luck_card(self.mock_player, self.mock_game)
        self.cards.pot_luck_deck.draw_card.assert_called_once_with(self.mock_player, self.mock_game)

    #  draw_opportunity_knocks_card(self, player, game)
    def test_draw_opportunity_knocks_card(self):
        self.cards.draw_opportunity_knocks_card(self.mock_player, self.mock_game)
        self.cards.opportunity_knocks_deck.draw_card.assert_called_once_with(self.mock_player, self.mock_game)

if __name__ == '__main__':
    unittest.main()