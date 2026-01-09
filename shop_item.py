import pygame


class ShopItem:
    def __init__(self, name, item_type, cost, description, x, y):
        self.name = name
        self.item_type = item_type
        self.cost = cost
        self.description = description
        self.x = x
        self.y = y
        self.width = 120
        self.height = 80
        self.purchased = False
        self.hover = False

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)

    def check_hover(self, player_rect):
        self.hover = self.get_rect().colliderect(player_rect)
        return self.hover

    def draw(self, screen, font, spore_count):
        if self.purchased:
            return

        rect = self.get_rect()
        # Background
        bg_color = (60, 80, 60) if not self.hover else (80, 120, 80)
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, (100, 150, 100), rect, 3)

        # Item name
        name_text = font.render(self.name, True, (255, 255, 255))
        screen.blit(name_text, (rect.x + 10, rect.y + 5))

        # Cost
        cost_color = (100, 255, 150) if spore_count >= self.cost else (255, 100, 100)
        cost_text = font.render(f"Cost: {self.cost}", True, cost_color)
        screen.blit(cost_text, (rect.x + 10, rect.y + 30))

        # Description
        desc_font = pygame.font.Font(None, 24)
        desc_text = desc_font.render(self.description, True, (200, 200, 200))
        screen.blit(desc_text, (rect.x + 10, rect.y + 55))

        # Buy prompt if hovering
        if self.hover:
            prompt_text = font.render("Press E to buy", True, (255, 255, 100))
            screen.blit(prompt_text, (rect.x + 10, rect.y - 25))
