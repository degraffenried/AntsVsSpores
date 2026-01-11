import random
import math


class EndlessLevelGenerator:
    def __init__(self):
        self.difficulty = 1.0
        self.level_count = 0
        self.screen_width = 1200
        self.screen_height = 800

    def reset(self):
        """Reset generator for new endless run"""
        self.difficulty = 1.0
        self.level_count = 0

    def generate_level(self):
        """Generate a random level, returns dict matching level JSON format"""
        self.level_count += 1

        # Every 5 levels is a shop
        if self.level_count % 5 == 0:
            return self._generate_shop_level()

        level_data = {
            "name": f"Endless Level {self.level_count}",
            "width": self.screen_width,
            "height": self.screen_height,
            "background_color": self._random_background(),
            "player_spawn": self._generate_spawn(),
            "platforms": self._generate_platforms(),
            "monsters": [],
            "is_shop": False
        }

        # Generate monsters on platforms
        level_data["monsters"] = self._generate_monsters(level_data["platforms"])

        # Increase difficulty for next level
        self.difficulty = 1.0 + (self.level_count * 0.15)

        return level_data

    def _generate_shop_level(self):
        """Generate a shop level for endless mode"""
        # Shop item costs scale with difficulty
        base_cost = max(6, (self.level_count // 5) * 4)

        all_items = [
            {"name": "Life Bundle", "type": "life_bundle", "cost": base_cost * 2, "description": "+3 Lives"},
            {"name": "Rapid Fire", "type": "weapon_rapid", "cost": base_cost + 4, "description": "Faster shooting"},
            {"name": "Spread Shot", "type": "weapon_spread", "cost": base_cost + 4, "description": "3-way shot"},
            {"name": "Missile", "type": "weapon_missile", "cost": base_cost * 2, "description": "Homing missiles"},
            {"name": "Damage Boost", "type": "damage_boost", "cost": base_cost, "description": "2x bullet damage"},
            {"name": "Speed Boost", "type": "speed_boost", "cost": base_cost, "description": "Move 50% faster"},
            {"name": "Magnet", "type": "magnet", "cost": base_cost - 2, "description": "Attract spores"},
        ]

        # Pick 3 random items
        selected = random.sample(all_items, 3)
        positions = [270, 570, 870]
        shop_items = []
        for i, item in enumerate(selected):
            shop_items.append({
                "name": item["name"],
                "type": item["type"],
                "cost": item["cost"],
                "description": item["description"],
                "x": positions[i],
                "y": 550
            })

        return {
            "name": f"Endless Shop {self.level_count // 5}",
            "width": self.screen_width,
            "height": self.screen_height,
            "background_color": [120, 160, 120],
            "is_shop": True,
            "player_spawn": {"x": 100, "y": 650},
            "portal_position": {"x": 560, "y": 60},
            "platforms": [
                {"x": 0, "y": 750, "width": 1200, "height": 50, "color": [60, 80, 60]},
                {"x": 200, "y": 600, "width": 200, "height": 20, "color": [80, 100, 80]},
                {"x": 500, "y": 600, "width": 200, "height": 20, "color": [80, 100, 80]},
                {"x": 800, "y": 600, "width": 200, "height": 20, "color": [80, 100, 80]},
                {"x": 350, "y": 450, "width": 200, "height": 20, "color": [80, 100, 80]},
                {"x": 650, "y": 450, "width": 200, "height": 20, "color": [80, 100, 80]},
                {"x": 500, "y": 300, "width": 200, "height": 20, "color": [80, 100, 80]},
                {"x": 500, "y": 150, "width": 200, "height": 20, "color": [100, 150, 100]}
            ],
            "monsters": [],
            "shop_items": shop_items
        }

    def _random_background(self):
        """Generate a random light background color for better contrast"""
        # Create themed backgrounds - lighter for visibility
        themes = [
            [140, 130, 160],   # Soft purple
            [120, 155, 135],   # Soft green
            [150, 135, 120],   # Soft brown
            [125, 145, 165],   # Soft blue
            [155, 150, 130],   # Soft tan
        ]
        base = random.choice(themes)
        # Add some variation
        return [
            max(100, min(180, base[0] + random.randint(-15, 15))),
            max(100, min(180, base[1] + random.randint(-15, 15))),
            max(100, min(180, base[2] + random.randint(-15, 15)))
        ]

    def _generate_spawn(self):
        """Generate player spawn point"""
        return {
            "x": random.randint(50, 200),
            "y": 650
        }

    def _generate_platforms(self):
        """Generate random platforms"""
        platforms = []

        # Platform color themes
        color_themes = [
            [100, 70, 50],   # Brown wood
            [70, 80, 90],    # Stone gray
            [50, 80, 50],    # Mossy green
            [90, 60, 40],    # Clay
            [60, 60, 80],    # Purple stone
        ]
        main_color = random.choice(color_themes)

        # Always add ground
        platforms.append({
            "x": 0,
            "y": 750,
            "width": self.screen_width,
            "height": 50,
            "color": [max(0, c - 20) for c in main_color]
        })

        # Generate platform layers
        num_layers = 4 + min(3, int(self.difficulty))
        y_spacing = 550 // num_layers

        for layer in range(num_layers):
            y = 700 - (layer + 1) * y_spacing
            num_platforms = random.randint(2, 4)

            # Distribute platforms across the width
            section_width = self.screen_width // num_platforms

            for p in range(num_platforms):
                x = section_width * p + random.randint(20, section_width - 120)
                width = random.randint(80, 160)

                # Ensure platforms don't go off screen
                x = max(0, min(x, self.screen_width - width))

                # Vary the y position slightly
                platform_y = y + random.randint(-30, 30)
                platform_y = max(100, min(platform_y, 700))

                # Slightly vary color
                platform_color = [
                    max(0, min(255, main_color[0] + random.randint(-15, 15))),
                    max(0, min(255, main_color[1] + random.randint(-15, 15))),
                    max(0, min(255, main_color[2] + random.randint(-15, 15)))
                ]

                platform_data = {
                    "x": x,
                    "y": platform_y,
                    "width": width,
                    "height": 20,
                    "color": platform_color
                }
                # 15% chance to be bouncy, 10% chance to be unstable
                roll = random.random()
                if roll < 0.15:
                    platform_data["bouncy"] = True
                    platform_data["color"] = [200, 80, 150]  # Pink for bouncy
                elif roll < 0.25:
                    platform_data["unstable"] = True
                    platform_data["color"] = [180, 120, 60]  # Orange/brown for unstable
                platforms.append(platform_data)

        # Add some extra floating platforms
        extra_platforms = random.randint(1, 3)
        for _ in range(extra_platforms):
            extra_platform = {
                "x": random.randint(100, self.screen_width - 150),
                "y": random.randint(150, 400),
                "width": random.randint(60, 100),
                "height": 20,
                "color": [max(0, c + 20) for c in main_color]
            }
            # 25% chance for floating platforms to be bouncy, 15% unstable
            roll = random.random()
            if roll < 0.25:
                extra_platform["bouncy"] = True
                extra_platform["color"] = [200, 80, 150]  # Pink for bouncy
            elif roll < 0.40:
                extra_platform["unstable"] = True
                extra_platform["color"] = [180, 120, 60]  # Orange/brown for unstable
            platforms.append(extra_platform)

        return platforms

    def _generate_monsters(self, platforms):
        """Generate monsters on platforms"""
        monsters = []

        # Available monster types (unlock more as difficulty increases)
        all_types = ["walker", "flyer", "spider", "blob", "taterbug", "razorback", "chompy", "snake", "shriek"]

        # Determine available types based on difficulty
        available_count = min(len(all_types), 2 + int(self.difficulty))
        available_types = all_types[:available_count]

        # Number of monsters scales with difficulty
        num_monsters = int(3 + self.difficulty * 2)
        num_monsters = min(num_monsters, 15)  # Cap at 15

        # Get valid platforms (not ground)
        valid_platforms = [p for p in platforms if p["y"] < 700 and p["width"] >= 60]
        if not valid_platforms:
            valid_platforms = platforms[1:]  # Skip ground

        for _ in range(num_monsters):
            if not valid_platforms:
                break

            platform = random.choice(valid_platforms)
            monster_type = random.choice(available_types)

            # Position monster on platform
            x = platform["x"] + random.randint(10, max(10, platform["width"] - 50))
            y = platform["y"] - 45

            # Scale stats with difficulty
            base_speed = 2
            base_health = 2

            speed = base_speed + int(self.difficulty * 0.3)
            health = base_health + int(self.difficulty * 0.4)
            patrol_range = random.randint(40, min(120, platform["width"] - 20))

            monster = {
                "type": monster_type,
                "x": x,
                "y": y,
                "patrol_range": patrol_range,
                "speed": min(speed, 5),  # Cap speed
                "health": min(health, 6)  # Cap health
            }

            monsters.append(monster)

        return monsters

    def get_spore_reward(self):
        """Get spore reward for current endless level"""
        return self.level_count

    def get_life_bonus(self):
        """Get life bonus (every 3 levels in endless mode)"""
        if self.level_count % 3 == 0:
            return 1
        return 0
