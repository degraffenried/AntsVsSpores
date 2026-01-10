#!/Users/jared/Documents/AntsVsSpores/venv/bin/python

import pygame
import json
import sys

# Import game classes from separate files
from player import Player
from bullet import Bullet
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

    # Game mode: "menu", "game", "endless", "editor"
    game_mode = "menu"

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

    game_state = GameState()

    def load_level(level_index, preserve_player_state=None):
        if level_index >= len(levels):
            return None  # No more levels - victory!

        map_data = load_map(levels[level_index])
        player = Player(map_data['player_spawn']['x'], map_data['player_spawn']['y'])

        # Preserve weapon unlocks from previous levels
        if preserve_player_state:
            player.has_rapid = preserve_player_state.get('has_rapid', False)
            player.has_spread = preserve_player_state.get('has_spread', False)
            player.weapon = preserve_player_state.get('weapon', 'normal')
        else:
            player.has_rapid = game_state.has_rapid
            player.has_spread = game_state.has_spread

        platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'])
                    for p in map_data['platforms']]
        monsters = [create_monster(m) for m in map_data['monsters']]
        monsters = [m for m in monsters if m is not None]
        bullets = []

        # Portal at top center of screen
        portal = Portal(screen_width // 2 - 40, 10)
        spore = None
        bg_color = tuple(map_data['background_color'])

        # Check if this is a shop level
        is_shop = map_data.get('is_shop', False)
        shop_items = []
        if is_shop:
            portal.activate()  # Portal is always active in shop
            for item_data in map_data.get('shop_items', []):
                shop_items.append(ShopItem(
                    item_data['name'],
                    item_data['type'],
                    item_data['cost'],
                    item_data['description'],
                    item_data['x'],
                    item_data['y']
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
            'shop_items': shop_items
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

    running = True
    game_over = False
    victory = False
    respawn_timer = 0
    is_endless_mode = False
    endless_level = 0

    def start_game(endless=False):
        nonlocal level_data, player, platforms, monsters, bullets, portal
        nonlocal spore, bg_color, has_spore, spore_spawned, is_shop, shop_items
        nonlocal game_over, victory, respawn_timer, is_endless_mode, endless_level, current_music

        game_state.reset()
        is_endless_mode = endless
        endless_level = 0
        game_over = False
        victory = False
        respawn_timer = 0

        if endless:
            endless_gen.reset()
            map_data = endless_gen.generate_level()
            endless_level = 1
        else:
            level_data = init_level()
            map_data = None

        if endless:
            player = Player(map_data['player_spawn']['x'], map_data['player_spawn']['y'])
            platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'])
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
                        platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'])
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
                if event.key == pygame.K_ESCAPE:
                    if game_mode == "test":
                        game_mode = "editor"
                        # Resize back to editor size
                        screen = pygame.display.set_mode((editor_width, editor_height))
                        pygame.display.set_caption("Level Editor - Ants vs Spores")
                        level_editor.update_screen(screen)
                        music_gen.stop()
                        continue
                    else:
                        game_mode = "menu"
                        music_gen.stop()
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
                                else:
                                    sound_gen.play("shop_error")

        if not game_over and not victory:
            # Handle respawn timer
            if respawn_timer > 0:
                respawn_timer -= 1
                if respawn_timer == 0:
                    player.health = player.max_health
            else:
                # Handle input
                keys = pygame.key.get_pressed()
                player.handle_input(keys)

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
                    bullet.update()
                    # Remove bullets that are off screen
                    if bullet.x < 0 or bullet.x > screen_width or bullet.y < 0 or bullet.y > screen_height:
                        bullets.remove(bullet)
                        continue

                    # Check bullet-monster collisions
                    bullet_rect = bullet.get_rect()
                    for monster in monsters[:]:
                        if bullet_rect.colliderect(monster.get_rect()):
                            if monster.take_damage(1):
                                monsters.remove(monster)
                                game_state.total_score += 100
                                sound_gen.play("enemy_death")
                            else:
                                sound_gen.play("enemy_hit")
                            if bullet in bullets:
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
                                player.health -= 1
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
                    spore = Spore(screen_width // 2, screen_height // 2)
                    spore_spawned = True
                    sound_gen.play("spore_spawn")

                # Update spore
                if spore and not spore.collected:
                    spore.update()
                    if player.get_rect().colliderect(spore.get_rect()):
                        spore.collected = True
                        has_spore = True
                        # Spore reward scales with level (level 1 = 1 spore, etc.)
                        spore_reward = game_state.current_level + 1
                        game_state.spore_count += spore_reward
                        portal.activate()
                        sound_gen.play("spore_collect")

                # Update shop items
                if is_shop:
                    for item in shop_items:
                        item.check_hover(player.get_rect())

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

                    # Grant 1 extra life for completing a level (not shop, not test mode)
                    if not is_shop and game_mode != "test":
                        game_state.lives += 1
                        sound_gen.play("extra_life")

                    # Save weapon state
                    player_state = {
                        'has_rapid': player.has_rapid,
                        'has_spread': player.has_spread,
                        'weapon': player.weapon
                    }
                    game_state.has_rapid = player.has_rapid
                    game_state.has_spread = player.has_spread

                    # Handle test mode - just victory
                    if game_mode == "test":
                        victory = True
                        music_gen.play('victory_theme', loop=False)
                        current_music = 'victory_theme'
                    # Handle endless mode - generate next level
                    elif is_endless_mode:
                        endless_level += 1
                        # Spores scale with endless level
                        game_state.spore_count += endless_level
                        # Life bonus every 3 levels
                        if endless_level % 3 == 0:
                            game_state.lives += 1
                            sound_gen.play("extra_life")

                        map_data = endless_gen.generate_level()
                        player = Player(map_data['player_spawn']['x'], map_data['player_spawn']['y'])
                        player.has_rapid = player_state['has_rapid']
                        player.has_spread = player_state['has_spread']
                        player.weapon = player_state['weapon']
                        platforms = [Platform(p['x'], p['y'], p['width'], p['height'], p['color'])
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

                        # Update endless stats
                        save_manager.update_endless_stats(endless_level, game_state.total_score)
                        save_manager.save()
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
            platform.draw(screen)

        # Draw shop items
        if is_shop:
            for item in shop_items:
                item.draw(screen, font, game_state.spore_count)

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
        elif is_shop:
            level_name = "SHOP"
        else:
            level_name = f"Level {game_state.current_level + 1}"
        level_text = font.render(level_name, True, (255, 255, 255))
        screen.blit(level_text, (screen_width - 120, 10))

        # Draw weapon indicator
        weapon_text = font.render(f"Weapon: {player.weapon.upper()}", True, (200, 200, 100))
        screen.blit(weapon_text, (screen_width - 200, 40))

        # Draw weapon switch hints if unlocked
        hints = ["1:Normal"]
        if player.has_rapid:
            hints.append("2:Rapid")
        if player.has_spread:
            hints.append("3:Spread")
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

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
