import pygame
import random
import time
import math

class DiceGUI:
    """
    Handles the dice rolling GUI, animation, sound effects, and double-roll tracking.

    This class is responsible for displaying the dice roll button, animating the dice roll, 
    and tracking consecutive double rolls. It also displays a clickable button to roll the dice,
    updates the UI to show the result of the dice roll, and shows the history of recent double rolls.

    Args:
        screen (pygame.Surface): The Pygame surface where the dice elements will be drawn.

    Attributes:
        dice_button (pygame.Rect): The rectangular area for the dice roll button.
        dice_images (list[pygame.Surface]): List of dice images for faces 1-6.
        roll_sound (pygame.mixer.Sound): Sound effect to play when the dice is rolled.
        dice_result (tuple): A tuple storing the result of the dice roll (die1, die2).
        double_history (list): Stores recent double rolls only.
        double_streak (int): Tracks the current streak of consecutive double rolls.
        rolling (bool): A flag to indicate whether the dice rolling animation is in progress.
        animation_start_time (float): The start time of the dice roll animation.
        animation_duration (float): Duration of the dice roll animation.
        last_animation_time (float): Last time the animation was updated.
        dice_rotation_angle (float): The rotation angle of the dice during animation.
        bounce_offset (int): The bounce offset for the dice during animation.
    """

    def __init__(self, screen):
        """
        Initializes the DiceGUI, setting up the necessary surfaces and sound effects.

        Args:
            screen (pygame.Surface): The Pygame surface where dice elements will be drawn.

        Returns:
            None

        Raises:
            pygame.error: If there is an issue initializing the Pygame mixer or loading sound files.

        Side Effects:
            Initializes dice images, sounds, and sets up default dice result and animation settings.
        """
        self.screen = screen
        self.dice_button = pygame.Rect(screen.get_width() // 2 - 75, screen.get_height() // 2 - 30, 150, 60)
        self.dice_images = [pygame.image.load(f"assets/Dice{i}.png") for i in range(1, 7)]
        pygame.mixer.init()
        self.roll_sound = pygame.mixer.Sound("assets/dice_roll.wav")

        self.dice_result = (1, 1)
        self.double_history = []  # Stores recent double rolls only
        self.double_streak = 0

        self.rolling = False
        self.animation_start_time = 0
        self.animation_duration = 1.5
        self.last_animation_time = 0
        self.dice_rotation_angle = 0
        self.bounce_offset = 0

    def draw(self):
        """
        Draws the dice roll button, dice faces, and double roll history on the screen.

        Args:
            screen (pygame.Surface): The Pygame surface where the dice and button are rendered.
            prop_data (list): Property data used to display tooltips or dynamic information on the board.

        Returns:
            None

        Raises:
            None

        Side Effects:
            Renders the dice button, dice images, and the double roll history on the screen.
            The appearance of dice changes depending on whether the dice are rolling or not.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = self.dice_button.collidepoint(mouse_x, mouse_y)

        # Draw roll button
        # button_color = (180, 0, 0) if hovered else (255, 0, 0)
        # pygame.draw.rect(self.screen, (0, 0, 0), self.dice_button, border_radius=10)
        # pygame.draw.rect(self.screen, button_color, self.dice_button.inflate(-4, -4), border_radius=10)

        # font = pygame.font.Font(None, 32)
        # text_surface = font.render("Roll Dice", True, (255, 255, 255))
        # text_rect = text_surface.get_rect(center=self.dice_button.center)
        # self.screen.blit(text_surface, text_rect)

        # Draw dice
        die_1, die_2 = self.dice_result
        dice_1_img = pygame.transform.scale(self.dice_images[die_1 - 1], (50, 50))
        dice_2_img = pygame.transform.scale(self.dice_images[die_2 - 1], (50, 50))

        dice_x = self.screen.get_width() // 2
        dice_y = self.dice_button.bottom + 30 + self.bounce_offset

        if self.rolling:
            # Animate dice rotation and bouncing
            angle = self.dice_rotation_angle
            dice_1_img = pygame.transform.rotate(dice_1_img, angle)
            dice_2_img = pygame.transform.rotate(dice_2_img, -angle)
            offset_x, offset_y = random.randint(-5, 5), random.randint(-5, 5)
            self.screen.blit(dice_1_img, (dice_x - 50 + offset_x, dice_y + offset_y))
            self.screen.blit(dice_2_img, (dice_x + 10 + offset_x, dice_y + offset_y))
        else:
            self.screen.blit(dice_1_img, (dice_x - 50, dice_y))
            self.screen.blit(dice_2_img, (dice_x + 10, dice_y))

        # Draw double history
        history_rect = pygame.Rect(self.dice_button.right + 20, self.dice_button.top, 140, 100)
        pygame.draw.rect(self.screen, (255, 255, 255), history_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), history_rect, 2)

        label = pygame.font.Font(None, 22).render("Double History", True, (0, 0, 0))
        self.screen.blit(label, (history_rect.x + 10, history_rect.y + 5))

        font = pygame.font.Font(None, 20)
        for i, roll in enumerate(reversed(self.double_history[-4:])):
            txt = font.render(f"{roll[0]} + {roll[1]}", True, (0, 0, 0))
            self.screen.blit(txt, (history_rect.x + 10, history_rect.y + 30 + i * 20))

    def handle_event(self, event):
        """
        Handles user input events, specifically mouse clicks on the dice roll button.

        Args:
            event (pygame.event): The Pygame event to process.

        Returns:
            None

        Raises:
            None

        Side Effects:
            Starts the dice roll animation when the roll button is clicked by the player.
        """
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     x, y = event.pos
        #     if self.dice_button.collidepoint(x, y) and not self.rolling:
        #         self.start_roll_animation()
        pass
        # no longer needed as dice rolling is handled programatically via end turn

    def start_roll_animation(self):
        """
        Begins the dice rolling animation sequence, playing the roll sound and selecting a random dice result.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            Changes the `rolling` attribute to True, initiates the animation, and plays the roll sound.
            Updates `dice_result` with a random value for the dice.
        """
        self.rolling = True
        self.animation_start_time = time.time()
        self.last_animation_time = self.animation_start_time
        self.dice_rotation_angle = 0
        self.bounce_offset = 0
        self.roll_sound.play()
        self.dice_result = (random.randint(1, 6), random.randint(1, 6))

    def update(self):
        """
        Updates the dice animation state, handling rotation, bouncing, and finalizing the roll result.

        Args:
            None

        Returns:
            None

        Raises:
            None

        Side Effects:
            Modifies the `dice_rotation_angle` and `bounce_offset` attributes to animate the dice.
            If the animation is complete, updates the `rolling` attribute to False and stores the final dice result.
            If the dice result is a double, increments the `double_streak` and adds the result to the `double_history`.
            If it's not a double, resets the `double_streak` and clears the `double_history`.
        """
        if self.rolling:
            now = time.time()
            elapsed = now - self.animation_start_time

            if elapsed < self.animation_duration:
                if now - self.last_animation_time > 0.1:
                    # self.dice_result = (random.randint(1, 6), random.randint(1, 6))
                    self.last_animation_time = now

                self.dice_rotation_angle = math.sin(elapsed * 10) * 10
                self.bounce_offset = int(math.sin(elapsed * 15) * 5)
            else:
                # Final dice result
                # self.dice_result = (random.randint(1, 6), random.randint(1, 6))
                self.rolling = False
                self.dice_rotation_angle = 0
                self.bounce_offset = 0

                die1, die2 = self.dice_result

                if die1 == die2:
                    self.double_streak += 1
                    self.double_history.append(self.dice_result)
                else:
                    self.double_streak = 0
                    self.double_history.clear()  # Reset history on non-double roll

    def get_dice_result(self):
        """
        Returns the final result of the dice roll once the rolling animation is completed.

        Args:
            None

        Returns:
            tuple: A tuple representing the final result of the dice roll, e.g., (3, 4).

        Raises:
            None

        Side Effects:
            None
        """
        return self.dice_result
