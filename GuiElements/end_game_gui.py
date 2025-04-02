import pygame
import sys

class EndGamePopup:
    def __init__(self, screen, winner_name):
        self.screen = screen
        self.winner_name = winner_name
        self.visible = True

        self.width, self.height = self.screen.get_size()
        self.popup_width = 400
        self.popup_height = 220
        self.popup_rect = pygame.Rect(
            self.width // 2 - self.popup_width // 2,
            self.height // 2 - self.popup_height // 2,
            self.popup_width,
            self.popup_height
        )

        self.font_title = pygame.font.Font(None, 48)
        self.font_body = pygame.font.Font(None, 32)
        self.font_button = pygame.font.Font(None, 30)

        self.quit_button = pygame.Rect(self.popup_rect.centerx - 60, self.popup_rect.y + 150, 120, 40)

    def draw(self):
        if not self.visible:
            return

        pygame.draw.rect(self.screen, (40, 40, 40), self.popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.popup_rect, 3, border_radius=10)

        title_surf = self.font_title.render("🎉 Game Over!", True, (255, 255, 255))
        self.screen.blit(title_surf, (self.popup_rect.centerx - title_surf.get_width() // 2, self.popup_rect.y + 20))

        winner_msg = f"{self.winner_name} Wins!"
        winner_surf = self.font_body.render(winner_msg, True, (255, 215, 0))
        self.screen.blit(winner_surf, (self.popup_rect.centerx - winner_surf.get_width() // 2, self.popup_rect.y + 80))

        pygame.draw.rect(self.screen, (200, 0, 0), self.quit_button, border_radius=6)
        quit_surf = self.font_button.render("Quit", True, (255, 255, 255))
        self.screen.blit(quit_surf, (self.quit_button.centerx - quit_surf.get_width() // 2, self.quit_button.y + 8))

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()


        

        
        