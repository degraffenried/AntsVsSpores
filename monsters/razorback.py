import pygame
import math
import random
from .base import Monster


class Razorback(Monster):
    """Aggressive taterbug variant that charges at players with spikes"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.width = 40
        self.height = 45
        self.color = (120, 40, 40)  # Dark red
        self.stripe_color = (80, 25, 25)  # Darker red for contrast
        self.spike_color = (60, 20, 20)  # Even darker for spikes

        # Rolling/attack state
        self.is_rolling = False
        self.roll_angle = 0
        self.roll_speed = 8  # Fast roll speed

        # Aggro state
        self.aggro = False
        self.aggro_range = 300
        self.target_x = 0

        # Attack pattern
        self.attack_cooldown = 0
        self.attack_cooldown_min = 30   # 0.5 second minimum between attacks
        self.attack_cooldown_max = 90   # 1.5 seconds maximum
        self.backing_off = False
        self.backup_timer = 0
        self.backup_duration = 30
        self.hit_player = False

        # Defensive roll (when hit but player too far)
        self.defensive_roll = False
        self.defensive_roll_timer = 0
        self.defensive_roll_duration = 45  # 0.75 seconds invulnerable

        # Spike animation
        self.spike_length = 0
        self.max_spike_length = 8

    def take_damage(self, damage):
        if self.is_rolling:
            return False  # Invulnerable when rolling
        self.health -= damage
        # Getting hit makes it roll up defensively
        if self.health > 0:
            self.is_rolling = True
            self.defensive_roll = True
            self.defensive_roll_timer = self.defensive_roll_duration
            self.hit_player = False
            self.backing_off = False
        return self.health <= 0

    def start_attack(self):
        """Begin a rolling attack"""
        self.is_rolling = True
        self.defensive_roll = False
        self.hit_player = False
        self.backing_off = False

    def reset_aggro(self):
        """Reset aggro state"""
        self.aggro = False
        self.is_rolling = False
        self.backing_off = False
        self.attack_cooldown = 60

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Check distance to player for aggro
        player_center_x = player.x + player.width / 2
        my_center_x = self.x + self.width / 2
        dist_to_player = abs(player_center_x - my_center_x)

        # Aggro if player is close
        if dist_to_player < self.aggro_range:
            self.aggro = True
            self.target_x = player_center_x
        elif dist_to_player > self.aggro_range * 1.5:
            self.aggro = False
            self.is_rolling = False
            self.backing_off = False

        # Update spike animation
        if self.is_rolling and not self.backing_off:
            self.spike_length = min(self.spike_length + 1, self.max_spike_length)
        else:
            self.spike_length = max(self.spike_length - 1, 0)

        # Handle attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0

        if self.backing_off:
            # Back away from player after hitting
            self.backup_timer -= 1
            backup_dir = -1 if self.target_x > my_center_x else 1

            # Check for edge before backing up
            if on_ground and not self.has_ground_ahead(platforms):
                # Can't back up - just stop
                self.backup_timer = 0
            else:
                self.x += self.speed * backup_dir * 1.5

            if self.backup_timer <= 0:
                self.backing_off = False
                self.is_rolling = False
                # Set random cooldown before next attack
                self.attack_cooldown = random.randint(self.attack_cooldown_min, self.attack_cooldown_max)

        elif self.is_rolling and self.defensive_roll:
            # Defensive roll - stay in place and count down timer
            self.defensive_roll_timer -= 1
            # Slowly spin in place
            self.roll_angle += 0.1
            if self.defensive_roll_timer <= 0:
                # Unroll after defensive period
                self.is_rolling = False
                self.defensive_roll = False
                # Short cooldown after defensive roll - ready to attack quickly
                self.attack_cooldown = 20

        elif self.is_rolling and self.aggro:
            # Rolling attack toward player
            roll_dir = 1 if self.target_x > my_center_x else -1
            self.direction = roll_dir

            # Check for edge
            if on_ground and not self.has_ground_ahead(platforms):
                # Stop at edge
                self.is_rolling = False
                self.attack_cooldown = random.randint(self.attack_cooldown_min, self.attack_cooldown_max)
            else:
                self.x += self.roll_speed * roll_dir
                self.roll_angle += self.roll_speed * roll_dir / 18

            # Check if we've reached/passed the player
            new_dist = abs(self.target_x - (self.x + self.width / 2))
            if new_dist < 30 or (roll_dir == 1 and self.x + self.width / 2 > self.target_x + 20) or \
               (roll_dir == -1 and self.x + self.width / 2 < self.target_x - 20):
                # Start backing off
                self.hit_player = True
                self.backing_off = True
                self.backup_timer = self.backup_duration

        elif self.aggro and self.attack_cooldown <= 0:
            # Start a new attack
            self.start_attack()
            self.target_x = player_center_x

        else:
            # Normal patrol when not aggroed
            if on_ground and not self.has_ground_ahead(platforms):
                self.direction *= -1

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
                elif self.vel_y < 0:
                    self.y = platform.rect.bottom
                    self.vel_y = 0

    def draw(self, screen):
        if self.is_rolling:
            # Rolled ball form with spikes
            center_x = int(self.x + 20)
            center_y = int(self.y + 20)
            radius = 18

            # Main ball
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius)

            # Rotating spoke lines and spikes
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

                # Draw spikes extending from edge
                if self.spike_length > 0:
                    spike_base_x = center_x + math.cos(angle) * radius
                    spike_base_y = center_y + math.sin(angle) * radius
                    spike_tip_x = center_x + math.cos(angle) * (radius + self.spike_length)
                    spike_tip_y = center_y + math.sin(angle) * (radius + self.spike_length)

                    # Draw spike as triangle
                    perp_angle = angle + math.pi / 2
                    spike_width = 3
                    left_x = spike_base_x + math.cos(perp_angle) * spike_width
                    left_y = spike_base_y + math.sin(perp_angle) * spike_width
                    right_x = spike_base_x - math.cos(perp_angle) * spike_width
                    right_y = spike_base_y - math.sin(perp_angle) * spike_width

                    pygame.draw.polygon(screen, self.spike_color, [
                        (spike_tip_x, spike_tip_y),
                        (left_x, left_y),
                        (right_x, right_y)
                    ])

            # Center dot
            pygame.draw.circle(screen, self.stripe_color, (center_x, center_y), 4)

            # Angry eyes on ball (if not backing off)
            if not self.backing_off:
                eye_angle = math.atan2(self.target_x - center_x, 1) if self.aggro else 0
                eye_offset_x = int(math.cos(eye_angle) * 5)
                pygame.draw.circle(screen, (255, 50, 50), (center_x - 5 + eye_offset_x, center_y - 3), 3)
                pygame.draw.circle(screen, (255, 50, 50), (center_x + 5 + eye_offset_x, center_y - 3), 3)
                pygame.draw.circle(screen, (20, 0, 0), (center_x - 5 + eye_offset_x, center_y - 3), 1)
                pygame.draw.circle(screen, (20, 0, 0), (center_x + 5 + eye_offset_x, center_y - 3), 1)
        else:
            # Elongated segmented body (similar to taterbug but red)
            pygame.draw.ellipse(screen, self.color,
                               (self.x, self.y + 10, self.width, 25))

            # Segment lines with small spike bumps
            for i in range(7):
                seg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, self.stripe_color,
                                (seg_x, self.y + 12), (seg_x, self.y + 33), 2)
                # Small spike bumps on top
                pygame.draw.polygon(screen, self.spike_color, [
                    (seg_x, self.y + 10),
                    (seg_x - 2, self.y + 14),
                    (seg_x + 2, self.y + 14)
                ])

            # Antennae
            pygame.draw.line(screen, (100, 30, 30),
                            (self.x + 5, self.y + 18), (self.x - 5, self.y + 10), 2)
            pygame.draw.line(screen, (100, 30, 30),
                            (self.x + 5, self.y + 22), (self.x - 5, self.y + 28), 2)

            # Legs
            for i in range(7):
                leg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, self.stripe_color,
                                (leg_x, self.y + 35), (leg_x - 2, self.y + 40), 2)
                pygame.draw.line(screen, self.stripe_color,
                                (leg_x + 2, self.y + 35), (leg_x + 4, self.y + 40), 2)

            # Angry eyes
            eye_color = (255, 100, 100) if self.aggro else (200, 80, 80)
            pygame.draw.circle(screen, eye_color, (int(self.x + 8), int(self.y + 18)), 3)
            pygame.draw.circle(screen, eye_color, (int(self.x + 8), int(self.y + 24)), 3)
            pygame.draw.circle(screen, (40, 0, 0), (int(self.x + 9), int(self.y + 18)), 1)
            pygame.draw.circle(screen, (40, 0, 0), (int(self.x + 9), int(self.y + 24)), 1)

        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (255, 50, 50), (self.x, self.y - 8, bar_width, 5))
