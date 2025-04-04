import sys
from property_tycoon import PropertyTycoon
import pygame

class Main:
    """
    The main entry point for the Property Tycoon game.

    This class initializes the `PropertyTycoon` game and starts the game loop.

    Args:
        None

    Attributes:
        None
    """

    if __name__ == "__main__":
        """
        Main entry point for starting the Property Tycoon game.

        Initializes the `PropertyTycoon` game instance and runs the game loop.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Creates an instance of the `PropertyTycoon` class.
            - Calls the `run()` method of the `PropertyTycoon` class, starting the game.
        """
        property_tycoon = PropertyTycoon()
        property_tycoon.run()
