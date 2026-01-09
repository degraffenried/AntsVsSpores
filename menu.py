import pygame


class MainMenu:
    def __init__(self, screen, save_manager):
        self.screen = screen
        self.save_manager = save_manager
        self.selected = 0
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

    def get_options(self):
        """Get menu options with unlock status"""
        game_beaten = self.save_manager.is_game_beaten()
        return [
            ("Start Game", True),
            ("Endless Mode", game_beaten),
            ("Level Editor", game_beaten),
            ("Quit", True)
        ]

    def handle_event(self, event):
        """Handle input events, return selected option name or None"""
        if event.type == pygame.KEYDOWN:
            options = self.get_options()

            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(options)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(options)
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                option_name, unlocked = options[self.selected]
                if unlocked:
                    return option_name
                return None
            elif event.key == pygame.K_ESCAPE:
                return "Quit"

        return None

    def draw(self):
        """Draw the main menu"""
        # Background
        self.screen.fill((20, 25, 40))

        # Draw some decorative elements
        for i in range(20):
            x = (i * 67) % self.screen_width
            y = (i * 43) % self.screen_height
            size = 2 + (i % 3)
            alpha = 50 + (i * 10) % 100
            pygame.draw.circle(self.screen, (50, 60, 80), (x, y), size)

        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("PLATFORM SHOOTER", True, (100, 200, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title, title_rect)

        # Subtitle / Champion badge
        subtitle_font = pygame.font.Font(None, 36)
        if self.save_manager.is_game_beaten():
            badge = subtitle_font.render("~ CHAMPION ~", True, (255, 215, 0))
            badge_rect = badge.get_rect(center=(self.screen_width // 2, 170))
            self.screen.blit(badge, badge_rect)

        # Menu options
        options = self.get_options()
        option_font = pygame.font.Font(None, 48)
        start_y = 280

        for i, (text, unlocked) in enumerate(options):
            # Determine color
            if i == self.selected and unlocked:
                color = (255, 255, 100)
                prefix = "> "
            elif unlocked:
                color = (200, 200, 200)
                prefix = "  "
            else:
                color = (80, 80, 80)
                prefix = "  "

            display_text = prefix + text
            if not unlocked:
                display_text += " [LOCKED]"

            rendered = option_font.render(display_text, True, color)
            text_rect = rendered.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            self.screen.blit(rendered, text_rect)

            # Draw selection box
            if i == self.selected and unlocked:
                box_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, (100, 100, 150), box_rect, 2)

        # Controls hint
        hint_font = pygame.font.Font(None, 28)
        hint = hint_font.render("UP/DOWN: Select | ENTER: Confirm | ESC: Quit", True, (120, 120, 140))
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(hint, hint_rect)

        # Stats display if game beaten
        if self.save_manager.is_game_beaten():
            stats = self.save_manager.data.get("statistics", {})
            stats_font = pygame.font.Font(None, 24)

            best_score = stats.get("best_score", 0)
            endless_best = self.save_manager.data.get("endless_mode", {}).get("highest_level_reached", 0)

            stats_text = f"Best Score: {best_score}"
            if endless_best > 0:
                stats_text += f" | Endless Best: Level {endless_best}"

            stats_rendered = stats_font.render(stats_text, True, (100, 100, 120))
            stats_rect = stats_rendered.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
            self.screen.blit(stats_rendered, stats_rect)


class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.selected = 0
        self.options = ["Resume", "Return to Menu", "Quit"]
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

    def handle_event(self, event):
        """Handle input events, return selected option name or None"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "Resume"
        return None

    def draw(self):
        """Draw pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 250))
        self.screen.blit(title, title_rect)

        # Options
        option_font = pygame.font.Font(None, 42)
        for i, text in enumerate(self.options):
            if i == self.selected:
                color = (255, 255, 100)
                prefix = "> "
            else:
                color = (180, 180, 180)
                prefix = "  "

            rendered = option_font.render(prefix + text, True, color)
            text_rect = rendered.get_rect(center=(self.screen_width // 2, 350 + i * 50))
            self.screen.blit(rendered, text_rect)
