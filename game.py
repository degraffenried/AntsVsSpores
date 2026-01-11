#!/Users/jared/Documents/AntsVsSpores/venv/bin/python

import pygame
import json
import sys

# Import game classes from separate files
from player import Player
from bullet import Bullet, Missile
from spore import Spore
from portal import Portal
from shop_item import ShopItem
from game_platform import Platform
from monsters import Monster, Walker, Flyer, Spider, Blob, Taterbug, Chompy, Snake, Shriek, create_monster
from sound_generator import SoundGenerator
from music_generator import MusicGenerator
from save_manager import SaveManager
from menu import MainMenu, PauseMenu
from endless_mode import EndlessLevelGenerator
from level_editor import LevelEditor
import random

# Shop Ant NPC class
class ShopAnt:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 70
        self.tips = [
            "Welcome to my shop!",
            "Good luck out there!",
            "Stay safe, friend!",
            "Damage boost is great for tough enemies!",
            "Spread shot covers more area!",
            "Save up for the best items!",
            "Watch out for spiders!",
            "The monsters are tough ahead...",
            "Need some spores?",
            "Here, take these!",
        ]
        self.current_tip = random.choice(self.tips)
        self.gave_gift = False
        self.gift_amount = 0
        self.near_player = False
        self.tip_timer = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def check_player_near(self, player_rect):
        """Check if player is near and handle gift"""
        detection_rect = pygame.Rect(self.x - 60, self.y - 40, self.width + 120, self.height + 80)
        was_near = self.near_player
        self.near_player = detection_rect.colliderect(player_rect)

        # First time approaching - chance to give gift
        if self.near_player and not was_near and not self.gave_gift:
            self.current_tip = random.choice(self.tips)
            self.tip_timer = 180  # Show tip for 3 seconds
            # 50% chance to give 1-2 spores
            if random.random() < 0.5:
                self.gift_amount = random.randint(1, 2)
                self.gave_gift = True
                return self.gift_amount
        return 0

    def update(self):
        if self.tip_timer > 0:
            self.tip_timer -= 1

    def cycle_dialogue(self):
        """Cycle to a new random dialogue"""
        if self.near_player:
            self.current_tip = random.choice(self.tips)
            self.tip_timer = 180

    def draw(self, screen, font):
        # Draw ant body similar to player but different color
        body_color = (80, 60, 45)  # Lighter brown
        highlight_color = (110, 90, 70)

        cx = self.x + self.width // 2

        # Abdomen
        abdomen_y = self.y + 50
        pygame.draw.ellipse(screen, body_color, (cx - 15, abdomen_y, 30, 22))
        pygame.draw.ellipse(screen, highlight_color, (cx - 10, abdomen_y + 3, 12, 8))

        # Thorax
        thorax_y = self.y + 32
        pygame.draw.ellipse(screen, body_color, (cx - 10, thorax_y, 20, 22))
        pygame.draw.ellipse(screen, highlight_color, (cx - 6, thorax_y + 4, 8, 6))

        # Head
        head_y = self.y + 16
        pygame.draw.circle(screen, body_color, (int(cx), int(head_y)), 12)
        pygame.draw.circle(screen, highlight_color, (int(cx - 3), int(head_y - 3)), 4)

        # Friendly eyes
        pygame.draw.circle(screen, (30, 30, 30), (int(cx - 5), int(head_y - 3)), 4)
        pygame.draw.circle(screen, (30, 30, 30), (int(cx + 5), int(head_y - 3)), 4)
        pygame.draw.circle(screen, (255, 255, 255), (int(cx - 4), int(head_y - 4)), 2)
        pygame.draw.circle(screen, (255, 255, 255), (int(cx + 6), int(head_y - 4)), 2)

        # Antennae
        pygame.draw.line(screen, body_color, (cx - 6, head_y - 10), (cx - 14, head_y - 22), 2)
        pygame.draw.line(screen, body_color, (cx - 14, head_y - 22), (cx - 10, head_y - 28), 2)
        pygame.draw.line(screen, body_color, (cx + 6, head_y - 10), (cx + 14, head_y - 22), 2)
        pygame.draw.line(screen, body_color, (cx + 14, head_y - 22), (cx + 10, head_y - 28), 2)

        # Legs
        leg_color = (60, 45, 35)
        for i, leg_y_off in enumerate([thorax_y + 5, thorax_y + 11, thorax_y + 17]):
            pygame.draw.line(screen, leg_color, (cx - 10, leg_y_off), (cx - 22, leg_y_off + 10), 2)
            pygame.draw.line(screen, leg_color, (cx - 22, leg_y_off + 10), (cx - 26, leg_y_off + 20), 2)
            pygame.draw.line(screen, leg_color, (cx + 10, leg_y_off), (cx + 22, leg_y_off + 10), 2)
            pygame.draw.line(screen, leg_color, (cx + 22, leg_y_off + 10), (cx + 26, leg_y_off + 20), 2)

        # Speech bubble if showing tip
        if self.near_player or self.tip_timer > 0:
            tip_text = self.current_tip
            if self.gave_gift and self.gift_amount > 0:
                tip_text = f"Here's {self.gift_amount} spore{'s' if self.gift_amount > 1 else ''} for you!"

            tip_surface = font.render(tip_text, True, (50, 50, 50))
            tip_rect = tip_surface.get_rect(center=(cx, self.y - 25))
            bubble_rect = tip_rect.inflate(16, 10)

            # Bubble background
            pygame.draw.rect(screen, (255, 255, 240), bubble_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 100, 80), bubble_rect, 2, border_radius=8)
            # Tail
            pygame.draw.polygon(screen, (255, 255, 240), [
                (cx - 8, self.y - 5),
                (cx + 8, self.y - 5),
                (cx, self.y + 5)
            ])
            pygame.draw.line(screen, (100, 100, 80), (cx - 8, self.y - 5), (cx, self.y + 5), 2)
            pygame.draw.line(screen, (100, 100, 80), (cx + 8, self.y - 5), (cx, self.y + 5), 2)

            screen.blit(tip_surface, tip_rect)


