import pygame
import json
import os


class LevelEditor:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Tools available
        self.tools = [
            "platform", "spawn", "portal",
            "walker", "flyer", "spider", "blob",
            "woodlouse", "chompy", "snake", "delete"
        ]
        self.selected_tool = 0

        # Level data
        self.platforms = []
        self.monsters = []
        self.spawn_point = {"x": 100, "y": 650}
        self.background_color = [30, 35, 45]

        # Editor state
        self.grid_snap = True
        self.grid_size = 20
        self.selected_element = None
        self.dragging = False
        self.drag_offset = (0, 0)

        # Platform being created
        self.creating_platform = False
        self.platform_start = None

        # Current platform size for new platforms
        self.platform_width = 100
        self.platform_height = 20

        # UI layout
        self.tool_panel_width = 130
        self.status_bar_height = 40
        self.preview_rect = pygame.Rect(0, 0, self.screen_width - self.tool_panel_width,
                                         self.screen_height - self.status_bar_height)

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)

        # File browser state
        self.show_save_dialog = False
        self.show_load_dialog = False
        self.filename_input = ""
        self.available_files = []

        # Ensure custom_levels directory exists
        if not os.path.exists("custom_levels"):
            os.makedirs("custom_levels")

    def reset(self):
        """Reset editor to blank level"""
        self.platforms = []
        self.monsters = []
        self.spawn_point = {"x": 100, "y": 650}
        self.background_color = [30, 35, 45]
        self.selected_element = None

        # Add default ground
        self.platforms.append({
            "x": 0, "y": 750, "width": self.screen_width - self.tool_panel_width,
            "height": 50, "color": [80, 80, 80]
        })

    def snap_to_grid(self, pos):
        """Snap position to grid if enabled"""
        if self.grid_snap:
            x = (pos[0] // self.grid_size) * self.grid_size
            y = (pos[1] // self.grid_size) * self.grid_size
            return (x, y)
        return pos

    def handle_event(self, event):
        """Handle input events, return action string or None"""
        # Handle dialogs first
        if self.show_save_dialog or self.show_load_dialog:
            return self._handle_dialog_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_left_click(event.pos)
            elif event.button == 3:  # Right click
                self._delete_at(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                if self.creating_platform:
                    self._finish_platform(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and self.selected_element:
                self._drag_element(event.pos)

        elif event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)

        elif event.type == pygame.MOUSEWHEEL:
            # Adjust platform width with scroll
            self.platform_width = max(40, min(300, self.platform_width + event.y * 20))

        return None

    def _handle_dialog_event(self, event):
        """Handle events in save/load dialogs"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_save_dialog = False
                self.show_load_dialog = False
                self.filename_input = ""
                return None

            if self.show_save_dialog:
                if event.key == pygame.K_RETURN:
                    if self.filename_input:
                        self.save_level(self.filename_input)
                        self.show_save_dialog = False
                        self.filename_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.filename_input = self.filename_input[:-1]
                elif event.unicode.isalnum() or event.unicode in "_-":
                    if len(self.filename_input) < 20:
                        self.filename_input += event.unicode

            elif self.show_load_dialog:
                if event.key == pygame.K_RETURN:
                    if self.available_files and self.selected_element is not None:
                        self.load_level(self.available_files[self.selected_element])
                        self.show_load_dialog = False
                        self.selected_element = None
                elif event.key == pygame.K_UP and self.available_files:
                    if self.selected_element is None:
                        self.selected_element = 0
                    else:
                        self.selected_element = (self.selected_element - 1) % len(self.available_files)
                elif event.key == pygame.K_DOWN and self.available_files:
                    if self.selected_element is None:
                        self.selected_element = 0
                    else:
                        self.selected_element = (self.selected_element + 1) % len(self.available_files)

        return None

    def _handle_left_click(self, pos):
        """Handle left mouse click"""
        # Check if clicking tool panel
        if pos[0] > self.preview_rect.right:
            self._select_tool(pos)
            return None

        # Check if in preview area
        if not self.preview_rect.collidepoint(pos):
            return None

        snapped = self.snap_to_grid(pos)
        tool = self.tools[self.selected_tool]

        if tool == "platform":
            self.creating_platform = True
            self.platform_start = snapped
        elif tool == "spawn":
            self.spawn_point = {"x": snapped[0], "y": snapped[1]}
        elif tool == "portal":
            pass  # Portal is always at top center
        elif tool == "delete":
            self._delete_at(pos)
        elif tool in ["walker", "flyer", "spider", "blob", "woodlouse", "chompy", "snake"]:
            self.monsters.append({
                "type": tool,
                "x": snapped[0],
                "y": snapped[1],
                "patrol_range": 80,
                "speed": 2,
                "health": 3
            })

        return None

    def _finish_platform(self, pos):
        """Finish creating a platform"""
        if self.platform_start:
            snapped = self.snap_to_grid(pos)
            x1, y1 = self.platform_start
            x2, y2 = snapped

            # Calculate dimensions
            x = min(x1, x2)
            y = min(y1, y2)
            width = max(40, abs(x2 - x1))
            height = max(20, abs(y2 - y1))

            if width < 40:
                width = self.platform_width
            if height < 15:
                height = 20

            self.platforms.append({
                "x": x, "y": y, "width": width, "height": height,
                "color": [100, 80, 60]
            })

        self.creating_platform = False
        self.platform_start = None

    def _select_tool(self, pos):
        """Select a tool from the panel"""
        panel_x = self.preview_rect.right
        relative_y = pos[1] - 60

        if relative_y >= 0:
            tool_index = relative_y // 35
            if 0 <= tool_index < len(self.tools):
                self.selected_tool = tool_index

    def _delete_at(self, pos):
        """Delete element at position"""
        # Check monsters
        for monster in self.monsters[:]:
            rect = pygame.Rect(monster["x"], monster["y"], 40, 40)
            if rect.collidepoint(pos):
                self.monsters.remove(monster)
                return

        # Check platforms (except ground)
        for platform in self.platforms[:]:
            if platform["y"] >= 750:  # Don't delete ground
                continue
            rect = pygame.Rect(platform["x"], platform["y"],
                              platform["width"], platform["height"])
            if rect.collidepoint(pos):
                self.platforms.remove(platform)
                return

    def _drag_element(self, pos):
        """Drag selected element"""
        pass  # Could implement dragging later

    def _handle_keydown(self, event):
        """Handle keyboard input"""
        mods = pygame.key.get_mods()

        if event.key == pygame.K_ESCAPE:
            return "menu"
        elif event.key == pygame.K_g:
            self.grid_snap = not self.grid_snap
        elif event.key == pygame.K_n and mods & pygame.KMOD_CTRL:
            self.reset()
        elif event.key == pygame.K_s and mods & pygame.KMOD_CTRL:
            self.show_save_dialog = True
            self.filename_input = ""
        elif event.key == pygame.K_o and mods & pygame.KMOD_CTRL:
            self.show_load_dialog = True
            self.selected_element = 0
            self._refresh_file_list()
        elif event.key == pygame.K_p:
            return "test_play"
        elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
            tool_index = event.key - pygame.K_1
            if tool_index < len(self.tools):
                self.selected_tool = tool_index

        return None

    def _refresh_file_list(self):
        """Refresh list of available level files"""
        self.available_files = []
        if os.path.exists("custom_levels"):
            for f in os.listdir("custom_levels"):
                if f.endswith(".json"):
                    self.available_files.append(f[:-5])  # Remove .json

    def save_level(self, filename):
        """Save current level to file"""
        level_data = {
            "name": filename,
            "width": self.screen_width - self.tool_panel_width,
            "height": self.screen_height,
            "background_color": self.background_color,
            "player_spawn": self.spawn_point,
            "platforms": self.platforms,
            "monsters": self.monsters
        }

        filepath = f"custom_levels/{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=4)

    def load_level(self, filename):
        """Load level from file"""
        filepath = f"custom_levels/{filename}.json"
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)

            self.platforms = data.get("platforms", [])
            self.monsters = data.get("monsters", [])
            self.spawn_point = data.get("player_spawn", {"x": 100, "y": 650})
            self.background_color = data.get("background_color", [30, 35, 45])

    def get_level_data(self):
        """Get current level as playable data"""
        return {
            "name": "Custom Level",
            "width": self.screen_width - self.tool_panel_width,
            "height": self.screen_height,
            "background_color": self.background_color,
            "player_spawn": self.spawn_point,
            "platforms": self.platforms,
            "monsters": self.monsters
        }

    def draw(self):
        """Draw the level editor"""
        # Background
        self.screen.fill(tuple(self.background_color))

        # Draw grid
        if self.grid_snap:
            for x in range(0, self.preview_rect.right, self.grid_size):
                pygame.draw.line(self.screen, (50, 55, 65), (x, 0),
                                (x, self.preview_rect.bottom), 1)
            for y in range(0, self.preview_rect.bottom, self.grid_size):
                pygame.draw.line(self.screen, (50, 55, 65), (0, y),
                                (self.preview_rect.right, y), 1)

        # Draw platforms
        for p in self.platforms:
            pygame.draw.rect(self.screen, tuple(p["color"]),
                           (p["x"], p["y"], p["width"], p["height"]))
            pygame.draw.rect(self.screen, (200, 200, 200),
                           (p["x"], p["y"], p["width"], p["height"]), 1)

        # Draw platform preview when creating
        if self.creating_platform and self.platform_start:
            mouse_pos = self.snap_to_grid(pygame.mouse.get_pos())
            x = min(self.platform_start[0], mouse_pos[0])
            y = min(self.platform_start[1], mouse_pos[1])
            w = max(40, abs(mouse_pos[0] - self.platform_start[0]))
            h = max(20, abs(mouse_pos[1] - self.platform_start[1]))
            pygame.draw.rect(self.screen, (100, 80, 60, 128), (x, y, w, h))
            pygame.draw.rect(self.screen, (255, 255, 100), (x, y, w, h), 2)

        # Draw spawn point
        pygame.draw.circle(self.screen, (50, 150, 255),
                          (self.spawn_point["x"] + 20, self.spawn_point["y"] + 20), 15)
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (self.spawn_point["x"] + 20, self.spawn_point["y"] + 20), 12)
        spawn_text = self.font.render("SPAWN", True, (50, 150, 255))
        self.screen.blit(spawn_text, (self.spawn_point["x"], self.spawn_point["y"] - 20))

        # Draw portal indicator
        portal_x = self.preview_rect.width // 2 - 40
        pygame.draw.rect(self.screen, (100, 200, 255), (portal_x, 10, 80, 60))
        pygame.draw.rect(self.screen, (255, 255, 255), (portal_x, 10, 80, 60), 2)
        portal_text = self.font.render("PORTAL", True, (255, 255, 255))
        self.screen.blit(portal_text, (portal_x + 10, 30))

        # Draw monsters
        monster_colors = {
            "walker": (200, 50, 50),
            "flyer": (150, 50, 200),
            "spider": (40, 40, 40),
            "blob": (100, 200, 100),
            "woodlouse": (80, 80, 90),
            "chompy": (200, 80, 80),
            "snake": (100, 180, 60)
        }
        for m in self.monsters:
            color = monster_colors.get(m["type"], (200, 50, 50))
            pygame.draw.rect(self.screen, color, (m["x"], m["y"], 40, 40))
            pygame.draw.rect(self.screen, (255, 255, 255), (m["x"], m["y"], 40, 40), 1)
            label = self.font.render(m["type"][:3].upper(), True, (255, 255, 255))
            self.screen.blit(label, (m["x"] + 5, m["y"] + 12))

        # Draw tool panel
        self._draw_tool_panel()

        # Draw status bar
        self._draw_status_bar()

        # Draw dialogs
        if self.show_save_dialog:
            self._draw_save_dialog()
        elif self.show_load_dialog:
            self._draw_load_dialog()

    def _draw_tool_panel(self):
        """Draw the tool selection panel"""
        panel_x = self.preview_rect.right
        panel_width = self.tool_panel_width

        # Panel background
        pygame.draw.rect(self.screen, (40, 45, 55),
                        (panel_x, 0, panel_width, self.screen_height))
        pygame.draw.line(self.screen, (80, 85, 95),
                        (panel_x, 0), (panel_x, self.screen_height), 2)

        # Title
        title = self.title_font.render("TOOLS", True, (200, 200, 220))
        self.screen.blit(title, (panel_x + 35, 20))

        # Tool buttons
        tool_colors = {
            "platform": (100, 80, 60),
            "spawn": (50, 150, 255),
            "portal": (100, 200, 255),
            "walker": (200, 50, 50),
            "flyer": (150, 50, 200),
            "spider": (40, 40, 40),
            "blob": (100, 200, 100),
            "woodlouse": (80, 80, 90),
            "chompy": (200, 80, 80),
            "snake": (100, 180, 60),
            "delete": (200, 50, 50)
        }

        for i, tool in enumerate(self.tools):
            y = 60 + i * 35
            color = tool_colors.get(tool, (100, 100, 100))

            # Highlight selected
            if i == self.selected_tool:
                pygame.draw.rect(self.screen, (80, 85, 95),
                               (panel_x + 5, y - 2, panel_width - 10, 30))
                pygame.draw.rect(self.screen, (255, 255, 100),
                               (panel_x + 5, y - 2, panel_width - 10, 30), 2)

            # Tool color indicator
            pygame.draw.rect(self.screen, color, (panel_x + 10, y + 3, 20, 20))

            # Tool name
            text = self.font.render(tool.capitalize(), True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 35, y + 5))

    def _draw_status_bar(self):
        """Draw the status bar"""
        bar_y = self.screen_height - self.status_bar_height

        pygame.draw.rect(self.screen, (30, 35, 45),
                        (0, bar_y, self.screen_width, self.status_bar_height))
        pygame.draw.line(self.screen, (80, 85, 95),
                        (0, bar_y), (self.screen_width, bar_y), 2)

        # Status text
        grid_status = "ON" if self.grid_snap else "OFF"
        status = f"Grid: {grid_status} | Platforms: {len(self.platforms)} | Monsters: {len(self.monsters)}"
        text = self.font.render(status, True, (180, 180, 200))
        self.screen.blit(text, (10, bar_y + 10))

        # Controls hint
        hint = "Ctrl+S: Save | Ctrl+O: Load | P: Test | G: Grid | ESC: Menu"
        hint_text = self.font.render(hint, True, (120, 120, 140))
        self.screen.blit(hint_text, (self.screen_width - 450, bar_y + 10))

    def _draw_save_dialog(self):
        """Draw save file dialog"""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 400, 150
        dialog_x = (self.screen_width - dialog_w) // 2
        dialog_y = (self.screen_height - dialog_h) // 2

        pygame.draw.rect(self.screen, (50, 55, 65),
                        (dialog_x, dialog_y, dialog_w, dialog_h))
        pygame.draw.rect(self.screen, (100, 105, 115),
                        (dialog_x, dialog_y, dialog_w, dialog_h), 2)

        # Title
        title = self.title_font.render("Save Level", True, (255, 255, 255))
        self.screen.blit(title, (dialog_x + 150, dialog_y + 15))

        # Input field
        pygame.draw.rect(self.screen, (30, 35, 45),
                        (dialog_x + 20, dialog_y + 60, dialog_w - 40, 35))
        pygame.draw.rect(self.screen, (100, 150, 200),
                        (dialog_x + 20, dialog_y + 60, dialog_w - 40, 35), 2)

        input_text = self.font.render(self.filename_input + "_", True, (255, 255, 255))
        self.screen.blit(input_text, (dialog_x + 30, dialog_y + 68))

        # Hint
        hint = self.font.render("Enter filename and press ENTER (ESC to cancel)",
                               True, (150, 150, 150))
        self.screen.blit(hint, (dialog_x + 45, dialog_y + 110))

    def _draw_load_dialog(self):
        """Draw load file dialog"""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 400, 300
        dialog_x = (self.screen_width - dialog_w) // 2
        dialog_y = (self.screen_height - dialog_h) // 2

        pygame.draw.rect(self.screen, (50, 55, 65),
                        (dialog_x, dialog_y, dialog_w, dialog_h))
        pygame.draw.rect(self.screen, (100, 105, 115),
                        (dialog_x, dialog_y, dialog_w, dialog_h), 2)

        # Title
        title = self.title_font.render("Load Level", True, (255, 255, 255))
        self.screen.blit(title, (dialog_x + 150, dialog_y + 15))

        # File list
        if self.available_files:
            for i, filename in enumerate(self.available_files[:8]):  # Show max 8
                y = dialog_y + 60 + i * 28

                if i == self.selected_element:
                    pygame.draw.rect(self.screen, (80, 85, 95),
                                   (dialog_x + 20, y - 2, dialog_w - 40, 26))
                    color = (255, 255, 100)
                else:
                    color = (200, 200, 200)

                text = self.font.render(filename, True, color)
                self.screen.blit(text, (dialog_x + 30, y))
        else:
            no_files = self.font.render("No saved levels found", True, (150, 150, 150))
            self.screen.blit(no_files, (dialog_x + 120, dialog_y + 120))

        # Hint
        hint = self.font.render("UP/DOWN: Select | ENTER: Load | ESC: Cancel",
                               True, (150, 150, 150))
        self.screen.blit(hint, (dialog_x + 55, dialog_y + 270))
