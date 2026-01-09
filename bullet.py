import pygame


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
