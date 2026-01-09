# AntsVsSpores

A retro-style 2D platformer game built with Python and Pygame. Navigate through challenging levels, defeat various monsters, collect spores, and reach the portal to progress.

## Features

- **7 Story Levels** - Progress through increasingly difficult platforming challenges
- **Endless Mode** - Procedurally generated levels with scaling difficulty (unlocks after beating the game)
- **Level Editor** - Create and save your own custom levels (unlocks after beating the game)
- **8 Monster Types** - Walker, Flyer, Spider, Blob, Taterbug, Chompy, Snake, and Shriek
- **Shop System** - Spend collected spores on upgrades like extra lives and life bundles
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
| Jump | Space |
| Shoot | Right Shift |
| Pause | Escape |
| Return to Menu | M (on victory/game over) |

### Level Editor Controls

| Action | Key/Mouse |
|--------|-----------|
| Place Element | Left Click |
| Delete Element | Right Click |
| Select Tool | 1-9, 0 |
| Toggle Grid | G |
| Save Level | Ctrl+S |
| Load Level | Ctrl+O |
| Test Play | P |
| Exit Editor | Escape |

## Gameplay

- Collect **spores** dropped by defeated monsters to spend in the shop
- Reach the **green portal** at the end of each level to progress
- Defeat monsters by shooting them - each type has unique behavior:
  - **Walker** - Patrols back and forth on platforms
  - **Flyer** - Hovers and moves through the air
  - **Spider** - Tracks toward the player when nearby
  - **Blob** - Bounces around erratically
  - **Taterbug** - Curls into an invulnerable ball when shot
  - **Chompy** - Charges at the player when in line of sight
  - **Snake** - Slithers with a multi-segment body
  - **Shriek** - Territorial bat that dive-bombs when agitated

## Project Structure

```
AntsVsSpores/
├── game.py              # Main game loop and state management
├── player.py            # Player class and movement
├── monsters.py          # All monster types
├── bullet.py            # Projectile logic
├── platform.py          # Platform class
├── portal.py            # Level exit portal
├── spore.py             # Collectible spores
├── shop_item.py         # Shop items
├── menu.py              # Main menu and pause menu
├── endless_mode.py      # Procedural level generator
├── level_editor.py      # Level creation tool
├── save_manager.py      # Save/load game progress
├── sound_generator.py   # Procedural sound effects
├── music_generator.py   # Procedural background music
├── sounds.json          # Sound effect definitions
├── music.json           # Music definitions
├── map.json             # Level 1 data
├── level2.json          # Level 2 data
├── ...                  # Additional level files
├── custom_levels/       # User-created levels
└── requirements.txt     # Python dependencies
```

## License

MIT License
