from GameElements.player import Player
from GameElements.bank import Bank
from GameElements.cards import Cards
import GuiElements
import json
import os

import GuiElements.dice_gui


class Game:

    def __init__(self, player_names, tokens, identities):
        self.players = [Player(name, token, identity, self) for name, token, identity in zip(player_names, tokens, identities)]
        self.current_player_index = 0
        self.running = True
        self.bank = Bank()
        self.fines = 0
        self.cards = Cards() 

    def play_turn(self, die1, die2):
        """Handles a single player's turn """
        player = self.players[self.current_player_index]
        print(f"\n🎲 {player.name}'s turn!")
        print(f"💰 Balance: £{player.balance}")
        player.move(die1, die2, (die1 == die2))

        self.handle_position(player)
        #self.player_options(player)
        if player.position == 11 and player.in_jail:
            player.consecutive_doubles = 0
        # self.next_turn(player)
        
    
    def handle_position(self, player):
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
                self.log_event(f"🅿️ {player.name} landed on Free Parking and collected £{self.fines}")
                self.fines = 0
            else:
                self.log_event(f"🅿️ {player.name} landed on Free Parking, but there's nothing to collect.")



        elif player.position == 1:
            print(f" {player.name} has landed at Go!")

        elif player.position == 11 and not player.in_jail:
            print(f"{player.name} is visiting jail")

        else:
            self.handle_property(player)



    def next_turn(self, player, die1, die2):
        """Moves to the next player's turn unless they rolled doubles."""
        if player.consecutive_doubles == 0:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        else:
            self.current_player_index = (self.current_player_index + 0) % len(self.players)

        
        self.play_turn(die1, die2)

    def handle_property(self, player):
        """Handles property interactions when a player lands on a space."""
        property_at_position = self.bank.properties.get(player.position, None)

        if property_at_position:
            if property_at_position.owner != player and property_at_position.owner is not None:
                rent = property_at_position.calculate_rent()
                player.pay_rent(property_at_position, rent)
            # elif not player.passed and property_at_position.owner is None:
            #     print(f"{player.name} has not passed go and thus is ineligible to buy a property")
            # else:
            #     self.prompt_property_purchase(player)

    def eligible_to_buy(self, player):
        property_at_position = self.bank.properties.get(player.position, None)
        if property_at_position is None:
            return False
        return player.balance >= property_at_position.price and player.passed and property_at_position.owner is None

    def prompt_property_purchase(self, player):
        """Prompt the player to buy a property or start an auction."""
        property_at_position = self.bank.properties.get(player.position, None)

        # 🧱 If it's not a buyable property (like tax, free parking, etc.)
        if property_at_position is None:
            return f"{player.name} cannot buy anything at this tile."

        print(f"{player.name} landed on {property_at_position.name}. It costs £{property_at_position.price}.")

        # 🧍 Already owned
        if property_at_position.owner is not None:
            if property_at_position.owner == player:
                print(f"{player.name} already owns {property_at_position.name}.")
                return f"You already own {property_at_position.name}."
            print(f"{player.name} has landed on {property_at_position.name}, which is owned by {property_at_position.owner.name}.")
            return f"{property_at_position.name} is already owned by {property_at_position.owner.name}."

        # 🚫 Hasn't passed GO
        if not player.passed:
            print(f"{player.name} has not passed GO and is ineligible to buy {property_at_position.name}.")
            return f"{player.name} has not passed GO and is ineligible to buy {property_at_position.name}."

        # 💸 Insufficient funds
        if player.balance < property_at_position.price:
            print(f"{player.name} does not have enough money to buy {property_at_position.name}.")
            return f"{player.name} does not have enough money to buy {property_at_position.name}."

        # ✅ Purchase
        if player.identity == "Human":
            player.buy_property(property_at_position)
            print(f"{player.name} has bought {property_at_position.name} for £{property_at_position.price}.")
            return f"{player.name} has bought {property_at_position.name} for £{property_at_position.price}."
        else:
            player.bot_buy_property(property_at_position)
            return f"{player.name}'s bot has bought {property_at_position.name} for £{property_at_position.price}."

    def start_auction(self, player):
        auction_players = self.players.copy()
        auction_players = auction_players[self.current_player_index:] + auction_players[:self.current_player_index]
        self.bank.auction_property(self.bank.properties.get(player.position, None), auction_players)

    # def player_options(self, player):
    #     """Displays actions a player can take after their turn."""
    #     while True:
    #         print(f"\n🎲 {player.name}'s Turn Options:")
    #         print("1️⃣  Manage a Property")
    #         print("2️⃣  Propose a Trade")
    #         print("3️⃣   End Turn")

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
    #                 print(f"🎲 {player.name} has ended their turn with a balance of £{player.balance}.")
    #                 print(r"-------------------------------------------------")
    #                 self.next_turn(player)  # Exit loop to continue game
    #             else:
    #                 print("❌ Invalid choice. Try again.")
    #         except ValueError:
    #             print("❌ Please enter a valid number.")

    def propose_trade(self, current_player, other_player):  # MAYBE MOVE TO GAME CLASS

        # Allows a player to offer a trade to another player
        # The trade can involve money, properties or both
        offer_properties = []
        request_properties = []
        offer_money = 0
        request_money = 0

        # Property Selection
        if current_player.owned_properties:
            print("\n📋 Your Properties:")
            for i, prop in enumerate(current_player.owned_properties, 1):
                print(f"{i}. {prop.name}")

            try:
                choice = input(
                    "Enter the numbers of the properties you want to offer (comma-separated) or press Enter to skip: ")
                if choice:
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    offer_properties = [current_player.owned_properties[i] for i in indices]
            except (ValueError, IndexError):
                print("❌ Invalid selection.")

        # Money offering
        try:
            offer_money = int(input("Enter amount of money to offer (or 0 to skip): "))
            if offer_money > current_player.balance:
                print("❌ You don't have enough money.")
                offer_money = 0

        except ValueError:
            print("❌ Invalid amount.")

        if other_player.owned_properties:
            print(f"\n📋 {other_player.name}'s Properties:")
            for i, prop in enumerate(other_player.owned_properties, 1):
                print(f"{i}. {prop.name}")

            try:
                choice = input(
                    "Enter the numbers of the properties you want in exchange (comma-separated) or press Enter to skip: ")
                if choice:
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    request_properties = [other_player.owned_properties[i] for i in indices]
            except (ValueError, IndexError):
                print("❌ Invalid selection.")

            # Money request
        try:
            request_money = int(input(f"Enter amount of money you want in exchange (or 0 to skip): "))
            if request_money > other_player.balance:
                print("❌ They don't have enough money.")
                request_money = 0
        except ValueError:
            print("❌ Invalid amount.")

            # Ensure at least something is being exchanged
        if not offer_properties and not request_properties and offer_money == 0 and request_money == 0:
            print("❌ Trade must involve at least one property or money exchange.")
            return

            # Confirm trade
        print("\n🔄 Trade Offer:")
        print(f"  {current_player.name} offers: " + ", ".join([p.name for p in offer_properties]) + (
            f" + £{offer_money}" if offer_money else ""))
        print(f"  {other_player.name} offers: " + ", ".join([p.name for p in request_properties]) + (
            f" + £{request_money}" if request_money else ""))

        if other_player.identity == "Human":
            confirm = input(f"{other_player.name}, do you accept this trade? (yes/no): ").strip().lower()
        else:
            confirm = other_player.bot_trade(offer_properties, request_properties, offer_money, request_money)
        if confirm == "yes":
            print(f"Requested properties before trade execution: {request_properties}")
            print(f"Executing trade with: {offer_properties}, {request_properties}, {offer_money}, {request_money}")
            self.execute_trade(current_player, other_player, offer_properties, request_properties, offer_money,
                               request_money)
        else:
            print("❌ Trade declined.")
            return

    def execute_trade(self, current_player, other_player, offer_properties, request_properties, offer_money,
                      request_money):
        # Executes a trade between two players, updating ownerships and balance

        # Transfer money
        if offer_money > 0:
            if current_player.balance < offer_money:
                print("❌ Insufficient funds to complete the trade.")
                return
            current_player.balance -= offer_money
            other_player.balance += offer_money
        if request_money > 0:
            if other_player.balance < request_money:
                print("❌ Insufficient funds to complete the trade.")
                return
            other_player.balance -= request_money
            current_player.balance += request_money
        for prop in offer_properties:
            prop.transfer_property(other_player)
        for prop in request_properties:
            prop.transfer_property(current_player)

        print("✅ Trade completed successfully!") 
        return

    def select_other_player(self, current_player):
        """
        Allows the current player to select another player from the game.
        Returns the selected player or None if the selection is invalid.
        """
        available_players = [p for p in self.players if p != current_player]

        print("\n📋 Select a player:")
        for i, player in enumerate(available_players, 1):
            print(f"{i}. {player.name} (Token: {player.token})")

        while True:
            try:
                choice = int(input("Enter the number of the player you want to select: "))
                if 1 <= choice <= len(available_players):
                    return available_players[choice - 1]
                else:
                    print("❌ Invalid choice. Try again.")
            except ValueError:
                print("❌ Please enter a valid number.")

    def handle_go_pass(self, player, new_position):
        """
        Moves the player to a specified position, ensuring they collect £200 if they pass GO.
        """
        if new_position < player.position:  
            player.passed_go = True
            player.balance += 200
            self.bank.balance -= 200
            print(f"🛤️ {player.name} passed GO and collected £200!")

        player.position = new_position  
        print(f"🚀 {player.name} moves to {new_position}")

    def log_event(self, message):
        if self.ui and hasattr(self.ui, "right_sidebar"):
            self.ui.right_sidebar.log_event(message)
        print(message)  



