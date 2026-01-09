import pygame
import math


class Portal:
    def __init__(self, x, y, width=80, height=60):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = False
        self.animation = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def activate(self):
        self.active = True

    def update(self):
        self.animation += 0.1

    def draw(self, screen):
        # Draw portal frame
        frame_color = (100, 100, 100) if not self.active else (100, 200, 255)
        pygame.draw.rect(screen, frame_color,
                        (self.x - 5, self.y - 5, self.width + 10, self.height + 10), 5)

        if self.active:
            # Swirling portal effect
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            for i in range(3):
                offset = self.animation + i * 2
                radius = 15 + i * 8 + math.sin(offset) * 5
                color_intensity = 150 + int(math.sin(offset) * 50)
                pygame.draw.circle(screen, (color_intensity, color_intensity, 255),
                                  (int(center_x), int(center_y)), int(radius), 3)
            # Center glow
            pygame.draw.circle(screen, (200, 220, 255),
                              (int(center_x), int(center_y)), 10)
        else:
            # Inactive portal - dark
            pygame.draw.rect(screen, (30, 30, 40),
                            (self.x, self.y, self.width, self.height))
            # "LOCKED" indicator
            font = pygame.font.Font(None, 20)
            text = font.render("LOCKED", True, (80, 80, 80))
            screen.blit(text, (self.x + 10, self.y + 25))
