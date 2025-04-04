import pygame

class JailPopup:
    """
    Manages the Jail popup in the game, allowing players to interact with options while in jail.

    This class is responsible for rendering the Jail popup window, displaying the available options 
    for a player who is in jail. The player can choose to roll for doubles, pay £50 to get out of jail, 
    use a "Get Out of Jail Free" card, or wait for their turn to skip.

    Args:
        screen (pygame.Surface): The Pygame surface where the popup will be drawn.
        player (Player): The player who is in jail.
        game (Game): The game instance that holds the game logic.

    Attributes:
        buttons (dict): Dictionary holding the positions and size of the buttons in the popup window.
        font (pygame.font.Font): The font used to render text in the popup window.
        hovered_button (str): Keeps track of which button is currently hovered over.
        button_width (int): The width of the buttons in the popup.
        button_height (int): The height of the buttons in the popup.
        visible (bool): Boolean flag to show or hide the popup.
    """   
    def __init__(self, screen, player, game):
        """
        Initializes the Jail popup with necessary parameters for rendering and interacting with the player.

        Args:
            screen (pygame.Surface): The Pygame surface where the popup will be drawn.
            player (Player): The player who is in jail and needs to interact with the popup.
            game (Game): The game instance containing the logic.

        Returns:
            None

        Raises:
            None

        Side Effects:
            Initializes the button positions, the font, and the visibility flag for the popup.
        """
        self.screen = screen
        self.player = player
        self.game = game
        self.visible = True
         

        self.font = pygame.font.SysFont(None, 28)
        self.hovered_button = None

        self.button_width = 250
        self.button_height = 40
        self.buttons = {
            "roll": pygame.Rect(475, 250, self.button_width, self.button_height),
            "pay": pygame.Rect(475, 300, self.button_width, self.button_height),
            "card": pygame.Rect(475, 350, self.button_width, self.button_height),
            "wait": pygame.Rect(475, 400, self.button_width, self.button_height),
        }

    def draw(self):
        """
        Draws the Jail popup on the screen with the available choices for the player in jail.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            Renders the popup window, including the title, available actions, and the buttons.
            The visual appearance of the buttons and the title is dynamically updated.
        """
        if not self.visible:
            return

        pygame.draw.rect(self.screen, (30, 30, 30), (400, 200, 400, 300))
        pygame.draw.rect(self.screen, (255, 255, 255), (400, 200, 400, 300), 3)

        title = self.font.render(f"{self.player.name} is in Jail!", True, (255, 255, 255))
        self.screen.blit(title, (460, 210))

        options = [
            ("Roll for Doubles", "roll"),
            ("Pay £50 to Get Out", "pay"),
            ("Use Jail Free Card", "card"),
            ("Wait Turn (Skip)", "wait"),
        ]

        for label, key in options:
            btn_rect = self.buttons[key]
            
            if self.hovered_button == key:
                color = (150, 150, 150)  
            else:
                color = (100, 100, 100)  

            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 2)

            text = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

            
    def update_hover(self, mouse_pos):
        """
        Updates the hovered button state based on the current mouse position.

        Args:
            mouse_pos (tuple): The current (x, y) position of the mouse cursor.

        Returns:
            None

        Raises:
            None

        Side Effects:
            Updates the `hovered_button` attribute, which highlights the button the user is hovering over.
        """
        self.hovered_button = None
        for key, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                self.hovered_button = key
                break

    def handle_event(self, event):
        """
        Handles user input events, such as mouse clicks on the popup buttons.

        Args:
            event (pygame.event): The Pygame event to process (e.g., mouse movement or button click).

        Returns:
            None

        Raises:
            None

        Side Effects:
            If the player clicks on a button, it calls `handle_choice()` to process the selected option.
            Closes the popup if a choice is made.
        """
        if not self.visible:
            return

        if event.type == pygame.MOUSEMOTION:
            self.update_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for key, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.handle_choice(key)
                    self.visible = False  
                    return


    def handle_choice(self, choice):
        """
        Handles the player's choice based on the selected option in the Jail popup.

        Args:
            choice (str): The option chosen by the player. Possible values are "roll", "pay", "card", or "wait".

        Returns:
            None

        Raises:
            None

        Side Effects:
            - If the player chooses "roll", it flags the player to roll the dice for doubles.
            - If the player chooses "pay", it deducts £50 from the player's balance to get out of jail.
            - If the player chooses "card", it uses a "Get Out of Jail Free" card if available.
            - If the player chooses "wait", it increments the jail turn counter and either releases the player or skips their turn.
            - Each option triggers a game log event and updates the player's state (in jail, balance, etc.).
        """
        player = self.player
        game = self.game

        if choice == "roll":
            #  Flag player to roll animated dice in main loop
            player.wants_to_roll_in_jail = True
            self.visible = False

        elif choice == "pay":
            if player.balance >= 50:
                player.balance -= 50
                game.fines += 50
                player.jail_turns = 0
                player.in_jail = False
                player.skip_turn = True  
                game.log_event(f"{player.name} paid £50 to get out of jail. They will resume next turn.")
                self.visible = False

            else:
                game.log_event(f"{player.name} doesn't have enough money to pay.")

        elif choice == "card":
            if player.get_out_of_jail_cards > 0:
                player.get_out_of_jail_cards -= 1
                player.jail_turns = 0
                player.in_jail = False
                player.position = 11  
                if hasattr(game.cards, "return_jail_card_to_bottom"):
                    game.cards.return_jail_card_to_bottom()
                game.log_event(f" {player.name} used a Get Out of Jail Free card.")
                self.visible = False
            else:
                game.log_event(f" {player.name} has no Get Out of Jail Free cards.")

        elif choice == "wait":
            player.jail_turns += 1
            if player.jail_turns >= 3:
                player.jail_turns = 0
                player.in_jail = False
                game.log_event(f"{player.name} has served their sentence and is now Just Visiting.")
            else:
                player.turns_skipped = 2  
            self.visible = False

