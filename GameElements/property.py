
class Property:
    color_group_sizes = {  # Store it inside the class
        "Brown": 2, "Blue": 3,"Station": 4, "Pink": 3, "Utilities": 2, "Orange": 3,
        "Red": 3, "Yellow": 3, "Green": 3, "Deep blue": 2
    }

    def __init__(self, position, name, price, rent, house_cost, group):
        self.name = name
        self.price = price
        self.position = position
        self.rent = rent
        self.house_cost = house_cost
        self.group = group
        self.completed = False
        self.houses = 0
        self.owner = None
        self.mortgaged = False
        self.already_auctioned = False # Wether the property has been auctioned this turn or not

    def calculate_rent(self, dice_roll=None):
        """Determines rent based on property type, ownership, and houses/hotels."""
        if self.group == "Utilities":
            if self.owner:
                utilities_count = sum(1 for p in self.owner.owned_properties if p.group == "Utilities")
                multiplier = 4 if utilities_count == 1 else 10
                if dice_roll is not None:
                    return dice_roll * multiplier
                else:
                    return 0  # Defensive: no roll passed

        elif self.group == "Station":
            if self.owner:
                station_count = sum(1 for p in self.owner.owned_properties if p.group == "Station")
                return [25, 50, 100, 200][station_count - 1]

        elif self.group in Property.color_group_sizes:
            if self.check_completion() and self.houses == 0:
                return self.rent[0] * 2  # Double rent for full set
            return self.rent[self.houses]

        return 0


    def property_details(self):
        return f"{self.name} | Owner: {self.owner.name} | Houses: {self.houses} | Rent: {self.calculate_rent()}"

    def transfer_property(self, new_owner):  # Transfer ownership of the property to another player
        # Adjust for group completion
        # Transfers property ownership to a new player, updating necessary values.

        if self.owner:
            self.owner.owned_properties.remove(self)  # Remove from old owner

        self.owner = new_owner
        new_owner.owned_properties.append(self)  # Add to new owner

        # Check if new owner now owns a complete set
        properties_in_group = [p for p in new_owner.owned_properties if p.group == self.group]
        if len(properties_in_group) == Property.color_group_sizes[
            self.group]:  # Assuming a dictionary of color group sizes
            # ADJUST
            for p in properties_in_group:
                p.completed = True
            print(f" {new_owner.name} now owns the full {self.group} set!")

        print(f"{self.name} is now owned by {new_owner.name}.")

    def check_completion(self):
        plr = self.owner
        count = sum(1 for p in plr.owned_properties if p.group == self.group)
        return count == Property.color_group_sizes[self.group]


