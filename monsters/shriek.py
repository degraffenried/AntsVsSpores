import pygame
import math
from .base import Monster


class Shriek(Monster):
    """Territorial bat that roams freely and dive-bombs when agitated"""
    def __init__(self, x, y, patrol_range, speed, health, aggro_duration=180):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (60, 20, 80)
        self.spawn_y = y
        self.anim = 0
        self.wing_phase = 0
        self.is_agitated = False
        self.agitation_timer = 0
        self.agitation_duration = aggro_duration  # frames of rage (60 = 1 second)
        self.roam_angle = 0  # For circular roaming pattern
        self.target_x = x
        self.target_y = y
        self.screech_cooldown = 0

    def take_damage(self, damage):
        self.health -= damage
        # Getting hit makes it ANGRY
        self.is_agitated = True
        self.agitation_timer = self.agitation_duration
        return self.health <= 0

    def reset_aggro(self):
        """Reset agitation state"""
        self.is_agitated = False
        self.agitation_timer = 0

    def update(self, platforms, player):
        self.anim += 1
        self.wing_phase += 0.4

        # Check if player gets too close - triggers agitation
        dist_to_player = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist_to_player < 150:
            self.is_agitated = True
            self.agitation_timer = self.agitation_duration

        if self.is_agitated:
            self.agitation_timer -= 1
            if self.agitation_timer <= 0:
                self.is_agitated = False

            # Dive toward player aggressively
            dx = player.x - self.x
            dy = player.y - self.y
            dist = max(1, math.sqrt(dx * dx + dy * dy))
            chase_speed = self.speed * 2.5
            self.x += (dx / dist) * chase_speed
            self.y += (dy / dist) * chase_speed

            # Update direction for drawing
            self.direction = 1 if dx > 0 else -1

            # Screech effect (visual cue)
            if self.screech_cooldown <= 0:
                self.screech_cooldown = 60
            else:
                self.screech_cooldown -= 1
        else:
            # Peaceful roaming in a figure-8 pattern around spawn point
            self.roam_angle += 0.02
            roam_radius_x = self.patrol_range
            roam_radius_y = self.patrol_range * 0.5

            self.target_x = self.spawn_x + math.sin(self.roam_angle) * roam_radius_x
            self.target_y = self.spawn_y + math.sin(self.roam_angle * 2) * roam_radius_y

            # Smoothly move toward target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            self.x += dx * 0.05
            self.y += dy * 0.05

            # Update direction for drawing
            if abs(dx) > 0.5:
                self.direction = 1 if dx > 0 else -1

    def draw(self, screen):
        # Wing flapping speed increases when agitated
        flap_speed = 2.0 if self.is_agitated else 1.0
        wing_offset = math.sin(self.wing_phase * flap_speed) * 12

        # Body color pulses red when agitated
        if self.is_agitated:
            pulse = abs(math.sin(self.anim * 0.3))
            body_color = (60 + int(140 * pulse), 20, 80)
        else:
            body_color = self.color

        # Furry body (oval)
        pygame.draw.ellipse(screen, body_color,
                           (self.x + 8, self.y + 12, 24, 20))

        # Head
        pygame.draw.circle(screen, body_color,
                          (int(self.x + 20), int(self.y + 10)), 10)

        # Ears (pointed)
        ear_offset = 8 * self.direction
        pygame.draw.polygon(screen, body_color, [
            (self.x + 12, self.y + 5),
            (self.x + 8, self.y - 8),
            (self.x + 18, self.y + 3)
        ])
        pygame.draw.polygon(screen, body_color, [
            (self.x + 28, self.y + 5),
            (self.x + 32, self.y - 8),
            (self.x + 22, self.y + 3)
        ])

        # Wings - membrane style
        wing_color = (80, 40, 100) if not self.is_agitated else (150, 40, 60)

        # Left wing
        pygame.draw.polygon(screen, wing_color, [
            (self.x + 10, self.y + 15),
            (self.x - 15, self.y + 5 - wing_offset),
            (self.x - 20, self.y + 15 - wing_offset * 0.5),
            (self.x - 10, self.y + 25),
            (self.x + 5, self.y + 22)
        ])
        # Wing bones
        pygame.draw.line(screen, body_color,
                        (self.x + 10, self.y + 15),
                        (self.x - 15, self.y + 5 - wing_offset), 2)
        pygame.draw.line(screen, body_color,
                        (self.x + 10, self.y + 18),
                        (self.x - 18, self.y + 15 - wing_offset * 0.5), 2)

        # Right wing
        pygame.draw.polygon(screen, wing_color, [
            (self.x + 30, self.y + 15),
            (self.x + 55, self.y + 5 - wing_offset),
            (self.x + 60, self.y + 15 - wing_offset * 0.5),
            (self.x + 50, self.y + 25),
            (self.x + 35, self.y + 22)
        ])
        # Wing bones
        pygame.draw.line(screen, body_color,
                        (self.x + 30, self.y + 15),
                        (self.x + 55, self.y + 5 - wing_offset), 2)
        pygame.draw.line(screen, body_color,
                        (self.x + 30, self.y + 18),
                        (self.x + 58, self.y + 15 - wing_offset * 0.5), 2)

        # Eyes - glow red when angry
        eye_color = (255, 50, 50) if self.is_agitated else (200, 150, 50)
        pygame.draw.circle(screen, eye_color,
                          (int(self.x + 16), int(self.y + 8)), 3)
        pygame.draw.circle(screen, eye_color,
                          (int(self.x + 24), int(self.y + 8)), 3)

        # Fangs
        pygame.draw.line(screen, (255, 255, 255),
                        (self.x + 17, self.y + 16), (self.x + 17, self.y + 20), 2)
        pygame.draw.line(screen, (255, 255, 255),
                        (self.x + 23, self.y + 16), (self.x + 23, self.y + 20), 2)

        # Screech effect when agitated
        if self.is_agitated and self.screech_cooldown > 50:
            for i in range(3):
                radius = 15 + i * 8
                alpha = 150 - i * 40
                pygame.draw.circle(screen, (255, 100, 100),
                                  (int(self.x + 20), int(self.y + 12)),
                                  radius, 1)

        # Health bar
        bar_width = self.width * (self.health / 2)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 12, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 12, bar_width, 5))
