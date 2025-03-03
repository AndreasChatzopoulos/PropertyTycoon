import random



class Player:
    def __init__(self, name, token, game):
        """Player initialization with reference to the existing Game instance."""
        self.name = name
        self.token = token
        self.game = game  # ✅ Fix: Store game reference instead of creating a new game
        self.balance = 1500
        self.owned_properties = []
        self.passed = False
        self.in_jail = False
        self.position = 0
        self.get_out_of_jail_cards = 0
        self.jail_turns = 0
        self.consecutive_doubles = 0

    def roll_dice(self):
        die1, die2 = random.randint(1, 6), random.randint(1, 6)
        double = (die1 == die2)
        return die1, die2, double

    def move(self):  # Handle Jail
        die1, die2, double = self.roll_dice()
        if double:
            self.consecutive_doubles += 1
            if self.consecutive_doubles >= 3:
                self.go_to_jail()
                self.consecutive_doubles = 0
                return
            else:
                if self.in_jail:
                    self.get_out_of_jail()
        elif self.in_jail:
            self.jail_turns += 1
            if self.jail_turns >= 3:
                self.get_out_of_jail(False, True)
            else:
                print(f"{self.name} stays in jail (Turn {self.jail_turns})")
                return self.consecutive_doubles > 0

        original_position = self.position
        self.position = (self.position + die1 + die2) % 40
        print(f"{self.name} moves to position {self.position}")
        if self.position < original_position:
            self.passed = True
            self.balance += 200
            self.game.bank.balance -= 200
            print(f"🛤️ {self.name} passed GO and collected £200!")

    def buy_property(self, property_at_position):
        # Deduct money from the player
        self.balance -= property_at_position.price

        # Add money to the bank
        self.game.bank.balance += property_at_position.price

        # Transfer ownership
        property_at_position.owner = self
        self.owned_properties.append(property_at_position)

        print(f"✅ {self.name} bought {property_at_position.name} for £{property_at_position.price}!")

    def go_to_jail(self):  # Adjust for doubles
        self.in_jail = True
        self.position = 11
        print(f"{self.name} has been sent to jail!")

    def get_out_of_jail(self, double=False, turns=False):

        if self.get_out_of_jail_cards > 0:
            print(f"{self.name} uses a Get Out of Jail Free card!")
            self.get_out_of_jail_cards -= 1
            self.jail_turns = 0
            self.in_jail = False
        elif double:
            print(f"{self.name} Rolled a Double!")
            self.jail_turns = 0
            self.in_jail = False
        elif turns:
            print(f"{self.name} Served 3 turns!")
            self.jail_turns = 0
            self.in_jail = False

    def pay_tax(self, amount):
        self.balance -= amount
        print(f"{self.name} paid income tax of £200!")

    def pay_rent(self, property_at_position, roll):
        """Handles rent payment when landing on an owned property."""
        amount_due = property_at_position.calculate_rent(roll)
        creditor = property_at_position.owner

        if self.balance >= amount_due:
            self.balance -= amount_due
            creditor.balance += amount_due
            print(f"{self.name} paid £{amount_due} in rent to {creditor.name}.")
        else:
            print(f"❌ {self.name} doesn’t have enough money to pay £{amount_due}! Selling assets...")
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
                options.append("1️⃣  Sell Houses/Hotels")
            if any(not p.mortgaged for p in
                   self.owned_properties):  # Checks if the player has any unmortgaged properties
                options.append("2️⃣  Mortgage Properties")
            if any(p.houses == 0 for p in
                   self.owned_properties):  # Checks if the player has any properties available to sell
                options.append("3️⃣  Sell Properties to the Bank")
            if len(self.owned_properties) > 1:  # Checks if the player has any available properties to trade
                options.append("4️⃣  Offer a Trade")
            options.append("5️⃣  Declare Bankruptcy")

            # Print available choices
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            # Get player's choice
            try:
                choice = int(input("Enter the number of your choice: "))
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
        for prop in self.owned_properties:
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
            elif options[choice] == "Sell the property to the bank":
                self.game.bank.sell_property_to_the_bank(self, selected_property)
                self.game.player_options(self)
            elif options[choice] == "Mortgage the property":
                self.game.bank.mortgage_property(self, selected_property)
                selected_property.mortgage()
            elif options[choice] == "Unmortgage the property":
                self.game.bank.unmortgage_property(self, selected_property)
                selected_property.unmortgage()
            elif options[choice] == "Sell houses from the property":
                self.game.bank.sell_houses_to_the_bank(self, selected_property)
            elif options[choice] == "Build houses on the property":
                number_of_houses = input("Enter the numbers of houses you want to build: ")
                self.game.bank.build(number_of_houses, selected_property, self)

    def move_player_to(self, new_position):
        """Moves the player to a new position, collecting £200 if they pass GO."""
        if new_position < self.position:
            print(f"🛤️ {self.name} passes GO and collects £200!")
            self.balance += 200

        self.position = new_position
        print(f"🚀 {self.name} moves to position {self.position}.")

    def assess_property_repair(self, game, house_cost, hotel_cost):
        """Charges players for property repairs."""
        total_houses = sum(p.houses for p in self.owned_properties if not p.mortgaged)
        total_hotels = sum(1 for p in self.owned_properties if p.houses == 5)

        total_cost = (total_houses * house_cost) + (total_hotels * hotel_cost)

        if total_cost > 0:
            print(f"🏚️ {self.name} pays £{total_cost} for property repairs.")
            self.balance -= total_cost
            game.fines += total_cost
