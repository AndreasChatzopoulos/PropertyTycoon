import unittest
from unittest.mock import MagicMock, patch
from game import Game
from player import Player
from bank import Bank
from cards import Cards

class TestGame(unittest.TestCase):
    def setUp(self):
        self.player_names = ["Alice", "Bob"]
        self.tokens = ["Car", "Hat"]
        self.identities = ["Human", "Human"]

        self.game = Game(self.player_names, self.tokens, self.identities)
        
        self.mock_player = MagicMock(spec=Player)
        self.mock_player.name = "Alice"
        self.mock_player.token = "Car"
        self.mock_player.identity = "Human"
        self.mock_player.position = 0
        self.mock_player.in_jail = False
        self.mock_player.balance = 1500
        self.mock_player.passed = False
        self.mock_player.consecutive_doubles = 0
        self.mock_player.move = MagicMock()
        self.mock_player.go_to_jail = MagicMock()
        self.mock_player.owned_properties = [MagicMock(name="Park Lane"), MagicMock(name="Mayfair")]

        self.other_mock_player = MagicMock()
        self.other_mock_player.balance = 500
        self.other_mock_player.name = "Player 2"
        self.other_mock_player.identity = "Human"
        self.other_mock_player.owned_properties = [MagicMock(name="Bond Street")]
        
        self.game.players = [self.mock_player] 
        self.game.cards = MagicMock(spec=Cards)
        self.game.player_options = MagicMock()

        self.mock_property_1 = MagicMock()
        self.mock_property_1.name = "Park Lane"
        self.mock_property_2 = MagicMock()
        self.mock_property_2.name = "Mayfair"
        self.mock_player.owned_properties = [self.mock_property_1, self.mock_property_2]
        self.other_mock_property = MagicMock()
        self.other_mock_property.name = "Bond Street"
        self.other_mock_player.owned_properties = [self.other_mock_property]

    # __init__(self, player_names, tokens, identities)
    @patch("game.Player")
    @patch("game.Bank")
    @patch("game.Cards")
    def test_game_initialization(self, MockCards, MockBank, MockPlayer):
        """Test that Game initializes with correct attributes."""
        mock_player1 = MagicMock(name="Player1")
        mock_player2 = MagicMock(name="Player2")
        MockPlayer.side_effect = [mock_player1, mock_player2]
        player_names = ["Alice", "Bob"]
        tokens = ["Hat", "Car"]
        identities = ["Human", "AI"]
        game = Game(player_names, tokens, identities)

        self.assertEqual(len(game.players), 2) 
        self.assertEqual(game.players[0], mock_player1) 
        self.assertEqual(game.players[1], mock_player2)
        self.assertEqual(game.current_player_index, 0)
        self.assertTrue(game.running)
        self.assertEqual(game.fines, 0)
        MockBank.assert_called_once()
        MockCards.assert_called_once()
    
    # play_turn(self)
    @patch("builtins.print")
    def test_play_turn_moves_player(self, mock_print):
        """Test that play_turn calls move() on the current player."""
        self.game.handle_position = MagicMock()
        self.game.next_turn = MagicMock()
        self.game.play_turn()
        self.mock_player.move.assert_called_once()

    @patch("builtins.print")
    def test_play_turn_handles_position(self, mock_print):
        """Test that play_turn calls handle_position with the current player."""
        self.game.handle_position = MagicMock()
        self.game.next_turn = MagicMock()
        self.game.play_turn()
        self.game.handle_position.assert_called_once_with(self.mock_player)
    
    @patch("builtins.print")
    def test_play_turn_calls_player_options(self, mock_print):
        """Test that play_turn calls player_options with the current player."""
        self.game.handle_position = MagicMock()
        self.game.next_turn = MagicMock()
        self.game.play_turn()
        self.game.player_options.assert_called_once_with(self.mock_player)
    
    @patch("builtins.print")
    def test_play_turn_resets_consecutive_doubles_when_in_jail(self, mock_print):
        """Test that consecutive doubles reset when the player is in jail."""
        self.game.handle_position = MagicMock()
        self.game.next_turn = MagicMock()
        self.mock_player.position = 11
        self.mock_player.in_jail = True
        self.mock_player.consecutive_doubles = 2

        self.game.play_turn()

        self.assertEqual(self.mock_player.consecutive_doubles, 0)

    @patch("builtins.print")
    def test_play_turn_calls_next_turn(self, mock_print):
        """Test that play_turn calls next_turn with the current player."""
        self.game.handle_position = MagicMock()
        self.game.next_turn = MagicMock()
        self.game.play_turn()
        self.game.next_turn.assert_called_once_with(self.mock_player)

    # handle_position(self, player)
    def test_handle_position_tax(self):
        """Test that handle_position correctly applies tax when landing on tax positions."""
        self.mock_player.configure_mock(pay_tax=MagicMock())

        # Test Income Tax (position 5)
        self.mock_player.position = 5
        print(f"Calling handle_position for player at position {self.mock_player.position}")
        self.game.handle_position(self.mock_player)
        self.mock_player.pay_tax.assert_called_once_with(200)  # Check if pay_tax(200) was called
        self.assertEqual(self.game.fines, 200)  # Ensure fines were updated

        # Reset mock to test Luxury Tax (position 39)
        self.mock_player.pay_tax.reset_mock()
        self.mock_player.position = 39
        self.game.handle_position(self.mock_player)
        self.mock_player.pay_tax.assert_called_once_with(75)  # Check if pay_tax(75) was called
        self.assertEqual(self.game.fines, 275)
    
    def test_handle_position_pot_luck(self):
        """Test that handle_position calls draw_pot_luck_card on Pot Luck positions."""
        self.mock_player.position = 3
        self.game.handle_position(self.mock_player)
        self.game.cards.draw_pot_luck_card.assert_called_once_with(self.mock_player, self.game)

    def test_handle_position_opportunity_knocks(self):
        """Test that handle_position calls draw_opportunity_knocks_card on Opportunity Knocks positions."""
        self.mock_player.position = 8
        self.game.handle_position(self.mock_player)
        self.game.cards.draw_opportunity_knocks_card.assert_called_once_with(self.mock_player, self.game)

    def test_handle_position_go_to_jail(self):
        """Test that handle_position calls go_to_jail when landing on position 31."""
        self.mock_player.position = 31
        self.game.handle_position(self.mock_player)
        self.mock_player.go_to_jail.assert_called_once()

    def test_handle_position_free_parking(self):
        """Test that handle_position gives the player all accumulated fines when landing on Free Parking (21)."""
        self.game.fines = 500
        self.mock_player.position = 21
        self.game.handle_position(self.mock_player)
        self.assertEqual(self.mock_player.balance, 2000)  # 1500 + 500
        self.assertEqual(self.game.fines, 0)

    def test_handle_position_go(self):
        """Test that handle_position prints a message when landing on Go."""
        self.mock_player.position = 1
        with patch('builtins.print') as mock_print:
            self.game.handle_position(self.mock_player)
            mock_print.assert_called_with(f" {self.mock_player.name} has landed at Go!")

    def test_handle_position_visiting_jail(self):
        """Test that handle_position prints a message when visiting jail but not in jail."""
        self.mock_player.position = 11
        self.mock_player.in_jail = False
        with patch('builtins.print') as mock_print:
            self.game.handle_position(self.mock_player)
            mock_print.assert_called_with(f"{self.mock_player.name} is visiting jail")
    
    # next_turn(self, player)
    def test_next_turn_no_doubles(self):
        """Test that next_turn moves to the next player if no doubles are rolled."""
        self.mock_player.consecutive_doubles = 0  # No doubles rolled
        initial_index = self.game.current_player_index
        self.game.play_turn = MagicMock()
        self.game.save_game = MagicMock()

        self.game.next_turn(self.mock_player)

        expected_index = (initial_index + 1) % len(self.game.players)
        self.assertEqual(self.game.current_player_index, expected_index)
        self.game.save_game.assert_called_once()
        self.game.play_turn.assert_called_once()

    def test_next_turn_rolled_doubles(self):
        """Test that next_turn does not change the player if doubles are rolled."""
        self.mock_player.consecutive_doubles = 1  # Rolled doubles
        initial_index = self.game.current_player_index
        self.game.play_turn = MagicMock()
        self.game.save_game = MagicMock()

        self.game.next_turn(self.mock_player)

        self.assertEqual(self.game.current_player_index, initial_index)
        self.game.save_game.assert_called_once()
        self.game.play_turn.assert_called_once()

    def test_next_turn_wraps_around(self):
        """Test that next_turn loops back to player 1 when last player finishes turn."""
        self.game.current_player_index = len(self.game.players) - 1  # Last player in list
        self.mock_player.consecutive_doubles = 0  # No doubles rolled
        self.game.play_turn = MagicMock()
        self.game.save_game = MagicMock()

        self.game.next_turn(self.mock_player)

        self.assertEqual(self.game.current_player_index, 0)
        self.game.save_game.assert_called_once()
        self.game.play_turn.assert_called_once()
    
    # handle_property(self, player)
    def test_handle_property_pays_rent(self):
        """Test that handle_property makes the player pay rent if the property is owned by another player."""
        mock_property = MagicMock()
        mock_property.owner = self.other_mock_player  # Owned by another player
        mock_property.calculate_rent.return_value = 50

        self.game.bank.properties = {self.mock_player.position: mock_property}

        self.game.handle_property(self.mock_player)

        mock_property.calculate_rent.assert_called_once()
        self.mock_player.pay_rent.assert_called_once_with(mock_property, 50)
    
    def test_handle_property_no_rent_if_owned_by_player(self):
        """Test that handle_property does nothing if the player lands on their own property."""
        mock_property = MagicMock()
        mock_property.price = 100
        mock_property.owner = self.mock_player  # Player owns the property

        self.game.bank.properties = {self.mock_player.position: mock_property}

        self.game.handle_property(self.mock_player)

        mock_property.calculate_rent.assert_not_called()
        self.mock_player.pay_rent.assert_not_called()
    
    def test_handle_property_ineligible_to_buy(self):
        """Test that handle_property prevents purchase if player hasn't passed GO."""
        mock_property = MagicMock()
        mock_property.price = 100
        mock_property.owner = None  # Unowned property
        self.mock_player.passed = False  # Has not passed GO

        self.game.bank.properties = {self.mock_player.position: mock_property}

        with patch("builtins.print") as mock_print:
            self.game.handle_property(self.mock_player)
            mock_print.assert_called_with(f"{self.mock_player.name} has not passed go and thus is ineligible to buy a property")
    
    def test_handle_property_prompts_purchase(self):
        """Test that handle_property prompts the player to buy if property is unowned and player is eligible."""
        mock_property = MagicMock()
        mock_property.price = 100
        mock_property.owner = None  # Unowned property
        self.mock_player.passed = True  # Has passed GO

        self.game.bank.properties = {self.mock_player.position: mock_property}

        with patch.object(self.game, "prompt_property_purchase") as mock_prompt:
            self.game.handle_property(self.mock_player)
            mock_prompt.assert_called_once_with(self.mock_player, mock_property)
    
    # prompt_property_purchase(self, player, property_at_position)
    def test_prompt_property_purchase_human_buys(self):
        """Test that a human player buys the property when they have enough balance and choose 'yes'."""
        mock_property = MagicMock()
        mock_property.name = "Boardwalk"
        mock_property.price = 400
        self.mock_player.balance = 500
        self.mock_player.passed = True
        self.mock_player.identity = "Human"

        with patch("builtins.input", return_value="yes"), patch.object(self.mock_player, "buy_property") as mock_buy:
            self.game.prompt_property_purchase(self.mock_player, mock_property)
            mock_buy.assert_called_once_with(mock_property)
    
    def test_prompt_property_purchase_human_declines(self):
        """Test that a human player declines to buy the property and triggers an auction."""
        mock_property = MagicMock()
        mock_property.name = "Boardwalk"
        mock_property.price = 400
        self.mock_player.balance = 500
        self.mock_player.passed = True
        self.mock_player.identity = "Human"

        with patch("builtins.input", return_value="no"), patch.object(self.game.bank, "auction_property") as mock_auction, patch("builtins.print") as mock_print:
            self.game.prompt_property_purchase(self.mock_player, mock_property)
            mock_auction.assert_called_once_with(mock_property, self.game.players)
            mock_print.assert_any_call(f"{self.mock_player.name} declined to buy {mock_property.name}. Starting auction!")
    
    def test_prompt_property_purchase_insufficient_funds(self):
        """Test that a player with insufficient funds automatically triggers an auction."""
        mock_property = MagicMock()
        mock_property.name = "Boardwalk"
        mock_property.price = 400
        self.mock_player.balance = 300  # Not enough funds
        self.mock_player.passed = True

        with patch.object(self.game.bank, "auction_property") as mock_auction, patch("builtins.print") as mock_print:
            self.game.prompt_property_purchase(self.mock_player, mock_property)
            mock_auction.assert_called_once_with(mock_property, self.game.players)
            mock_print.assert_any_call(f"{self.mock_player.name} declined to buy {mock_property.name}. Starting auction!")
    
    def test_prompt_property_purchase_not_passed_go(self):
        """Test that a player who hasn't passed GO cannot buy the property."""
        mock_property = MagicMock()
        mock_property.name = "Boardwalk"
        mock_property.price = 400
        self.mock_player.balance = 500
        self.mock_player.passed = False  # Has not passed GO

        with patch.object(self.game.bank, "auction_property") as mock_auction, patch("builtins.print") as mock_print:
            self.game.prompt_property_purchase(self.mock_player, mock_property)
            mock_auction.assert_called_once_with(mock_property, self.game.players)
            mock_print.assert_any_call(f"{self.mock_player.name} declined to buy {mock_property.name}. Starting auction!")

    # propose_trade(self, current_player, other_player)
    @patch("builtins.input", side_effect=["1", "0", "1", "0", "yes"])
    def test_propose_trade_success(self, mock_input):
        """Test a successful trade execution"""
        self.game.execute_trade = MagicMock()
        self.game.propose_trade(self.mock_player, self.other_mock_player)

        self.game.execute_trade.assert_called_once_with(
            self.mock_player,
            self.other_mock_player,
            [self.mock_property_1],  # Offered property
            [self.other_mock_property],  # Requested property
            0,  # Offered money
            0   # Requested money
        )
    
    @patch("builtins.input", side_effect=["99", "99", "99", "no"]) 
    def test_propose_trade_insufficient_funds(self, mock_input):
        """Test proposing a trade with insufficient funds"""
        self.game.execute_trade = MagicMock() 
        self.mock_player.balance = 0 
        self.other_mock_player.balance = 500

        self.game.propose_trade(self.mock_player, self.other_mock_player)

        self.game.execute_trade.assert_not_called()
    
    @patch("builtins.input", side_effect=["0", "0", "invalid", "0", "no"])
    def test_propose_trade_rejection(self, mock_input):
        """Test rejecting a proposed trade"""
        self.game.execute_trade = MagicMock()
        self.mock_player.balance = 1500
        self.other_mock_player.balance = 500

        self.game.propose_trade(self.mock_player, self.other_mock_player)

        self.game.execute_trade.assert_not_called()

    # execute_trade(self, current_player, other_player, offer_properties, request_properties, offer_money, request_money)
    def test_execute_trade_money_transfer(self):
        """Test that money is correctly transferred between players in a trade."""
        self.mock_player.balance = 1000
        self.other_mock_player.balance = 500

        self.game.execute_trade(self.mock_player, self.other_mock_player, [], [], 200, 100)

        self.assertEqual(self.mock_player.balance, 900)  # 1000 - 200 + 100
        self.assertEqual(self.other_mock_player.balance, 600)  # 500 - 100 + 200
    
    def test_execute_trade_property_transfer(self):
        """Test that properties are correctly transferred between players."""
        mock_property_1 = MagicMock()
        mock_property_2 = MagicMock()

        self.game.execute_trade(self.mock_player, self.other_mock_player, [mock_property_1], [mock_property_2], 0, 0)

        mock_property_1.transfer_property.assert_called_once_with(self.other_mock_player)
        mock_property_2.transfer_property.assert_called_once_with(self.mock_player)
    
    def test_execute_trade_money_and_property_transfer(self):
        """Test that both money and properties are correctly transferred in a trade."""
        mock_property_1 = MagicMock()
        mock_property_2 = MagicMock()

        self.game.execute_trade(self.mock_player, self.other_mock_player, [mock_property_1], [mock_property_2], 300, 150)

        self.assertEqual(self.mock_player.balance, 1350)  # 1000 - 300 + 150
        self.assertEqual(self.other_mock_player.balance, 650)  # 500 - 150 + 300
        mock_property_1.transfer_property.assert_called_once_with(self.other_mock_player)
        mock_property_2.transfer_property.assert_called_once_with(self.mock_player)
    
    def test_execute_trade_no_transfer(self):
        """Test that no changes occur if no money or properties are involved in the trade."""
        initial_balance_p1 = self.mock_player.balance
        initial_balance_p2 = self.other_mock_player.balance

        self.game.execute_trade(self.mock_player, self.other_mock_player, [], [], 0, 0)

        self.assertEqual(self.mock_player.balance, initial_balance_p1)
        self.assertEqual(self.other_mock_player.balance, initial_balance_p2)

    # select_other_player(self, current_player)
    def test_select_other_player_valid_choice(self):
        """Test selecting a valid player from the list."""
        other_player = MagicMock()
        other_player.name = "Alice"
        other_player.token = "Hat"
        self.game.players = [self.mock_player, other_player]

        with patch("builtins.input", return_value="1"):
            selected = self.game.select_other_player(self.mock_player)
            self.assertEqual(selected, other_player)
    
    def test_select_other_player_invalid_choice_out_of_range(self):
        """Test entering an out-of-range number, ensuring it prompts again."""
        other_player = MagicMock()
        other_player.name = "Alice"
        other_player.token = "Hat"
        self.game.players = [self.mock_player, other_player]

        with patch("builtins.input", side_effect=["2", "1"]), patch("builtins.print") as mock_print:
            selected = self.game.select_other_player(self.mock_player)
            self.assertEqual(selected, other_player)
            mock_print.assert_any_call("❌ Invalid choice. Try again.")
    
    def test_select_other_player_invalid_choice_non_numeric(self):
        """Test entering a non-numeric input, ensuring it prompts again."""
        other_player = MagicMock()
        other_player.name = "Alice"
        other_player.token = "Hat"
        self.game.players = [self.mock_player, other_player]

        with patch("builtins.input", side_effect=["abc", "1"]), patch("builtins.print") as mock_print:
            selected = self.game.select_other_player(self.mock_player)
            self.assertEqual(selected, other_player)
            mock_print.assert_any_call("❌ Please enter a valid number.")
    
    # handle_go_pass(self, player, new_position)
    def test_handle_go_pass_crosses_go(self):
        """Test that a player receives £200 when passing GO."""
        self.mock_player.position = 30  # Simulate a position near GO
        self.mock_player.balance = 1000  # Initial balance
        self.mock_player.passed_go = False

        self.game.bank.balance = 5000  # Set initial bank balance

        self.game.handle_go_pass(self.mock_player, 5)  # Move to position 5, crossing GO

        self.assertEqual(self.mock_player.balance, 1200)  # +200 from GO
        self.assertEqual(self.game.bank.balance, 4800)  # -200 from bank
        self.assertTrue(self.mock_player.passed_go)
        self.assertEqual(self.mock_player.position, 5)
    
    def test_handle_go_pass_no_go_cross(self):
        """Test that a player does not receive £200 if they do not pass GO."""
        self.mock_player.position = 10  # Player starts at position 10
        self.mock_player.balance = 1000  # Initial balance
        self.mock_player.passed_go = False

        self.game.bank.balance = 5000  # Set initial bank balance

        self.game.handle_go_pass(self.mock_player, 20)  # Move forward but don't pass GO

        self.assertEqual(self.mock_player.balance, 1000)  # No change
        self.assertEqual(self.game.bank.balance, 5000)  # No change
        self.assertFalse(self.mock_player.passed_go)
        self.assertEqual(self.mock_player.position, 20)


if __name__ == '__main__':
    unittest.main()