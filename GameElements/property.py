
class Property:
    """
    Represents a property tile on the game board.

    This class models the behavior and attributes of a property, including ownership, rent calculations,
    group membership (e.g., colors or utilities), house management, and mortgage status.

    Attributes:
        position (int): The board position of the property.
        name (str): The name of the property.
        price (int): The cost to purchase the property.
        rent (list or int): Rent tiers for different house levels or special rent logic (e.g., stations/utilities).
        house_cost (int): The cost to build one house on the property.
        group (str): The color or category group the property belongs to.
        completed (bool): Whether the player owns the full set of this color group.
        houses (int): Number of houses currently on the property (0–4) or 5 for a hotel.
        owner (Player or None): The current owner of the property.
        mortgaged (bool): Whether the property is mortgaged.
        already_auctioned (bool): Whether the property has been auctioned in the current turn.

    Class Attributes:
        color_group_sizes (dict): A static dictionary mapping property groups to the number of tiles required
                                  for a complete set (used for completion checks).

    Example:
        A station might have increasing rent depending on how many stations a player owns.
        A utility calculates rent based on dice rolls.

    Methods:
        calculate_rent(dice_roll=None): Calculates rent based on group and property state.
        property_details(): Returns a human-readable summary of the property.
        transfer_property(new_owner): Transfers ownership and checks for group completion.
        check_completion(): Checks if the owner owns all properties in the group.
    """
    color_group_sizes = {  # Store it inside the class
        "Brown": 2, "Blue": 3,"Station": 4, "Pink": 3, "Utilities": 2, "Orange": 3,
        "Red": 3, "Yellow": 3, "Green": 3, "Deep blue": 2
    }

    def __init__(self, position, name, price, rent, house_cost, group):
        """
        Initializes a new Property instance.

        Args:
            position (int): The tile index of the property on the board.
            name (str): The name of the property (e.g., "Old Kent Road").
            price (int): The purchase cost of the property.
            rent (list or int): Rent structure for the property (list for buildable properties, int or list for special ones).
            house_cost (int): The cost to build a single house on the property.
            group (str): The color or category group the property belongs to (e.g., "Red", "Utilities", "Station").

        Attributes Set:
            completed (bool): Whether the owner owns the full group (initially False).
            houses (int): Number of houses built on the property (0 by default).
            owner (Player or None): The player who owns the property (None if unowned).
            mortgaged (bool): Indicates if the property is mortgaged.
            already_auctioned (bool): Tracks if the property was auctioned during the current turn.
        """
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
        """
        Calculates the rent a player must pay when landing on this property.

        Rent calculation depends on the property's group:
        - For 'Utilities': Based on a dice roll and number of utilities owned.
        - For 'Station': Based on the number of stations owned.
        - For standard color groups: Rent increases with number of houses and doubles if the group is fully owned.

        Args:
            dice_roll (int, optional): The total of the dice rolled. Required for utilities to compute rent.

        Returns:
            int: The amount of rent due. Returns 0 if conditions are invalid (e.g., no owner, dice_roll missing for utilities).
        """
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
        """
        Returns a string summarizing the property's current status.

        Includes the property name, owner's name, number of houses, and current rent.

        Returns:
            str: A formatted string with key property details.
        """
        return f"{self.name} | Owner: {self.owner.name} | Houses: {self.houses} | Rent: {self.calculate_rent()}"

    def transfer_property(self, new_owner):
        """
        Transfers ownership of this property to a new player.

        The method updates the current and new owner's property lists accordingly,
        and checks whether the new owner now completes a color group set.

        Args:
            new_owner (Player): The player who is acquiring ownership of the property.

        Side Effects:
            - Removes property from the previous owner's owned properties list.
            - Adds property to the new owner's owned properties list.
            - Updates the property's owner reference.
            - Sets the 'completed' flag for all properties in the group if the full set is acquired.
            - Prints transaction status messages.
        """
          # Transfer ownership of the property to another player
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

            for p in properties_in_group:
                p.completed = True
            print(f" {new_owner.name} now owns the full {self.group} set!")

        print(f"{self.name} is now owned by {new_owner.name}.")

    def check_completion(self):
        """
        Checks if the property's owner owns all properties in the same color group.

        Returns:
            bool: True if the owner has a complete set of this property's color group, False otherwise.

        Note:
            This method does not modify state—it only performs the check. 
            The 'completed' flag should be set separately where needed.
        """
        plr = self.owner
        count = sum(1 for p in plr.owned_properties if p.group == self.group)
        return count == Property.color_group_sizes[self.group]


