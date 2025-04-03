from GameElements.property import Property
from collections import deque


class Bank:

    def __init__(self):
        self.balance = 50000
        self.properties = {}
        self.initialize_properties()

    def initialize_properties(self):
        property_data = [
            (2, "The Old Creek", 60, [2, 10, 30, 90, 160, 250], 50, "Brown"),
            (4, "Gangsters Paradise", 60, [4, 20, 60, 180, 320, 450], 50, "Brown"),
            (6, "Brighton Station", 200, [25, 50, 100, 200], 0, "Station"),
            (7, "The Angels Delight", 100, [6, 30, 90, 270, 400, 550], 50, "Light Blue"),
            (9, "Potter Avenue", 100, [6, 30, 90, 270, 400, 550], 50, "Light Blue"),
            (10, "Granger Drive", 120, [8, 40, 100, 300, 450, 600], 50, "Light Blue"),
            (12, "Skywalker Drive", 140, [10, 50, 150, 450, 625, 750], 100, "Pink"),
            (13, "Tesla Power Co", 150, [4, 10], 0, "Utilities"),
            (14, "Wookie Hole", 140, [10, 50, 150, 450, 625, 750], 100, "Pink"),
            (15, "Rey Lane", 160, [12, 60, 180, 500, 700, 900], 100, "Pink"),
            (16, "Hove Station", 200, [25, 50, 100, 200], 0, "Station"),
            (17, "Bishop Drive", 180, [14, 70, 200, 550, 750, 950], 100, "Orange"),
            (19, "Dunham Street", 180, [14, 70, 200, 550, 750, 950], 100, "Orange"),
            (20, "Broyles Lane", 200, [16, 80, 220, 600, 800, 1000], 100, "Orange"),
            (22, "Yue Fei Square", 220, [18, 90, 250, 700, 875, 1050], 150, "Red"),
            (24, "Mulan Rouge", 220, [18, 90, 250, 700, 875, 1050], 150, "Red"),
            (25, "Han Xin Gardens", 240, [20, 100, 300, 750, 925, 1100], 150, "Red"),
            (26, "Falmer Station", 200, [25, 50, 100, 200], 0, "Station"),
            (27, "Shatner Close", 260, [22, 110, 330, 800, 975, 1150], 150, "Yellow"),
            (28, "Picard Avenue", 260, [22, 110, 330, 800, 975, 1150], 150, "Yellow"),
            (29, "Edison Water", 150, [4, 10], 0, "Utilities"),
            (30, "Crusher Creek", 280, [24, 120, 360, 850, 1025, 1200], 150, "Yellow"),
            (32, "Sirat Mews", 300, [26, 130, 390, 900, 1100, 1275], 200, "Green"),
            (33, "Ghengis Crescent", 300, [26, 130, 390, 900, 1100, 1275], 200, "Green"),
            (35, "Ibis Close", 320, [28, 150, 450, 1000, 1200, 1400], 200, "Green"),
            (36, "Portslade Station", 200, [25, 50, 100, 200], 0, "Station"),
            (38, "James Webb Way", 350, [35, 175, 500, 1100, 1300, 1500], 200, "Deep blue"),
            (40, "Turing Heights", 400, [50, 200, 600, 1400, 1700, 2000], 200, "Deep lbue"),
        ]

        for data in property_data:
            position = data[0]
            self.properties[position] = Property(*data)

    def auction_property(self, auction_property, players):
        """Conducts a fair auction with proper bidding rounds."""
        """Auction should only start if at least 1 other player has passed go"""
        #count number of players who have player.passed = True
        if [player.passed for player in players].count(True) <= 1:        
            print("Auction cannot start because no other player has passed GO.")
            return

        print(f"Auctioning {auction_property.name}!")

        highest_bidder = None
        active_bidders = [p for p in players if p.balance >= 0 and p.passed]

        highest_bidder, highest_bid = self.bid_property(active_bidders, auction_property)

        highest_bidder.balance -= highest_bid
        self.balance += highest_bid
        auction_property.transfer_property(highest_bidder)
        print(f"🎉 {highest_bidder.name} won {auction_property.name} for £{highest_bid}")

    def bid_property(self, active_bidders, property, highest_bid=0):
        def valid_bid(bid, player):
            if bid.lower() == "exit":
                return True
            try:
                if int(bid) > player.balance:
                    print("You can't bid more than your balance!")
                    return False
                elif int(bid) <= highest_bid:
                    print("You must bid higher than the current highest bid!")
                    return False
                return True
            except ValueError:
                print("Invalid input, try again.")
                return False
            
        bidding_queue = deque(active_bidders)

        while len(bidding_queue) > 1:

            player = bidding_queue.popleft()

            print(f"{player.name}'s current balance: £{player.balance}")

            if highest_bid > player.balance:
                print(f"{player.name} only has £{player.balance} and the current highest bid is £{highest_bid}.")
                continue
            
            if player.identity == "Human":
                while True:
                    bid = input(f"{player.name}, enter your bid (or 'exit' to exit): ")
                    if valid_bid(bid, player):
                        if bid != "exit":
                            bid = int(bid)
                        break
            else:
                bid = player.bot_bid(highest_bid, property)
                # The bot only gets one chance to submit a valid bid. Otherwise, it will pass. This is to prevent the bot from getting stuck in an infinite loop.
                print(f"{player.name} bids {bid}.")
                if not valid_bid(bid, player):
                    print(f"{player.name} tried to bid an invalid amount. Since {player.name} is a bot, it will pass.")
                    bid = "exit"

            if bid == 'exit':
                print(f"{player.name} has exited the auction.")
                continue

            highest_bid = int(bid)
            bidding_queue.append(player)

        return bidding_queue[0], highest_bid


    def sell_property_to_the_bank(self, plr, sold_property):
        if sold_property not in plr.owned_properties:
            return f"{sold_property.name} is not owned by {plr.name}."

        if sold_property.houses > 0:
            return f"{sold_property.name} still has {sold_property.houses} house(s). Sell them before selling the property."

        if sold_property.mortgaged:
            value = sold_property.price // 2
            plr.balance += value
            self.balance -= value
            sold_property.mortgaged = False
            msg = f"{plr.name} sold mortgaged {sold_property.name} to the bank for £{value}."
        else:
            value = sold_property.price
            plr.balance += value
            self.balance -= value
            msg = f"{plr.name} sold {sold_property.name} to the bank for £{value}."

        plr.owned_properties.remove(sold_property)
        sold_property.owner = None
        print(msg)
        return msg


    def sell_houses_to_the_bank(self, plr, selected_property):
        """Allows the player to sell one house to the bank for half the build cost."""
        if selected_property.houses == 0:
            message = f"No houses available to sell on {selected_property.name}."
            print(message)
            return message
        else:
            group_properties = [prop for prop in selected_property.owner.owned_properties if prop.group == selected_property.group]
            max_houses = max(prop.houses for prop in group_properties)
            if selected_property.houses - 1 < max_houses - 1:
                print(f"{selected_property.owner.name} is attempting to sell houses on {selected_property.name}, but the number of houses in the group must be symmetrical (difference of at most 1).")
                return (f"{selected_property.owner.name} is attempting to sell houses on {selected_property.name}, but the number of houses in the group must be symmetrical (difference of at most 1).")

        num = 1  # 1 house at a time
        sale_value = (selected_property.house_cost // 2) * num

        selected_property.houses -= num
        plr.balance += sale_value

        message = f"{plr.name} sold {num} house(s) from {selected_property.name} for £{sale_value}."
        print(message)
        if hasattr(plr.game, "log_event"):
            plr.game.log_event(message)

        return message



    def mortgage_property(self, plr, selected_property):
        """Allows the player to mortgage a property to raise funds"""
        if selected_property.mortgaged:
            print(f"{plr.name} tried to mortgage {selected_property.name} to the bank but it's already mortgaged.")
            return (f"{plr.name} tried to mortgage {selected_property.name} to the bank but it's already mortgaged.")
        elif not selected_property.houses == 0:
            print(f"{plr.name} tried to mortgage {selected_property.name} but it already has houses built on it.")
            return (f"{plr.name} tried to mortgage {selected_property.name} but it already has houses built on it.")

        selected_property.mortgaged = True
        mortgage_value = selected_property.price // 2
        plr.balance += mortgage_value
        self.balance -= mortgage_value
        print(f"{plr.name} mortgaged {selected_property.name} .")

    def unmortgage_property(self, plr, selected_property):
        """Allows player to unmortgage a property"""
        mortgage_value = selected_property.price // 2
        if not selected_property.mortgaged:
            print(f"{plr.name} tried to unmortgage {selected_property.name} from the bank but it's not mortgaged.")
            return (f"{plr.name} tried to unmortgage {selected_property.name} from the bank but it's not mortgaged.")
        elif plr.balance < mortgage_value:
            print(
                f"{plr.name} tried to unmortgage {selected_property.name} from the bank but he doesn't have the sufficient balance.")
            return (
                f"{plr.name} tried to unmortgage {selected_property.name} from the bank but he doesn't have the sufficient balance.")

        selected_property.mortgaged = False
        plr.balance -= mortgage_value
        self.balance += mortgage_value
        print(f"{plr.name} unmortgaged {selected_property.name} .")
        return (f"{plr.name} unmortgaged {selected_property.name} .")


    def build(self, number_of_houses, selected_property, plr):  # MAYBE SHOULD BE IN PROPERTY
        total_cost = number_of_houses * selected_property.house_cost

        if not selected_property.check_completion():
            print(
                f"{selected_property.owner.name} is attempting to build on {selected_property.name} a property of group {selected_property.group} which has not completed.")
            return (f"{selected_property.owner.name} is attempting to build on {selected_property.name} a property of group {selected_property.group} which has not completed.")
        elif selected_property.owner.balance < total_cost:
            print(
                f"{selected_property.owner.name} doesn't have enough money to build {number_of_houses} on {selected_property.name}.")
            return (f"{selected_property.owner.name} doesn't have enough money to build {number_of_houses} on {selected_property.name}.")
        elif selected_property.houses + number_of_houses > 5:  # Checks if the number exceeds the maximum number houses
            print(
                f"{selected_property.owner.name} is attempting to build more than the maximum number of houses on {selected_property.name}  which is 5 for any given property.")
            return (f"{selected_property.owner.name} is attempting to build more than the maximum number of houses on {selected_property.name}  which is 5 for any given property.")

        group_properties = [prop for prop in selected_property.owner.owned_properties if prop.group == selected_property.group]
        min_houses = min(prop.houses for prop in group_properties)
        if selected_property.houses + number_of_houses > min_houses + 1:
            print(
                f"{selected_property.owner.name} is attempting to build houses on {selected_property.name}, but the number of houses in the group must be symmetrical (difference of at most 1).")
            return (f"{selected_property.owner.name} is attempting to build houses on {selected_property.name}, but the number of houses in the group must be symmetrical (difference of at most 1).")
        else :
            selected_property.houses += number_of_houses
            plr.balance -= total_cost
            self.balance += total_cost
            print(f"{selected_property.owner.name} built {number_of_houses} house(s) on {selected_property.name}")
            return (f"{selected_property.owner.name} built {number_of_houses} house(s) on {selected_property.name}")

    def pay_player(self, player, amount):
        """Pays a player the specified amount."""
        if self.balance >= amount:
            self.balance -= amount
            player.balance += amount
            print(f"{player.name} received £{amount}.")
        else:
            print(f"{self.name} doesn’t have enough money to pay £{amount}! Selling assets...")
            self.avoid_bankruptcy(amount, player)

    def receive_payment(self, player, amount):
        """Receives payment from a player."""
        if player.balance >= amount:
            self.balance += amount
            player.balance -= amount
            print(f"{player.name} paid £{amount}.")
        else:
            print(f"{player.name} doesn’t have enough money to pay £{amount}! Selling assets...")
            player.avoid_bankruptcy(amount, self)
