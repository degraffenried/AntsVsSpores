import pygame
from .base import Monster


class Walker(Monster):
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (200, 50, 50)

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0
        if on_ground and not self.has_ground_ahead(platforms):
            self.direction *= -1

        # Patrol movement
        self.x += self.speed * self.direction

        # Reverse direction at patrol bounds
        if self.x > self.spawn_x + self.patrol_range:
            self.direction = -1
        elif self.x < self.spawn_x - self.patrol_range:
            self.direction = 1

        # Check horizontal collisions
        monster_rect = self.get_rect()
        for platform in platforms:
            if monster_rect.colliderect(platform.rect):
                if self.direction > 0:
                    self.x = platform.rect.left - self.width
                else:
                    self.x = platform.rect.right
                self.direction *= -1

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
        # Body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Eyes
        eye_offset = 8 if self.direction > 0 else -2
        pygame.draw.circle(screen, (255, 255, 255),
                          (int(self.x + self.width // 2 + eye_offset), int(self.y + 12)), 8)
        pygame.draw.circle(screen, (0, 0, 0),
                          (int(self.x + self.width // 2 + eye_offset + 2 * self.direction), int(self.y + 12)), 4)
        # Angry eyebrows
        pygame.draw.line(screen, (0, 0, 0),
                        (self.x + self.width // 2 + eye_offset - 6, self.y + 5),
                        (self.x + self.width // 2 + eye_offset + 6, self.y + 8), 2)
        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))
