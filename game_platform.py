import pygame


class Platform:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = tuple(color)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Draw a highlight on top
        pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in self.color),
                        (self.rect.x, self.rect.y, self.rect.width, 3))
