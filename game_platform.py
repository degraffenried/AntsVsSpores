import pygame
import math


class Platform:
    def __init__(self, x, y, width, height, color, bouncy=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = tuple(color)
        self.bouncy = bouncy
        self.bounce_power = -18  # How high to bounce
        self.anim = 0  # Animation timer for bouncy platforms

    def update(self):
        """Update platform animation"""
        if self.bouncy:
            self.anim += 0.15

    def draw(self, screen):
        if self.bouncy:
            # Bouncy platform with animated spring look
            bounce_offset = math.sin(self.anim) * 2

            # Main platform (pink/magenta color)
            pygame.draw.rect(screen, (200, 80, 150), self.rect)

            # Spring coil pattern
            coil_color = (255, 150, 200)
            num_coils = max(3, self.rect.width // 25)
            coil_spacing = self.rect.width / num_coils
            for i in range(num_coils):
                coil_x = self.rect.x + coil_spacing * (i + 0.5)
                coil_y = self.rect.y + self.rect.height // 2 + bounce_offset
                pygame.draw.circle(screen, coil_color, (int(coil_x), int(coil_y)), 6)
                pygame.draw.circle(screen, (255, 200, 230), (int(coil_x - 1), int(coil_y - 1)), 2)

            # Top highlight
            pygame.draw.rect(screen, (255, 150, 200),
                            (self.rect.x, self.rect.y, self.rect.width, 3))
        else:
            # Normal platform
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw a highlight on top
            pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in self.color),
                            (self.rect.x, self.rect.y, self.rect.width, 3))
