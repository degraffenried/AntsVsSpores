import pygame


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

    def separate_from(self, other):
        """Push this monster away from another monster if overlapping.
        Returns True if separation occurred."""
        my_rect = self.get_rect()
        other_rect = other.get_rect()

        if not my_rect.colliderect(other_rect):
            return False

        # Calculate overlap
        overlap_left = my_rect.right - other_rect.left
        overlap_right = other_rect.right - my_rect.left
        overlap_top = my_rect.bottom - other_rect.top
        overlap_bottom = other_rect.bottom - my_rect.top

        # Find smallest horizontal overlap
        if overlap_left < overlap_right:
            h_overlap = -overlap_left
        else:
            h_overlap = overlap_right

        # Find smallest vertical overlap
        if overlap_top < overlap_bottom:
            v_overlap = -overlap_top
        else:
            v_overlap = overlap_bottom

        # Push apart along the axis with smallest overlap
        if abs(h_overlap) < abs(v_overlap):
            # Horizontal separation - each monster moves half the distance
            self.x += h_overlap / 2
            other.x -= h_overlap / 2
        else:
            # Vertical separation - only if not a big difference (avoid stacking issues)
            if abs(v_overlap) < 20:
                self.y += v_overlap / 2
                other.y -= v_overlap / 2

        return True
