from GameElements.player import Player
from GameElements.bank import Bank
from GameElements.cards import Cards
from GuiElements.auction_popup_gui import AuctionPopup
import GuiElements
import json
import os

import GuiElements.dice_gui


class Game:
    """"
    Manages the core game logic and state for a digital board game (Property Tycoon variant).

    This class coordinates player turns, dice rolls, property interactions, card draws, trades,
    auctions, and game-ending conditions. It interacts closely with the Player, Bank, Card, and GUI systems.

    Responsibilities:
    - Initialize players and assign identity, tokens, and game reference.
    - Handle turn progression, including doubles logic and jail rules.
    - Determine and execute effects based on player position on the board.
    - Manage property transactions including purchases, rent, auctions, and construction.
    - Support trade proposals and execution (console only).
    - Log events and manage game-end conditions.

    Attributes:
        players (list[Player]): List of all players in the game.
        current_player_index (int): Index tracking the active player's turn.
        running (bool): Flag indicating if the game is still ongoing.
        bank (Bank): The shared bank handling money, properties, mortgages, and buildings.
        fines (int): Amount of accumulated money to be collected at Free Parking.
        cards (Cards): Manages the Pot Luck and Opportunity Knocks card decks.
    """

    def __init__(self, player_names, tokens, identities):
        """
        Initializes the Game instance by setting up players, the bank, and card decks.

        Args:
            player_names (list[str]): List of player names.
            tokens (list[str]): List of player token identifiers (e.g., "Dog", "Boot").
            identities (list[str]): List of player identities ("Human" or "Bot").

        Side Effects:
            - Creates Player instances and assigns them to the game.
            - Initializes the Bank and sets the fine pool to zero.
            - Creates the Pot Luck and Opportunity Knocks card decks.
        """
        self.players = [Player(name, token, identity, self) for name, token, identity in zip(player_names, tokens, identities)]
        self.current_player_index = 0
        self.running = True
        self.bank = Bank()
        self.fines = 0
        self.cards = Cards() 

    def play_turn(self, die1, die2):
        """
        Executes a single turn for the current player by moving them based on dice results 
        and handling any events at the resulting board position.

        Args:
            die1 (int): Result of the first dice roll.
            die2 (int): Result of the second dice roll.

        Side Effects:
            - Moves the player and updates their position.
            - Calls the appropriate handler based on the tile landed on (e.g., tax, property, jail).
            - Logs output to the console.
            - Resets consecutive doubles if player is in jail.
            - Increments the player's turn count.
        """
        player = self.players[self.current_player_index]
        print(f"\n {player.name}'s turn!")
        print(f" Balance: £{player.balance}")
        player.move(die1, die2, (die1 == die2))

        self.handle_position(player)
        if player.position == 11 and player.in_jail:
            player.consecutive_doubles = 0

        player.turns_taken += 1
        


        
    
    def handle_position(self, player):
        """
        Determines and processes the outcome of a player's current board position.

        Depending on the position, the player may be charged tax, draw a card, go to jail,
        collect money from Free Parking, or trigger property handling logic.

        Args:
            player (Player): The player whose position is being evaluated.

        Side Effects:
            - Updates player's balance if taxes are paid or Free Parking is collected.
            - Draws cards and applies their effects (Pot Luck / Opportunity Knocks).
            - Sends the player to jail if on tile 31.
            - Logs events via the UI if applicable.
            - May trigger rent payments or property purchase logic via `handle_property()`.
            - Automatically builds houses for bot players who meet certain conditions.
        """
        
        if player.position in [5, 39]:  # Income Tax & Luxury Tax
            tax_amount = 200 if player.position == 5 else 75
            player.pay_tax(tax_amount)
            self.fines += tax_amount

        elif player.position in [3, 18, 34]:
            print("Pot luck")
            self.cards.draw_pot_luck_card(player, self)

        elif player.position in [8, 23, 37]:
            print("Opportunity Knocks")
            self.cards.draw_opportunity_knocks_card(player, self)

        elif player.position == 31:
            player.go_to_jail()

        elif player.position == 21:
            if self.fines > 0:
                player.balance += self.fines
                self.log_event(f"{player.name} landed on Free Parking and collected £{self.fines}")
                self.fines = 0
            else:
                self.log_event(f"{player.name} landed on Free Parking, but there's nothing to collect.")



        elif player.position == 1:
            print(f" {player.name} has landed at Go!")

        elif player.position == 11 and not player.in_jail:
            print(f"{player.name} is visiting jail")

        else:
            self.handle_property(player)

        if player.identity != 'Human':
            for prop in player.owned_properties:
                if prop.check_completion() and player.balance > 200: 
                    msg = self.bank.build(1, prop, player)
                    self.log_event(msg)



    def next_turn(self, player, die1, die2):
        """
        Advances to the next player's turn unless the current player rolled doubles.

        If the player did not roll doubles, the turn passes to the next player in sequence.
        If they did roll doubles, they get another turn.

        Args:
            player (Player): The player whose turn just occurred.
            die1 (int): The result of the first die.
            die2 (int): The result of the second die.

        Side Effects:
            - Updates `current_player_index` to determine the next active player.
            - Triggers the next player's turn via `play_turn()`.
        """
        if player.consecutive_doubles == 0:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        else:
            self.current_player_index = (self.current_player_index + 0) % len(self.players)

        
        self.play_turn(die1, die2)

    def handle_property(self, player):
        """
        Handles interactions when a player lands on a property tile.

        This includes:
        - Paying rent if the property is owned by another player.
        - Initiating a purchase or auction if the property is unowned and the player is eligible.
        - Preventing purchase if the player has not passed GO.

        Args:
            player (Player): The player who has landed on a property space.

        Side Effects:
            - Transfers rent from the current player to the property's owner.
            - Logs property events such as failed purchases or auctions.
            - May trigger `prompt_property_purchase()` for bot players.
            - May initiate an auction via `start_auction()` if applicable.
        """
        property_at_position = self.bank.properties.get(player.position, None)
        if property_at_position:
            if property_at_position.owner and property_at_position.owner != player:
                last_roll = player.last_roll if hasattr(player, 'last_roll') else 0
                rent = property_at_position.calculate_rent(last_roll)
                player.pay_rent(property_at_position, last_roll)

            elif property_at_position.owner is None:
                if not player.passed:
                    if player.identity != "Human":
                        self.log_event(f" {player.name} has not passed GO and is not eligible to buy {property_at_position.name}.")
                else:
                    if player.identity != "Human":
                        # Let bots decide automatically
                        purchase_result = self.prompt_property_purchase(player)

                        if purchase_result == "declined":
                            self.log_event(f"{player.name} can't afford {property_at_position.name}.")
                            eligible_bidders = self.get_eligible_auction_players()
                            if len(eligible_bidders) > 1:
                                self.log_event(f"Property purchase declined. Starting auction for {property_at_position.name}")
                                self.start_auction(player)
                            else:
                                self.log_event(" Not enough eligible bidders to start an auction. Property remains unowned.")
                    else:
                        self.log_event(f"{player.name} can choose to buy {property_at_position.name} using the Buy button.")


    def eligible_to_buy(self, player):
        """
        Determines if a player is eligible to purchase the property they are currently on.

        A player is eligible if:
        - There is a property at their current position.
        - They have passed GO.
        - They have enough money to afford the property.
        - The property is currently unowned.

        Args:
            player (Player): The player attempting to buy a property.

        Returns:
            bool: True if the player is eligible to buy the property, False otherwise.
        """
        property_at_position = self.bank.properties.get(player.position, None)
        if property_at_position is None:
            return False
        return player.balance >= property_at_position.price and player.passed and property_at_position.owner is None

    def prompt_property_purchase(self, player):
        """
        Handles the property purchase logic based on player identity and eligibility.

        For human players, checks if they can afford the property and purchases it automatically.
        For bots, delegates the decision to the bot's strategy method.
        Returns a message or status indicating the result of the attempt.

        Args:
            player (Player): The player attempting to purchase a property.

        Returns:
            str: 
                - "bought" if the property was successfully purchased.
                - "declined" if the bot chose not to buy or couldn't afford it.
                - A message explaining why a human player can't buy (e.g., not passed GO, already owned).
        """       
        property_at_position = self.bank.properties.get(player.position, None)
        if property_at_position is None:
            return f"{player.name} cannot buy anything at this tile."

        if property_at_position.owner:
            return f"{property_at_position.name} is already owned by {property_at_position.owner.name}."

        if not player.passed:
            return f"{player.name} hasn't passed GO and can't buy {property_at_position.name}."

        if player.identity == "Human":
            if player.balance < property_at_position.price:
                return f"{player.name} can't afford {property_at_position.name}."
            player.buy_property(property_at_position)
            return "bought"

        else:
            # Bot decision
            decision = player.bot_buy_property(property_at_position)
            if decision == "yes":
                player.buy_property(property_at_position)
                return "bought"
            else:
                return "declined"


    def start_auction(self, player):
        """
        Initiates an auction for the property the player has landed on.

        The auction is set up by rotating the player order starting from the current player,
        and initializing an AuctionPopup UI element. The property is marked to indicate
        that it has already been auctioned during this turn.

        Args:
            player (Player): The player who declined the property purchase, triggering the auction.

        Side Effects:
            - Displays an auction popup in the GUI.
            - Sets the `already_auctioned` flag on the property to True.
        """
        auction_players = self.players.copy()
        auction_players = auction_players[self.current_player_index:] + auction_players[:self.current_player_index]
        prop = self.bank.properties.get(player.position, None)
        self.ui.auction_popup = AuctionPopup(self.ui.screen, auction_players, prop, self)
        prop.already_auctioned = True # Assigned the property already auctioned for this turm

    # Removed terminal game play options after merged with UI.
    # def player_options(self, player):
    #     """Displays actions a player can take after their turn."""
    #     while True:
    #         print(f"\n {player.name}'s Turn Options:")
    #         print("1️ Manage a Property")
    #         print("2  Propose a Trade")
    #         print("3️   End Turn")

    #         try:
    #             if player.identity == "Human":
    #                 choice = int(input("Enter the number of your choice: "))
    #             else:
    #                 choice = player.bot_options()
    #             if choice == 1:
    #                 player.manage_property()
    #             elif choice == 2:
    #                 other_player = self.select_other_player(player)
    #                 self.propose_trade(player, other_player)
    #             elif choice == 3:
    #                 print(f" {player.name} has ended their turn with a balance of £{player.balance}.")
    #                 print(r"-------------------------------------------------")
    #                 self.next_turn(player)  # Exit loop to continue game
    #             else:
    #                 print(" Invalid choice. Try again.")
    #         except ValueError:
    #             print(" Please enter a valid number.")

    def propose_trade(self, current_player, other_player): 
        """
        Handles initiating a trade between two players.

        This method checks whether the game is running in GUI mode. If so, trading is currently 
        disabled and a log message is displayed. If trading were to be implemented (e.g., in CLI mode),
        this function would serve as the entry point for negotiating trades between players.

        Args:
            current_player (Player): The player proposing the trade.
            other_player (Player): The player receiving the trade offer.

        Side Effects:
            - Logs a message if trading is unavailable in GUI mode.
        """
        if self.ui:
            self.log_event("Trading is currently not available in GUI mode.")
            return # never linked to frontend 


        # # Allows a player to offer a trade to another player
        # # The trade can involve money, properties or both
        # offer_properties = []
        # request_properties = []
        # offer_money = 0
        # request_money = 0

        # # Property Selection
        # if current_player.owned_properties:
        #     print("\n Your Properties:")
        #     for i, prop in enumerate(current_player.owned_properties, 1):
        #         print(f"{i}. {prop.name}")

        #     try:
        #         choice = input(
        #             "Enter the numbers of the properties you want to offer (comma-separated) or press Enter to skip: ")
        #         if choice:
        #             indices = [int(x.strip()) - 1 for x in choice.split(",")]
        #             offer_properties = [current_player.owned_properties[i] for i in indices]
        #     except (ValueError, IndexError):
        #         print(" Invalid selection.")

        # # Money offering
        # try:
        #     offer_money = int(input("Enter amount of money to offer (or 0 to skip): "))
        #     if offer_money > current_player.balance:
        #         print("You don't have enough money.")
        #         offer_money = 0

        # except ValueError:
        #     print("Invalid amount.")

        # if other_player.owned_properties:
        #     print(f"\n{other_player.name}'s Properties:")
        #     for i, prop in enumerate(other_player.owned_properties, 1):
        #         print(f"{i}. {prop.name}")

        #     try:
        #         choice = input(
        #             "Enter the numbers of the properties you want in exchange (comma-separated) or press Enter to skip: ")
        #         if choice:
        #             indices = [int(x.strip()) - 1 for x in choice.split(",")]
        #             request_properties = [other_player.owned_properties[i] for i in indices]
        #     except (ValueError, IndexError):
        #         print(" Invalid selection.")

        #     # Money request
        # try:
        #     request_money = int(input(f"Enter amount of money you want in exchange (or 0 to skip): "))
        #     if request_money > other_player.balance:
        #         print(" They don't have enough money.")
        #         request_money = 0
        # except ValueError:
        #     print(" Invalid amount.")

        #     # Ensure at least something is being exchanged
        # if not offer_properties and not request_properties and offer_money == 0 and request_money == 0:
        #     print(" Trade must involve at least one property or money exchange.")
        #     return

        #     # Confirm trade
        # print("\n Trade Offer:")
        # print(f"  {current_player.name} offers: " + ", ".join([p.name for p in offer_properties]) + (
        #     f" + £{offer_money}" if offer_money else ""))
        # print(f"  {other_player.name} offers: " + ", ".join([p.name for p in request_properties]) + (
        #     f" + £{request_money}" if request_money else ""))

        # if other_player.identity == "Human":
        #     confirm = input(f"{other_player.name}, do you accept this trade? (yes/no): ").strip().lower()
        # else:
        #     confirm = other_player.bot_trade(offer_properties, request_properties, offer_money, request_money)
        # if confirm == "yes":
        #     print(f"Requested properties before trade execution: {request_properties}")
        #     print(f"Executing trade with: {offer_properties}, {request_properties}, {offer_money}, {request_money}")
        #     self.execute_trade(current_player, other_player, offer_properties, request_properties, offer_money,
        #                        request_money)
        # else:
        #     print(" Trade declined.")
        #     return

    def execute_trade(self, current_player, other_player, offer_properties, request_properties, offer_money,
                      request_money):
        """
        Executes a trade between two players by transferring properties and/or money.

        This method deducts and credits money from each player's balance based on the agreed trade amounts.
        It also transfers ownership of the specified properties between players.

        Args:
            current_player (Player): The player initiating the trade and making the offer.
            other_player (Player): The player receiving the trade offer.
            offer_properties (list): List of Property objects offered by the current_player.
            request_properties (list): List of Property objects requested from the other_player.
            offer_money (int): Amount of money offered by current_player.
            request_money (int): Amount of money requested from other_player.

        Side Effects:
            - Updates player balances.
            - Transfers property ownership.
            - Logs success or failure messages to the console.
        """       
        # Executes a trade between two players, updating ownerships and balance

        # Transfer money
        if offer_money > 0:
            if current_player.balance < offer_money:
                print("Insufficient funds to complete the trade.")
                return
            current_player.balance -= offer_money
            other_player.balance += offer_money
        if request_money > 0:
            if other_player.balance < request_money:
                print("Insufficient funds to complete the trade.")
                return
            other_player.balance -= request_money
            current_player.balance += request_money
        for prop in offer_properties:
            prop.transfer_property(other_player)
        for prop in request_properties:
            prop.transfer_property(current_player)

        print("Trade completed successfully!") 
        return

    def select_other_player(self, current_player):
        """
        Allows the current player to select another player to trade with.

        This method presents the current player with a list of other players in the game 
        and allows them to choose one for potential trading, unless the game is in GUI mode.

        Args:
            current_player (Player): The player who is initiating the selection.

        Returns:
            Player | None: The selected player object if a valid choice is made, otherwise None.

        Raises:
            None

        Side Effects:
            - Logs a message if the game is in GUI mode and trading is disabled.
        """
        if self.ui:
            self.log_event("Trading is currently not available in GUI mode.")
            return

        # available_players = [p for p in self.players if p != current_player]

        # print("\n Select a player:")
        # for i, player in enumerate(available_players, 1):
        #     print(f"{i}. {player.name} (Token: {player.token})")

        # while True:
        #     try:
        #         choice = int(input("Enter the number of the player you want to select: "))
        #         if 1 <= choice <= len(available_players):
        #             return available_players[choice - 1]
        #         else:
        #             print(" Invalid choice. Try again.")
        #     except ValueError:
        #         print(" Please enter a valid number.")

    def handle_go_pass(self, player, new_position):
        """
        Moves the player to a specified position and awards £200 if they pass GO.

        This method checks whether the player has passed the GO position on the board
        (by comparing the current and new position). If so, it credits the player £200
        and deducts it from the bank. Then it updates the player's position.

        Args:
            player (Player): The player who is being moved.
            new_position (int): The destination tile index on the board.

        Returns:
            None

        Side Effects:
            - Updates the player's position.
            - Adjusts the balances of the player and the bank if GO is passed.
            - Prints messages reflecting the player's movement and GO bonus.
        """
        if new_position < player.position:  
            player.passed_go = True
            player.balance += 200
            self.bank.balance -= 200
            print(f"{player.name} passed GO and collected £200!")

        player.position = new_position  
        print(f"{player.name} moves to {new_position}")

    def log_event(self, message):
        """
        Logs a game event to both the GUI (if available) and the console.

        Args:
            message (str): The event message to be logged.

        Returns:
            None

        Side Effects:
            - Displays the message in the GUI sidebar if available.
            - Prints the message to the console.
        """
        if self.ui and hasattr(self.ui, "right_sidebar"):
            self.ui.right_sidebar.log_event(message)
        print(message)  

    def get_eligible_auction_players(self):
        """
        Retrieves a list of players eligible to participate in an auction.

        Returns:
            list: A list of Player objects who have passed GO and are thus eligible to bid in auctions.

        Raises:
            None
        """
        return [p for p in self.players if p.passed]
    

    def check_end_game(self):
        """
        Checks if the game has reached an end condition (i.e., only one player remaining).

        If one or no players remain in the game:
        - Triggers the end game popup if UI is available.
        - Sets the game state to not running.

        Returns:
            None
        """
        active_players = [p for p in self.players]

        if len(active_players) <= 1:
            winner = active_players[0] if active_players else None
            if hasattr(self, "ui") and self.ui:
                self.ui.trigger_end_game_popup(winner.name)
            self.running = False
            
    def determine_winner_abridged(self):
        """
        Determines the winner(s) of the game in abridged mode based on total net worth.

        Calculates net worth for each player by summing:
        - Cash balance
        - Property values
        - Value of houses built

        The player(s) with the highest net worth is declared the winner. 
        Handles ties and logs the result to the game log.

        Returns:
            str: The name of the winner or a concatenated string of winners in case of a tie.
        """
        highest_networth = -1
        winners = []

        for p in self.players:
            property_value = sum(prop.price for prop in p.owned_properties)
            house_value = sum(prop.house_cost * prop.houses for prop in p.owned_properties)
            networth = p.balance + property_value + house_value

            if networth > highest_networth:
                highest_networth = networth
                winners = [p.name]
            elif networth == highest_networth:
                winners.append(p.name)

        if len(winners) == 1:
            winner_str = winners[0]
            self.log_event(f"Abridged mode ended. {winner_str} wins with £{highest_networth} in assets!")
        else:
            winner_str = " & ".join(winners)
            self.log_event(f"Abridged mode ended in a draw! {winner_str} share the win with £{highest_networth} in assets each.")

        return winner_str  


    def remove_player(self, player):
        """
        Removes a player from the game and returns their properties to the bank.

        This method:
        - Transfers ownership of all the player's properties back to the bank.
        - Removes the player from the game’s active player list.
        - Resets the current player index if needed.
        - Logs the removal event to the UI log.
        - Triggers a check to determine if the game should end.

        Args:
            player (Player): The player to be removed from the game.

        Returns:
            None
        """
        player.return_properties_to_bank()
        if player in self.players:
            self.players.remove(player)

        if self.current_player_index >= len(self.players):
            self.current_player_index = 0

        self.ui.right_sidebar.log_event(f"{player.name} has been removed from the game.")
        self.check_end_game()


       





