import pygame
import math
import random


class Monster:
    def __init__(self, x, y, patrol_range, speed, health):
        self.spawn_x = x
        self.spawn_y = y
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

    def reset_aggro(self):
        """Reset any aggro/targeting state. Override in subclasses with aggro behavior."""
        pass

    def has_ground_ahead(self, platforms, check_distance=10, screen_height=800):
        """Check if there's ground ahead in the direction the monster is moving.
        Returns True if safe to continue, False if there's a deadly drop ahead.

        This method checks:
        1. Is there ground immediately ahead at foot level?
        2. If not, is there any platform below to land on before falling off screen?
        """
        # Check a point ahead of the monster
        check_x = self.x + (self.width + check_distance) if self.direction > 0 else self.x - check_distance
        check_y = self.y + self.height + 5  # Just below the monster's feet

        # First, check for immediate ground ahead
        check_rect = pygame.Rect(check_x, check_y, 5, 10)
        for platform in platforms:
            if check_rect.colliderect(platform.rect):
                return True  # Ground immediately ahead, safe to proceed

        # No immediate ground - check if there's any platform below to land on
        # Scan downward from the edge to see if there's a safe landing
        return self._has_safe_landing(check_x, self.y + self.height, platforms, screen_height)

    def _has_safe_landing(self, x, start_y, platforms, screen_height=800, max_fall=None):
        """Check if there's a platform to land on when falling from position (x, start_y).
        Returns True if there's a safe landing, False if would fall off screen."""
        if max_fall is None:
            max_fall = screen_height  # Check all the way to screen bottom

        # Create a vertical scan line from current position down
        scan_width = self.width  # Use monster's width for the scan
        scan_x = x - scan_width // 2  # Center the scan on x position

        # Check in vertical increments
        for check_y in range(int(start_y), int(start_y + max_fall), 20):
            # If we've gone past screen bottom, no safe landing
            if check_y > screen_height - 50:  # Leave some margin
                return False

            scan_rect = pygame.Rect(scan_x, check_y, scan_width, 20)
            for platform in platforms:
                if scan_rect.colliderect(platform.rect):
                    # Found a platform to land on!
                    return True

        # Reached max fall distance without finding platform
        return False

    def is_safe_to_move(self, platforms, screen_height=800):
        """Comprehensive safety check before moving in current direction.
        Returns True if it's safe to continue moving, False if should turn around."""
        return self.has_ground_ahead(platforms, check_distance=10, screen_height=screen_height)


class Walker(Monster):
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (200, 50, 50)

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0
        if on_ground and not self.has_ground_ahead(platforms):
            self.direction *= -1

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


