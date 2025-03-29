import unittest
from unittest.mock import MagicMock, patch
from GameElements.bank import Bank
from GameElements.property import Property

class TestBank(unittest.TestCase):
    def setUp(self):
        self.bank = Bank()
        self.property = MagicMock()
        self.property.name = "Brighton Station"
        self.property.price = 400
        self.property.houses = 0
        self.property.house_cost = 100
        self.property.mortgaged = False
        self.property.group = "Blue"
        self.property.transfer_property = MagicMock()

        self.player1 = MagicMock()
        self.player1.name = "Alice"
        self.player1.balance = 1000
        self.player1.passed = True
        self.player1.identity = "Human"
        self.player1.owned_properties = [self.property]

        self.player2 = MagicMock()
        self.player2.name = "Bob"
        self.player2.balance = 1500
        self.player2.passed = True
        self.player2.identity = "Human"

        self.player3 = MagicMock()
        self.player3.name = "Charlie"
        self.player3.balance = 500
        self.player3.passed = False
        self.player3.identity = "Human"
    
    # __init__(self)
    def test_initialization(self):
        self.assertEqual(self.bank.balance, 50000)
        self.assertEqual(len(self.bank.properties), 28)
        expected_positions = {2, 4, 6, 7, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20,
                              22, 24, 25, 26, 27, 28, 29, 30, 32, 33, 35, 36, 38, 40}
        self.assertEqual(set(self.bank.properties.keys()), expected_positions)
        for prop in self.bank.properties.values():
            self.assertIsInstance(prop, Property)
    
    # auction_property(self, auction_property, players)
    def test_auction_cannot_start_if_not_enough_players_passed(self):
        self.bank.auction_property(self.property, [self.player1, self.player3])
        self.property.transfer_property.assert_not_called()

    def test_auction_transfers_property_to_highest_bidder(self):
        self.bank.bid_property = MagicMock(return_value=(self.player2, 300))
        self.bank.auction_property(self.property, [self.player1, self.player2])
        self.assertEqual(self.player2.balance, 1200)  # 1500 - 300
        self.property.transfer_property.assert_called_once_with(self.player2)

    # bid_property(self, active_bidders, property, highest_bid=0)
    @patch("builtins.input", side_effect=["500", "exit"])  
    def test_bid_property_human_bidding(self, mock_input):
        """Test human players bidding on a property"""
        active_bidders = [self.player1, self.player2]
        winner, final_bid = self.bank.bid_property(active_bidders, self.property)

        self.assertEqual(winner, self.player1)
        self.assertEqual(final_bid, 500)

    @patch("builtins.input", side_effect=["200", "600", "exit"])  
    def test_bid_property_multiple_human_bids(self, mock_input):
        """Test multiple bids from human players"""
        active_bidders = [self.player1, self.player2]
        winner, final_bid = self.bank.bid_property(active_bidders, self.property)

        self.assertEqual(winner, self.player2)
        self.assertEqual(final_bid, 600)
    
    @patch("builtins.input", side_effect=["300", "exit"])
    def test_bid_property_one_exit(self, mock_input):
        """Test when one player exits the auction"""
        active_bidders = [self.player1, self.player2]
        winner, final_bid = self.bank.bid_property(active_bidders, self.property)

        self.assertEqual(winner, self.player1)
        self.assertEqual(final_bid, 300)
    
    @patch("builtins.input", side_effect=["exit", "exit"])
    def test_bid_property_all_exit(self, mock_input):
        """Test when all players exit the auction"""
        active_bidders = [self.player1, self.player2]
        winner, final_bid = self.bank.bid_property(active_bidders, self.property)

        # The last remaining player should win by default with the starting bid
        self.assertEqual(winner, self.player2)
        self.assertEqual(final_bid, 0)
    
    @patch("builtins.input", side_effect=["450", "exit"])
    def test_bid_property_invalid_bid_then_exit(self, mock_input):
        """Test invalid bid (higher than balance) and exit"""
        self.player1.balance = 400  # Lower balance to make bid invalid
        active_bidders = [self.player1, self.player2]

        winner, final_bid = self.bank.bid_property(active_bidders, self.property)

        self.assertEqual(winner, self.player2)
        self.assertEqual(final_bid, 0)
    
    @patch("builtins.input", side_effect=["exit"])
    def test_bid_property_single_exit(self, mock_input):
        """Test a single player exiting immediately"""
        active_bidders = [self.player1]
        winner, final_bid = self.bank.bid_property(active_bidders, self.property)

        self.assertEqual(winner, self.player1)
        self.assertEqual(final_bid, 0)

    # sell_property_to_the_bank(self, plr, sold_property)
    def test_sell_unmortgaged_property_to_bank(self):
        """Selling an unmortgaged property should transfer full price."""
        initial_bank_balance = self.bank.balance
        initial_player_balance = self.player1.balance

        self.bank.sell_property_to_the_bank(self.player1, self.property)

        self.assertEqual(self.bank.balance, initial_bank_balance - 400)
        self.assertEqual(self.player1.balance, initial_player_balance + 400)
        self.assertNotIn(self.property, self.player1.owned_properties)
        self.assertIsNone(self.property.owner)
    
    def test_sell_mortgaged_property(self):
        """Selling a mortgaged property should transfer half the price."""
        self.property.mortgaged = True
        initial_bank_balance = self.bank.balance
        initial_player_balance = self.player1.balance

        self.bank.sell_property_to_the_bank(self.player1, self.property)

        self.assertEqual(self.bank.balance, initial_bank_balance - 200)  # 400 / 2
        self.assertEqual(self.player1.balance, initial_player_balance + 200)
        self.assertFalse(self.property.mortgaged)
        self.assertNotIn(self.property, self.player1.owned_properties)
        self.assertIsNone(self.property.owner)
    
    def test_cannot_sell_property_with_houses(self):
        """A property with houses cannot be sold."""
        self.property.houses = 1
        initial_player_balance = self.player1.balance

        self.bank.sell_property_to_the_bank(self.player1, self.property)

        self.assertEqual(self.player1.balance, initial_player_balance)
        self.assertIn(self.property, self.player1.owned_properties)

    def test_cannot_sell_unowned_property(self):
        """A player cannot sell a property they don’t own."""
        self.bank.sell_property_to_the_bank(self.player2, self.property)

        self.assertIn(self.property, self.player1.owned_properties) # No change

    # sell_houses_to_the_bank(self, plr, selected_property)
    @patch('builtins.input', side_effect=["2"])
    def test_sell_houses_valid_input(self, mock_input):
        """Selling houses should increase player and bank balance, decrease house count."""
        self.property.houses = 3
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance
        initial_houses = self.property.houses

        self.bank.sell_houses_to_the_bank(self.player1, self.property)

        self.assertEqual(self.player1.balance, initial_player_balance + 200)  # 2 houses * 100 each
        self.assertEqual(self.bank.balance, initial_bank_balance + 200)
        self.assertEqual(self.property.houses, initial_houses - 2)
    
    @patch('builtins.input', side_effect=["0", "4", "1"])
    def test_sell_houses_invalid_then_valid(self, mock_input):
        """Invalid inputs should prompt retry; valid input should process normally."""
        self.property.houses = 3
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance
        initial_houses = self.property.houses

        self.bank.sell_houses_to_the_bank(self.player1, self.property)

        self.assertEqual(self.player1.balance, initial_player_balance + 100)  # 1 house * 100 each
        self.assertEqual(self.bank.balance, initial_bank_balance + 100)
        self.assertEqual(self.property.houses, initial_houses - 1)

    @patch('builtins.input', side_effect=["a", "-1", "3"])
    def test_sell_houses_non_numeric_input(self, mock_input):
        """Non-numeric input should prompt retry until valid input is given."""
        self.property.houses = 3
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance
        initial_houses = self.property.houses

        self.bank.sell_houses_to_the_bank(self.player1, self.property)

        self.assertEqual(self.player1.balance, initial_player_balance + 300)  # 3 houses * 100 each
        self.assertEqual(self.bank.balance, initial_bank_balance + 300)
        self.assertEqual(self.property.houses, initial_houses - 3)

    def test_sell_houses_no_houses(self):
        """Trying to sell houses when none exist should do nothing."""
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance

        self.bank.sell_houses_to_the_bank(self.player1, self.property)

        self.assertEqual(self.player1.balance, initial_player_balance)
        self.assertEqual(self.bank.balance, initial_bank_balance)
        self.assertEqual(self.property.houses, 0)

    # mortgage_property(self, plr, selected_property)
    def test_successful_mortgage(self):
        """Test if a property can be successfully mortgaged."""
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance

        self.bank.mortgage_property(self.player1, self.property)

        self.assertTrue(self.property.mortgaged)
        self.assertEqual(self.player1.balance, initial_player_balance - 200)  # 400 / 2
        self.assertEqual(self.bank.balance, initial_bank_balance + 200)
    
    def test_mortgage_already_mortgaged_property(self):
        """Test trying to mortgage an already mortgaged property (should not change anything)."""
        self.property.mortgaged = True  # Already mortgaged
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance

        self.bank.mortgage_property(self.player1, self.property)

        self.assertTrue(self.property.mortgaged)  # Should remain mortgaged
        self.assertEqual(self.player1.balance, initial_player_balance) 
        self.assertEqual(self.bank.balance, initial_bank_balance)
    
    def test_mortgage_property_with_houses(self):
        """Test trying to mortgage a property that has houses (should not be allowed)."""
        self.property.houses = 2  # Property has houses
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance

        self.bank.mortgage_property(self.player1, self.property)

        self.assertFalse(self.property.mortgaged)  # Mortgage status should not change
        self.assertEqual(self.player1.balance, initial_player_balance)
        self.assertEqual(self.bank.balance, initial_bank_balance)

    # unmortgage_property(self, plr, selected_property)
    def test_successful_unmortgage(self):
        """Test if a property can be successfully unmortgaged."""
        self.property.mortgaged = True
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance

        self.bank.unmortgage_property(self.player1, self.property)

        self.assertFalse(self.property.mortgaged)
        self.assertEqual(self.player1.balance, initial_player_balance + 200)  # 400 / 2
        self.assertEqual(self.bank.balance, initial_bank_balance - 200)

    def test_unmortgage_not_mortgaged_property(self):
        """Test trying to unmortgage a property that is not mortgaged (should not change anything)."""
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance

        self.bank.unmortgage_property(self.player1, self.property)

        self.assertFalse(self.property.mortgaged)  # Should remain unmortgaged
        self.assertEqual(self.player1.balance, initial_player_balance) 
        self.assertEqual(self.bank.balance, initial_bank_balance)
    
    def test_unmortgage_insufficient_funds(self):
        """Test trying to unmortgage a property when the player has insufficient funds (should not be allowed)."""
        self.property.mortgaged = True
        self.player1.balance = 100  # Not enough to unmortgage
        initial_bank_balance = self.bank.balance

        self.bank.unmortgage_property(self.player1, self.property)

        self.assertTrue(self.property.mortgaged)  # Should still be mortgaged
        self.assertEqual(self.player1.balance, 100)  # No balance change
        self.assertEqual(self.bank.balance, initial_bank_balance)
    
    # build(self, number_of_houses, selected_property, plr)
    def test_successful_build(self):
        """Test if houses can be successfully built when conditions are met."""
        self.property.owner = self.player1
        self.property.check_completion = MagicMock(return_value=True)
        initial_player_balance = self.player1.balance
        initial_bank_balance = self.bank.balance
        initial_house_count = self.property.houses

        self.bank.build(2, self.property, self.player1)

        self.assertEqual(self.property.houses, initial_house_count + 2)  # House count increases
        self.assertEqual(self.player1.balance, initial_player_balance - 200)  # 2 * 100
        self.assertEqual(self.bank.balance, initial_bank_balance + 200)
    
    def test_build_not_completed_group(self):
        """Test attempting to build when the property group is not completed."""
        self.property.check_completion.return_value = False  # Property not fully owned
        initial_house_count = self.property.houses

        self.bank.build(2, self.property, self.player1)

        self.assertEqual(self.property.houses, initial_house_count)
    
    def test_build_insufficient_funds(self):
        """Test attempting to build when the player doesn't have enough money."""
        self.property.owner = self.player1
        self.property.check_completion = MagicMock(return_value=True)
        self.player1.balance = 50  # Not enough to build

        initial_house_count = self.property.houses
        initial_bank_balance = self.bank.balance

        self.bank.build(2, self.property, self.player1)

        self.assertEqual(self.property.houses, initial_house_count)  # No house added
        self.assertEqual(self.bank.balance, initial_bank_balance)
    
    def test_build_exceeds_max_houses(self):
        """Test attempting to build when the number of houses exceeds the max limit (5)."""
        self.property.owner = self.player1
        self.property.check_completion = MagicMock(return_value=True)
        self.property.houses = 4  # Already has 4 houses

        initial_bank_balance = self.bank.balance

        self.bank.build(2, self.property, self.player1)

        self.assertEqual(self.property.houses, 4)  # House count should not exceed 5
        self.assertEqual(self.bank.balance, initial_bank_balance)

    # pay_player(self, player, amount)
    def test_pay_player_success(self):
        """Test successful payment from bank to player."""
        initial_bank_balance = self.bank.balance
        initial_player_balance = self.player1.balance

        self.bank.pay_player(self.player1, 500)

        self.assertEqual(self.bank.balance, initial_bank_balance - 500)  # Bank decreases
        self.assertEqual(self.player1.balance, initial_player_balance + 500)

    # receive_payment(self, player, amount)
    def test_receive_payment_success(self):
        """Test successful payment from player to bank."""
        initial_bank_balance = self.bank.balance
        initial_player_balance = self.player1.balance

        self.bank.receive_payment(self.player1, 500)

        self.assertEqual(self.bank.balance, initial_bank_balance + 500)  # Bank increases
        self.assertEqual(self.player1.balance, initial_player_balance - 500)

if __name__ == '__main__':
    unittest.main()