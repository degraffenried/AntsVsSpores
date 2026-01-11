import pygame
import math


class Bullet:
    def __init__(self, x, y, direction, speed=12, angle=0):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 6
        self.speed = speed
        self.direction = direction
        self.angle = angle  # Vertical angle for spread shot
        self.color = (255, 255, 0)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x += self.speed * self.direction
        self.y += self.speed * self.angle  # Apply vertical movement

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (255, 200, 0), (self.x + 2, self.y + 1, self.width - 4, self.height - 2))


class Missile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.width = 14
        self.height = 8
        self.speed = 8
        self.direction = direction
        self.vel_x = self.speed * direction
        self.vel_y = 0
        self.color = (255, 100, 50)
        self.turn_rate = 0.15  # How fast it can turn toward target

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, monsters=None):
        # Find nearest monster and home toward it
        if monsters:
            nearest = None
            nearest_dist = float('inf')
            for monster in monsters:
                if monster.health <= 0:
                    continue
                mx = monster.x + monster.width / 2
                my = monster.y + monster.height / 2
                dist = math.sqrt((mx - self.x) ** 2 + (my - self.y) ** 2)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = monster

            if nearest and nearest_dist < 400:  # Only home within range
                mx = nearest.x + nearest.width / 2
                my = nearest.y + nearest.height / 2
                # Calculate desired direction
                dx = mx - self.x
                dy = my - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    # Desired velocity
                    target_vx = (dx / dist) * self.speed
                    target_vy = (dy / dist) * self.speed
                    # Gradually turn toward target
                    self.vel_x += (target_vx - self.vel_x) * self.turn_rate
                    self.vel_y += (target_vy - self.vel_y) * self.turn_rate

        # Move
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, screen):
        # Missile body
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        # Flame trail
        flame_x = self.x - 6 if self.vel_x > 0 else self.x + self.width
        pygame.draw.circle(screen, (255, 200, 50), (int(flame_x), int(self.y + self.height / 2)), 4)
        pygame.draw.circle(screen, (255, 255, 100), (int(flame_x), int(self.y + self.height / 2)), 2)
