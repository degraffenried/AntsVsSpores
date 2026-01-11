# Ants vs Spores

A retro-style 2D platformer game built with Python and Pygame. Navigate through challenging levels, defeat various monsters, collect spores, and reach the portal to progress.

## Features

- **7 Story Levels** - Progress through increasingly difficult platforming challenges
- **Endless Mode** - Procedurally generated levels with scaling difficulty and shops every 5 levels
- **Tutorial Mode** - Learn the game mechanics through guided tutorial levels
- **Level Editor** - Create and save your own custom levels with all platform types and monsters
- **9 Monster Types** - Each with unique AI behaviors and attack patterns
- **4 Weapon Types** - Normal, Rapid Fire, Spread Shot, and Homing Missiles
- **7 Power-ups** - Customize your playstyle with various upgrades
- **Special Platforms** - Bouncy platforms and unstable crumbling platforms
- **Shop System** - Spend collected spores on weapons, power-ups, and extra lives
- **Double/Triple Jump** - Navigate tricky platforming sections
- **Pause Menu** - Pause anytime with ESC or P
- **Procedural 8-bit Audio** - Retro sound effects and music generated in real-time
- **Save System** - Progress is saved automatically

## Requirements

- Python 3.11+
- Pygame 2.6+
- NumPy

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/degraffenried/AntsVsSpores.git
   cd AntsVsSpores
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the game:
   ```bash
   python game.py
   ```

## Controls

| Action | Key |
|--------|-----|
| Move Left | A |
| Move Right | D |
| Jump / Double Jump / Triple Jump | Space |
| Shoot | Right Shift (hold for rapid fire) |
| Weapon: Normal | 1 |
| Weapon: Rapid Fire | 2 (when unlocked) |
| Weapon: Spread Shot | 3 (when unlocked) |
| Weapon: Missile | 4 (when unlocked) |
| Pause | Escape or P |
| Return to Menu | M (on victory/game over) |

### Level Editor Controls

| Action | Key/Mouse |
|--------|-----------|
| Place Element | Left Click |
| Delete Element | Right Click |
| Select Tool | 1-9, 0 |
| Cycle Tools | Q/E or Scroll Wheel |
| Toggle Grid | G |
| New Level | Ctrl+N |
| Save Level | Ctrl+S |
| Load Level | Ctrl+O |
| Test Play | P |
| Exit Editor | Escape |

## Gameplay

- Defeat all monsters in a level to spawn the **spore**
- Collect the spore and reach the **portal** to complete the level
- Spores are currency - spend them in the shop on upgrades
- Talk to the shop ant with Enter - they might give you a gift!
- Each monster type has unique behavior and requires different tactics

### Monsters

| Monster | Behavior |
|---------|----------|
| **Walker** | Patrols back and forth on platforms |
| **Flyer** | Hovers and moves through the air in patterns |
| **Spider** | Tracks toward player, can climb walls to reach higher platforms |
| **Blob** | Terrified gooey creature that sloshes away from player, flattens when scared |
| **Taterbug** | Armored bug that curls into an invulnerable rolling ball when shot |
| **Razorback** | Aggressive taterbug variant with spikes that charges at the player, rolls up defensively when hit |
| **Chompy** | Aggressive charger that rushes at player when in line of sight |
| **Snake** | Multi-segment slithering predator that lunges and wraps around player to bite |
| **Shriek** | Territorial bat that dive-bombs when player enters its territory |

### Platforms

| Platform | Description |
|----------|-------------|
| **Normal** | Standard solid platform |
| **Bouncy** | Pink platforms that launch the player high into the air |
| **Unstable** | Orange/brown platforms that shake and crumble after standing on them for 3 seconds |

## Weapons

| Weapon | Description |
|--------|-------------|
| **Normal** | Standard single shot, balanced fire rate |
| **Rapid Fire** | Hold to shoot continuously at a faster rate |
| **Spread Shot** | 3-way shot pattern, covers more area |
| **Missile** | Homing missiles that track nearby enemies |

## Power-ups

| Power-up | Description |
|----------|-------------|
| **Life Bundle** | Gain 3 extra lives |
| **Damage Boost** | Bullets deal 2x damage |
| **Speed Boost** | Move 50% faster |
| **Pierce** | Bullets pass through enemies |
| **Shield** | Take half damage from enemies |
| **Extra Jump** | Gain a third jump |
| **Magnet** | Attract spores from a distance |

## Project Structure

```
AntsVsSpores/
├── game.py              # Main game loop and state management
├── player.py            # Player class, movement, and weapons
├── bullet.py            # Projectile and missile logic
├── game_platform.py     # Platform class (normal, bouncy, unstable)
├── portal.py            # Level exit portal
├── spore.py             # Collectible spores
├── shop_item.py         # Shop items and upgrades
├── menu.py              # Main menu and pause menu
├── endless_mode.py      # Procedural level generator
├── level_editor.py      # Level creation tool
├── save_manager.py      # Save/load game progress
├── sound_generator.py   # Procedural sound effects
├── music_generator.py   # Procedural background music
├── monsters/            # Monster AI modules
│   ├── base.py          # Base monster class
│   ├── walker.py        # Walker monster
│   ├── flyer.py         # Flyer monster
│   ├── spider.py        # Spider monster
│   ├── blob.py          # Blob monster
│   ├── taterbug.py      # Taterbug monster
│   ├── razorback.py     # Razorback monster
│   ├── chompy.py        # Chompy monster
│   ├── snake.py         # Snake monster
│   └── shriek.py        # Shriek monster
├── sounds.json          # Sound effect definitions
├── music.json           # Music definitions
├── map.json             # Level 1 data
├── level2.json          # Level 2 data
├── level3.json          # Level 3 data
├── level4.json          # Level 4 data
├── level5_shop.json     # Shop level
├── level6.json          # Level 6 data
├── level7.json          # Level 7 data
├── custom_levels/       # User-created levels
├── tutorial_levels/     # Tutorial level data
└── requirements.txt     # Python dependencies
```

## License

MIT License
