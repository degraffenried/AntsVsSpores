import pygame
import json
import sys

# Import game classes from separate files
from player import Player
from bullet import Bullet
from spore import Spore
from portal import Portal
from shop_item import ShopItem
from platform import Platform
from monsters import Monster, Walker, Flyer, create_monster
from sound_generator import SoundGenerator
from music_generator import MusicGenerator

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
    controls = font.render("WASD: Move | SPACE: Jump | Click: Shoot", True, (150, 150, 150))
    screen.blit(controls, (10, 770))


def game_over_screen(screen, font, score):
    overlay = pygame.Surface((1200, 800))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))

    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    restart_text = font.render("Press R to Restart or ESC to Quit", True, (200, 200, 200))

    screen.blit(game_over_text, (500, 300))
    screen.blit(score_text, (520, 380))
    screen.blit(restart_text, (420, 460))


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
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Platform Shooter")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

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

    # Initialize first level
    level_data = init_level()
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

    # Start playing music
    music_gen.play('main_theme')
    current_music = 'main_theme'

    running = True
    game_over = False
    victory = False
    respawn_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over and not victory and respawn_timer <= 0:
                    player.shoot(bullets, sound_gen)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if (game_over or victory) and event.key == pygame.K_r:
                    # Full restart
                    game_state.reset()
                    level_data = init_level()
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
                    game_over = False
                    victory = False
                    respawn_timer = 0
                    # Restart music
                    music_gen.play('main_theme')
                    current_music = 'main_theme'
                if not game_over and not victory and respawn_timer <= 0:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                        player.jump(sound_gen)
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

                        # Remove monsters that fall off the map
                        if monster.y > screen_height:
                            monsters.remove(monster)
                            game_state.total_score += 50  # Partial points for fall death
                            continue

                        # Check player-monster collision
                        if player.get_rect().colliderect(monster.get_rect()):
                            player.health -= 1
                            if not player_hit_this_frame:
                                sound_gen.play("player_hit")
                                player_hit_this_frame = True
                            # Knockback
                            if player.x < monster.x:
                                player.x -= 20
                            else:
                                player.x += 20

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
                        game_state.spore_count += 1
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

                    # Grant 2 extra lives for completing a level (not shop)
                    if not is_shop:
                        game_state.lives += 2
                        sound_gen.play("extra_life")

                    # Save weapon state
                    player_state = {
                        'has_rapid': player.has_rapid,
                        'has_spread': player.has_spread,
                        'weapon': player.weapon
                    }
                    game_state.has_rapid = player.has_rapid
                    game_state.has_spread = player.has_spread

                    game_state.current_level += 1
                    level_data = load_level(game_state.current_level, player_state)

                    if level_data is None:
                        victory = True
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
                        player.x = level_data['map_data']['player_spawn']['x']
                        player.y = level_data['map_data']['player_spawn']['y']
                        player.vel_x = 0
                        player.vel_y = 0

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
        level_name = "SHOP" if is_shop else f"Level {game_state.current_level + 1}"
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

            victory_text = font.render("VICTORY!", True, (100, 255, 100))
            score_text = font.render(f"Final Score: {game_state.total_score}", True, (255, 255, 255))
            spores_text = font.render(f"Spores Collected: {game_state.spore_count}", True, (100, 255, 150))
            lives_text = font.render(f"Lives Remaining: {game_state.lives}", True, (255, 200, 200))
            restart_text = font.render("Press R to Play Again or ESC to Quit", True, (200, 200, 200))

            screen.blit(victory_text, (530, 280))
            screen.blit(score_text, (510, 350))
            screen.blit(spores_text, (480, 400))
            screen.blit(lives_text, (490, 450))
            screen.blit(restart_text, (380, 520))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
