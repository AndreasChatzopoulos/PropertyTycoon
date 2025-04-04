import random
import pygame



class Player:
    """
    Represents a player in the Property Tycoon game.

    Each player has a name, token, identity (e.g., Human or Bot), and various 
    attributes to track their state throughout the game such as their balance, 
    current position on the board, jail status, and properties they own.

    The Player class contains all core methods to:
    - Roll dice and move across the board
    - Buy, sell, mortgage, and manage properties
    - Handle special tile interactions (e.g., tax, cards, jail)
    - Pay rent and taxes
    - Handle bankruptcy and financial decision-making
    - Execute bot behavior and AI strategies (for non-human players)

    Attributes:
        name (str): The name of the player.
        token (str): The chosen token icon or name.
        identity (str): Either "Human" or bot type (e.g., "Basic Bot").
        game (Game): Reference to the current game instance.
        balance (int): The player's current money balance.
        owned_properties (list): Properties currently owned by the player.
        passed (bool): Whether the player has passed the GO tile.
        in_jail (bool): Jail status.
        position (int): Current board position (1 to 40).
        get_out_of_jail_cards (int): Number of "Get Out of Jail Free" cards.
        jail_turns (int): Number of turns spent in jail.
        consecutive_doubles (int): Track for rolling doubles consecutively.
        turns_taken (int): Number of turns the player has completed.
        turns_skipped (int): Turns the player had to skip (e.g., from jail).
        just_sent_to_jail (bool): If the player was just sent to jail.
    """
    def __init__(self, name, token, identity, game):
        """
        Initializes a Player instance with default attributes and references.

        Args:
            name (str): The name of the player.
            token (str): A visual or symbolic representation of the player.
            identity (str): Describes the type of player ("Human", "Basic Bot", etc.).
            game (Game): Reference to the Game instance the player is part of.

        Attributes:
            balance (int): The player's starting balance (default £1500).
            owned_properties (list): A list of properties the player owns.
            passed (bool): Flag to indicate if the player has passed GO.
            in_jail (bool): True if the player is currently in jail.
            position (int): The current board position of the player (1-based).
            get_out_of_jail_cards (int): Number of "Get Out of Jail Free" cards held.
            jail_turns (int): How many turns the player has spent in jail.
            consecutive_doubles (int): Counter for tracking double rolls.
            turns_taken (int): Total number of turns the player has taken.
            turns_skipped (int): Turns missed (e.g., due to jail).
            just_sent_to_jail (bool): True if the player was sent to jail this turn.
        """
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
        self.turns_taken = 0
        self.turns_skipped = 0  
        self.just_sent_to_jail = False


    def roll_dice(self):
        """
        Simulates rolling two six-sided dice and determines if the result is a double.

        Returns:
            tuple: A tuple containing three elements:
                - die1 (int): The result of the first die roll (1-6).
                - die2 (int): The result of the second die roll (1-6).
                - double (bool): True if both dice show the same number, indicating a double.
        """
        die1, die2 = random.randint(1, 6), random.randint(1, 6)
        print(f"{self.name} rolls {die1} and {die2} for a total of ({die1 + die2})")
        double = (die1 == die2)
        return die1, die2, double

    def move(self, die1, die2, double):
        """
        Handles player movement on the board, including jail logic, doubles handling, and passing GO.

        If the player is in jail:
            - A human player's turn is deferred for UI handling.
            - A bot attempts to roll doubles or is released after 3 turns.

        If the player rolls three consecutive doubles, they are sent to jail.

        Players who pass GO receive £200.

        Args:
            die1 (int): Value of the first die roll.
            die2 (int): Value of the second die roll.
            double (bool): Indicates if a double was rolled (both dice show same number).

        Side Effects:
            - Updates player position, balance, jail status, and consecutive doubles.
            - Logs events to the game log.
            - Visually animates movement if in GUI mode.
        """
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
        self.last_roll = steps
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
        """
        Handles the purchase of a property by the player.

        Deducts the property's price from the player's balance, adds it to the bank's balance,
        updates ownership, and logs the purchase.

        Args:
            property_at_position (Property): The property object the player is purchasing.

        Side Effects:
            - Updates player and bank balances.
            - Transfers property ownership to the player.
            - Logs the event to the game log.
        """
        self.balance -= property_at_position.price

        self.game.bank.balance += property_at_position.price

        property_at_position.owner = self
        self.owned_properties.append(property_at_position)

        message = f"{self.name} bought {property_at_position.name} for £{property_at_position.price}!"
        print(message)
        self.game.log_event(message)

    def go_to_jail(self):
        """
        Sends the player to jail.

        Sets the player's `in_jail` flag to True, updates their position to the jail tile (position 11),
        and logs the event. If a jail sound is configured in the UI, it will be played.

        Side Effects:
            - Updates player position and jail status.
            - Triggers jail sound effect if available.
            - Logs the event to the game log.
        """
        self.in_jail = True
        self.position = 11
        self.just_sent_to_jail = True
        self.game.log_event(f"{self.name} has been sent to jail!")

        if hasattr(self.game, "ui") and hasattr(self.game.ui, "jail_sound") and self.game.ui.jail_sound:
            self.game.ui.jail_sound.play()


    def get_out_of_jail(self, double=False, turns=False):
        """
        Attempts to release the player from jail based on specific conditions.

        A player may be released from jail by one of the following:
        - Rolling a double.
        - Using a 'Get Out of Jail Free' card.
        - Paying a £50 fine (for bots only).
        - Serving 3 full turns in jail (for bots only).

        Args:
            double (bool): Whether the player rolled a double this turn.
            turns (bool): Whether the player has been in jail for 3 turns.

        Side Effects:
            - Updates player status (`in_jail`, `jail_turns`, `balance`).
            - Logs the outcome to the game event log.
            - Plays jail release sound (if available).
        """
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
        """
        Deducts a tax amount from the player's balance. Triggers bankruptcy handling if the player cannot afford it.

        Args:
            amount (int): The tax amount to be paid.

        Side Effects:
            - Reduces the player's balance if sufficient.
            - Logs the payment or failed attempt.
            - Calls bankruptcy handling if the balance is insufficient.
        """
        if self.balance >= amount:
            self.balance -= amount
            self.game.log_event(f"{self.name} paid tax of £{amount}!")
        else:
            self.game.log_event(f"{self.name} cannot afford tax of £{amount}!")
            self.avoid_bankruptcy(amount, None)


    def pay_rent(self, property_at_position, roll):
        """
        Handles rent payment when the player lands on a property owned by another player.

        Args:
            property_at_position (Property): The property where the player landed.
            roll (int): The result of the player's last dice roll (used for utilities).

        Side Effects:
            - Deducts rent from the player's balance if they can afford it.
            - Transfers rent to the property owner (creditor).
            - Logs the rent transaction or inability to pay.
            - Initiates bankruptcy handling if the player cannot pay the rent.
        """
        creditor = property_at_position.owner

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
            message = f"{self.name} doesn’t have enough money to pay £{amount_due} rent to {creditor.name}! Attempting to raise funds..."
            print(message)
            self.game.log_event(message)
            self.avoid_bankruptcy(amount_due, creditor)



    def select_property(self, action):  
        """
        Prompts the user to select one of their owned properties for a specified action.

        Args:
            action (str): Description of the action the property is being selected for (e.g., "sell", "mortgage").

        Returns:
            Property | None: The selected Property object if valid, otherwise None.

        Side Effects:
            - Prints the player's owned properties to the console.
            - Prompts the user for input via the terminal.
        """
        if not self.owned_properties:
            print(f"{self.name} has no properties to {action}.")
            return None

        print(f" {self.name}'s Owned Properties:")
        for idx, prop in enumerate(self.owned_properties, start=1):  
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

    def avoid_bankruptcy(self, amount_due, creditor):
        """
        Attempts to raise funds to avoid bankruptcy. Bots resolve automatically; humans are prompted via GUI.

        Args:
            amount_due (int): The total amount the player owes.
            creditor (Player | None): The player or bank to whom the debt is owed.

        Returns:
            None

        Side Effects:
            - For bots, triggers automatic property sales, mortgages, or bankruptcy.
            - For humans, displays a bankruptcy popup via the UI.
            - Adjusts balances, ownerships, and logs relevant events.
        """
        if self.identity != "Human":
            # Bot automatically tries to sell/mortgage properties to raise funds
            for prop in sorted(self.owned_properties, key=lambda p: p.price):
                if self.balance >= amount_due:
                    break

                if prop.houses > 0:
                    self.game.bank.sell_houses_to_the_bank(self, prop)

                if not prop.mortgaged and self.balance < amount_due:
                    self.game.bank.mortgage_property(self, prop)

                if prop.houses == 0 and self.balance < amount_due:
                    self.game.bank.sell_property_to_the_bank(self, prop)

            if self.balance >= amount_due:
                self.balance -= amount_due
                if creditor:
                    creditor.balance += amount_due
                    self.game.log_event(f"{self.name} paid £{amount_due} to {creditor.name}.")
            else:
                self.declare_bankruptcy(creditor, amount_due)
            return

        self.game.ui.bankruptcy_popup = self.game.ui.create_bankruptcy_popup(self, amount_due, creditor)


    def declare_bankruptcy(self, creditor, debt):
        """
        Handles the process when a player goes bankrupt.

        Transfers all of the player's properties to the creditor (another player or the bank),
        removes the player from the game, and updates the game log and UI.

        Args:
            creditor (Player | None): The recipient of the player’s assets. If None, assets go to the bank.
            debt (int): The amount the player is unable to pay.

        Returns:
            None

        Side Effects:
            - Transfers ownership of properties.
            - Removes player from the game.
            - Resets player balance and property list.
            - Updates the UI and game log.
        """
        print(f"{self.name} is bankrupt! Cannot pay £{debt} to {creditor.name if creditor else 'the Bank'}.")

        if creditor:
            for prop in self.owned_properties[:]:
                prop.transfer_property(creditor)
        else:
            self.return_properties_to_bank()

        self.owned_properties.clear()
        self.balance = 0

        message = f"{self.name} has gone bankrupt and is out of the game."
        print(message)
        self.game.log_event(message)

        self.game.remove_player(self)

        if hasattr(self.game.ui, "bankruptcy_popup") and self.game.ui.bankruptcy_popup:
            self.game.ui.bankruptcy_popup.visible = False
            self.game.ui.bankruptcy_popup = None



    def return_properties_to_bank(self):
        """
        Resets ownership of all properties owned by the player.

        This is typically called when a player goes bankrupt and their properties need to be returned to the bank.

        Args:
            None

        Returns:
            None

        Side Effects:
            - Clears the player's list of owned properties.
            - Sets the owner of each property to None.
        """
        for prop in self.owned_properties[:]:
            self.owned_properties.remove(prop)
            prop.owner = None  


    # def manage_property(self): # Terminal game function 
    #     """
    #     Provides an interactive interface for a human player to manage one of their owned properties.

    #     The player can choose to:
    #     - Sell the property to the bank (only if no houses are built)
    #     - Mortgage the property
    #     - Unmortgage the property
    #     - Sell houses (if any exist)
    #     - Build houses (if property is completed and below max houses)

    #     This method is intended for use in a terminal-based interface and may be deprecated in GUI versions.

    #     Args:
    #         None

    #     Returns:
    #         None

    #     Side Effects:
    #         - Updates player's balance and property status based on their management decisions.
    #         - Prints options and prompts to the terminal.
    #     """
    #     if not self.owned_properties:
    #         print(f"{self.name} has no properties to manage.")
    #         return

    #     # Let the player select a property
    #     selected_property = self.select_property("manage")
    #     if not selected_property:
    #         return

    #     while True:
    #         print(f"\n Managing {selected_property.name}:")
    #         print("Balance:", self.balance)

    #         # Dynamically generate available options
    #         options = {}
    #         option_number = 1

    #         if selected_property.houses == 0:  # Selling only possible when no houses exist
    #             options[option_number] = "Sell the property to the bank"
    #             option_number += 1
    #         if not selected_property.mortgaged:
    #             options[option_number] = "Mortgage the property"
    #             option_number += 1
    #         if selected_property.mortgaged:
    #             options[option_number] = "Unmortgage the property"
    #             option_number += 1
    #         if selected_property.houses > 0:
    #             options[option_number] = "Sell houses from the property"
    #             option_number += 1
    #         if selected_property.completed and selected_property.houses < 5:
    #             options[option_number] = "Build houses on the property"
    #             option_number += 1

    #         # Show available options
    #         for key, value in options.items():
    #             print(f"{key}. {value}")
    #         print(f"{option_number}. Exit Property Management")  # Exit option

    #         # Get player's choice
    #         try:
    #             choice = int(input("Enter the number of your choice: "))
    #             if choice not in options and choice != option_number:
    #                 print("Invalid choice. Try again.")
    #                 continue
    #         except ValueError:
    #             print("Please enter a valid number.")
    #             continue

    #         # Execute the chosen option
    #         if choice == option_number:  # Exit
    #             print("Exiting property management.")
    #             return
    #         else:
    #             if options[choice] == "Sell the property to the bank":
    #                 self.game.bank.sell_property_to_the_bank(self, selected_property)
    #             elif options[choice] == "Mortgage the property":
    #                 self.game.bank.mortgage_property(self, selected_property)
    #             elif options[choice] == "Unmortgage the property":
    #                 self.game.bank.unmortgage_property(self, selected_property)
    #             elif options[choice] == "Sell houses from the property":
    #                 self.game.bank.sell_houses_to_the_bank(self, selected_property)
    #             elif options[choice] == "Build houses on the property":
    #                 number_of_houses = 1
    #                 self.game.bank.build(number_of_houses, selected_property, self)


    def move_player_to(self, new_position):
        """
        Moves the player to a specific board position. 
        Awards £200 if the movement passes GO.

        Args:
            new_position (int): The target tile number to move the player to (1–40).

        Returns:
            None

        Side Effects:
            - Updates the player's position.
            - Increases player balance and sets `passed` flag if GO is passed.
            - Logs movement events to the game log.
        """
        tile_name = "Unknown tile"

        if hasattr(self.game, "ui") and hasattr(self.game.ui, "board"):
            try:
                tile_name = self.game.ui.board.spaces[new_position - 1].name
            except (IndexError, AttributeError):
                pass

        if new_position < self.position:
            self.balance += 200
            self.passed = True
            message = f"{self.name} passes GO and collects £200!"
            print(message)
            self.game.log_event(message)

        self.position = new_position

        if self.position != 1:
            message = f"{self.name} moves to {tile_name}."
            print(message)
            self.game.log_event(message)


    def assess_property_repair(self, game, house_cost, hotel_cost):
        """
        Charges the player for repairs based on the number of houses and hotels they own.

        Args:
            game (Game): The current game instance to update fines and log events.
            house_cost (int): The repair cost per house.
            hotel_cost (int): The repair cost per hotel (5 houses on a property).

        Returns:
            None

        Side Effects:
            - Deducts the repair cost from the player's balance.
            - Adds the total repair cost to the game's fines pool.
            - Logs the event to the game log.
            - Triggers bankruptcy handling if the player can't afford the repairs.
        """
        total_houses = sum(p.houses for p in self.owned_properties if not p.mortgaged)
        total_hotels = sum(1 for p in self.owned_properties if p.houses == 5 and not p.mortgaged)

        total_cost = (total_houses * house_cost) + (total_hotels * hotel_cost)

        if total_cost > 0:
            print(f"{self.name} must pay £{total_cost} for property repairs.")
            
            if self.balance >= total_cost:
                self.balance -= total_cost
                game.fines += total_cost
                game.log_event(f"{self.name} paid £{total_cost} for property repairs.")
            else:
                game.log_event(f"{self.name} cannot afford £{total_cost} for property repairs.")
                self.avoid_bankruptcy(total_cost, None)


    def bot_bid(self, highest_bid, property):
        """
        Determines the bot's bidding behavior during an auction.

        The "Basic Bot" will bid approximately 10% of the difference between 
        the current highest bid and the property's value, but only up to 1.5x 
        the property price or its own balance, whichever is lower.

        Args:
            highest_bid (int): The current highest bid in the auction.
            property (Property): The property being auctioned.

        Returns:
            str: The bot's bid as a string, or "exit" if it chooses not to bid.

        Behavior:
            - If the bot is not "Basic Bot", it always exits.
            - Ensures bot does not bid over its own balance or irrational amounts.
        """
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
        """
        Determines whether the bot will buy a property when landing on it.

        The "Basic Bot" will buy the property if it has enough balance to afford it.
        Other bot identities will always decline the purchase.

        Args:
            property (Property): The property the bot is considering to purchase.

        Returns:
            str: "yes" if the bot decides to buy, otherwise "no".

        Behavior:
            - "Basic Bot" buys only if its balance is greater than the property's price.
            - Other bot types automatically return "no".
        """
        if self.identity == "Basic Bot":
            if self.balance > property.price:
                return "yes"
            else:
                return "no"
        else:
            return "no"
        
    def bot_get_out_of_jail(self):
        """
        Determines whether the bot should pay to get out of jail.

        The "Basic Bot" will pay £50 to get out of jail if it has sufficient funds.

        Returns:
            str: "yes" if the bot will pay to get out, "no" otherwise.

        Behavior:
            - "Basic Bot" returns "yes" if balance >= £50.
            - Other bot types return "no".
        """
        if self.identity == "Basic Bot" and self.balance >= 50:
            return "yes"
        return "no"
    
    def bot_options(self):
        """
        Returns the bot's decision for post-turn options.

        This is a placeholder method that currently always returns option 5.

        Returns:
            int: A fixed value of 5, representing a specific post-turn action.

        Behavior:
            - Used for skipping or finalizing turn in basic bots.
        """
        if self.identity == "Basic Bot":
            return 5
        return 5
    
    def bot_trade(self, offer_properties, request_properties, offer_money, request_money):
        """
        Determines whether the bot accepts a proposed trade.

        Args:
            offer_properties (list): Properties offered by the current player.
            request_properties (list): Properties requested from the bot.
            offer_money (int): Money offered by the current player.
            request_money (int): Money requested from the bot.

        Returns:
            str: "no" to decline the trade (always).

        Behavior:
            - "Basic Bot" currently declines all trade offers.
        """
        if self.identity == "Basic Bot":
            return "no"
        return "no"