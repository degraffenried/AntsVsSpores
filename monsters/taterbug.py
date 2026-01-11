import pygame
import math
from .base import Monster


class Taterbug(Monster):
    """Armored bug that curls into invulnerable ball when shot"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (80, 80, 90)
        self.stripe_color = (40, 40, 50)  # Darker for more contrast
        self.is_rolled = False
        self.roll_timer = 0
        self.roll_duration = 120  # 2 seconds at 60fps
        self.roll_angle = 0  # Rotation angle for ball form

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
            roll_speed = self.speed * self.direction * 3
            self.x += roll_speed
            # Update rotation angle based on movement (radius ~18 pixels)
            self.roll_angle += roll_speed / 18
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
                    # Falling - land on top
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                elif self.vel_y < 0:
                    # Moving up - push down from platform bottom
                    self.y = platform.rect.bottom
                    self.vel_y = 0

    def draw(self, screen):
        if self.is_rolled:
            # Rolled ball form
            center_x = int(self.x + 20)
            center_y = int(self.y + 20)
            radius = 18
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius)

            # Rotating spoke lines
            num_spokes = 6
            for i in range(num_spokes):
                angle = self.roll_angle + (i * math.pi * 2 / num_spokes)
                # Inner point (near center)
                inner_x = center_x + math.cos(angle) * 4
                inner_y = center_y + math.sin(angle) * 4
                # Outer point (near edge)
                outer_x = center_x + math.cos(angle) * (radius - 2)
                outer_y = center_y + math.sin(angle) * (radius - 2)
                pygame.draw.line(screen, self.stripe_color,
                                (inner_x, inner_y), (outer_x, outer_y), 2)

            # Center dot
            pygame.draw.circle(screen, self.stripe_color, (center_x, center_y), 4)
        else:
            # Elongated segmented body
            pygame.draw.ellipse(screen, self.color,
                               (self.x, self.y + 10, self.width, 25))

            # Segment lines - more contrasted
            for i in range(7):
                seg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, self.stripe_color,
                                (seg_x, self.y + 12), (seg_x, self.y + 33), 2)

            # Antennae
            pygame.draw.line(screen, (70, 70, 80),
                            (self.x + 5, self.y + 18), (self.x - 5, self.y + 10), 2)
            pygame.draw.line(screen, (70, 70, 80),
                            (self.x + 5, self.y + 22), (self.x - 5, self.y + 28), 2)

            # Legs
            for i in range(7):
                leg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, self.stripe_color,
                                (leg_x, self.y + 35), (leg_x - 2, self.y + 40), 2)
                pygame.draw.line(screen, self.stripe_color,
                                (leg_x + 2, self.y + 35), (leg_x + 4, self.y + 40), 2)

        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))
