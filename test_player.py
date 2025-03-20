import unittest
from unittest.mock import Mock, patch
import random
from player import Player

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.mock_game = Mock()
        self.mock_game.bank.balance = 10000
        self.mock_game.fines = 0
        self.mock_game.bank.properties = []
        self.player = Player("Alice", "Hat", "Human", self.mock_game)

    # __init__(self, name, token, game)
    def test_initialization(self):
        self.assertEqual(self.player.name, "Alice")
        self.assertEqual(self.player.token, "Hat")
        self.assertEqual(self.player.balance, 1500)
        self.assertEqual(self.player.position, 1)
        self.assertFalse(self.player.in_jail)
        self.assertEqual(self.player.get_out_of_jail_cards, 0)
        self.assertEqual(self.player.jail_turns, 0)
        self.assertEqual(self.player.consecutive_doubles, 0)
        self.assertEqual(self.player.owned_properties, [])

    # roll_dice(self)
    @patch("random.randint")
    def test_roll_dice(self, mock_randint):
        mock_randint.side_effect = [3, 3]
        die1, die2, double = self.player.roll_dice()
        self.assertEqual(die1, 3)
        self.assertEqual(die2, 3)
        self.assertTrue(double)

    # move(self)
    @patch("random.randint")
    def test_move_normal(self, mock_randint):
        mock_randint.side_effect = [4, 2]  # Rolls 4 and 2
        self.player.move()
        self.assertEqual(self.player.position, 7)
        self.assertFalse(self.player.passed)

    @patch("random.randint")
    def test_move_passing_go(self, mock_randint):
        self.player.position = 39
        mock_randint.side_effect = [2, 2]  # Rolls 2 and 2
        self.player.move()
        self.assertEqual(self.player.position, 3)
        self.assertTrue(self.player.passed)
        self.assertEqual(self.player.balance, 1700)  # Collected £200
        self.assertEqual(self.mock_game.bank.balance, 9800)

    @patch("random.randint")
    def test_move_double_three_times_goes_to_jail(self, mock_randint):
        mock_randint.side_effect = [2, 2, 3, 3, 5, 5]  # Three consecutive doubles
        self.player.move()  # 1st double
        self.assertEqual(self.player.position, 5)
        self.player.move()  # 2nd double
        self.assertEqual(self.player.position, 11)
        self.player.move()  # 3rd double -> Should go to jail
        self.assertTrue(self.player.in_jail)
        self.assertEqual(self.player.position, 11)
        self.assertEqual(self.player.consecutive_doubles, 0)

    # go_to_jail(self)
    def test_go_to_jail(self):
        self.player.go_to_jail()
        self.assertTrue(self.player.in_jail)
        self.assertEqual(self.player.position, 11)
        self.assertEqual(self.player.consecutive_doubles, 0)
        self.assertEqual(self.player.jail_turns, 0)

    # get_out_of_jail(self, double, turns)
    def test_get_out_of_jail_with_card(self):
        self.player.in_jail = True
        self.player.get_out_of_jail_cards = 1
        self.player.get_out_of_jail(double=False, turns=False)
        self.assertFalse(self.player.in_jail)
        self.assertEqual(self.player.get_out_of_jail_cards, 0)

    def test_get_out_of_jail_by_rolling_double(self):
        self.player.in_jail = True
        self.player.get_out_of_jail(double=True, turns=False)
        self.assertFalse(self.player.in_jail)
        self.assertEqual(self.player.jail_turns, 0)

    @patch("builtins.input", return_value="yes")
    def test_get_out_of_jail_by_paying_fine(self, mock_input):
        self.player.in_jail = True
        self.player.get_out_of_jail(double=False, turns=False)
        self.assertFalse(self.player.in_jail)
        self.assertEqual(self.player.balance, 1450)  # Paid £50 fine

    def test_get_out_of_jail_after_three_turns(self):
        self.player.in_jail = True
        self.player.jail_turns = 3
        self.player.get_out_of_jail(double=False, turns=True)
        self.assertFalse(self.player.in_jail)
        self.assertEqual(self.player.jail_turns, 0)

    # pay_tax(self, amount)
    def test_pay_tax(self):
        self.player.pay_tax(200)
        self.assertEqual(self.player.balance, 1300)

    # pay_rent(self, property_at_position, roll)
    def test_pay_rent_sufficient_balance(self):
        mock_property = Mock()
        mock_property.calculate_rent.return_value = 100
        mock_property.owner = Mock()
        mock_property.owner.name = "Bob"
        mock_property.owner.balance = 1500
        
        self.player.pay_rent(mock_property, 8)
        self.assertEqual(self.player.balance, 1400)
        self.assertEqual(mock_property.owner.balance, 1600)
    
    def test_pay_rent_insufficient_balance(self):
        mock_property = Mock()
        mock_property.calculate_rent.return_value = 2000
        mock_property.owner = Mock()
        mock_property.owner.name = "Bob"
        mock_property.owner.balance = 1500
        
        with patch.object(self.player, "avoid_bankruptcy") as mock_avoid:
            self.player.pay_rent(mock_property, 8)
            mock_avoid.assert_called_once_with(2000, mock_property.owner)

    # buy_property(self, property_at_position)
    def test_buy_property(self):
        mock_property = Mock()
        mock_property.price = 300
        mock_property.name = "Park Lane"
        
        self.player.buy_property(mock_property)
        self.assertEqual(self.player.balance, 1200)
        self.assertEqual(self.mock_game.bank.balance, 10300)
        self.assertEqual(mock_property.owner, self.player)
        self.assertIn(mock_property, self.player.owned_properties)
    
    # select_property(self, action)
    @patch("builtins.input", return_value="1")
    def test_select_property(self, mock_input):
        mock_property = Mock()
        mock_property.name = "Mayfair"
        self.player.owned_properties.append(mock_property)
        
        selected_property = self.player.select_property("sell")
        self.assertEqual(selected_property, mock_property)

    # avoid_bankruptcy(self, amount_due, creditor)
    @patch("builtins.input", side_effect=["1"])
    def test_avoid_bankruptcy_enough_balance(self, mock_input):
        self.player.balance = 1000
        creditor = Mock()
        creditor.balance = 500
        self.player.avoid_bankruptcy(500, creditor)
        self.assertEqual(self.player.balance, 500)
        self.assertEqual(creditor.balance, 1000)

    @patch("builtins.input", side_effect=["5"])
    def test_avoid_bankruptcy_declares_bankruptcy(self, mock_input):
        self.player.balance = 200
        creditor = Mock()
        with patch.object(self.player, "declare_bankruptcy") as mock_declare:
            self.player.avoid_bankruptcy(500, creditor)
            mock_declare.assert_called_once_with(creditor, 500)

    # declare_bankruptcy(self, creditor, debt)
    def test_declare_bankruptcy(self):
        creditor = Mock()
        creditor.name = "Bob"
        self.player.owned_properties = [Mock(), Mock()]
        self.player.declare_bankruptcy(creditor, 500)
        for prop in self.player.owned_properties:
            prop.transfer_property.assert_called_with(creditor)
        self.assertEqual(self.player.balance, 0)

    def test_declare_bankruptcy_no_creditor(self):
        self.player.owned_properties = [Mock(), Mock()]
        with patch.object(self.player, "return_properties_to_bank") as mock_return:
            self.player.declare_bankruptcy(None, 500)
            mock_return.assert_called_once()
        self.assertEqual(self.player.balance, 0)
    
    # return_properties_to_bank(self)
    def test_return_properties_to_bank(self):
        prop1, prop2 = Mock(), Mock()
        self.player.owned_properties = [prop1, prop2]
        self.player.return_properties_to_bank()
        self.assertEqual(len(self.player.owned_properties), 0)
        self.assertIn(prop1, self.mock_game.bank.properties)
        self.assertIn(prop2, self.mock_game.bank.properties)
        self.assertIsNone(prop1.owner)
        self.assertIsNone(prop2.owner)
        print(self.player.owned_properties)

    # move_player_to(self, new_position)
    def test_move_player_to(self):
        self.player.position = 10
        self.player.move_player_to(15)
        self.assertEqual(self.player.position, 15)
        self.assertEqual(self.player.balance, 1500)

    def test_move_player_to_passing_go(self):
        self.player.position = 30
        self.player.move_player_to(5)
        self.assertEqual(self.player.position, 5)
        self.assertEqual(self.player.balance, 1700)

    # assess_property_repair(self, game, house_cost, hotel_cost)
    def test_assess_property_repair(self):
        prop1, prop2 = Mock(), Mock()
        prop1.houses = 5
        prop2.houses = 3
        prop1.mortgaged = False
        prop2.mortgaged = False
        self.player.owned_properties = [prop1, prop2]
        self.player.assess_property_repair(self.mock_game, 100, 120)
        self.assertEqual(self.mock_game.fines, 920)
        self.assertEqual(self.player.balance, 580)
    
    # manage_property(self)

