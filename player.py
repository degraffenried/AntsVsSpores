import pygame
from bullet import Bullet


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        self.facing_right = True
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.color = (50, 150, 255)
        self.jump_count = 0
        self.max_jumps = 2
        # Weapon system: 'normal', 'rapid', 'spread'
        self.weapon = 'normal'
        self.has_rapid = False
        self.has_spread = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def handle_input(self, keys):
        # Horizontal movement with A and D
        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_d]:
            self.vel_x = self.speed
            self.facing_right = True

        # Weapon switching with 1, 2, 3 keys
        if keys[pygame.K_1]:
            self.weapon = 'normal'
        if keys[pygame.K_2] and self.has_rapid:
            self.weapon = 'rapid'
        if keys[pygame.K_3] and self.has_spread:
            self.weapon = 'spread'

        # Jump handled separately via key event for double jump

    def jump(self, sound_gen=None):
        if self.jump_count < self.max_jumps:
            self.vel_y = self.jump_power
            if sound_gen:
                if self.jump_count == 0:
                    sound_gen.play("jump")
                else:
                    sound_gen.play("double_jump")
            self.jump_count += 1
            self.on_ground = False

    def shoot(self, bullets, sound_gen=None):
        if self.shoot_cooldown <= 0:
            direction = 1 if self.facing_right else -1
            bullet_x = self.x + self.width if self.facing_right else self.x - 10
            bullet_y = self.y + self.height // 2 - 5

            if self.weapon == 'normal':
                bullets.append(Bullet(bullet_x, bullet_y, direction))
                self.shoot_cooldown = 15
                if sound_gen:
                    sound_gen.play("shoot")
            elif self.weapon == 'rapid':
                bullets.append(Bullet(bullet_x, bullet_y, direction, speed=16))
                self.shoot_cooldown = 8
                if sound_gen:
                    sound_gen.play("shoot_rapid")
            elif self.weapon == 'spread':
                # 3-way shot
                bullets.append(Bullet(bullet_x, bullet_y, direction, speed=10))
                bullets.append(Bullet(bullet_x, bullet_y - 15, direction, speed=10, angle=-0.3))
                bullets.append(Bullet(bullet_x, bullet_y + 15, direction, speed=10, angle=0.3))
                self.shoot_cooldown = 20
                if sound_gen:
                    sound_gen.play("shoot_spread")

    def update(self, platforms):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

        # Move horizontally
        self.x += self.vel_x

        # Check horizontal collisions
        player_rect = self.get_rect()
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.x = platform.rect.left - self.width
                elif self.vel_x < 0:
                    self.x = platform.rect.right

        # Move vertically
        self.y += self.vel_y

        # Check vertical collisions
        self.on_ground = False
        player_rect = self.get_rect()
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                elif self.vel_y < 0:
                    self.y = platform.rect.bottom
                    self.vel_y = 0

        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def resolve_pushed_collision(self, platforms):
        """Resolve collisions when pushed by external forces (monsters, etc).
        Call this after any external position changes."""
        player_rect = self.get_rect()
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # Calculate overlap on each axis
                overlap_left = player_rect.right - platform.rect.left
                overlap_right = platform.rect.right - player_rect.left
                overlap_top = player_rect.bottom - platform.rect.top
                overlap_bottom = platform.rect.bottom - player_rect.top

                # Find smallest overlap to determine push direction
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_left:
                    self.x = platform.rect.left - self.width
                elif min_overlap == overlap_right:
                    self.x = platform.rect.right
                elif min_overlap == overlap_top:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                elif min_overlap == overlap_bottom:
                    self.y = platform.rect.bottom
                    self.vel_y = 0

    def draw(self, screen):
        # Draw body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw head
        pygame.draw.circle(screen, (255, 220, 180),
                          (int(self.x + self.width // 2), int(self.y + 12)), 12)
        # Draw gun
        gun_x = self.x + self.width if self.facing_right else self.x - 15
        gun_y = self.y + self.height // 2 - 3
        pygame.draw.rect(screen, (80, 80, 80), (gun_x, gun_y, 15, 6))
        # Draw eye to show direction
        eye_x = self.x + self.width // 2 + (4 if self.facing_right else -4)
        pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(self.y + 10)), 3)
