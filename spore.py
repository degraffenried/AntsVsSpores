import pygame
import math


class Spore:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.float_offset = 0
        self.collected = False
        self.color = (100, 255, 150)
        self.glow_color = (150, 255, 200)

    def get_rect(self):
        actual_y = self.y + math.sin(self.float_offset) * 8
        return pygame.Rect(self.x - self.radius, actual_y - self.radius,
                          self.radius * 2, self.radius * 2)

    def update(self):
        self.float_offset += 0.05

    def draw(self, screen):
        if self.collected:
            return
        actual_y = self.y + math.sin(self.float_offset) * 8
        # Glow effect
        glow_radius = self.radius + 5 + math.sin(self.float_offset * 2) * 3
        pygame.draw.circle(screen, self.glow_color,
                          (int(self.x), int(actual_y)), int(glow_radius))
        # Main spore
        pygame.draw.circle(screen, self.color,
                          (int(self.x), int(actual_y)), self.radius)
        # Inner highlight
        pygame.draw.circle(screen, (200, 255, 230),
                          (int(self.x - 4), int(actual_y - 4)), 5)