class Spider(Monster):
    """Crawls on platforms and walls, moves toward player when nearby"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (25, 25, 30)
        self.leg_anim = 0
        self.is_climbing = False
        self.climb_direction = 0  # 1 = climbing up, -1 = climbing down
        self.wall_side = 0  # -1 = left wall, 1 = right wall
        self.current_wall = None  # Reference to the wall platform being climbed

    def update(self, platforms, player):
        self.leg_anim += 0.4  # Faster leg animation

        if self.is_climbing:
            # Climbing a wall
            self.vel_y = 0  # No gravity while climbing
            climb_speed = self.speed * 1.2

            # Move up the wall
            self.y -= climb_speed

            # Check if we've reached the top of the wall
            if self.current_wall:
                wall_top = self.current_wall.rect.top
                if self.y <= wall_top - self.height:
                    # Reached top - step onto the platform
                    self.y = wall_top - self.height
                    self.is_climbing = False
                    self.current_wall = None
                    # Move onto the platform
                    if self.wall_side == -1:
                        self.x = self.current_wall.rect.left if self.current_wall else self.x
                    else:
                        self.x = self.current_wall.rect.right - self.width if self.current_wall else self.x
                    self.direction = -self.wall_side  # Face away from wall
        else:
            # Normal ground movement
            # Apply gravity
            self.vel_y += self.gravity
            if self.vel_y > 20:
                self.vel_y = 20

            # Check for edge before moving (only when on ground)
            on_ground = self.vel_y == 0
            ground_ahead = self.has_ground_ahead(platforms)

            # Track player if within range
            dist_to_player = abs(player.x - self.x)
            if dist_to_player < 250:  # Increased detection range
                if player.x > self.x:
                    self.direction = 1
                else:
                    self.direction = -1
                # Only move toward player if there's ground ahead (or we can climb)
                if not on_ground or ground_ahead:
                    self.x += self.speed * self.direction * 1.5
            else:
                # Check for edge during patrol
                if on_ground and not ground_ahead:
                    self.direction *= -1
                # Normal patrol movement
                self.x += self.speed * self.direction
                if self.x > self.spawn_x + self.patrol_range:
                    self.direction = -1
                elif self.x < self.spawn_x - self.patrol_range:
                    self.direction = 1

            # Move vertically
            self.y += self.vel_y

            # Check collisions
            monster_rect = self.get_rect()
            for platform in platforms:
                if monster_rect.colliderect(platform.rect):
                    # Vertical collision (landing)
                    if self.vel_y > 0 and self.y + self.height > platform.rect.top:
                        if self.y < platform.rect.top:
                            self.y = platform.rect.top - self.height
                            self.vel_y = 0
                    # Horizontal collision (hitting a wall) - start climbing!
                    elif self.vel_y <= 0 or on_ground:
                        # Check if we hit the side of a platform
                        if self.direction > 0 and self.x + self.width > platform.rect.left and self.x < platform.rect.left:
                            # Hit left side of platform - climb it
                            self.is_climbing = True
                            self.wall_side = 1
                            self.current_wall = platform
                            self.x = platform.rect.left - self.width
                        elif self.direction < 0 and self.x < platform.rect.right and self.x + self.width > platform.rect.right:
                            # Hit right side of platform - climb it
                            self.is_climbing = True
                            self.wall_side = -1
                            self.current_wall = platform
                            self.x = platform.rect.right

    def draw(self, screen):
        # Body colors - darker, more menacing
        body_color = self.color
        abdomen_color = (35, 30, 40)

        # Abdomen (back) - larger, more bulbous
        pygame.draw.ellipse(screen, abdomen_color,
                           (self.x + 5, self.y + 12, 30, 26))
        # Abdomen markings - red hourglass pattern
        pygame.draw.polygon(screen, (150, 0, 0), [
            (self.x + 20, self.y + 18),
            (self.x + 15, self.y + 25),
            (self.x + 20, self.y + 28),
            (self.x + 25, self.y + 25)
        ])

        # Cephalothorax (front body)
        pygame.draw.ellipse(screen, body_color,
                           (self.x + 10, self.y + 5, 20, 16))

        # 8 long, scary jointed legs
        leg_move = math.sin(self.leg_anim) * 6
        leg_color = (20, 20, 25)
        leg_highlight = (45, 40, 50)

        # Leg attachment points on body
        leg_bases = [
            (-2, 10), (0, 14), (2, 18), (4, 22),  # Left side
        ]

        for i, (base_x, base_y) in enumerate(leg_bases):
            # Alternating leg movement
            offset = leg_move if i % 2 == 0 else -leg_move
            climb_offset = 0
            if self.is_climbing:
                # Legs reach toward wall when climbing
                climb_offset = 5 * self.wall_side

            # Left legs - 3 segments each
            lx, ly = self.x + 20 + base_x, self.y + base_y

            # First segment (coxa) - goes up and out
            mid1_x = lx - 18 + climb_offset
            mid1_y = ly - 8 + offset * 0.5
            pygame.draw.line(screen, leg_color, (lx, ly), (mid1_x, mid1_y), 3)

            # Second segment (femur) - goes down and out
            mid2_x = mid1_x - 12
            mid2_y = mid1_y + 15 + offset
            pygame.draw.line(screen, leg_color, (mid1_x, mid1_y), (mid2_x, mid2_y), 2)

            # Third segment (tarsus) - the "foot", touches ground
            end_x = mid2_x - 5
            end_y = mid2_y + 10 + offset * 0.3
            pygame.draw.line(screen, leg_highlight, (mid2_x, mid2_y), (end_x, end_y), 2)
            # Claw at the end
            pygame.draw.circle(screen, (60, 50, 70), (int(end_x), int(end_y)), 2)

            # Right legs - mirror of left
            rx, ry = self.x + 20 - base_x, self.y + base_y

            # First segment
            rmid1_x = rx + 18 - climb_offset
            rmid1_y = ry - 8 - offset * 0.5
            pygame.draw.line(screen, leg_color, (rx, ry), (rmid1_x, rmid1_y), 3)

            # Second segment
            rmid2_x = rmid1_x + 12
            rmid2_y = rmid1_y + 15 - offset
            pygame.draw.line(screen, leg_color, (rmid1_x, rmid1_y), (rmid2_x, rmid2_y), 2)

            # Third segment
            rend_x = rmid2_x + 5
            rend_y = rmid2_y + 10 - offset * 0.3
            pygame.draw.line(screen, leg_highlight, (rmid2_x, rmid2_y), (rend_x, rend_y), 2)
            # Claw
            pygame.draw.circle(screen, (60, 50, 70), (int(rend_x), int(rend_y)), 2)

        # Pedipalps (small front appendages)
        palp_move = math.sin(self.leg_anim * 1.5) * 2
        pygame.draw.line(screen, leg_color,
                        (self.x + 15, self.y + 8),
                        (self.x + 8, self.y + 5 + palp_move), 2)
        pygame.draw.line(screen, leg_color,
                        (self.x + 25, self.y + 8),
                        (self.x + 32, self.y + 5 - palp_move), 2)

        # Chelicerae (fangs)
        fang_extend = abs(math.sin(self.leg_anim * 0.5)) * 3
        pygame.draw.line(screen, (80, 0, 0),
                        (self.x + 17, self.y + 12),
                        (self.x + 14, self.y + 18 + fang_extend), 3)
        pygame.draw.line(screen, (80, 0, 0),
                        (self.x + 23, self.y + 12),
                        (self.x + 26, self.y + 18 + fang_extend), 3)

        # Multiple eyes - 8 eyes in two rows
        eye_color = (180, 0, 0)
        eye_glow = (255, 50, 50)
        # Front row - 4 larger eyes
        for i, ex in enumerate([-4, -1, 2, 5]):
            size = 3 if i in [1, 2] else 2  # Middle eyes larger
            pygame.draw.circle(screen, eye_glow, (int(self.x + 20 + ex), int(self.y + 8)), size)
            pygame.draw.circle(screen, eye_color, (int(self.x + 20 + ex), int(self.y + 8)), size - 1)
        # Back row - 4 smaller eyes
        for ex in [-3, 0, 3, 6]:
            pygame.draw.circle(screen, eye_color, (int(self.x + 19 + ex), int(self.y + 5)), 1)

        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 12, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 12, bar_width, 5))


class Blob(Monster):
    """Bouncy blob that splits into smaller blobs when damaged"""
    def __init__(self, x, y, patrol_range, speed, health, size=1.0):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (100, 200, 100)
        self.wobble = 0
        self.size = size
        self.width = int(40 * size)
        self.height = int(40 * size)
        self.bounce_vel = -8
        self.max_health = health
        self.split_spawned = False

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Wobble animation
        self.wobble += 0.15

        # Check for edge before moving (check when descending)
        if self.vel_y > 0 and not self.has_ground_ahead(platforms):
            self.direction *= -1

        # Patrol movement with bouncing
        self.x += self.speed * self.direction

        if self.x > self.spawn_x + self.patrol_range:
            self.direction = -1
        elif self.x < self.spawn_x - self.patrol_range:
            self.direction = 1

        # Move vertically
        self.y += self.vel_y

        # Check vertical collisions and bounce
        monster_rect = self.get_rect()
        for platform in platforms:
            if monster_rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.y = platform.rect.top - self.height
                    self.vel_y = self.bounce_vel  # Bounce!

    def draw(self, screen):
        wobble_x = math.sin(self.wobble) * 3
        wobble_y = math.cos(self.wobble) * 3

        # Main body - green blob
        pygame.draw.ellipse(screen, self.color,
                           (self.x + wobble_x, self.y + wobble_y,
                            self.width - wobble_x, self.height - wobble_y))

        # Inner highlight
        pygame.draw.ellipse(screen, (150, 255, 150),
                           (self.x + 8 + wobble_x, self.y + 5 + wobble_y,
                            self.width - 16, self.height // 2))

        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 12), int(self.y + 15)), int(4 * self.size))
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 28), int(self.y + 15)), int(4 * self.size))

        # Gleam
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 13), int(self.y + 14)), int(2 * self.size))
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 29), int(self.y + 14)), int(2 * self.size))

        # Health bar
        bar_width = self.width * (self.health / self.max_health)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))


class Taterbug(Monster):
    """Armored bug that curls into invulnerable ball when shot"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (80, 80, 90)
        self.is_rolled = False
        self.roll_timer = 0
        self.roll_duration = 120  # 2 seconds at 60fps

    def take_damage(self, damage):
        if self.is_rolled:
            return False  # Invulnerable when rolled
        # Take damage and roll up
        self.health -= damage
        if self.health > 0:
            self.is_rolled = True
            self.roll_timer = self.roll_duration
        return self.health <= 0

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0
        if on_ground and not self.has_ground_ahead(platforms):
            self.direction *= -1

        # Handle roll state
        if self.is_rolled:
            self.roll_timer -= 1
            if self.roll_timer <= 0:
                self.is_rolled = False
            # Roll faster in ball form
            self.x += self.speed * self.direction * 3
        else:
            # Normal patrol
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

    def draw(self, screen):
        if self.is_rolled:
            # Rolled ball form
            pygame.draw.circle(screen, self.color, (int(self.x + 20), int(self.y + 20)), 18)
            # Segment lines on ball
            for i in range(5):
                arc_x = self.x + 5 + i * 6
                pygame.draw.arc(screen, (60, 60, 70),
                               (arc_x, self.y + 5, 8, 30), 0, math.pi, 2)
        else:
            # Elongated segmented body
            pygame.draw.ellipse(screen, self.color,
                               (self.x, self.y + 10, self.width, 25))

            # Segment lines
            for i in range(7):
                seg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, (60, 60, 70),
                                (seg_x, self.y + 12), (seg_x, self.y + 33), 1)

            # Antennae
            pygame.draw.line(screen, (70, 70, 80),
                            (self.x + 5, self.y + 18), (self.x - 5, self.y + 10), 2)
            pygame.draw.line(screen, (70, 70, 80),
                            (self.x + 5, self.y + 22), (self.x - 5, self.y + 28), 2)

            # Legs
            for i in range(7):
                leg_x = self.x + 5 + i * 5
                pygame.draw.line(screen, (60, 60, 70),
                                (leg_x, self.y + 35), (leg_x - 2, self.y + 40), 1)
                pygame.draw.line(screen, (60, 60, 70),
                                (leg_x + 2, self.y + 35), (leg_x + 4, self.y + 40), 1)

        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))


