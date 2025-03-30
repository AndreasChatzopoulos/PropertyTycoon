import random
import pygame



class Player:
    def __init__(self, name, token, identity, game):
        """Player initialization with reference to the existing Game instance."""
        self.name = name
        self.token = token
        self.identity = identity
        self.game = game  #  Fix: Store game reference instead of creating a new game
        self.balance = 1500
        self.owned_properties = []
        self.passed = False
        self.in_jail = False
        self.position = 1
        self.get_out_of_jail_cards = 0
        self.jail_turns = 0
        self.consecutive_doubles = 0

    def roll_dice(self):
        die1, die2 = random.randint(1, 6), random.randint(1, 6)
        print(f"{self.name} rolls {die1} and {die2} for a total of ({die1 + die2})")
        double = (die1 == die2)
        return die1, die2, double

    def move(self, die1, die2, double):
        if self.in_jail:
            if self.identity == "Human":
                self.game.log_event(f"{self.name} is in jail. Awaiting decision...")
                return
            else:
                if double:
                    self.get_out_of_jail(True, False)
                else:
                    self.jail_turns += 1
                    self.get_out_of_jail(False, self.jail_turns >= 3)
                    if self.in_jail:
                        self.game.log_event(f"{self.name} stays in jail (Turn {self.jail_turns})")
                        self.consecutive_doubles = 0
                        return

        if double:
            self.consecutive_doubles += 1
            self.game.log_event(f"{self.name} rolled a double! ({die1}, {die2})")

            if self.consecutive_doubles >= 3:
                self.game.log_event(f"{self.name} rolled 3 consecutive doubles and is sent to jail!")
                self.go_to_jail()
                self.consecutive_doubles = 0
                return
        else:
            self.consecutive_doubles = 0

        steps = die1 + die2
        self.game.log_event(f"{self.name} moves {steps} steps.")

        for _ in range(steps):
            old_position = self.position
            self.position = self.position + 1 if self.position < 40 else 1

            if self.position == 1:
                self.passed = True
                self.balance += 200
                self.game.bank.balance -= 200
                self.game.log_event(f"🛤️ {self.name} passed GO and collected £200!")

            if hasattr(self.game, "ui") and self.game.ui:
                self.game.ui.draw()
                pygame.display.flip()
                pygame.time.wait(150)

        special_tiles = {
            1: "GO",
            3: "Pot Luck",
            5: "Income Tax",
            8: "Opportunity Knocks",
            11: "Just Visiting Jail" if not self.in_jail else "Jail",
            18: "Pot Luck",
            21: "Free Parking",
            23: "Opportunity Knocks",
            31: "Go To Jail",
            34: "Pot Luck",
            37: "Opportunity Knocks",
            39: "Luxury Tax"
        }

        property_obj = self.game.bank.properties.get(self.position)
        tile_name = property_obj.name if property_obj else special_tiles.get(self.position, "Unknown Tile")

        self.game.log_event(f"{self.name} landed on tile {tile_name}")



    def buy_property(self, property_at_position):
        self.balance -= property_at_position.price

        self.game.bank.balance += property_at_position.price

        property_at_position.owner = self
        self.owned_properties.append(property_at_position)

        message = f"✅ {self.name} bought {property_at_position.name} for £{property_at_position.price}!"
        print(message)
        self.game.log_event(message)

    def go_to_jail(self):  
        self.in_jail = True
        self.position = 11
        message = f"{self.name} has been sent to jail!"
        print(message)
        self.game.log_event(message)

    def get_out_of_jail(self, double=False, turns=False):
        if double:
            print(f"{self.name} rolled a double to get out of jail!")
            self.jail_turns = 0
            self.in_jail = False
            self.game.log_event(f"{self.name} rolled a double and got out of jail!")
            return

        if self.get_out_of_jail_cards > 0:
            self.get_out_of_jail_cards -= 1
            self.jail_turns = 0
            self.in_jail = False
            print(f"{self.name} used a Get Out of Jail Free card!")
            self.game.log_event(f"{self.name} used a Get Out of Jail Free card to leave jail.")
            return

        # Only allow bots to auto-decide here — human decisions are made via GUI popup
        if self.identity != "Human":
            if self.balance >= 50:
                self.balance -= 50
                self.jail_turns = 0
                self.in_jail = False
                print(f"{self.name} paid £50 to get out of jail!")
                self.game.log_event(f"{self.name} paid £50 to get out of jail.")
            elif turns:
                print(f"{self.name} served 3 turns and is now free.")
                self.jail_turns = 0
                self.in_jail = False
                self.game.log_event(f"{self.name} served 3 turns and is out of jail.")


    def pay_tax(self, amount):
        self.balance -= amount
        message = f"{self.name} paid tax of £{amount}!"
        print(message)
        self.game.log_event(message)

    def pay_rent(self, property_at_position, roll):
        """Handles rent payment when landing on an owned property."""
        creditor = property_at_position.owner

        # If the owner is in jail, they can't collect rent
        if creditor.in_jail:
            message = f"{creditor.name} is in jail and cannot collect rent from {self.name}."
            print(message)
            self.game.log_event(message)
            return

        amount_due = property_at_position.calculate_rent(roll)

        if self.balance >= amount_due:
            self.balance -= amount_due
            creditor.balance += amount_due

            message = f"{self.name} paid £{amount_due} rent to {creditor.name}."
            print(message)
            self.game.log_event(message)

        else:
            message = f"❌ {self.name} doesn’t have enough money to pay £{amount_due} rent to {creditor.name}! Attempting to raise funds..."
            print(message)
            self.game.log_event(message)

            self.avoid_bankruptcy(amount_due, creditor)



    def select_property(self, action):  # Method so the user selects property to sell
        """
        Helper method to let the user select one of their owned properties.
        """
        if not self.owned_properties:
            print(f"{self.name} has no properties to {action}.")
            return None

        print(f" {self.name}'s Owned Properties:")
        for idx, prop in enumerate(self.owned_properties, start=1):  # Traverses through the properties
            print(f"{idx}. {prop.name} | Price: £{prop.price} | Houses: {prop.houses} | Mortgaged: {prop.mortgaged}")

        while True:
            try:
                choice = int(input(f"Select the property to {action} (1-{len(self.owned_properties)}): "))
                if 1 <= choice <= len(self.owned_properties):
                    return self.owned_properties[choice - 1]
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def avoid_bankruptcy(self, amount_due, creditor):  # Update bank.py and creditor balance

        # Interactive method allowing the player to choose how to avoid bankruptcy.

        print(f"{self.name} needs to pay {amount_due} to {creditor.name if creditor else 'the bank.py'}.")

        while self.balance < amount_due:

            if not self.owned_properties:  # Prevents infinite loop if no assets
                self.declare_bankruptcy(creditor, amount_due)
                return

            print(f" Current Balance: £{self.balance}")
            print(f" Amount Due: £{amount_due}")

            options = []  # Produces the options dynamically so there is no redundancy
            if any(p.houses > 0 for p in self.owned_properties):  # Checks if the player has any properties with houses
                options.append("Sell Houses/Hotels")
            if any(not p.mortgaged for p in
                   self.owned_properties):  # Checks if the player has any unmortgaged properties
                options.append("Mortgage Properties")
            if any(p.houses == 0 for p in
                   self.owned_properties):  # Checks if the player has any properties available to sell
                options.append("Sell Properties to the Bank")
            if len(self.owned_properties) > 1:  # Checks if the player has any available properties to trade
                options.append("Offer a Trade")
            options.append("Declare Bankruptcy")

            # Print available choices
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            # Get player's choice
            try:
                if self.identity == "Human":
                    choice = int(input("Enter the number of your choice: "))
                else:
                    choice = self.bot_avoid_bankruptcy(options, amount_due, creditor)
                if choice < 1 or choice > len(options):
                    print("Invalid choice. Try again.")
                    continue
            except ValueError:
                print("Please enter a number.")
                continue

            # Execute the chosen option
            action = options[choice - 1]
            if "Sell Houses" in action:
                prop = self.select_property("Sell Houses")
                self.game.bank.sell_houses_to_the_bank(self, prop)
            elif "Mortgage" in action:
                prop = self.select_property("Mortgage Property")
                self.game.bank.mortgage_property(self, prop)
            elif "Sell Properties" in action:
                prop = self.select_property("Sell Property")
                self.game.bank.sell_property_to_the_bank(self, prop)
            elif "Offer a Trade" in action:  # Method to select player form game's players
                self.game.propose_trade(self, )
            elif "Declare Bankruptcy" in action:
                self.declare_bankruptcy(creditor, amount_due)
                return

            # Stop if enough money has been raised
            if self.balance >= amount_due:
                break

            # Pay the creditor if the balance is sufficient
        if self.balance >= amount_due:
            self.balance -= amount_due
            if creditor:
                creditor.balance += amount_due
                print(
                    f" {self.name} successfully paid £{amount_due} to {creditor.name if creditor else 'the bank.py'}.")
        else:
            self.declare_bankruptcy(creditor, amount_due)

    def declare_bankruptcy(self, creditor, debt):
        """Handle bankruptcy"""""

        print(f"{self.name} is bankrupt! Cannot pay {debt} to {creditor.name if creditor else 'the bank.py'}.")
        if creditor:
            for properties in self.owned_properties:
                properties.transfer_property(creditor)

        else:
            self.return_properties_to_bank()  # Return to bank.py if no creditor

        self.balance = 0
        print(f"💔 {self.name} has left the game.")

    def return_properties_to_bank(self):
        for prop in self.owned_properties[:]:
            self.owned_properties.remove(prop)
            self.game.bank.properties.append(prop)
            prop.owner = None

    def manage_property(self):
        """
        Allows the player to select one of their owned properties and manage it.
        Available actions:
        - Sell the property to the bank
        - Mortgage the property
        - Unmortgage the property
        - Sell houses
        - Build houses
        """
        if not self.owned_properties:
            print(f"❌ {self.name} has no properties to manage.")
            return

        # Let the player select a property
        selected_property = self.select_property("manage")
        if not selected_property:
            return

        while True:
            print(f"\n🏠 Managing {selected_property.name}:")
            print("💰 Balance:", self.balance)

            # Dynamically generate available options
            options = {}
            option_number = 1

            if selected_property.houses == 0:  # Selling only possible when no houses exist
                options[option_number] = "Sell the property to the bank"
                option_number += 1
            if not selected_property.mortgaged:
                options[option_number] = "Mortgage the property"
                option_number += 1
            if selected_property.mortgaged:
                options[option_number] = "Unmortgage the property"
                option_number += 1
            if selected_property.houses > 0:
                options[option_number] = "Sell houses from the property"
                option_number += 1
            if selected_property.completed and selected_property.houses < 5:
                options[option_number] = "Build houses on the property"
                option_number += 1

            # Show available options
            for key, value in options.items():
                print(f"{key}. {value}")
            print(f"{option_number}. Exit Property Management")  # Exit option

            # Get player's choice
            try:
                choice = int(input("Enter the number of your choice: "))
                if choice not in options and choice != option_number:
                    print("❌ Invalid choice. Try again.")
                    continue
            except ValueError:
                print("❌ Please enter a valid number.")
                continue

            # Execute the chosen option
            if choice == option_number:  # Exit
                print("🏠 Exiting property management.")
                return
            else:
                if options[choice] == "Sell the property to the bank":
                    self.game.bank.sell_property_to_the_bank(self, selected_property)
                elif options[choice] == "Mortgage the property":
                    self.game.bank.mortgage_property(self, selected_property)
                elif options[choice] == "Unmortgage the property":
                    self.game.bank.unmortgage_property(self, selected_property)
                elif options[choice] == "Sell houses from the property":
                    self.game.bank.sell_houses_to_the_bank(self, selected_property)
                elif options[choice] == "Build houses on the property":
                    number_of_houses = 1
                    self.game.bank.build(number_of_houses, selected_property, self)


    def move_player_to(self, new_position):
        """Moves the player to a new position, collecting £200 if they pass GO."""
        tile_name = "Unknown tile"

        if hasattr(self.game, "ui") and hasattr(self.game.ui, "board"):
            try:
                tile_name = self.game.ui.board.spaces[new_position - 1].name
            except (IndexError, AttributeError):
                pass

        if new_position < self.position:
            self.balance += 200
            self.passed = True
            message = f"🛤️ {self.name} passes GO and collects £200!"
            print(message)
            self.game.log_event(message)

        self.position = new_position

        if self.position != 1:
            message = f"🚀 {self.name} moves to {tile_name}."
            print(message)
            self.game.log_event(message)


    def assess_property_repair(self, game, house_cost, hotel_cost):
        """Charges players for property repairs."""
        total_houses = sum(p.houses for p in self.owned_properties if not p.mortgaged)
        total_hotels = sum(1 for p in self.owned_properties if p.houses == 5)

        total_cost = (total_houses * house_cost) + (total_hotels * hotel_cost)

        if total_cost > 0:
            print(f"🏚️ {self.name} pays £{total_cost} for property repairs.")
            self.balance -= total_cost
            game.fines += total_cost

    def bot_bid(self, highest_bid, property):
        #The intermediate bot will bid 10% of the difference between the highest bid and the property value, up to 1.5x the property value.
        if self.identity == "Basic Bot":
            if highest_bid < property.price:
                bid = (highest_bid + (property.price - highest_bid) * 0.1) + 1
            else:
                bid = highest_bid + (property.price * 0.1)
            bid = int(bid)
            if bid > self.balance or bid > property.price * 1.5:
                return "exit"
        else:
            bid = "exit"
        return str(bid)
    
    def bot_buy_property(self, property):
        if self.identity == "Basic Bot":
            if self.balance > property.price:
                return "yes"
            else:
                return "no"
        else:
            return "no"
        
    def bot_get_out_of_jail(self):
        if self.identity == "Basic Bot" and self.balance >= 50:
            return "yes"
        return "no"
    
    def bot_avoid_bankruptcy(self, options, amount_due, creditor):
        if self.identity == "Basic Bot":
            option = options.index("Declare Bankruptcy") + 1
        return option
    
    def bot_options(self):
        if self.identity == "Basic Bot":
            return 5
        return 5
    
    def bot_trade(self, offer_properties, request_properties, offer_money, request_money):
        if self.identity == "Basic Bot":
            return "no"
        return "no"