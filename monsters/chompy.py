import pygame
import math
from .base import Monster


class Chompy(Monster):
    """Charges at player when in line of sight"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (200, 50, 50)
        self.is_charging = False
        self.anim = 0
        self.charge_speed = 8

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        self.anim += 1

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0
        ground_ahead = self.has_ground_ahead(platforms)

        # Check if player is in line of sight (same Y level, within range)
        y_diff = abs(player.y - self.y)
        x_diff = abs(player.x - self.x)

        if y_diff < 50 and x_diff < 300:
            self.is_charging = True
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1
            # Only charge if there's ground ahead
            if not on_ground or ground_ahead:
                self.x += self.charge_speed * self.direction
        else:
            self.is_charging = False
            # Check for edge during patrol
            if on_ground and not ground_ahead:
                self.direction *= -1
            # Normal patrol
            self.x += self.speed * self.direction
            if self.x > self.spawn_x + self.patrol_range:
                self.direction = -1
            elif self.x < self.spawn_x - self.patrol_range:
                self.direction = 1

        # Move vertically
        self.y += self.vel_y

        # Check vertical collisions
        monster_rect = self.get_rect()
        for platform in platforms:
            if monster_rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0

    def draw(self, screen):
        # Round body
        pygame.draw.circle(screen, self.color,
                          (int(self.x + 20), int(self.y + 25)), 18)

        # Mouth animation
        mouth_open = abs(math.sin(self.anim * 0.3)) * 10 if self.is_charging else 5

        # Teeth
        for i in range(4):
            tooth_x = self.x + 8 + i * 6
            # Upper teeth
            pygame.draw.polygon(screen, (255, 255, 255), [
                (tooth_x, self.y + 22),
                (tooth_x + 3, self.y + 28),
                (tooth_x + 6, self.y + 22)
            ])
            # Lower teeth
            pygame.draw.polygon(screen, (255, 255, 255), [
                (tooth_x, self.y + 28 + mouth_open),
                (tooth_x + 3, self.y + 22 + mouth_open),
                (tooth_x + 6, self.y + 28 + mouth_open)
            ])

        # Dark mouth interior
        pygame.draw.rect(screen, (50, 0, 0),
                        (self.x + 8, self.y + 24, 24, mouth_open))

        # Angry eyes
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x + 12), int(self.y + 12)), 5)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x + 28), int(self.y + 12)), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 13), int(self.y + 13)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 29), int(self.y + 13)), 3)

        # Angry eyebrows
        if self.is_charging:
            pygame.draw.line(screen, (0, 0, 0), (self.x + 8, self.y + 6), (self.x + 16, self.y + 10), 2)
            pygame.draw.line(screen, (0, 0, 0), (self.x + 32, self.y + 6), (self.x + 24, self.y + 10), 2)

        # Health bar
        bar_width = self.width * (self.health / 4)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))
