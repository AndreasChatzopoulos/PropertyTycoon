from player import Player
from bank import Bank
from cards import Cards
import json
import os


class Game:

    def __init__(self, player_names, tokens):
        self.players = [Player(name, token, self) for name, token in zip(player_names, tokens)]
        self.current_player_index = 0
        self.running = True
        self.bank = Bank()
        self.fines = 0
        self.cards = Cards()


    def save_game(self, filename="savegame.json"):
        """Saves the current game state to a JSON file."""
        game_data = {
            "players": [{
                "name": p.name,
                "token": p.token,
                "balance": p.balance,
                "position": p.position,
                "properties": [prop.name for prop in p.owned_properties]
            } for p in self.players],
            "bank_balance": self.bank.balance
        }

        with open(filename, "w") as f:
            json.dump(game_data, f, indent=4)
        print("💾 Game successfully saved!")

    def load_game(self, filename="savegame.json"):
        """Loads game state from a JSON file."""
        if not os.path.exists(filename):
            print("❌ No saved game found!")
            return

        with open(filename, "r") as f:
            game_data = json.load(f)

        # Restore bank balance
        self.bank.balance = game_data["bank_balance"]

        # Restore players
        for p_data, player in zip(game_data["players"], self.players):
            player.name = p_data["name"]
            player.token = p_data["token"]
            player.balance = p_data["balance"]
            player.position = p_data["position"]

            # Assign properties back to players
            player.owned_properties = []
            for prop_name in p_data["properties"]:
                for prop in self.bank.properties:
                    if prop.name == prop_name:
                        prop.owner = player
                        player.owned_properties.append(prop)

        print("✅ Game successfully loaded!")


    @staticmethod
    def load_players_from_file(filename="players.json"):
        """Loads player names and tokens from a JSON file."""
        filepath = os.path.join(os.path.dirname(__file__), filename)

        if not os.path.exists(filepath):
            print("❌ Player file not found! Starting with default players.")
            return ["Alice", "Bob"], ["Boot", "Ship"]

        with open(filepath, "r") as f:
            data = json.load(f)
            player_names = [p["name"] for p in data["players"]]
            player_tokens = [p["token"] for p in data["players"]]
            return player_names, player_tokens

    def play_turn(self):
        """Handles a single player's turn """
        player = self.players[self.current_player_index]
        print(f"\n🎲 {player.name}'s turn!")
        double = player.move()

        self.handle_position(player)
        self.player_options(player)
        self.next_turn(double, player)
        
    
    def handle_position(self, player):
        if player.position in [4, 38]:  # Income Tax & Luxury Tax
            tax_amount = 200 if player.position == 4 else 75
            player.pay_tax(tax_amount)
            self.fines += tax_amount

        elif player.position in [3, 18, 34]:
            print("Pot luck")
            self.cards.draw_pot_luck_card(player, self)

        elif player.position in [8, 23, 37]:
            print("Oppurtunity Knocks")
            self.cards.draw_opportunity_knocks_card(player, self)

        elif player.position == 31:
            player.go_to_jail()

        elif player.position == 21:
            player.balance += self.fines
            self.fines = 0

        elif player.position == 1:
            print(f" {player.name} has landed at Go!")

        elif player.position == 11 and not player.in_jail:
            print(f"{player.name} is visiting jail")

        else:
            self.handle_property(player)



    def next_turn(self, rolled_doubles, player):
        """Moves to the next player's turn unless they rolled doubles."""
        if not rolled_doubles:
            player.consecutive_doubles = 0
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        else:
            self.current_player_index = (self.current_player_index + 0) % len(self.players)

        # Auto-save game after every turn
        self.save_game()
        self.play_turn()

    def handle_property(self, player):
        """Handles property interactions when a player lands on a space."""
        property_at_position = self.bank.properties.get(player.position, None)

        if property_at_position:
            if property_at_position.owner != player and property_at_position.owner is not None:
                rent = property_at_position.calculate_rent()
                player.pay_rent(property_at_position, rent)
            elif not player.passed and property_at_position.owner is None:
                print(f"{player.name} has not passed go and thus is ineligible to buy a property")
            else:
                self.prompt_property_purchase(player, property_at_position)

    def prompt_property_purchase(self, player, property_at_position):
        """Prompt the player to buy a property or start an auction."""
        print(f"{player.name} landed on {property_at_position.name}. It costs £{property_at_position.price}.")

        if player.balance >= property_at_position.price and player.passed:
            choice = input("Do you want to buy it? (yes/no): ").strip().lower()

            if choice == "yes":
                player.buy_property(property_at_position)
                return

        print(f"{player.name} declined to buy {property_at_position.name}. Starting auction!")
        self.bank.auction_property(property_at_position, self.players)

    def player_options(self, player):
        """Displays actions a player can take after their turn."""
        while True:
            print(f"\n🎲 {player.name}'s Turn Options:")
            print("1️⃣  Manage a Property")
            print("2️⃣  Propose a Trade")
            print("3️⃣  Save Game 💾")
            print("4️⃣  Load Game 📂")
            print("5️⃣  End Turn")

            try:
                choice = int(input("Enter the number of your choice: "))
                if choice == 1:
                    player.manage_property()
                elif choice == 2:
                    other_player = self.select_other_player(player)
                    self.propose_trade(player, other_player)
                elif choice == 3:
                    self.save_game()
                elif choice == 4:
                    self.load_game()
                elif choice == 5:
                    print(f"🎲 {player.name} has ended their turn.")
                    return  # Exit loop to continue game
                else:
                    print("❌ Invalid choice. Try again.")
            except ValueError:
                print("❌ Please enter a valid number.")

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

        confirm = input(f"{other_player.name}, do you accept this trade? (yes/no): ").strip().lower()
        if confirm == "yes":
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
            current_player.balance -= offer_money
            other_player.balance += offer_money
        if request_money > 0:
            other_player.balance -= request_money
            current_player.balance += request_money

            # Transfer properties
        for prop in offer_properties:
            prop.transfer_property(other_player)
        for prop in request_properties:
            prop.transfer_property(current_player)

        print("✅ Trade completed successfully!")  # mA m
        return

    def select_other_player(self, current_player):
        """
        Allows the current player to select another player from the game.
        Returns the selected player or None if the selection is invalid.
        """
        # Get a list of all players except the current player
        available_players = [p for p in self.players if p != current_player]

        # Display available players
        print("\n📋 Select a player:")
        for i, player in enumerate(available_players, 1):
            print(f"{i}. {player.name} (Token: {player.token})")

        # Get player's choice
        while True:
            try:
                choice = int(input("Enter the number of the player you want to select: "))
                if 1 <= choice <= len(available_players):
                    return available_players[choice - 1]  # Return the chosen player
                else:
                    print("❌ Invalid choice. Try again.")
            except ValueError:
                print("❌ Please enter a valid number.")

    def handle_go_pass(self, player, new_position):
        """
        Moves the player to a specified position, ensuring they collect £200 if they pass GO.
        """
        if new_position < player.position:  # ✅ Player crosses GO
            player.passed_go = True
            player.balance += 200
            self.bank.balance -= 200
            print(f"🛤️ {player.name} passed GO and collected £200!")

        player.position = new_position  # ✅ Update position
        print(f"🚀 {player.name} moves to {new_position}")

