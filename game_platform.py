import pygame
import math
import random


class Platform:
    def __init__(self, x, y, width, height, color, bouncy=False, unstable=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.color = tuple(color)
        self.bouncy = bouncy
        self.bounce_power = -18  # How high to bounce
        self.anim = 0  # Animation timer for bouncy platforms
        # Unstable platform properties
        self.unstable = unstable
        self.stand_timer = 0  # How long player has been standing
        self.crumble_time = 180  # 3 seconds at 60fps
        self.crumbled = False
        self.respawn_timer = 0
        self.respawn_time = 300  # 5 seconds to respawn
        self.shake_offset = 0

    def update(self, player_rect=None):
        """Update platform animation"""
        if self.bouncy:
            self.anim += 0.15

        # Handle unstable platform logic
        if self.unstable:
            if self.crumbled:
                # Respawn timer
                self.respawn_timer += 1
                if self.respawn_timer >= self.respawn_time:
                    self.crumbled = False
                    self.respawn_timer = 0
                    self.stand_timer = 0
                    self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            else:
                # Check if player is standing on this platform
                if player_rect:
                    player_bottom = player_rect.bottom
                    player_on_platform = (
                        player_rect.right > self.rect.left and
                        player_rect.left < self.rect.right and
                        player_bottom >= self.rect.top and
                        player_bottom <= self.rect.top + 10
                    )
                    if player_on_platform:
                        self.stand_timer += 1
                        # Shake more as it gets closer to crumbling
                        shake_intensity = (self.stand_timer / self.crumble_time) * 4
                        self.shake_offset = random.uniform(-shake_intensity, shake_intensity)

                        if self.stand_timer >= self.crumble_time:
                            self.crumbled = True
                            self.rect = pygame.Rect(0, 0, 0, 0)  # Make it non-solid
                    else:
                        # Slowly recover if player steps off
                        if self.stand_timer > 0:
                            self.stand_timer = max(0, self.stand_timer - 2)
                        self.shake_offset = 0

    def draw(self, screen):
        if self.unstable:
            # Don't draw if crumbled
            if self.crumbled:
                # Draw faint outline where platform will respawn
                respawn_progress = self.respawn_timer / self.respawn_time
                if respawn_progress > 0.7:  # Show outline when almost respawned
                    alpha = int((respawn_progress - 0.7) / 0.3 * 100)
                    draw_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    pygame.draw.rect(screen, (150, 100, 80), draw_rect, 2)
                return

            # Unstable platform - orange/brown cracked look
            draw_x = self.x + self.shake_offset
            draw_rect = pygame.Rect(draw_x, self.y, self.width, self.height)

            # Color fades to red as it's about to crumble
            danger_level = self.stand_timer / self.crumble_time
            base_color = (
                int(180 + danger_level * 75),  # More red
                int(120 - danger_level * 80),  # Less green
                int(60 - danger_level * 40)    # Less blue
            )
            pygame.draw.rect(screen, base_color, draw_rect)

            # Crack pattern
            crack_color = (100, 60, 40)
            # Draw some crack lines
            cx = self.x + self.width // 3
            pygame.draw.line(screen, crack_color,
                           (cx + self.shake_offset, self.y),
                           (cx + 10 + self.shake_offset, self.y + self.height), 2)
            cx2 = self.x + self.width * 2 // 3
            pygame.draw.line(screen, crack_color,
                           (cx2 + self.shake_offset, self.y + self.height),
                           (cx2 - 5 + self.shake_offset, self.y), 2)

            # Top highlight
            pygame.draw.rect(screen, (200, 150, 100),
                           (draw_x, self.y, self.width, 3))

        elif self.bouncy:
            # Bouncy platform with animated spring look
            bounce_offset = math.sin(self.anim) * 2

            # Main platform (pink/magenta color)
            pygame.draw.rect(screen, (200, 80, 150), self.rect)

            # Spring coil pattern
            coil_color = (255, 150, 200)
            num_coils = max(3, self.rect.width // 25)
            coil_spacing = self.rect.width / num_coils
            for i in range(num_coils):
                coil_x = self.rect.x + coil_spacing * (i + 0.5)
                coil_y = self.rect.y + self.rect.height // 2 + bounce_offset
                pygame.draw.circle(screen, coil_color, (int(coil_x), int(coil_y)), 6)
                pygame.draw.circle(screen, (255, 200, 230), (int(coil_x - 1), int(coil_y - 1)), 2)

            # Top highlight
            pygame.draw.rect(screen, (255, 150, 200),
                            (self.rect.x, self.rect.y, self.rect.width, 3))
        else:
            # Normal platform
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw a highlight on top
            pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in self.color),
                            (self.rect.x, self.rect.y, self.rect.width, 3))
