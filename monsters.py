import pygame
import math


class Monster:
    def __init__(self, x, y, patrol_range, speed, health):
        self.spawn_x = x
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.patrol_range = patrol_range
        self.speed = speed
        self.health = health
        self.direction = 1
        self.vel_y = 0
        self.gravity = 0.8

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def update(self, platforms, player):
        pass

    def draw(self, screen):
        pass


class Walker(Monster):
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (200, 50, 50)

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

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


def create_monster(data):
    monster_type = data.get('type', 'walker')
    if monster_type == 'walker':
        return Walker(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'flyer':
        return Flyer(data['x'], data['y'], data['patrol_range'],
                    data['speed'], data['health'])
    return None