class Chompy(Monster):
    """Charges at player when in line of sight"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (200, 50, 50)
        self.is_charging = False
        self.anim = 0
        self.charge_speed = 8

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        self.anim += 1

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0
        ground_ahead = self.has_ground_ahead(platforms)

        # Check if player is in line of sight (same Y level, within range)
        y_diff = abs(player.y - self.y)
        x_diff = abs(player.x - self.x)

        if y_diff < 50 and x_diff < 300:
            self.is_charging = True
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1
            # Only charge if there's ground ahead
            if not on_ground or ground_ahead:
                self.x += self.charge_speed * self.direction
        else:
            self.is_charging = False
            # Check for edge during patrol
            if on_ground and not ground_ahead:
                self.direction *= -1
            # Normal patrol
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

    def draw(self, screen):
        # Round body
        pygame.draw.circle(screen, self.color,
                          (int(self.x + 20), int(self.y + 25)), 18)

        # Mouth animation
        mouth_open = abs(math.sin(self.anim * 0.3)) * 10 if self.is_charging else 5

        # Teeth
        for i in range(4):
            tooth_x = self.x + 8 + i * 6
            # Upper teeth
            pygame.draw.polygon(screen, (255, 255, 255), [
                (tooth_x, self.y + 22),
                (tooth_x + 3, self.y + 28),
                (tooth_x + 6, self.y + 22)
            ])
            # Lower teeth
            pygame.draw.polygon(screen, (255, 255, 255), [
                (tooth_x, self.y + 28 + mouth_open),
                (tooth_x + 3, self.y + 22 + mouth_open),
                (tooth_x + 6, self.y + 28 + mouth_open)
            ])

        # Dark mouth interior
        pygame.draw.rect(screen, (50, 0, 0),
                        (self.x + 8, self.y + 24, 24, mouth_open))

        # Angry eyes
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x + 12), int(self.y + 12)), 5)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x + 28), int(self.y + 12)), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 13), int(self.y + 13)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 29), int(self.y + 13)), 3)

        # Angry eyebrows
        if self.is_charging:
            pygame.draw.line(screen, (0, 0, 0), (self.x + 8, self.y + 6), (self.x + 16, self.y + 10), 2)
            pygame.draw.line(screen, (0, 0, 0), (self.x + 32, self.y + 6), (self.x + 24, self.y + 10), 2)

        # Health bar
        bar_width = self.width * (self.health / 4)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))


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
                self._start_lunge(player)
                return

        # Normal patrol movement
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Check for edge before moving (only when on ground)
        on_ground = self.vel_y == 0
        if on_ground and not self.has_ground_ahead(platforms):
            self.direction *= -1

        # Movement speed - faster when aggroed
        if self.is_aggroed:
            base_speed = self.speed * 2.0
            # Chase player
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1
        else:
            base_speed = self.speed * 1.2

        self.x += base_speed * self.direction

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

        # Update position history for normal movement
        self._update_position_history()

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
                    self.y = platform.rect.top - self.height
                    self.is_lunging = False
                    self.lunge_vel_y = 0
                    self.lunge_vel_x = 0
                    return

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


def create_monster(data):
    monster_type = data.get('type', 'walker')
    if monster_type == 'walker':
        return Walker(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'flyer':
        return Flyer(data['x'], data['y'], data['patrol_range'],
                    data['speed'], data['health'])
    elif monster_type == 'spider':
        return Spider(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'blob':
        return Blob(data['x'], data['y'], data['patrol_range'],
                   data['speed'], data['health'])
    elif monster_type == 'taterbug':
        return Taterbug(data['x'], data['y'], data['patrol_range'],
                        data['speed'], data['health'])
    elif monster_type == 'chompy':
        return Chompy(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'snake':
        return Snake(data['x'], data['y'], data['patrol_range'],
                    data['speed'], data['health'],
                    data.get('aggro_duration', 180))
    elif monster_type == 'shriek':
        return Shriek(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'],
                     data.get('aggro_duration', 180))
    return None
