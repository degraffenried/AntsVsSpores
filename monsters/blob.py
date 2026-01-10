import pygame
import math
import random
from .base import Monster


class Blob(Monster):
    """Terrified gooey blob that moves by sloshing its mass forward."""
    def __init__(self, x, y, patrol_range, speed, health, size=1.0):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (70, 180, 70)
        self.size = size
        self.max_health = health
        self.split_spawned = False

        # Base dimensions
        self.base_radius = 18 * size
        self.width = int(self.base_radius * 2)
        self.height = int(self.base_radius * 2)

        # Slosh state - pools connected by stretchy goo
        self.slosh_phase = 0.0  # 0 to 1
        self.slosh_speed = 0.012  # Slower for more visible motion
        self.slosh_distance = 32 * size  # Long stretch for visible gooping
        self.is_mid_slosh = False

        # Pool positions and sizes (0 to 1 representing mass fraction)
        self.back_mass = 1.0  # Starts with all mass in back
        self.front_mass = 0.0
        self.back_x = x + self.base_radius
        self.front_x = x + self.base_radius
        self.pool_y = y  # Y position (bottom-aligned to platform)

        # Neck properties (thin connection between pools)
        self.neck_thickness = 0.0  # 0 to 1

        # Slime
        self.slime_trails = []
        self.slime_duration = 180
        self.slime_timer = 0

        # Animation
        self.wobble = 0
        self.drip_offset = random.random() * math.pi * 2

        # Fear system
        self.is_scared = False
        self.fear_timer = 0
        self.fear_duration = 300
        self.detection_range = 150

        # Scared visuals
        self.tremble = 0.0
        self.eye_dart_timer = 0
        self.eye_dart_offset = 0
        self.spread_amount = 0.0  # Makes it wider/flatter when scared

    def get_rect(self):
        """Return collision rect - positioned to cover the visible blob"""
        # Center the rect on the blob's visual position
        rect_x = min(self.back_x, self.front_x) - self.base_radius
        rect_width = int(abs(self.front_x - self.back_x) + self.base_radius * 2)

        if self.is_scared and self.spread_amount > 0.2:
            rect_height = int(self.base_radius * 1.5)
        else:
            rect_height = int(self.base_radius * 2.8)

        rect_y = self.pool_y + self.base_radius * 1.5 - rect_height
        return pygame.Rect(rect_x, rect_y, rect_width, rect_height)

    def take_damage(self, damage):
        self.health -= damage
        self.is_scared = True
        self.fear_timer = self.fear_duration
        return self.health <= 0

    def reset_aggro(self):
        self.is_scared = False
        self.fear_timer = 0

    def _find_escape_direction(self, player):
        return -1 if player.x > self.x else 1

    def _has_platform_below(self, check_x, platforms, screen_height=800):
        """Check if there's ANY platform below this x position before screen bottom"""
        for check_y in range(int(self.pool_y + 50), screen_height - 50, 20):
            check_rect = pygame.Rect(check_x - 25, check_y, 50, 20)
            for platform in platforms:
                if check_rect.colliderect(platform.rect):
                    return True
        return False

    def _has_ground_at(self, check_x, platforms):
        """Check if there's ground directly at this x position"""
        ground_rect = pygame.Rect(check_x - 20, self.pool_y + self.base_radius + 5, 40, 20)
        for platform in platforms:
            if ground_rect.colliderect(platform.rect):
                return True
        return False

    def _can_slosh_forward(self, platforms, screen_height=800):
        """Check if we can safely slosh in current direction - NEVER go off screen"""
        future_x = self.back_x + self.slosh_distance * self.direction

        # Hard screen edge limits - never go past these
        if future_x < 60 or future_x > 1140:
            return False

        # Check if there's ground at the future position
        if self._has_ground_at(future_x, platforms):
            return True

        # No immediate ground - DO NOT proceed unless there's definitely a platform below
        if not self._has_platform_below(future_x, platforms, screen_height):
            return False

        # Extra safety: check current platform edge
        # If we're near an edge and would step off, don't do it
        current_has_ground = self._has_ground_at(self.back_x, platforms)
        next_has_ground = self._has_ground_at(future_x, platforms)

        if current_has_ground and not next_has_ground:
            # We're about to step off an edge - only allow if there's definitely a platform below
            if not self._has_platform_below(future_x, platforms, screen_height):
                return False

        return True

    def update(self, platforms, player):
        self.wobble += 0.1
        self.tremble += 0.5
        self.eye_dart_timer += 1

        if self.eye_dart_timer > 12:
            self.eye_dart_timer = 0
            if self.is_scared:
                self.eye_dart_offset = random.uniform(-2, 2)

        # Check for player proximity
        dist_to_player = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist_to_player < self.detection_range:
            if not self.is_scared:
                self.is_scared = True
                self.fear_timer = self.fear_duration
            self.fear_timer = max(self.fear_timer, self.fear_duration // 2)

        if self.is_scared:
            self.fear_timer -= 1
            if self.fear_timer <= 0:
                self.is_scared = False

        # Spread when scared (wider, flatter) - quickly flatten when scared, slowly return to normal
        if self.is_scared:
            target_spread = 0.5
            self.spread_amount += (target_spread - self.spread_amount) * 0.15  # Fast flatten
        else:
            target_spread = 0.0
            self.spread_amount += (target_spread - self.spread_amount) * 0.08  # Slower return
            # Snap to zero if very close
            if self.spread_amount < 0.02:
                self.spread_amount = 0.0

        # Direction
        if self.is_scared:
            self.direction = self._find_escape_direction(player)

        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Update slime trails
        self.slime_trails = [(sx, sy, t - 1) for sx, sy, t in self.slime_trails if t > 1]

        # === SLOSHING MOVEMENT ===
        slosh_speed = self.slosh_speed * (1.2 if self.is_scared else 1.0)

        # Check if we can continue in this direction
        if not self.is_mid_slosh:
            if not self._can_slosh_forward(platforms):
                self.direction *= -1

        self.slosh_phase += slosh_speed

        if self.slosh_phase < 0.25:
            # Phase 1: Tiny tendril reaches out first
            extend = self.slosh_phase / 0.25  # 0 to 1
            extend = extend ** 0.4  # Quick initial reach

            self.front_x = self.back_x + self.slosh_distance * self.direction * extend
            self.front_mass = 0.02 + extend * 0.08  # Tiny: 2% to 10%
            self.back_mass = 1.0 - self.front_mass
            self.neck_thickness = 0.2 + extend * 0.25  # Thin tendril
            self.is_mid_slosh = True

        elif self.slosh_phase < 0.65:
            # Phase 2: Mass transfers - front fills up, back shrinks
            transfer = (self.slosh_phase - 0.25) / 0.4  # 0 to 1
            transfer = transfer ** 0.6

            self.front_x = self.back_x + self.slosh_distance * self.direction
            self.front_mass = 0.10 + transfer * 0.70  # 10% to 80%
            self.back_mass = 1.0 - self.front_mass
            self.neck_thickness = 0.45 + transfer * 0.25  # Gets thicker as mass flows

            # Drop slime from shrinking back pool
            self.slime_timer += 1
            if self.slime_timer > 6:
                self.slime_trails.append((self.back_x, self.pool_y + self.base_radius * 1.5, self.slime_duration))
                self.slime_timer = 0

        elif self.slosh_phase < 1.0:
            # Phase 3: Back catches up, merges into front
            merge = (self.slosh_phase - 0.65) / 0.35  # 0 to 1
            merge = merge ** 1.5  # Accelerate at end

            target_x = self.back_x + self.slosh_distance * self.direction
            self.back_x = self.back_x + (target_x - self.back_x) * merge
            self.front_x = target_x
            self.front_mass = 0.80 + merge * 0.20  # 80% to 100%
            self.back_mass = 1.0 - self.front_mass
            self.neck_thickness = 0.70 * (1.0 - merge)  # Neck disappears as pools merge

        else:
            # Slosh complete - reset for next slosh
            self.slosh_phase = 0.0
            self.back_x = self.front_x
            self.front_mass = 0.5
            self.back_mass = 0.5
            self.neck_thickness = 0.0
            self.is_mid_slosh = False

            # Drop slime at rest position
            self.slime_trails.append((self.back_x, self.pool_y + self.base_radius * 1.5, self.slime_duration))

            # Patrol bounds when not scared
            if not self.is_scared:
                if self.back_x > self.spawn_x + self.patrol_range:
                    self.direction = -1
                elif self.back_x < self.spawn_x - self.patrol_range:
                    self.direction = 1

        # SAFETY: Clamp positions to screen bounds - never go off screen
        self.back_x = max(60, min(1140, self.back_x))
        self.front_x = max(60, min(1140, self.front_x))

        # If we're at an edge, turn around
        if self.back_x <= 60 or self.back_x >= 1140:
            self.direction *= -1
            self.is_mid_slosh = False
            self.slosh_phase = 0.0

        # Update main position and collision rect
        self.x = min(self.back_x, self.front_x) - self.base_radius
        self.width = int(abs(self.front_x - self.back_x) + self.base_radius * 2)
        # Height for collision - shorter ONLY when actively scared and spread, otherwise tall
        if self.is_scared and self.spread_amount > 0.2:
            self.height = int(self.base_radius * 1.5)  # Somewhat flattened when scared
        else:
            self.height = int(self.base_radius * 2.8)  # Tall blob - easy to hit

        # Also update y position for collision rect to be higher up
        self.y = self.pool_y - self.height + self.base_radius * 1.5

        # Vertical movement
        self.pool_y += self.vel_y

        # Platform collision
        feet_rect = pygame.Rect(self.back_x - self.base_radius, self.pool_y + self.base_radius,
                                self.base_radius * 2, 10)
        for platform in platforms:
            if feet_rect.colliderect(platform.rect) and self.vel_y > 0:
                self.pool_y = platform.rect.top - self.base_radius * 1.5
                self.vel_y = 0

        self.y = self.pool_y

    def draw(self, screen):
        # Draw slime trails
        for sx, sy, timer in self.slime_trails:
            alpha = int(100 * (timer / self.slime_duration))
            size = int(5 + 3 * (timer / self.slime_duration))
            surf = pygame.Surface((size * 2, size), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (90, 190, 70, alpha), (0, 0, size * 2, size))
            screen.blit(surf, (sx - size, sy - size // 2))

        # Tremble offset when scared
        tr_x = math.sin(self.tremble * 2) * (2 if self.is_scared else 0)
        tr_y = math.cos(self.tremble * 3) * (1 if self.is_scared else 0)

        # Colors
        if self.is_scared:
            pulse = abs(math.sin(self.tremble * 0.3)) * 0.3
            color = (int(70 + 40 * pulse), int(180 + 20 * pulse), int(70 - 20 * pulse))
            shadow = (50, 150, 50)
            highlight = (120, 230, 110)
        else:
            color = self.color
            shadow = (50, 140, 50)
            highlight = (100, 220, 100)

        # Calculate pool sizes based on mass
        # Only spread out (flatter, wider) when scared - otherwise normal height
        if self.is_scared and self.spread_amount > 0.05:
            spread_mult = 1.0 + self.spread_amount * 0.6
            height_mult = 1.0 / (1.0 + self.spread_amount * 0.4)
        else:
            spread_mult = 1.0
            height_mult = 1.0

        back_radius = self.base_radius * math.sqrt(self.back_mass) * spread_mult
        front_radius = self.base_radius * math.sqrt(self.front_mass) * spread_mult

        # Normal height ratio is 1.8, only reduce when actively scared and spread
        back_height = back_radius * 1.8 * height_mult
        front_height = front_radius * 1.8 * height_mult

        # Y positions - bottom aligned
        base_y = self.pool_y + self.base_radius * 1.5

        # Draw the blob as one continuous stretching goo shape
        pool_dist = abs(self.front_x - self.back_x)
        left_x = min(self.back_x, self.front_x)
        right_x = max(self.back_x, self.front_x)

        # Determine which end is which based on direction
        if self.direction > 0:
            back_pool_x = self.back_x
            front_pool_x = self.front_x
            back_r = back_radius
            front_r = front_radius
            back_h = back_height
            front_h = front_height
        else:
            back_pool_x = self.back_x
            front_pool_x = self.front_x
            back_r = back_radius
            front_r = front_radius
            back_h = back_height
            front_h = front_height

        # Draw continuous goo from back to front using many overlapping ellipses
        num_blobs = max(8, int(pool_dist / 2) + 4)  # Lots of overlapping blobs

        for i in range(num_blobs):
            t = i / max(1, num_blobs - 1)  # 0 at back, 1 at front

            # Position along the stretch
            blob_x = back_pool_x + (front_pool_x - back_pool_x) * t

            # Size interpolation - smoothly transition from back size to front size
            # Use smooth interpolation so it looks like continuous goo
            smooth_t = t * t * (3 - 2 * t)  # Smoothstep

            # Interpolate radius and height
            blob_radius = back_r + (front_r - back_r) * smooth_t
            blob_h = back_h + (front_h - back_h) * smooth_t

            # Make middle section slightly thinner (pinched)
            pinch = 1.0 - (0.25 * math.sin(t * math.pi))  # Slight pinch in middle
            blob_radius *= pinch
            blob_h *= pinch

            # Minimum size so it's always visible
            blob_radius = max(blob_radius, 6)
            blob_h = max(blob_h, 8)

            blob_w = blob_radius * 2
            blob_y = base_y - blob_h

            # Draw shadow
            pygame.draw.ellipse(screen, shadow,
                (blob_x - blob_w/2 - 1 + tr_x, blob_y + 3 + tr_y, blob_w + 2, blob_h + 2))
            # Draw goo blob
            pygame.draw.ellipse(screen, color,
                (blob_x - blob_w/2 + tr_x, blob_y + tr_y, blob_w, blob_h))

        # Draw highlight on the larger pool (back or front depending on mass)
        if self.back_mass >= self.front_mass and back_radius > 4:
            hx = back_pool_x - back_radius * 0.5 + tr_x
            hy = base_y - back_height + 3 + tr_y
            pygame.draw.ellipse(screen, highlight,
                (hx, hy, back_radius, back_height * 0.35))
        elif front_radius > 4:
            hx = front_pool_x - front_radius * 0.5 + tr_x
            hy = base_y - front_height + 3 + tr_y
            pygame.draw.ellipse(screen, highlight,
                (hx, hy, front_radius, front_height * 0.35))

        # Drips on main pool
        main_x = self.front_x if self.front_mass > self.back_mass else self.back_x
        main_r = max(front_radius, back_radius)
        drip_time = pygame.time.get_ticks() / 1000.0 + self.drip_offset
        for i in range(2):
            dp = drip_time * 2 + i * 1.5
            dy = (math.sin(dp) * 0.5 + 0.5) * 4
            dx = main_x - main_r * 0.5 + main_r * i + tr_x
            ds = int(3 + math.sin(dp) * 1)
            pygame.draw.ellipse(screen, color, (dx, base_y - 2 + dy + tr_y, ds, ds + 2))

        # Eyes - on the larger pool, facing movement direction
        eye_x = self.front_x if self.front_mass >= self.back_mass else self.back_x
        eye_pool_r = front_radius if self.front_mass >= self.back_mass else back_radius
        eye_pool_h = front_height if self.front_mass >= self.back_mass else back_height

        if eye_pool_r > 5:  # Only draw eyes if pool is big enough
            eye_y = base_y - eye_pool_h * 0.6 + tr_y
            eye_spacing = eye_pool_r * 0.6

            # Eye size
            if self.is_scared:
                ew, eh = int(10 * self.size), int(12 * self.size)
                pupil_r = int(2 * self.size)
            else:
                ew, eh = int(8 * self.size), int(10 * self.size)
                pupil_r = int(3 * self.size)

            eye_white = (210, 245, 210) if self.is_scared else (180, 240, 180)

            # Left eye
            pygame.draw.ellipse(screen, eye_white,
                (eye_x - eye_spacing - ew // 2 + tr_x, eye_y - eh // 2, ew, eh))
            # Right eye
            pygame.draw.ellipse(screen, eye_white,
                (eye_x + eye_spacing - ew // 2 + tr_x, eye_y - eh // 2, ew, eh))

            # Pupils
            pupil_ox = self.direction * 2 + (self.eye_dart_offset if self.is_scared else 0)
            pygame.draw.circle(screen, (20, 50, 20),
                (int(eye_x - eye_spacing + pupil_ox + tr_x), int(eye_y)), pupil_r)
            pygame.draw.circle(screen, (20, 50, 20),
                (int(eye_x + eye_spacing + pupil_ox + tr_x), int(eye_y)), pupil_r)

            # Gleam
            pygame.draw.circle(screen, (255, 255, 255),
                (int(eye_x - eye_spacing - 2 + tr_x), int(eye_y - 2)), 2)
            pygame.draw.circle(screen, (255, 255, 255),
                (int(eye_x + eye_spacing - 2 + tr_x), int(eye_y - 2)), 2)

            # Worried brows when scared
            if self.is_scared:
                by = eye_y - eh // 2 - 4
                pygame.draw.line(screen, (40, 100, 40),
                    (eye_x - eye_spacing - ew // 2 + tr_x, by + 3),
                    (eye_x - eye_spacing + ew // 2 + tr_x, by), 2)
                pygame.draw.line(screen, (40, 100, 40),
                    (eye_x + eye_spacing - ew // 2 + tr_x, by),
                    (eye_x + eye_spacing + ew // 2 + tr_x, by + 3), 2)

            # Sweat when scared
            if self.is_scared:
                st = pygame.time.get_ticks() / 400.0
                for i in range(2):
                    syo = (st + i * 0.5) % 1.0 * 6
                    sxx = eye_x + (-eye_spacing if i == 0 else eye_spacing) + tr_x
                    pygame.draw.ellipse(screen, (150, 200, 255),
                        (sxx - 2, eye_y - eh // 2 - 6 + syo, 3, 5))

        # Health bar
        bar_x = min(self.front_x, self.back_x) - self.base_radius
        bar_y = base_y - max(front_height, back_height) - 12
        bar_w = 36 * self.size
        pygame.draw.rect(screen, (0, 0, 0), (bar_x + tr_x, bar_y + tr_y, bar_w, 5))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x + tr_x, bar_y + tr_y, bar_w * (self.health / self.max_health), 5))
