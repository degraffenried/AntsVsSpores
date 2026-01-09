import json
import os
from datetime import datetime


class SaveManager:
    SAVE_FILE = "savegame.json"

    def __init__(self):
        self.data = self._get_default_data()
        self.load()

    def _get_default_data(self):
        return {
            "version": "1.0",
            "game_beaten": False,
            "first_beaten_date": None,
            "statistics": {
                "total_playthroughs": 0,
                "total_deaths": 0,
                "total_monsters_killed": 0,
                "total_spores_collected": 0,
                "best_score": 0
            },
            "endless_mode": {
                "highest_level_reached": 0,
                "best_endless_score": 0
            },
            "custom_levels": []
        }

    def load(self):
        """Load save data from file"""
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, 'r') as f:
                    loaded = json.load(f)
                    self._merge_data(loaded)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults on error

    def _merge_data(self, loaded):
        """Merge loaded data with defaults, preserving loaded values"""
        for key, value in loaded.items():
            if key in self.data:
                if isinstance(value, dict) and isinstance(self.data[key], dict):
                    self.data[key].update(value)
                else:
                    self.data[key] = value

    def save(self):
        """Save current state to file"""
        with open(self.SAVE_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def mark_game_beaten(self):
        """Mark the game as beaten to unlock features"""
        if not self.data["game_beaten"]:
            self.data["game_beaten"] = True
            self.data["first_beaten_date"] = datetime.now().isoformat()
        self.data["statistics"]["total_playthroughs"] += 1

    def is_game_beaten(self):
        """Check if endless mode and level editor are unlocked"""
        return self.data["game_beaten"]

    def update_statistics(self, deaths=0, kills=0, spores=0, score=0):
        """Update gameplay statistics"""
        stats = self.data["statistics"]
        stats["total_deaths"] += deaths
        stats["total_monsters_killed"] += kills
        stats["total_spores_collected"] += spores
        stats["best_score"] = max(stats["best_score"], score)

    def update_endless_stats(self, level, score):
        """Update endless mode statistics"""
        endless = self.data["endless_mode"]
        endless["highest_level_reached"] = max(endless["highest_level_reached"], level)
        endless["best_endless_score"] = max(endless["best_endless_score"], score)

    def add_custom_level(self, level_name):
        """Add a custom level to the saved list"""
        if level_name not in self.data["custom_levels"]:
            self.data["custom_levels"].append(level_name)

    def get_custom_levels(self):
        """Get list of saved custom levels"""
        return self.data["custom_levels"]
