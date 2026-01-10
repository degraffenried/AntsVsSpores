import pygame
import math
from .base import Monster


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
