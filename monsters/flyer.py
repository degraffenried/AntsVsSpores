import pygame
import math
from .base import Monster


class Flyer(Monster):
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (150, 50, 200)
        self.float_offset = 0
        self.float_speed = 0.1

    def update(self, platforms, player):
        # Float up and down
        self.float_offset += self.float_speed
        float_y = math.sin(self.float_offset) * 20

        # Patrol movement
        self.x += self.speed * self.direction

        # Reverse direction at patrol bounds
        if self.x > self.spawn_x + self.patrol_range:
            self.direction = -1
        elif self.x < self.spawn_x - self.patrol_range:
            self.direction = 1

        # Store actual y for collision
        self.actual_y = self.y + float_y

    def get_rect(self):
        actual_y = getattr(self, 'actual_y', self.y)
        return pygame.Rect(self.x, actual_y, self.width, self.height)

    def draw(self, screen):
        actual_y = getattr(self, 'actual_y', self.y)
        # Body (bat-like)
        pygame.draw.ellipse(screen, self.color,
                           (self.x, actual_y + 10, self.width, self.height - 15))
        # Wings
        wing_offset = abs(math.sin(self.float_offset * 3)) * 10
        pygame.draw.polygon(screen, self.color, [
            (self.x + self.width // 2, actual_y + 20),
            (self.x - 15, actual_y + 10 + wing_offset),
            (self.x, actual_y + 25)
        ])
        pygame.draw.polygon(screen, self.color, [
            (self.x + self.width // 2, actual_y + 20),
            (self.x + self.width + 15, actual_y + 10 + wing_offset),
            (self.x + self.width, actual_y + 25)
        ])
        # Eyes
        pygame.draw.circle(screen, (255, 0, 0),
                          (int(self.x + 12), int(actual_y + 18)), 5)
        pygame.draw.circle(screen, (255, 0, 0),
                          (int(self.x + self.width - 12), int(actual_y + 18)), 5)
        # Health bar
        bar_width = self.width * self.health
        pygame.draw.rect(screen, (0, 0, 0), (self.x, actual_y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, actual_y - 8, bar_width, 5))
