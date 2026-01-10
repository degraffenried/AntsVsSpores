import pygame
import math
from .base import Monster


class Taterbug(Monster):
    """Armored bug that curls into invulnerable ball when shot"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (80, 80, 90)
        self.is_rolled = False
        self.roll_timer = 0
        self.roll_duration = 120  # 2 seconds at 60fps

    def take_damage(self, damage):
        if self.is_rolled:
            return False  # Invulnerable when rolled
        # Take damage and roll up
        self.health -= damage
        if self.health > 0:
            self.is_rolled = True
            self.roll_timer = self.roll_duration
        return self.health <= 0

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0
        if on_ground and not self.has_ground_ahead(platforms):
            self.direction *= -1

        # Handle roll state
        if self.is_rolled:
            self.roll_timer -= 1
            if self.roll_timer <= 0:
                self.is_rolled = False
            # Roll faster in ball form
            self.x += self.speed * self.direction * 3
        else:
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
        if self.is_rolled:
            # Rolled ball form
            pygame.draw.circle(screen, self.color, (int(self.x + 20), int(self.y + 20)), 18)
            # Segment lines on ball
            for i in range(5):
                arc_x = self.x + 5 + i * 6
                pygame.draw.arc(screen, (60, 60, 70),
                               (arc_x, self.y + 5, 8, 30), 0, math.pi, 2)
        else:
            # Elongated segmented body
            pygame.draw.ellipse(screen, self.color,
                               (self.x, self.y + 10, self.width, 25))

            # Segment lines
            for i in range(7):
                seg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, (60, 60, 70),
                                (seg_x, self.y + 12), (seg_x, self.y + 33), 1)

            # Antennae
            pygame.draw.line(screen, (70, 70, 80),
                            (self.x + 5, self.y + 18), (self.x - 5, self.y + 10), 2)
            pygame.draw.line(screen, (70, 70, 80),
                            (self.x + 5, self.y + 22), (self.x - 5, self.y + 28), 2)

            # Legs
            for i in range(7):
                leg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, (60, 60, 70),
                                (leg_x, self.y + 35), (leg_x - 2, self.y + 40), 1)
                pygame.draw.line(screen, (60, 60, 70),
                                (leg_x + 2, self.y + 35), (leg_x + 4, self.y + 40), 1)

        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))
