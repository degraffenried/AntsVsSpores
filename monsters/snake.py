import pygame
import math
import random
from .base import Monster


class Snake(Monster):
    """Slithering snake with multiple body segments using position history.
    Can aggro, lunge at player, wrap around them and bite!"""
    def __init__(self, x, y, patrol_range, speed, health, aggro_duration=180):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (80, 140, 50)
        self.belly_color = (120, 180, 80)
        self.pattern_color = (50, 100, 30)
        self.aggro_color = (120, 80, 40)  # Brownish when angry

        # Snake configuration
        self.num_segments = 12
        self.segment_spacing = 5  # pixels between segment samples in history
        self.head_size = 10
        self.body_width = 7  # max body width

        # Position history - stores past head positions
        # We need enough history to place all segments
        self.history_length = self.num_segments * self.segment_spacing
        self.position_history = [(x + 20, y + 30) for _ in range(self.history_length)]

        self.anim = 0
        self.tongue_out = False
        self.tongue_flick = 0
        self.slither_phase = 0

        # Aggro state
        self.aggro_duration = aggro_duration
        self.is_aggroed = False
        self.aggro_timer = 0
        self.detection_range = 120  # How close player needs to be to trigger aggro

        # Lunge state
        self.is_lunging = False
        self.lunge_vel_x = 0
        self.lunge_vel_y = 0

        # Wrap state
        self.is_wrapped = False
        self.wrap_target = None  # Reference to player when wrapped
        self.wrap_angle = 0  # Current angle around player
        self.wrap_timer = 0
        self.wrap_duration = 90  # How long to stay wrapped before releasing
        self.bite_cooldown = 0
        self.bite_damage = 1

    def take_damage(self, damage):
        self.health -= damage
        # Getting hit makes it angry!
        if not self.is_wrapped:  # Don't reset aggro while wrapped
            self.is_aggroed = True
            self.aggro_timer = self.aggro_duration
        return self.health <= 0

    def reset_aggro(self):
        """Reset all aggro and wrap states"""
        self.is_aggroed = False
        self.aggro_timer = 0
        self.is_lunging = False
        self.lunge_vel_x = 0
        self.lunge_vel_y = 0
        self.is_wrapped = False
        self.wrap_target = None
        self.wrap_timer = 0

    def update(self, platforms, player):
        self.anim += 1
        self.slither_phase += 0.25

        # Tongue flicking - more frequent when aggroed
        self.tongue_flick += 1
        flick_rate = 40 if self.is_aggroed else 80
        if self.tongue_flick > flick_rate:
            self.tongue_flick = 0
        self.tongue_out = self.tongue_flick < 15

        # Handle wrapped state
        if self.is_wrapped and self.wrap_target:
            self._update_wrapped(player)
            return

        # Check for aggro trigger
        dist_to_player = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist_to_player < self.detection_range and not self.is_aggroed:
            self.is_aggroed = True
            self.aggro_timer = self.aggro_duration

        # Handle aggro timer
        if self.is_aggroed:
            self.aggro_timer -= 1
            if self.aggro_timer <= 0:
                self.is_aggroed = False
                self.is_lunging = False

        # Handle lunging state
        if self.is_lunging:
            self._update_lunge(platforms, player)
            return

        # Check if should start lunging at player
        if self.is_aggroed and not self.is_lunging:
            # Lunge if player is in range and we're on ground
            on_ground = self.vel_y == 0 or self.vel_y < 1
            if dist_to_player < 200 and on_ground:
                # Only lunge if we can reach the player or land safely
                if self._can_lunge_safely(player, platforms):
                    self._start_lunge(player)
                    return

        # Normal patrol movement
        # Check on_ground BEFORE adding gravity
        on_ground = self.vel_y == 0

        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Movement speed - faster when aggroed
        if self.is_aggroed:
            base_speed = self.speed * 2.0
            # Chase player, but check if it's safe first
            wanted_direction = 1 if player.x > self.x else -1
            self.direction = wanted_direction
            # Check if safe to go toward player
            if on_ground and not self.has_ground_ahead(platforms):
                # Not safe - don't move toward player
                self.direction = -wanted_direction
                # Check if the other direction is safe
                if not self.has_ground_ahead(platforms):
                    # Both directions unsafe - stay put
                    base_speed = 0
                    self.direction = wanted_direction  # Face player but don't move
        else:
            base_speed = self.speed * 1.2
            # Normal patrol - check for edge
            if on_ground and not self.has_ground_ahead(platforms):
                self.direction *= -1

        self.x += base_speed * self.direction

        # Patrol bounds only when not aggroed
        if not self.is_aggroed:
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

        # Update position history for normal movement
        self._update_position_history()

    def _can_lunge_safely(self, player, platforms, screen_height=800):
        """Check if lunging toward player would be safe (reach player or land on platform)"""
        # Calculate lunge trajectory (same as _start_lunge)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.sqrt(dx * dx + dy * dy))

        lunge_power = 12
        vel_x = (dx / dist) * lunge_power
        vel_y = -8
        gravity = self.gravity * 0.8

        # Simulate the lunge trajectory
        sim_x = self.x
        sim_y = self.y

        for _ in range(120):  # Simulate up to 2 seconds
            vel_y += gravity
            sim_x += vel_x
            sim_y += vel_y

            # Check if we'd reach the player
            dist_to_player = math.sqrt((player.x - sim_x) ** 2 + (player.y - sim_y) ** 2)
            if dist_to_player < 40:
                return True  # Would reach the player

            # Check if we'd land on a platform
            sim_rect = pygame.Rect(sim_x, sim_y, self.width, self.height)
            for platform in platforms:
                if sim_rect.colliderect(platform.rect) and vel_y > 0:
                    return True  # Would land on a platform

            # Check if we'd fall off screen
            if sim_y > screen_height:
                return False  # Would fall to death

        # If simulation ended without landing, not safe
        return False

    def _start_lunge(self, player):
        """Start lunging toward the player"""
        self.is_lunging = True

        # Calculate lunge trajectory
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.sqrt(dx * dx + dy * dy))

        # Lunge speed and arc
        lunge_power = 12
        self.lunge_vel_x = (dx / dist) * lunge_power
        self.lunge_vel_y = -8  # Jump up first, then arc down

        self.direction = 1 if dx > 0 else -1

    def _update_lunge(self, platforms, player):
        """Update snake during lunge"""
        # Apply gravity to lunge
        self.lunge_vel_y += self.gravity * 0.8

        # Move
        self.x += self.lunge_vel_x
        self.y += self.lunge_vel_y

        # Check if we've hit the player - start wrapping!
        dist_to_player = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist_to_player < 30:
            self._start_wrap(player)
            return

        # Check for landing on platforms
        monster_rect = self.get_rect()
        for platform in platforms:
            if monster_rect.colliderect(platform.rect):
                if self.lunge_vel_y > 0:
                    # Falling - land on top
                    self.y = platform.rect.top - self.height
                    self.is_lunging = False
                    self.lunge_vel_y = 0
                    self.lunge_vel_x = 0
                    return
                elif self.lunge_vel_y < 0:
                    # Moving up - push down from platform bottom
                    self.y = platform.rect.bottom
                    self.lunge_vel_y = 0

        # Check if fallen too far (missed the player)
        if self.y > self.spawn_y + 200:
            self.is_lunging = False

        # Update position history during lunge
        self._update_position_history()

    def _start_wrap(self, player):
        """Start wrapping around the player"""
        self.is_wrapped = True
        self.is_lunging = False
        self.wrap_target = player
        self.wrap_timer = self.wrap_duration
        self.wrap_angle = math.atan2(self.y - player.y, self.x - player.x)
        self.bite_cooldown = random.randint(60, 120)  # First bite after 1-2 seconds

    def _update_wrapped(self, player):
        """Update snake while wrapped around player"""
        self.wrap_timer -= 1
        self.wrap_angle += 0.15  # Rotate around player

        # Follow player position
        wrap_radius = 25
        self.x = player.x + math.cos(self.wrap_angle) * wrap_radius - 20
        self.y = player.y + math.sin(self.wrap_angle) * wrap_radius - 20

        # Bite periodically
        self.bite_cooldown -= 1
        if self.bite_cooldown <= 0:
            player.health -= self.bite_damage
            self.bite_cooldown = random.randint(60, 120)  # Bite every 1-2 seconds
            self.tongue_out = True  # Show tongue when biting

        # Update position history to wrap around player
        # Use increments that account for segment_spacing so segments stay evenly spaced
        center_x = player.x + player.width // 2
        center_y = player.y + player.height // 2
        angle_per_entry = 0.25 / self.segment_spacing
        radius_per_entry = 0.5 / self.segment_spacing
        for i in range(len(self.position_history)):
            angle = self.wrap_angle - i * angle_per_entry
            radius = wrap_radius + (i * radius_per_entry)  # Spiral outward slightly
            hx = center_x + math.cos(angle) * radius
            hy = center_y + math.sin(angle) * radius
            self.position_history[i] = (hx, hy)

        # Release after wrap duration
        if self.wrap_timer <= 0:
            self._release_wrap()

    def _release_wrap(self):
        """Release from wrapped state"""
        self.is_wrapped = False
        self.wrap_target = None
        # Jump away from player
        self.vel_y = -6
        self.x += self.direction * 30
        # Reset aggro timer
        self.aggro_timer = self.aggro_duration // 2

    def _update_position_history(self):
        """Update position history for drawing segments.
        Interpolates positions when moving fast to keep segments evenly spaced."""
        wave_offset = math.sin(self.slither_phase) * 6
        head_x = self.x + 20
        head_y = self.y + 30 + wave_offset

        # Calculate distance from last recorded position
        if self.position_history:
            last_x, last_y = self.position_history[0]
            dx = head_x - last_x
            dy = head_y - last_y
            dist = math.sqrt(dx * dx + dy * dy)

            # Target distance between history entries for smooth segments
            target_step = 2.0

            if dist > target_step:
                # Interpolate multiple points to keep segments connected
                num_steps = max(1, int(dist / target_step))
                for i in range(1, num_steps + 1):
                    t = i / num_steps
                    interp_x = last_x + dx * t
                    interp_y = last_y + dy * t
                    self.position_history.insert(0, (interp_x, interp_y))
            else:
                self.position_history.insert(0, (head_x, head_y))
        else:
            self.position_history.insert(0, (head_x, head_y))

        # Trim history to max length
        if len(self.position_history) > self.history_length:
            self.position_history = self.position_history[:self.history_length]

    def _get_segment_positions(self):
        """Get positions for each segment from history with wave motion"""
        positions = []
        for i in range(self.num_segments):
            history_index = i * self.segment_spacing
            if history_index < len(self.position_history):
                base_x, base_y = self.position_history[history_index]
                # Add perpendicular wave motion that travels down the body
                wave = math.sin(self.slither_phase - i * 0.5) * (4 + i * 0.3)
                positions.append((base_x + wave * 0.3, base_y))
            else:
                # Fallback if history isn't long enough yet
                positions.append(self.position_history[-1])
        return positions

    def _get_segment_size(self, index):
        """Get size of segment - tapers from head to tail"""
        # Head is largest, tapers toward tail
        if index == 0:
            return self.head_size
        # Body tapers gradually
        progress = index / (self.num_segments - 1)
        # Smooth taper: starts wide, gets thinner toward tail
        size = self.body_width * (1 - progress * 0.7)
        return max(2, size)

    def draw(self, screen):
        positions = self._get_segment_positions()

        # Determine colors based on state
        if self.is_aggroed or self.is_wrapped:
            # Angry colors - more red/brown
            body_color = self.aggro_color
            pattern_color = (80, 50, 30)
            belly_color = (160, 120, 80)
            # Pulsing effect when wrapped
            if self.is_wrapped:
                pulse = abs(math.sin(self.anim * 0.2))
                body_color = (
                    int(self.aggro_color[0] + 60 * pulse),
                    int(self.aggro_color[1] - 20 * pulse),
                    int(self.aggro_color[2])
                )
        else:
            body_color = self.color
            pattern_color = self.pattern_color
            belly_color = self.belly_color

        # Draw body segments from tail to head (so head draws on top)
        for i in range(len(positions) - 1, 0, -1):
            x, y = positions[i]
            size = self._get_segment_size(i)

            # Alternating pattern colors for scales effect
            if i % 2 == 0:
                color = body_color
            else:
                color = pattern_color

            # Draw segment as ellipse for more snake-like shape
            segment_rect = (int(x - size), int(y - size * 0.6),
                          int(size * 2), int(size * 1.2))
            pygame.draw.ellipse(screen, color, segment_rect)

            # Add belly highlight
            belly_rect = (int(x - size * 0.5), int(y),
                         int(size), int(size * 0.4))
            pygame.draw.ellipse(screen, belly_color, belly_rect)

        # Draw head
        if positions:
            hx, hy = positions[0]
            head_w = self.head_size * 2.2
            head_h = self.head_size * 1.4

            # Head shape - pointed in direction of travel
            if self.direction > 0:
                head_rect = (int(hx - self.head_size * 0.8), int(hy - head_h / 2),
                            int(head_w), int(head_h))
            else:
                head_rect = (int(hx - head_w + self.head_size * 0.8), int(hy - head_h / 2),
                            int(head_w), int(head_h))

            pygame.draw.ellipse(screen, body_color, head_rect)

            # Eyes - positioned based on direction
            eye_base_x = hx + (4 if self.direction > 0 else -4)
            eye_y = hy - 2

            # Eye color changes when aggroed - red and angry!
            if self.is_aggroed or self.is_wrapped:
                eye_color = (255, 50, 50)  # Red eyes when angry
            else:
                eye_color = (200, 200, 50)  # Yellow normally

            # Eye whites
            pygame.draw.circle(screen, eye_color,
                              (int(eye_base_x - 2), int(eye_y)), 3)
            pygame.draw.circle(screen, eye_color,
                              (int(eye_base_x + 2), int(eye_y)), 3)

            # Slit pupils
            pupil_x = eye_base_x + (1 if self.direction > 0 else -1)
            pygame.draw.line(screen, (0, 0, 0),
                            (pupil_x - 2, eye_y - 2),
                            (pupil_x - 2, eye_y + 2), 1)
            pygame.draw.line(screen, (0, 0, 0),
                            (pupil_x + 2, eye_y - 2),
                            (pupil_x + 2, eye_y + 2), 1)

            # Forked tongue
            if self.tongue_out:
                tongue_base_x = hx + (self.head_size if self.direction > 0 else -self.head_size)
                tongue_end_x = tongue_base_x + (8 if self.direction > 0 else -8)
                tongue_mid_x = tongue_base_x + (5 if self.direction > 0 else -5)

                # Main tongue
                pygame.draw.line(screen, (180, 40, 40),
                                (int(tongue_base_x), int(hy)),
                                (int(tongue_mid_x), int(hy)), 2)
                # Fork
                pygame.draw.line(screen, (180, 40, 40),
                                (int(tongue_mid_x), int(hy)),
                                (int(tongue_end_x), int(hy - 3)), 1)
                pygame.draw.line(screen, (180, 40, 40),
                                (int(tongue_mid_x), int(hy)),
                                (int(tongue_end_x), int(hy + 3)), 1)

        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))