class TestPlayerBotMethods(unittest.TestCase):
    def setUp(self):
        self.mock_game = Mock()
        self.mock_game.bank.balance = 10000
        self.player = Player("Bot", "Car", "Basic Bot", self.mock_game)
        self.player.balance = 1000  # Setting balance for test cases

    # bot_bid(self, highest_bid, property)
    def test_bot_bid_lower_than_property_value(self):
        mock_property = Mock()
        mock_property.price = 200
        highest_bid = 150
        result = self.player.bot_bid(highest_bid, mock_property)
        self.assertEqual(result, "156")  # 150 + (200-150)*0.1 + 1 = 156

    def test_bot_bid_higher_than_property_value(self):
        mock_property = Mock()
        mock_property.price = 200
        highest_bid = 220
        result = self.player.bot_bid(highest_bid, mock_property)
        self.assertEqual(result, "240")  # 220 + (200 * 0.1) = 240

    def test_bot_bid_exceeds_1_5x_property_value(self):
        mock_property = Mock()
        mock_property.price = 200
        highest_bid = 290  # 1.5 * 200 = 300 max, bid would go over
        result = self.player.bot_bid(highest_bid, mock_property)
        self.assertEqual(result, "exit")

    def test_bot_bid_exceeds_balance(self):
        self.player.balance = 250
        mock_property = Mock()
        mock_property.price = 500
        highest_bid = 400
        result = self.player.bot_bid(highest_bid, mock_property)
        self.assertEqual(result, "exit")

    # bot_buy_property(self, property)
    def test_bot_buy_property_affordable(self):
        mock_property = Mock()
        mock_property.price = 500
        result = self.player.bot_buy_property(mock_property)
        self.assertEqual(result, "yes")

    def test_bot_buy_property_unaffordable(self):
        self.player.balance = 400
        mock_property = Mock()
        mock_property.price = 500
        result = self.player.bot_buy_property(mock_property)
        self.assertEqual(result, "no")

    # bot_get_out_of_jail(self)
    def test_bot_get_out_of_jail_can_afford(self):
        self.player.balance = 100
        result = self.player.bot_get_out_of_jail()
        self.assertEqual(result, "yes")

    def test_bot_get_out_of_jail_cannot_afford(self):
        self.player.balance = 30
        result = self.player.bot_get_out_of_jail()
        self.assertEqual(result, "no")

    # bot_avoid_bankruptcy(self, options, amount_due, creditor)
    def test_bot_avoid_bankruptcy(self):
        options = ["Sell Property", "Mortgage Property", "Declare Bankruptcy"]
        amount_due = 500
        creditor = Mock()
        result = self.player.bot_avoid_bankruptcy(options, amount_due, creditor)
        self.assertEqual(result, 3)  # Declares bankruptcy

    # bot_options(self)
    def test_bot_options(self):
        result = self.player.bot_options()
        self.assertEqual(result, 5)

    # bot_trade(self, offer_properties, request_properties, offer_money, request_money)
    def test_bot_trade(self):
        result = self.player.bot_trade([], [], 0, 0)
        self.assertEqual(result, "no")

if __name__ == "__main__":
    unittest.main()