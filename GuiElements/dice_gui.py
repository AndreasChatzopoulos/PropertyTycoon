import pygame
import random
import time
import math

class DiceGUI:
    """
    Handles the dice rolling GUI, animation, sound effects, and double-roll tracking.
    Displays a clickable roll button, dice images, and a double-roll history panel.
    """

    def __init__(self, screen):
        """
        Initialize the DiceGUI.

        Parameters:
        - screen: Pygame surface where dice elements will be drawn.
        - event_logger: Optional function to log game events (e.g., updates to a sidebar).
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
        """Draw the dice button, dice faces, and the double roll history."""
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
        """Handle mouse click on the roll button."""
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     x, y = event.pos
        #     if self.dice_button.collidepoint(x, y) and not self.rolling:
        #         self.start_roll_animation()
        pass
        # no longer needed as dice rolling is handled programatically via end turn

    def start_roll_animation(self):
        """Begin the dice rolling animation sequence."""
        self.rolling = True
        self.animation_start_time = time.time()
        self.last_animation_time = self.animation_start_time
        self.dice_rotation_angle = 0
        self.bounce_offset = 0
        self.roll_sound.play()
        self.dice_result = (random.randint(1, 6), random.randint(1, 6))

    def update(self):
        """Update dice animation state and process final result."""
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
        """Return the final dice result once rolling is done."""
        return self.dice_result
