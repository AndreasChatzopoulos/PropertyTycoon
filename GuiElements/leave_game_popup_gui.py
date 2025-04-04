import pygame

class LeaveGamePopup:
    """
    Manages the "Leave Game" popup, allowing players to vote on whether another player can leave the game.

    This class handles the process of voting whether a player can leave the game. It presents the voting 
    options to the players in sequence and updates the game state based on the votes.

    Args:
        screen (pygame.Surface): The Pygame surface where the popup will be drawn.
        leaver (Player): The player who wants to leave the game.
        players (list[Player]): List of all players in the game, excluding the leaver.
        game (Game): The game instance that holds the game logic.

    Attributes:
        votes (dict): Dictionary holding the votes for each player.
        current_voter_index (int): Index tracking which player's vote is being processed.
        visible (bool): Flag indicating if the popup is visible.
        yes_button (pygame.Rect): The "Yes" vote button's rectangle.
        no_button (pygame.Rect): The "No" vote button's rectangle.
    """
    def __init__(self, screen, leaver, players, game):
        """
        Initializes the LeaveGame popup and sets up the necessary buttons, votes, and layout.

        Args:
            screen (pygame.Surface): The Pygame surface where the popup will be drawn.
            leaver (Player): The player who wants to leave the game.
            players (list[Player]): List of players in the game, excluding the leaver.
            game (Game): The game instance that holds the game logic.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Sets up the popup rectangle and button positions.
            - Initializes the voting system.
        """
        self.screen = screen
        self.game = game
        self.leaver = leaver
        self.players = [p for p in players if p != leaver]
        self.votes = {}  
        self.visible = True
        self.current_voter_index = 0

        self.font = pygame.font.Font(None, 30)
        self.popup_rect = pygame.Rect(screen.get_width() // 2 - 250, screen.get_height() // 2 - 150, 500, 300)

        self.yes_button = pygame.Rect(self.popup_rect.centerx - 120, self.popup_rect.bottom - 80, 100, 40)
        self.no_button = pygame.Rect(self.popup_rect.centerx + 20, self.popup_rect.bottom - 80, 100, 40)

    def draw(self):
        """
        Draws the LeaveGame popup and the voting buttons, updating the visual elements for the current state.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Renders the popup window with the vote buttons and messages.
            - Dynamically updates the button colors based on mouse hover.
        """
        if not self.visible:
            return

        pygame.draw.rect(self.screen, (30, 30, 30), self.popup_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.popup_rect, 3, border_radius=8)

        header = self.font.render(f"{self.leaver.name} wants to leave the game.", True, (255, 255, 255))
        voter = self.font.render(f"{self.current_voter().name}, do you approve?", True, (255, 255, 255))

        self.screen.blit(header, (self.popup_rect.centerx - header.get_width() // 2, self.popup_rect.y + 30))
        self.screen.blit(voter, (self.popup_rect.centerx - voter.get_width() // 2, self.popup_rect.y + 80))

        mouse_pos = pygame.mouse.get_pos()
        yes_hover = self.yes_button.collidepoint(mouse_pos)
        no_hover = self.no_button.collidepoint(mouse_pos)

        yes_color = (0, 255, 0) if yes_hover else (0, 200, 0)
        no_color = (255, 0, 0) if no_hover else (200, 0, 0)

        pygame.draw.rect(self.screen, yes_color, self.yes_button)
        pygame.draw.rect(self.screen, no_color, self.no_button)

        yes_text = self.font.render("Yes", True, (255, 255, 255))
        no_text = self.font.render("No", True, (255, 255, 255))
        self.screen.blit(yes_text, (self.yes_button.centerx - yes_text.get_width() // 2, self.yes_button.y + 8))
        self.screen.blit(no_text, (self.no_button.centerx - no_text.get_width() // 2, self.no_button.y + 8))


    def handle_event(self, event):
        """
        Handles user input events such as mouse clicks for the voting buttons.

        Args:
            event (pygame.event): The Pygame event to handle (e.g., mouse button clicks).

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Registers a vote for the current player based on their selection.
            - Calls `vote()` to update the voting process.
        """
        if not self.visible:
            return

        if self.current_voter().identity != 'Human':
            self.vote(True)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.yes_button.collidepoint(event.pos):
                self.vote(True)
            elif self.no_button.collidepoint(event.pos):
                self.vote(False)

    def vote(self, approved):
        """
        Records the vote of the current player and moves on to the next player, or ends the voting process.

        Args:
            approved (bool): True if the player voted "Yes", False if they voted "No".

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Updates the votes dictionary with the player's decision.
            - If a player votes "No", the leaver remains in the game and the process ends.
            - If all players approve, the leaver is removed from the game and the popup is closed.
        """
        voter = self.current_voter()
        self.votes[voter] = approved

        if not approved:
            self.visible = False
            self.game.log_event(f"{voter.name} voted NO. {self.leaver.name} stays in the game.")
            return

        self.current_voter_index += 1

        if self.current_voter_index >= len(self.players):
            self.visible = False
            self.game.log_event(f"All players approved. {self.leaver.name} has left the game.")
            self.game.remove_player(self.leaver)

    def current_voter(self):
        """
        Returns the current player who is casting their vote.

        Args:
            None

        Returns:
            Player: The player who is currently voting.

        Raises:
            None

        Side Effects:
            - Returns the player at the current voting index.
        """
        return self.players[self.current_voter_index]