# Initialize pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)


# Load map data
def load_map(filename):
    with open(filename, 'r') as f:
        return json.load(f)


# Load sound definitions
def load_sounds(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def draw_ui(screen, player, font, score):
    # Health bar
    pygame.draw.rect(screen, (50, 50, 50), (10, 10, 204, 24))
    pygame.draw.rect(screen, (200, 50, 50), (12, 12, player.health * 2, 20))
    pygame.draw.rect(screen, (255, 100, 100), (12, 12, player.health * 2, 8))
    health_text = font.render(f"HP: {player.health}", True, (255, 255, 255))
    screen.blit(health_text, (220, 12))

    # Score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 40))

    # Controls hint
    controls = font.render("WASD: Move | SPACE: Jump | RShift: Shoot", True, (150, 150, 150))
    screen.blit(controls, (10, 770))


def game_over_screen(screen, font, score):
    overlay = pygame.Surface((1200, 800))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))

    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    restart_text = font.render("Press R to Restart | M for Menu | ESC to Quit", True, (200, 200, 200))

    screen.blit(game_over_text, (500, 300))
    screen.blit(score_text, (520, 380))
    screen.blit(restart_text, (350, 460))


def main():
    # Level files - level 5 is a shop
    levels = ['map.json', 'level2.json', 'level3.json', 'level4.json',
              'level5_shop.json', 'level6.json', 'level7.json']

    # Tutorial levels
    tutorial_levels = [
        'tutorial_levels/tutorial1.json', 'tutorial_levels/tutorial2.json',
        'tutorial_levels/tutorial3.json', 'tutorial_levels/tutorial4.json',
        'tutorial_levels/tutorial5.json', 'tutorial_levels/tutorial6.json',
        'tutorial_levels/tutorial7.json', 'tutorial_levels/tutorial8.json',
        'tutorial_levels/tutorial9.json', 'tutorial_levels/tutorial10.json',
        'tutorial_levels/tutorial11.json', 'tutorial_levels/tutorial12.json'
    ]

    # Load and generate sounds
    sound_defs = load_sounds('sounds.json')
    sound_gen = SoundGenerator(sound_defs)

    # Load and generate music
    music_gen = MusicGenerator('music.json')
    current_music = None

    # Set up display
    screen_width = 1200
    screen_height = 800
    editor_width = 1400
    editor_height = 900
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Platform Shooter")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # Initialize save manager and menu
    save_manager = SaveManager()
    main_menu = MainMenu(screen, save_manager)
    endless_gen = EndlessLevelGenerator()
    level_editor = None  # Created when entering editor mode

    # Game mode: "menu", "game", "endless", "editor", "tutorial"
    game_mode = "menu"
    tutorial_prompt = ""  # Current tutorial instruction text

    # Persistent game state
    class GameState:
        def __init__(self):
            self.reset()

        def reset(self):
            self.current_level = 0
            self.total_score = 0
            self.lives = 3
            self.spore_count = 0
            self.has_rapid = False
            self.has_spread = False
            self.has_missile = False
            self.damage_boost = False
            self.speed_boost = False
            self.has_magnet = False
            self.has_pierce = False
            self.has_shield = False
            self.extra_jump = False

    game_state = GameState()

    def load_level(level_index, preserve_player_state=None, level_list=None):
        # Use provided level list or default to main levels
        current_levels = level_list if level_list else levels

        if level_index >= len(current_levels):
            return None  # No more levels - victory!

        map_data = load_map(current_levels[level_index])
        player = Player(map_data['player_spawn']['x'], map_data['player_spawn']['y'])

        # Preserve weapon unlocks and power-ups from previous levels
        if preserve_player_state:
            player.has_rapid = preserve_player_state.get('has_rapid', False)
            player.has_spread = preserve_player_state.get('has_spread', False)
            player.has_missile = preserve_player_state.get('has_missile', False)
            player.damage_boost = preserve_player_state.get('damage_boost', False)
            player.speed_boost = preserve_player_state.get('speed_boost', False)
            player.has_magnet = preserve_player_state.get('has_magnet', False)
            player.has_pierce = preserve_player_state.get('has_pierce', False)
            player.has_shield = preserve_player_state.get('has_shield', False)
            player.extra_jump = preserve_player_state.get('extra_jump', False)
            player.weapon = preserve_player_state.get('weapon', 'normal')
        else:
            player.has_rapid = game_state.has_rapid
            player.has_spread = game_state.has_spread
            player.has_missile = game_state.has_missile
            player.damage_boost = game_state.damage_boost
            player.speed_boost = game_state.speed_boost
            player.has_magnet = game_state.has_magnet
            player.has_pierce = game_state.has_pierce
            player.has_shield = game_state.has_shield
            player.extra_jump = game_state.extra_jump

        platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'], p.get('bouncy', False), p.get('unstable', False))
                    for p in map_data['platforms']]
        monsters = [create_monster(m) for m in map_data['monsters']]
        monsters = [m for m in monsters if m is not None]
        bullets = []

        # Portal position - use custom if provided, else center top
        portal_pos = map_data.get('portal_position', {'x': screen_width // 2 - 40, 'y': 10})
        portal = Portal(portal_pos['x'], portal_pos['y'])
        spore = None
        bg_color = tuple(map_data['background_color'])

        # Check if this is a shop level
        is_shop = map_data.get('is_shop', False)
        shop_items = []
        if is_shop:
            portal.activate()  # Portal is always active in shop
            # Generate 3 random shop items
            all_items = [
                {"name": "Life Bundle", "type": "life_bundle", "cost": 12, "description": "+3 Lives"},
                {"name": "Rapid Fire", "type": "weapon_rapid", "cost": 10, "description": "Faster shooting"},
                {"name": "Spread Shot", "type": "weapon_spread", "cost": 10, "description": "3-way shot"},
                {"name": "Missile", "type": "weapon_missile", "cost": 12, "description": "Homing missiles"},
                {"name": "Damage Boost", "type": "damage_boost", "cost": 8, "description": "2x bullet damage"},
                {"name": "Speed Boost", "type": "speed_boost", "cost": 8, "description": "Move 50% faster"},
                {"name": "Magnet", "type": "magnet", "cost": 6, "description": "Attract spores"},
            ]
            # Pick 3 random items
            selected = random.sample(all_items, 3)
            positions = [270, 570, 870]  # x positions for 3 items
            for i, item_data in enumerate(selected):
                shop_items.append(ShopItem(
                    item_data['name'],
                    item_data['type'],
                    item_data['cost'],
                    item_data['description'],
                    positions[i],
                    550
                ))

        return {
            'map_data': map_data,
            'player': player,
            'platforms': platforms,
            'monsters': monsters,
            'bullets': bullets,
            'portal': portal,
            'spore': spore,
            'bg_color': bg_color,
            'has_spore': False,
            'spore_spawned': False,
            'is_shop': is_shop,
            'shop_items': shop_items,
            'tutorial_prompt': map_data.get('tutorial_prompt', '')
        }

    def init_level():
        level_data = load_level(game_state.current_level)
        return level_data

    # Game variables (will be initialized when starting a game)
    level_data = None
    player = None
    platforms = []
    monsters = []
    bullets = []
    portal = None
    spore = None
    bg_color = (30, 35, 45)
    has_spore = False
    spore_spawned = False
    is_shop = False
    shop_items = []
    shop_ant = None

    running = True
    game_over = False
    victory = False
    respawn_timer = 0
    is_endless_mode = False
    endless_level = 0
    is_tutorial_mode = False
    tutorial_level = 0
    paused = False
    pause_menu = PauseMenu(screen)

    def start_game(endless=False, tutorial=False):
        nonlocal level_data, player, platforms, monsters, bullets, portal
        nonlocal spore, bg_color, has_spore, spore_spawned, is_shop, shop_items, shop_ant
        nonlocal game_over, victory, respawn_timer, is_endless_mode, endless_level, current_music
        nonlocal is_tutorial_mode, tutorial_level, tutorial_prompt, paused

        game_state.reset()
        paused = False
        is_endless_mode = endless
        is_tutorial_mode = tutorial
        endless_level = 0
        tutorial_level = 0
        game_over = False
        victory = False
        respawn_timer = 0

        if endless:
            endless_gen.reset()
            map_data = endless_gen.generate_level()
            endless_level = 1
        elif tutorial:
            # Load first tutorial level
            tutorial_level = 0
            level_data = load_level(tutorial_level, level_list=tutorial_levels)
            map_data = None
        else:
            level_data = init_level()
            map_data = None

        if endless:
            player = Player(map_data['player_spawn']['x'], map_data['player_spawn']['y'])
            platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'], p.get('bouncy', False), p.get('unstable', False))
                        for p in map_data['platforms']]
            monsters = [create_monster(m) for m in map_data['monsters']]
            monsters = [m for m in monsters if m is not None]
            bullets = []
            portal = Portal(screen_width // 2 - 40, 10)
            spore = None
            bg_color = tuple(map_data['background_color'])
            has_spore = False
            spore_spawned = False
            is_shop = False
            shop_items = []
            shop_ant = None
            tutorial_prompt = ""
        else:
            player = level_data['player']
            platforms = level_data['platforms']
            monsters = level_data['monsters']
            bullets = level_data['bullets']
            portal = level_data['portal']
            spore = level_data['spore']
            bg_color = level_data['bg_color']
            has_spore = level_data['has_spore']
            spore_spawned = level_data['spore_spawned']
            is_shop = level_data['is_shop']
            shop_items = level_data['shop_items']
            tutorial_prompt = level_data.get('tutorial_prompt', "")
            # Create shop ant if this is a shop level
            if is_shop:
                shop_ant = ShopAnt(600, 680)  # Position in center of shop
            else:
                shop_ant = None
            # For tutorial levels with no enemies, pre-activate portal
            if tutorial and len(monsters) == 0 and not is_shop:
                portal.activate()

        music_gen.play('main_theme')
        current_music = 'main_theme'

    # Main application loop
    while running:
        # MENU MODE
        if game_mode == "menu":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    result = main_menu.handle_event(event)
                    if result == "Start Game":
                        game_mode = "game"
                        start_game(endless=False)
                    elif result == "Tutorial":
                        game_mode = "tutorial"
                        start_game(endless=False, tutorial=True)
                    elif result == "Endless Mode":
                        game_mode = "endless"
                        start_game(endless=True)
                    elif result == "Level Editor":
                        game_mode = "editor"
                        # Resize window for editor
                        screen = pygame.display.set_mode((editor_width, editor_height))
                        pygame.display.set_caption("Level Editor - Ants vs Spores")
                        level_editor = LevelEditor(screen)
                        level_editor.reset()
                        music_gen.stop()
                    elif result == "Quit":
                        running = False

            # Draw menu
            main_menu.draw()
            pygame.display.flip()
            clock.tick(60)
            continue

        # EDITOR MODE
        if game_mode == "editor":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    result = level_editor.handle_event(event)
                    if result == "menu":
                        game_mode = "menu"
                        # Restore normal window size
                        screen = pygame.display.set_mode((screen_width, screen_height))
                        pygame.display.set_caption("Platform Shooter")
                        main_menu = MainMenu(screen, save_manager)
                    elif result == "test_play":
                        # Test play the custom level
                        game_mode = "test"
                        # Resize to game size for testing
                        screen = pygame.display.set_mode((screen_width, screen_height))
                        pygame.display.set_caption("Test Play - Press ESC to return")
                        test_data = level_editor.get_level_data()
                        player = Player(test_data['player_spawn']['x'], test_data['player_spawn']['y'])
                        platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'], p.get('bouncy', False), p.get('unstable', False))
                                    for p in test_data['platforms']]
                        monsters = [create_monster(m) for m in test_data['monsters']]
                        monsters = [m for m in monsters if m is not None]
                        bullets = []
                        portal_pos = test_data.get('portal_position', {'x': screen_width // 2 - 40, 'y': 10})
                        portal = Portal(portal_pos['x'], portal_pos['y'])
                        spore = None
                        bg_color = tuple(test_data['background_color'])
                        has_spore = False
                        spore_spawned = False
                        is_shop = False
                        shop_items = []
                        game_over = False
                        victory = False
                        respawn_timer = 0
                        # Store level data for respawning
                        level_data = {
                            'map_data': test_data,
                            'player': player,
                            'platforms': platforms,
                            'monsters': monsters,
                            'bullets': bullets,
                            'portal': portal,
                            'spore': spore,
                            'bg_color': bg_color,
                            'has_spore': False,
                            'spore_spawned': False,
                            'is_shop': False,
                            'shop_items': []
                        }
                        game_state.reset()
                        music_gen.play('main_theme')
                        current_music = 'main_theme'

            if game_mode == "editor":
                level_editor.draw()
                pygame.display.flip()
                clock.tick(60)
                continue

        # GAME/ENDLESS/TEST MODE - Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Handle pause toggle with ESC or P
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if game_mode == "test":
                        game_mode = "editor"
                        # Resize back to editor size
                        screen = pygame.display.set_mode((editor_width, editor_height))
                        pygame.display.set_caption("Level Editor - Ants vs Spores")
                        level_editor.update_screen(screen)
                        music_gen.stop()
                        continue
                    elif not game_over and not victory:
                        paused = not paused
                        pause_menu.selected = 0
                        continue

                # Handle pause menu when paused
                if paused:
                    result = pause_menu.handle_event(event)
                    if result == "Resume":
                        paused = False
                    elif result == "Return to Menu":
                        paused = False
                        game_mode = "menu"
                        music_gen.stop()
                    elif result == "Quit":
                        running = False
                    continue
                if (game_over or victory) and event.key == pygame.K_r:
                    if game_mode == "test":
                        # Return to editor
                        game_mode = "editor"
                        # Resize back to editor size
                        screen = pygame.display.set_mode((editor_width, editor_height))
                        pygame.display.set_caption("Level Editor - Ants vs Spores")
                        level_editor.update_screen(screen)
                        music_gen.stop()
                        continue
                    elif is_endless_mode:
                        # Restart endless mode
                        start_game(endless=True)
                    elif is_tutorial_mode:
                        # Restart tutorial
                        start_game(endless=False, tutorial=True)
                    else:
                        # Full restart normal game
                        start_game(endless=False)
                if (game_over or victory) and event.key == pygame.K_m:
                    # Return to menu
                    game_mode = "menu"
                    music_gen.stop()
                    continue
                if not game_over and not victory and respawn_timer <= 0:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                        player.jump(sound_gen)
                    # Shoot with Right Shift
                    if event.key == pygame.K_RSHIFT:
                        player.shoot(bullets, sound_gen)
                    # Shop purchase
                    if event.key == pygame.K_e and is_shop:
                        for item in shop_items:
                            if item.hover and not item.purchased:
                                if game_state.spore_count >= item.cost:
                                    game_state.spore_count -= item.cost
                                    item.purchased = True
                                    sound_gen.play("shop_buy")

                                    if item.item_type == 'life':
                                        game_state.lives += 1
                                        sound_gen.play("extra_life")
                                    elif item.item_type == 'life_bundle':
                                        game_state.lives += 3
                                        sound_gen.play("extra_life")
                                    elif item.item_type == 'weapon_rapid':
                                        game_state.has_rapid = True
                                        player.has_rapid = True
                                    elif item.item_type == 'weapon_spread':
                                        game_state.has_spread = True
                                        player.has_spread = True
                                    elif item.item_type == 'weapon_missile':
                                        player.has_missile = True
                                    elif item.item_type == 'damage_boost':
                                        player.damage_boost = True
                                    elif item.item_type == 'speed_boost':
                                        player.speed_boost = True
                                    elif item.item_type == 'magnet':
                                        player.has_magnet = True
                                    elif item.item_type == 'pierce':
                                        player.has_pierce = True
                                    elif item.item_type == 'shield':
                                        player.has_shield = True
                                    elif item.item_type == 'extra_jump':
                                        player.extra_jump = True
                                else:
                                    sound_gen.play("shop_error")
                    # Cycle shop ant dialogue with Enter
                    if event.key == pygame.K_RETURN and is_shop and shop_ant:
                        shop_ant.cycle_dialogue()

        if not game_over and not victory and not paused and player:
            # Handle respawn timer
            if respawn_timer > 0:
                respawn_timer -= 1
                if respawn_timer == 0:
                    player.health = player.max_health
            else:
                # Handle input
                keys = pygame.key.get_pressed()
                player.handle_input(keys)

                # Handle continuous shooting when key is held (needed for rapid fire)
                if keys[pygame.K_RSHIFT]:
                    player.shoot(bullets, sound_gen)

                # Update player
                player.update(platforms)

                # Keep player in bounds
                if player.x < 0:
                    player.x = 0
                if player.x > screen_width - player.width:
                    player.x = screen_width - player.width
                if player.y > screen_height:
                    player.health = 0

                # Update bullets
                for bullet in bullets[:]:
                    # Missiles need monsters for homing
                    if isinstance(bullet, Missile):
                        bullet.update(monsters)
                    else:
                        bullet.update()
                    # Remove bullets that are off screen
                    if bullet.x < 0 or bullet.x > screen_width or bullet.y < 0 or bullet.y > screen_height:
                        bullets.remove(bullet)
                        continue

                    # Check bullet-monster collisions
                    bullet_rect = bullet.get_rect()
                    for monster in monsters[:]:
                        if bullet_rect.colliderect(monster.get_rect()):
                            # Damage boost doubles damage
                            damage = 2 if player.damage_boost else 1
                            if monster.take_damage(damage):
                                monsters.remove(monster)
                                game_state.total_score += 100
                                sound_gen.play("enemy_death")
                            else:
                                sound_gen.play("enemy_hit")
                            # Pierce bullets go through enemies
                            if not player.has_pierce and bullet in bullets:
                                bullets.remove(bullet)
                                break

                # Update monsters (not in shop)
                if not is_shop:
                    player_hit_this_frame = False
                    for monster in monsters[:]:
                        monster.update(platforms, player)

                    # Separate overlapping monsters
                    for i, monster in enumerate(monsters):
                        for other in monsters[i+1:]:
                            monster.separate_from(other)

                    for monster in monsters[:]:
                        # Remove monsters that fall off the map
                        if monster.y > screen_height:
                            monsters.remove(monster)
                            game_state.total_score += 50  # Partial points for fall death
                            continue

                        # Check player-monster collision (only take damage once per frame)
                        if player.get_rect().colliderect(monster.get_rect()):
                            if not player_hit_this_frame:
                                # Shield reduces damage to half (rounded up)
                                damage = 1 if not player.has_shield else 0.5
                                player.health -= damage
                                sound_gen.play("player_hit")
                                player_hit_this_frame = True
                                # Knockback
                                if player.x < monster.x:
                                    player.x -= 20
                                else:
                                    player.x += 20
                                # Resolve any collisions from knockback (don't push into walls)
                                player.resolve_pushed_collision(platforms)

                # Check if all enemies defeated - spawn spore (not in shop)
                if not is_shop and len(monsters) == 0 and not spore_spawned:
                    # Use custom spore position if available
                    if level_data and level_data.get('map_data'):
                        spore_pos = level_data['map_data'].get('spore_position', {})
                        spore_x = spore_pos.get('x', screen_width // 2)
                        spore_y = spore_pos.get('y', screen_height // 2)
                    else:
                        spore_x = screen_width // 2
                        spore_y = screen_height // 2
                    spore = Spore(spore_x, spore_y)
                    spore_spawned = True
                    sound_gen.play("spore_spawn")

                # Update spore
                if spore and not spore.collected:
                    spore.update()
                    # Magnet effect - attract spore to player
                    if player.has_magnet:
                        dx = player.x + player.width / 2 - spore.x
                        dy = player.y + player.height / 2 - spore.y
                        dist = (dx * dx + dy * dy) ** 0.5
                        if dist < 300 and dist > 0:  # Attraction range
                            attract_speed = 5
                            spore.x += (dx / dist) * attract_speed
                            spore.y += (dy / dist) * attract_speed
                    if player.get_rect().colliderect(spore.get_rect()):
                        spore.collected = True
                        has_spore = True
                        # Spore reward scales with level (level 1 = 1 spore, etc.)
                        spore_reward = game_state.current_level + 1
                        game_state.spore_count += spore_reward
                        portal.activate()
                        sound_gen.play("spore_collect")

                # Update shop items and shop ant
                if is_shop:
                    for item in shop_items:
                        item.check_hover(player.get_rect())
                    # Update shop ant
                    if shop_ant:
                        shop_ant.update()
                        gift = shop_ant.check_player_near(player.get_rect())
                        if gift > 0:
                            game_state.spore_count += gift
                            sound_gen.play("spore_collect")

                # Update portal
                portal.update()

                # Switch to intense music when health is low (not in shop)
                if not is_shop and not victory:
                    if player.health <= 30 and current_music != 'intense_theme':
                        music_gen.play('intense_theme')
                        current_music = 'intense_theme'
                    elif player.health > 30 and current_music == 'intense_theme':
                        music_gen.play('main_theme')
                        current_music = 'main_theme'

                # Check if player enters active portal
                if portal.active and player.get_rect().colliderect(portal.get_rect()):
                    sound_gen.play("level_complete")

                    # Save weapon state and power-ups
                    player_state = {
                        'has_rapid': player.has_rapid,
                        'has_spread': player.has_spread,
                        'has_missile': player.has_missile,
                        'damage_boost': player.damage_boost,
                        'speed_boost': player.speed_boost,
                        'has_magnet': player.has_magnet,
                        'has_pierce': player.has_pierce,
                        'has_shield': player.has_shield,
                        'extra_jump': player.extra_jump,
                        'weapon': player.weapon
                    }
                    game_state.has_rapid = player.has_rapid
                    game_state.has_spread = player.has_spread
                    game_state.has_missile = player.has_missile
                    game_state.damage_boost = player.damage_boost
                    game_state.speed_boost = player.speed_boost
                    game_state.has_magnet = player.has_magnet
                    game_state.has_pierce = player.has_pierce
                    game_state.has_shield = player.has_shield
                    game_state.extra_jump = player.extra_jump

                    # Handle test mode - just victory
                    if game_mode == "test":
                        victory = True
                        music_gen.play('victory_theme', loop=False)
                        current_music = 'victory_theme'
                    # Handle endless mode - generate next level
                    elif is_endless_mode:
                        endless_level += 1
                        # Spores scale with endless level (not for shop levels)
                        if not is_shop:
                            game_state.spore_count += endless_level
                        # No automatic life bonus - lives only from shop

                        map_data = endless_gen.generate_level()
                        player = Player(map_data['player_spawn']['x'], map_data['player_spawn']['y'])
                        player.has_rapid = player_state['has_rapid']
                        player.has_spread = player_state['has_spread']
                        player.weapon = player_state['weapon']
                        platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'], p.get('bouncy', False), p.get('unstable', False))
                                    for p in map_data['platforms']]
                        monsters = [create_monster(m) for m in map_data['monsters']]
                        monsters = [m for m in monsters if m is not None]
                        bullets = []
                        portal = Portal(screen_width // 2 - 40, 10)
                        spore = None
                        bg_color = tuple(map_data['background_color'])
                        has_spore = False
                        spore_spawned = False

                        # Check if this is a shop level
                        is_shop = map_data.get('is_shop', False)
                        shop_items = []
                        if is_shop:
                            portal.activate()  # Portal always active in shop
                            for item_data in map_data.get('shop_items', []):
                                shop_items.append(ShopItem(
                                    item_data['name'],
                                    item_data['type'],
                                    item_data['cost'],
                                    item_data['description'],
                                    item_data['x'],
                                    item_data['y']
                                ))
                            # Create shop ant
                            shop_ant = ShopAnt(600, 680)
                            # Switch to shop music
                            if current_music != 'shop_theme':
                                music_gen.play('shop_theme')
                                current_music = 'shop_theme'
                        else:
                            shop_ant = None
                            # Switch back to main theme if coming from shop
                            if current_music != 'main_theme':
                                music_gen.play('main_theme')
                                current_music = 'main_theme'

                        # Update endless stats
                        save_manager.update_endless_stats(endless_level, game_state.total_score)
                        save_manager.save()
                    # Handle tutorial mode - go to next tutorial level
                    elif is_tutorial_mode:
                        tutorial_level += 1

                        # Check if tutorial is complete
                        if tutorial_level >= len(tutorial_levels):
                            victory = True
                            music_gen.play('victory_theme', loop=False)
                            current_music = 'victory_theme'
                        else:
                            level_data = load_level(tutorial_level, player_state, level_list=tutorial_levels)
                            player = level_data['player']
                            platforms = level_data['platforms']
                            monsters = level_data['monsters']
                            bullets = level_data['bullets']
                            portal = level_data['portal']
                            spore = level_data['spore']
                            bg_color = level_data['bg_color']
                            has_spore = level_data['has_spore']
                            spore_spawned = level_data['spore_spawned']
                            is_shop = level_data['is_shop']
                            shop_items = level_data['shop_items']
                            tutorial_prompt = level_data.get('tutorial_prompt', '')
                            # Create shop ant for shop levels
                            if is_shop:
                                shop_ant = ShopAnt(600, 680)
                                game_state.spore_count = max(game_state.spore_count, 5)
                            else:
                                shop_ant = None
                            # For tutorial levels with no enemies, pre-activate portal
                            if len(monsters) == 0 and not is_shop:
                                portal.activate()
                    else:
                        # Normal game mode
                        game_state.current_level += 1
                        level_data = load_level(game_state.current_level, player_state)

                        if level_data is None:
                            victory = True
                            # Save progress - game beaten!
                            save_manager.mark_game_beaten()
                            save_manager.update_statistics(score=game_state.total_score,
                                                          spores=game_state.spore_count)
                            save_manager.save()
                            music_gen.play('victory_theme', loop=False)
                            current_music = 'victory_theme'
                        else:
                            player = level_data['player']
                            platforms = level_data['platforms']
                            monsters = level_data['monsters']
                            bullets = level_data['bullets']
                            portal = level_data['portal']
                            spore = level_data['spore']
                            bg_color = level_data['bg_color']
                            has_spore = level_data['has_spore']
                            spore_spawned = level_data['spore_spawned']
                            is_shop = level_data['is_shop']
                            shop_items = level_data['shop_items']
                            # Create shop ant for shop levels
                            if is_shop:
                                shop_ant = ShopAnt(600, 680)
                            else:
                                shop_ant = None

                            # Switch music based on level type
                            if is_shop and current_music != 'shop_theme':
                                music_gen.play('shop_theme')
                                current_music = 'shop_theme'
                            elif not is_shop and current_music != 'main_theme':
                                music_gen.play('main_theme')
                                current_music = 'main_theme'

                # Check player death
                if player.health <= 0 and respawn_timer <= 0:
                    game_state.lives -= 1
                    sound_gen.play("player_death")

                    if game_state.lives <= 0:
                        game_over = True
                        sound_gen.play("game_over")
                        music_gen.stop()
                        current_music = None
                    else:
                        # Respawn at level start
                        respawn_timer = 120  # 2 seconds
                        if is_endless_mode:
                            # Use default spawn point for endless mode
                            player.x = 100
                            player.y = 650
                        else:
                            # Use stored spawn point (works for both normal and test mode)
                            player.x = level_data['map_data']['player_spawn']['x']
                            player.y = level_data['map_data']['player_spawn']['y']
                        player.vel_x = 0
                        player.vel_y = 0
                        # Reset monster aggro so they don't immediately attack the fresh player
                        for monster in monsters:
                            monster.reset_aggro()

        # Draw everything
        screen.fill(bg_color)

        # Draw portal first (behind everything)
        portal.draw(screen)

        for platform in platforms:
            platform.update(player.get_rect() if player else None)
            platform.draw(screen)

        # Draw shop items and shop ant
        if is_shop:
            for item in shop_items:
                item.draw(screen, font, game_state.spore_count)
            if shop_ant:
                shop_ant.draw(screen, font)

        for monster in monsters:
            monster.draw(screen)

        # Draw spore
        if spore and not spore.collected:
            spore.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        # Draw player (flash when respawning)
        if respawn_timer <= 0 or (respawn_timer // 10) % 2 == 0:
            player.draw(screen)

        # Draw UI
        draw_ui(screen, player, font, game_state.total_score)

        # Draw lives
        lives_text = font.render(f"Lives: {game_state.lives}", True, (255, 100, 100))
        screen.blit(lives_text, (220, 40))

        # Draw spore count
        pygame.draw.circle(screen, (100, 255, 150), (330, 52), 10)
        spore_count_text = font.render(f"x{game_state.spore_count}", True, (100, 255, 150))
        screen.blit(spore_count_text, (345, 40))

        # Draw level indicator
        if is_endless_mode:
            level_name = f"Endless {endless_level}"
        elif game_mode == "test":
            level_name = "TEST"
        elif is_tutorial_mode:
            level_name = f"Tutorial {tutorial_level + 1}/{len(tutorial_levels)}"
        elif is_shop:
            level_name = "SHOP"
        else:
            level_name = f"Level {game_state.current_level + 1}"
        level_text = font.render(level_name, True, (255, 255, 255))
        screen.blit(level_text, (screen_width - 180 if is_tutorial_mode else screen_width - 120, 10))

        # Draw tutorial prompt if in tutorial mode
        if is_tutorial_mode and tutorial_prompt:
            prompt_font = pygame.font.Font(None, 32)
            # Draw background box for prompt
            prompt_surface = prompt_font.render(tutorial_prompt, True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(center=(screen_width // 2, 120))
            bg_rect = prompt_rect.inflate(20, 10)
            pygame.draw.rect(screen, (40, 40, 60), bg_rect)
            pygame.draw.rect(screen, (100, 100, 150), bg_rect, 2)
            screen.blit(prompt_surface, prompt_rect)

        # Draw weapon indicator
        weapon_text = font.render(f"Weapon: {player.weapon.upper()}", True, (200, 200, 100))
        screen.blit(weapon_text, (screen_width - 200, 40))

        # Draw weapon switch hints if unlocked
        hints = ["1:Normal"]
        if player.has_rapid:
            hints.append("2:Rapid")
        if player.has_spread:
            hints.append("3:Spread")
        if player.has_missile:
            hints.append("4:Missile")
        hint_text = font.render(" | ".join(hints), True, (150, 150, 150))
        screen.blit(hint_text, (10, screen_height - 30))

        # Draw spore indicator for current level
        if has_spore and not is_shop:
            hint_text = font.render("Go to portal!", True, (100, 200, 255))
            screen.blit(hint_text, (screen_width // 2 - 70, 80))
        elif spore_spawned and spore and not spore.collected:
            hint_text = font.render("Get the SPORE!", True, (100, 255, 150))
            screen.blit(hint_text, (screen_width // 2 - 80, 80))

        # Shop instructions
        if is_shop:
            shop_title = font.render("~ SHOP - Spend your Spores! ~", True, (255, 255, 100))
            screen.blit(shop_title, (screen_width // 2 - 150, 80))
            exit_hint = font.render("Enter portal when done", True, (150, 150, 150))
            screen.blit(exit_hint, (screen_width // 2 - 100, 110))

        if game_over:
            game_over_screen(screen, font, game_state.total_score)

        if victory:
            # Victory screen
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 50, 0))
            overlay.set_alpha(180)
            screen.blit(overlay, (0, 0))

            if game_mode == "test":
                victory_text = font.render("LEVEL COMPLETE!", True, (100, 255, 100))
                restart_text = font.render("Press R to Return to Editor | M for Menu", True, (200, 200, 200))
            elif is_endless_mode:
                victory_text = font.render("GAME OVER!", True, (100, 255, 100))
                endless_text = font.render(f"You reached Endless Level {endless_level}!", True, (255, 255, 100))
                screen.blit(endless_text, (420, 310))
                restart_text = font.render("Press R to Play Again | M for Menu", True, (200, 200, 200))
            else:
                victory_text = font.render("VICTORY!", True, (100, 255, 100))
                unlock_text = font.render("Endless Mode & Level Editor UNLOCKED!", True, (255, 215, 0))
                screen.blit(unlock_text, (380, 310))
                restart_text = font.render("Press R to Play Again | M for Menu", True, (200, 200, 200))

            score_text = font.render(f"Final Score: {game_state.total_score}", True, (255, 255, 255))
            spores_text = font.render(f"Spores Collected: {game_state.spore_count}", True, (100, 255, 150))
            lives_text = font.render(f"Lives Remaining: {game_state.lives}", True, (255, 200, 200))

            screen.blit(victory_text, (500, 260))
            screen.blit(score_text, (510, 380))
            screen.blit(spores_text, (480, 420))
            screen.blit(lives_text, (490, 460))
            screen.blit(restart_text, (400, 520))

        # Draw pause menu if paused
        if paused:
            pause_menu.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
