import pygame
import random
import time
import math

class DiceGUI:
    """
    This class handles everything related to displaying and rolling a pair of dice
    in a game. It includes animations, sound effects, and bounce/rotation effects 
    to make the dice roll visually appealing.
    """

    def __init__(self, screen):
        """
        Initializes the dice rolling system, including UI button, sound effects,
        dice images, and animation state.

        Parameters:
        screen (pygame.Surface): The main game screen to draw on.
        """
        self.screen = screen

        # Create a button centered on screen for rolling the dice
        self.dice_button = pygame.Rect(
            screen.get_width() // 2 - 75,  # X-position (centered)
            screen.get_height() // 2 - 30,  # Y-position (vertical center)
            150, 60  # Width, Height
        )

        # Load dice images (from 1 to 6)
        self.dice_images = [pygame.image.load(f"assets/Dice{i}.png") for i in range(1, 7)]

        # Load dice roll sound effect
        pygame.mixer.init()
        self.roll_sound = pygame.mixer.Sound("assets/dice_roll.wav")

        self.dice_result = (1, 1)  # Default dice values

        # Animation state variables
        self.rolling = False  # Whether animation is in progress
        self.animation_start_time = 0
        self.animation_duration = 1.5  # Total animation time in seconds
        self.last_animation_time = 0  # For timing between shake frames
        self.dice_rotation_angle = 0  # Rotational animation for dice
        self.bounce_offset = 0  # Vertical bounce animation

    def draw(self):
        """
        Draw the dice roll button and show the dice.
        If the dice are currently rolling, animate them with bounce and rotation.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = self.dice_button.collidepoint(mouse_x, mouse_y)

        # Change color if the mouse hovers over the button
        button_color = (180, 0, 0) if hovered else (255, 0, 0)
        border_color = (0, 0, 0)
        text_color = (255, 255, 255)

        # Draw the button (border + inner)
        pygame.draw.rect(self.screen, border_color, self.dice_button, border_radius=10)
        pygame.draw.rect(self.screen, button_color, self.dice_button.inflate(-4, -4), border_radius=10)

        # Draw the button text
        font = pygame.font.Font(None, 32)
        text_surface = font.render("Roll Dice", True, text_color)
        text_rect = text_surface.get_rect(center=self.dice_button.center)
        self.screen.blit(text_surface, text_rect)

        # Get current dice values
        die_1, die_2 = self.dice_result

        # Resize the dice images for display
        dice_1_image = pygame.transform.scale(self.dice_images[die_1 - 1], (50, 50))
        dice_2_image = pygame.transform.scale(self.dice_images[die_2 - 1], (50, 50))

        # Position the dice below the button
        dice_x = self.screen.get_width() // 2
        dice_y = self.dice_button.bottom + 30 + self.bounce_offset

        if self.rolling:
            # Animate: rotate dice and shake positions slightly
            angle = self.dice_rotation_angle
            dice_1_image = pygame.transform.rotate(dice_1_image, angle)
            dice_2_image = pygame.transform.rotate(dice_2_image, -angle)

            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)

            self.screen.blit(dice_1_image, (dice_x - 50 + offset_x, dice_y + offset_y))
            self.screen.blit(dice_2_image, (dice_x + 10 + offset_x, dice_y + offset_y))
        else:
            # Static dice display
            self.screen.blit(dice_1_image, (dice_x - 50, dice_y))
            self.screen.blit(dice_2_image, (dice_x + 10, dice_y))

    def handle_event(self, event):
        """
        Handles mouse clicks to start the dice roll when the button is clicked.

        Parameters:
        event (pygame.Event): The current Pygame event (e.g. mouse click).
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Start rolling if button is clicked and dice aren't already rolling
            if self.dice_button.collidepoint(x, y) and not self.rolling:
                self.start_roll_animation()

    def start_roll_animation(self):
        """
        Starts the dice rolling animation by resetting timers, 
        picking a random result, and playing sound.
        """
        self.rolling = True
        self.animation_start_time = time.time()
        self.last_animation_time = self.animation_start_time
        self.dice_rotation_angle = 0
        self.bounce_offset = 0
        self.roll_sound.play()

        # Set initial dice result (final result will be randomized during animation)
        self.dice_result = (random.randint(1, 6), random.randint(1, 6))

    def update(self):
        """
        Updates the dice animation frame if rolling is active.
        Controls rotation, bounce, and result randomization during animation.
        """
        if self.rolling:
            current_time = time.time()
            elapsed_time = current_time - self.animation_start_time

            if elapsed_time < self.animation_duration:
                # Randomize dice face every 0.1s during animation
                if current_time - self.last_animation_time > 0.1:
                    self.dice_result = (random.randint(1, 6), random.randint(1, 6))
                    self.last_animation_time = current_time

                # Update rotation and bounce for smooth animation
                self.dice_rotation_angle = math.sin(elapsed_time * 10) * 10
                self.bounce_offset = int(math.sin(elapsed_time * 15) * 5)

            else:
                # Animation finished – lock in final result and reset animation state
                self.dice_result = (random.randint(1, 6), random.randint(1, 6))
                self.rolling = False
                self.dice_rotation_angle = 0
                self.bounce_offset = 0

    def get_dice_result(self):
        """
        Returns the last rolled dice result.

        Returns:
        tuple: (die1, die2) values from 1 to 6.
               Returns (0, 0) if still rolling.
        """
        return self.dice_result if not self.rolling else (0, 0)
