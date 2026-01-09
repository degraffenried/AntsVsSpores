import pygame
import math


class Monster:
    def __init__(self, x, y, patrol_range, speed, health):
        self.spawn_x = x
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


class Walker(Monster):
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (200, 50, 50)

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

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
    """Crawls on platforms, moves toward player when nearby"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (40, 40, 40)
        self.leg_anim = 0

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Track player if within range
        dist_to_player = abs(player.x - self.x)
        if dist_to_player < 200:
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1
            self.x += self.speed * self.direction * 1.5
        else:
            # Normal patrol movement
            self.x += self.speed * self.direction
            if self.x > self.spawn_x + self.patrol_range:
                self.direction = -1
            elif self.x < self.spawn_x - self.patrol_range:
                self.direction = 1

        self.leg_anim += 0.3

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
        # Body - two connected circles
        pygame.draw.circle(screen, self.color, (int(self.x + 20), int(self.y + 15)), 12)
        pygame.draw.circle(screen, (50, 50, 50), (int(self.x + 20), int(self.y + 28)), 14)

        # 8 legs with animation
        leg_move = math.sin(self.leg_anim) * 3
        for i, (lx, ly) in enumerate([(-8, 12), (-10, 20), (-9, 28), (-6, 34)]):
            offset = leg_move if i % 2 == 0 else -leg_move
            # Left legs
            pygame.draw.line(screen, (30, 30, 30),
                            (self.x + 20 + lx, self.y + ly),
                            (self.x + 20 + lx - 12, self.y + ly + 8 + offset), 2)
            # Right legs
            pygame.draw.line(screen, (30, 30, 30),
                            (self.x + 20 - lx, self.y + ly),
                            (self.x + 20 - lx + 12, self.y + ly + 8 + offset), 2)

        # Eyes - red dots
        for i in range(4):
            pygame.draw.circle(screen, (200, 0, 0), (int(self.x + 12 + i * 4), int(self.y + 8)), 2)

        # Health bar
        bar_width = self.width * (self.health / 3)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))


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


class Woodlouse(Monster):
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

        # Check if player is in line of sight (same Y level, within range)
        y_diff = abs(player.y - self.y)
        x_diff = abs(player.x - self.x)

        if y_diff < 50 and x_diff < 300:
            self.is_charging = True
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1
            self.x += self.charge_speed * self.direction
        else:
            self.is_charging = False
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
    """Slithering snake with multiple body segments"""
    def __init__(self, x, y, patrol_range, speed, health):
        super().__init__(x, y, patrol_range, speed, health)
        self.color = (100, 180, 60)
        self.segments = [(x, y) for _ in range(5)]  # 5 body segments
        self.anim = 0
        self.tongue_out = False

    def update(self, platforms, player):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        self.anim += 1
        self.tongue_out = (self.anim % 60) < 20

        # Slithering movement with wave
        wave = math.sin(self.anim * 0.15) * 2
        self.x += (self.speed + wave) * self.direction

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

        # Update segment positions (follow the head)
        new_segments = [(self.x + 20, self.y + 20)]
        for i, (sx, sy) in enumerate(self.segments[:-1]):
            # Each segment follows the one in front with delay
            target_x, target_y = new_segments[-1]
            offset = 12  # Distance between segments
            dx = target_x - sx
            dy = target_y - sy
            dist = max(1, math.sqrt(dx * dx + dy * dy))
            new_x = target_x - (dx / dist) * offset
            new_y = target_y - (dy / dist) * offset
            new_segments.append((new_x, new_y + math.sin(self.anim * 0.2 + i) * 3))
        self.segments = new_segments

    def draw(self, screen):
        # Draw body segments (back to front)
        for i, (sx, sy) in enumerate(reversed(self.segments[1:])):
            segment_size = 10 - i
            color_val = 80 + i * 15
            pygame.draw.circle(screen, (color_val, 150 + i * 10, 50),
                              (int(sx), int(sy)), segment_size)

        # Head (larger)
        hx, hy = self.segments[0]
        pygame.draw.circle(screen, self.color, (int(hx), int(hy)), 14)

        # Eyes
        eye_offset = 5 if self.direction > 0 else -5
        pygame.draw.circle(screen, (255, 255, 0),
                          (int(hx + eye_offset - 3), int(hy - 3)), 4)
        pygame.draw.circle(screen, (255, 255, 0),
                          (int(hx + eye_offset + 3), int(hy - 3)), 4)

        # Slit pupils
        pygame.draw.line(screen, (0, 0, 0),
                        (hx + eye_offset - 3, hy - 5),
                        (hx + eye_offset - 3, hy - 1), 2)
        pygame.draw.line(screen, (0, 0, 0),
                        (hx + eye_offset + 3, hy - 5),
                        (hx + eye_offset + 3, hy - 1), 2)

        # Forked tongue
        if self.tongue_out:
            tongue_x = hx + (10 if self.direction > 0 else -10)
            pygame.draw.line(screen, (200, 50, 50),
                            (hx + (7 if self.direction > 0 else -7), hy),
                            (tongue_x, hy), 2)
            pygame.draw.line(screen, (200, 50, 50),
                            (tongue_x, hy), (tongue_x + 3, hy - 3), 1)
            pygame.draw.line(screen, (200, 50, 50),
                            (tongue_x, hy), (tongue_x + 3, hy + 3), 1)

        # Health bar
        bar_width = self.width * (self.health / 2)
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 8, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 8, bar_width, 5))


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
    elif monster_type == 'woodlouse':
        return Woodlouse(data['x'], data['y'], data['patrol_range'],
                        data['speed'], data['health'])
    elif monster_type == 'chompy':
        return Chompy(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'snake':
        return Snake(data['x'], data['y'], data['patrol_range'],
                    data['speed'], data['health'])
    return None
