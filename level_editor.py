import pygame
import json
import os


class LevelEditor:
    # Game window dimensions (what the player sees during gameplay)
    GAME_WIDTH = 1200
    GAME_HEIGHT = 800

    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Tools available
        self.tools = [
            "platform", "spawn", "portal",
            "walker", "flyer", "spider", "blob",
            "taterbug", "chompy", "snake", "shriek", "delete"
        ]
        self.selected_tool = 0

        # Level data
        self.platforms = []
        self.monsters = []
        self.spawn_point = {"x": 100, "y": 650}
        self.portal_position = {"x": 560, "y": 10}  # Default top center
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
        self.tool_panel_width = 150
        self.tool_panel_collapsed = False
        self.collapsed_panel_width = 30
        self.status_bar_height = 40
        self._update_preview_rect()

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)

        # File browser state
        self.show_save_dialog = False
        self.show_load_dialog = False
        self.show_new_dialog = False
        self.filename_input = ""
        self.available_files = []
        self.load_scroll_offset = 0
        self.load_visible_items = 12  # Number of files visible at once

        # Monster editor state
        self.show_monster_editor = False
        self.editing_monster = None
        self.monster_editor_field = 0  # 0=patrol_range, 1=speed, 2=health

        # Track unsaved changes
        self.is_dirty = False
        self.current_filename = None
        self._last_saved_state = None

        # Ensure custom_levels directory exists
        if not os.path.exists("custom_levels"):
            os.makedirs("custom_levels")

    def _update_preview_rect(self):
        """Update preview rectangle based on panel state"""
        panel_width = self.collapsed_panel_width if self.tool_panel_collapsed else self.tool_panel_width
        self.preview_rect = pygame.Rect(0, 0, self.screen_width - panel_width,
                                         self.screen_height - self.status_bar_height)

    def update_screen(self, screen):
        """Update screen reference after resize"""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self._update_preview_rect()

    def _get_state_snapshot(self):
        """Get a snapshot of current state for dirty checking"""
        import copy
        return {
            "platforms": copy.deepcopy(self.platforms),
            "monsters": copy.deepcopy(self.monsters),
            "spawn_point": copy.deepcopy(self.spawn_point),
            "portal_position": copy.deepcopy(self.portal_position)
        }

    def _mark_dirty(self):
        """Mark the level as having unsaved changes"""
        self.is_dirty = True

    def _mark_clean(self):
        """Mark the level as saved"""
        self.is_dirty = False
        self._last_saved_state = self._get_state_snapshot()

    def reset(self):
        """Reset editor to blank level"""
        self.platforms = []
        self.monsters = []
        self.spawn_point = {"x": 100, "y": 650}
        self.portal_position = {"x": 560, "y": 10}
        self.background_color = [30, 35, 45]
        self.selected_element = None
        self.current_filename = None

        self._mark_clean()

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
        if self.show_save_dialog or self.show_load_dialog or self.show_new_dialog:
            return self._handle_dialog_event(event)
        if self.show_monster_editor:
            return self._handle_monster_editor_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_left_click(event.pos)
            elif event.button == 2:  # Middle click - edit monster
                self._open_monster_editor(event.pos)
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
        """Handle events in save/load/new dialogs"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_save_dialog = False
                self.show_load_dialog = False
                self.show_new_dialog = False
                self.filename_input = ""
                return None

            if self.show_save_dialog:
                if event.key == pygame.K_RETURN:
                    if self.filename_input:
                        self.save_level(self.filename_input)
                        self.show_save_dialog = False
                        self.filename_input = ""
                        # Check if there's a pending action after save
                        after_action = getattr(self, '_after_save_action', None)
                        self._after_save_action = None
                        if after_action == 'menu':
                            return "menu"
                        elif after_action == 'new':
                            self.reset()
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
                        self.load_scroll_offset = 0
                elif event.key == pygame.K_UP and self.available_files:
                    if self.selected_element is None:
                        self.selected_element = 0
                    else:
                        self.selected_element = (self.selected_element - 1) % len(self.available_files)
                    # Scroll up if selection is above visible area
                    if self.selected_element < self.load_scroll_offset:
                        self.load_scroll_offset = self.selected_element
                    # Handle wrap-around to bottom
                    elif self.selected_element == len(self.available_files) - 1:
                        self.load_scroll_offset = max(0, len(self.available_files) - self.load_visible_items)
                elif event.key == pygame.K_DOWN and self.available_files:
                    if self.selected_element is None:
                        self.selected_element = 0
                    else:
                        self.selected_element = (self.selected_element + 1) % len(self.available_files)
                    # Scroll down if selection is below visible area
                    if self.selected_element >= self.load_scroll_offset + self.load_visible_items:
                        self.load_scroll_offset = self.selected_element - self.load_visible_items + 1
                    # Handle wrap-around to top
                    elif self.selected_element == 0:
                        self.load_scroll_offset = 0

            elif self.show_new_dialog:
                if event.key == pygame.K_y:
                    # Save first
                    self.show_new_dialog = False
                    self.show_save_dialog = True
                    self.filename_input = self.current_filename or ""
                    self._after_save_action = getattr(self, '_pending_action', 'new')
                elif event.key == pygame.K_n:
                    # Discard changes
                    self.show_new_dialog = False
                    pending = getattr(self, '_pending_action', 'new')
                    self._pending_action = None
                    if pending == 'menu':
                        return "menu"
                    else:
                        self.reset()
                elif event.key == pygame.K_c:
                    # Cancel
                    self.show_new_dialog = False
                    self._pending_action = None

        return None

    def _handle_left_click(self, pos):
        """Handle left mouse click"""
        # Check if clicking the collapse/expand button
        panel_x = self.preview_rect.right
        if self.tool_panel_collapsed:
            # Check if clicking expand button
            if panel_x <= pos[0] <= panel_x + self.collapsed_panel_width:
                if 5 <= pos[1] <= 35:
                    self.tool_panel_collapsed = False
                    self._update_preview_rect()
                    return None
        else:
            # Check if clicking collapse button (top right of panel)
            if panel_x <= pos[0] <= panel_x + 25 and 5 <= pos[1] <= 25:
                self.tool_panel_collapsed = True
                self._update_preview_rect()
                return None
            # Check if clicking tool panel
            if pos[0] > panel_x:
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
            self._mark_dirty()
        elif tool == "portal":
            self.portal_position = {"x": snapped[0], "y": snapped[1]}
            self._mark_dirty()
        elif tool == "delete":
            self._delete_at(pos)
        elif tool in ["walker", "flyer", "spider", "blob", "taterbug", "chompy", "snake", "shriek"]:
            monster_data = {
                "type": tool,
                "x": snapped[0],
                "y": snapped[1],
                "patrol_range": 80,
                "speed": 2,
                "health": 3
            }
            # Snake and Shriek have additional aggro_duration property
            if tool in ["snake", "shriek"]:
                monster_data["aggro_duration"] = 180  # 3 seconds default
            self.monsters.append(monster_data)
            self._mark_dirty()

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
            self._mark_dirty()

        self.creating_platform = False
        self.platform_start = None

    def _select_tool(self, pos):
        """Select a tool from the panel"""
        panel_x = self.preview_rect.right
        relative_y = pos[1] - 45  # Match the y offset in _draw_tool_buttons

        if relative_y >= 0:
            tool_index = relative_y // 32  # Match the spacing in _draw_tool_buttons
            if 0 <= tool_index < len(self.tools):
                self.selected_tool = tool_index

    def _delete_at(self, pos):
        """Delete element at position"""
        # Check monsters
        for monster in self.monsters[:]:
            rect = pygame.Rect(monster["x"], monster["y"], 40, 40)
            if rect.collidepoint(pos):
                self.monsters.remove(monster)
                self._mark_dirty()
                return

        # Check platforms
        for platform in self.platforms[:]:
            rect = pygame.Rect(platform["x"], platform["y"],
                              platform["width"], platform["height"])
            if rect.collidepoint(pos):
                self.platforms.remove(platform)
                self._mark_dirty()
                return

    def _drag_element(self, pos):
        """Drag selected element"""
        pass  # Could implement dragging later

    def _find_monster_at(self, pos):
        """Find monster at given position, return monster dict or None"""
        for monster in self.monsters:
            rect = pygame.Rect(monster["x"], monster["y"], 40, 40)
            if rect.collidepoint(pos):
                return monster
        return None

    def _open_monster_editor(self, pos):
        """Open monster editor for monster at position"""
        monster = self._find_monster_at(pos)
        if monster:
            self.editing_monster = monster
            self.show_monster_editor = True
            self.monster_editor_field = 0

    def _get_monster_field_count(self):
        """Get number of editable fields for current monster"""
        if self.editing_monster and self.editing_monster.get("type") in ["snake", "shriek"]:
            return 4  # patrol_range, speed, health, aggro_duration
        return 3  # patrol_range, speed, health

    def _handle_monster_editor_event(self, event):
        """Handle events in monster editor dialog"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_monster_editor = False
                self.editing_monster = None
                return None

            if event.key == pygame.K_RETURN:
                self.show_monster_editor = False
                self.editing_monster = None
                return None

            field_count = self._get_monster_field_count()

            # Navigate fields with up/down
            if event.key == pygame.K_UP:
                self.monster_editor_field = (self.monster_editor_field - 1) % field_count
            elif event.key == pygame.K_DOWN or event.key == pygame.K_TAB:
                self.monster_editor_field = (self.monster_editor_field + 1) % field_count

            # Adjust values with left/right
            elif event.key == pygame.K_LEFT:
                self._adjust_monster_field(-1)
            elif event.key == pygame.K_RIGHT:
                self._adjust_monster_field(1)

            # Number input for direct value entry
            elif event.unicode.isdigit():
                self._set_monster_field_digit(int(event.unicode))

        return None

    def _adjust_monster_field(self, delta):
        """Adjust the currently selected monster field by delta"""
        if not self.editing_monster:
            return

        field_names = ["patrol_range", "speed", "health"]
        if self.editing_monster.get("type") in ["snake", "shriek"]:
            field_names.append("aggro_duration")

        if self.monster_editor_field >= len(field_names):
            return

        field = field_names[self.monster_editor_field]

        # Different increments for different fields
        if field == "patrol_range":
            increment = 10 * delta
            min_val, max_val = 0, 500
        elif field == "speed":
            increment = 1 * delta
            min_val, max_val = 1, 10
        elif field == "health":
            increment = 1 * delta
            min_val, max_val = 1, 50
        elif field == "aggro_duration":
            increment = 30 * delta  # 0.5 second increments
            min_val, max_val = 30, 600  # 0.5 to 10 seconds
        else:
            return

        new_val = self.editing_monster.get(field, min_val) + increment
        self.editing_monster[field] = max(min_val, min(max_val, new_val))
        self._mark_dirty()

    def _set_monster_field_digit(self, digit):
        """Set monster field based on digit input"""
        if not self.editing_monster:
            return

        field_names = ["patrol_range", "speed", "health"]
        if self.editing_monster.get("type") in ["snake", "shriek"]:
            field_names.append("aggro_duration")

        if self.monster_editor_field >= len(field_names):
            return

        field = field_names[self.monster_editor_field]
        current = self.editing_monster.get(field, 0)

        # Shift current value and add digit
        if field == "patrol_range":
            new_val = (current % 100) * 10 + digit
            new_val = min(500, new_val)
        elif field == "aggro_duration":
            new_val = (current % 100) * 10 + digit
            new_val = max(30, min(600, new_val))
        else:
            new_val = (current % 10) * 10 + digit
            if field == "speed":
                new_val = max(1, min(10, new_val))
            else:  # health
                new_val = max(1, min(50, new_val))

        self.editing_monster[field] = new_val
        self._mark_dirty()

    def _handle_keydown(self, event):
        """Handle keyboard input"""
        mods = pygame.key.get_mods()

        if event.key == pygame.K_ESCAPE:
            # Check for unsaved changes before exiting
            if self.is_dirty:
                self.show_new_dialog = True
                self._pending_action = "menu"
                return None
            return "menu"
        elif event.key == pygame.K_g:
            self.grid_snap = not self.grid_snap
        elif event.key == pygame.K_TAB:
            # Toggle tool panel
            self.tool_panel_collapsed = not self.tool_panel_collapsed
            self._update_preview_rect()
        elif event.key == pygame.K_n and mods & pygame.KMOD_CTRL:
            # New level - check for unsaved changes
            if self.is_dirty:
                self.show_new_dialog = True
            else:
                self.reset()
        elif event.key == pygame.K_s and mods & pygame.KMOD_CTRL:
            self.show_save_dialog = True
            self.filename_input = self.current_filename or ""
        elif event.key == pygame.K_o and mods & pygame.KMOD_CTRL:
            self.show_load_dialog = True
            self.selected_element = 0
            self.load_scroll_offset = 0
            self._refresh_file_list()
        elif event.key == pygame.K_p:
            return "test_play"
        elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
            tool_index = event.key - pygame.K_1
            if tool_index < len(self.tools):
                self.selected_tool = tool_index
        elif event.key == pygame.K_0:
            # 0 selects 10th tool
            if 9 < len(self.tools):
                self.selected_tool = 9

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
            "width": self.preview_rect.width,
            "height": self.screen_height,
            "background_color": self.background_color,
            "player_spawn": self.spawn_point,
            "portal_position": self.portal_position,
            "platforms": self.platforms,
            "monsters": self.monsters
        }

        filepath = f"custom_levels/{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=4)

        self.current_filename = filename
        self._mark_clean()

    def load_level(self, filename):
        """Load level from file"""
        filepath = f"custom_levels/{filename}.json"
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)

            self.platforms = data.get("platforms", [])
            self.monsters = data.get("monsters", [])
            self.spawn_point = data.get("player_spawn", {"x": 100, "y": 650})
            self.portal_position = data.get("portal_position", {"x": 560, "y": 10})
            self.background_color = data.get("background_color", [30, 35, 45])
            self.current_filename = filename
            self._mark_clean()

    def get_level_data(self):
        """Get current level as playable data"""
        return {
            "name": "Custom Level",
            "width": self.screen_width - self.tool_panel_width,
            "height": self.screen_height,
            "background_color": self.background_color,
            "player_spawn": self.spawn_point,
            "portal_position": self.portal_position,
            "platforms": self.platforms,
            "monsters": self.monsters
        }

    def draw(self):
        """Draw the level editor"""
        # Background
        self.screen.fill(tuple(self.background_color))

        # Draw grid only within game window bounds
        if self.grid_snap:
            grid_max_x = min(self.GAME_WIDTH, self.preview_rect.right)
            grid_max_y = min(self.GAME_HEIGHT, self.preview_rect.bottom)
            for x in range(0, grid_max_x + 1, self.grid_size):
                pygame.draw.line(self.screen, (50, 55, 65), (x, 0),
                                (x, grid_max_y), 1)
            for y in range(0, grid_max_y + 1, self.grid_size):
                pygame.draw.line(self.screen, (50, 55, 65), (0, y),
                                (grid_max_x, y), 1)

        # Draw game window boundary
        boundary_x = min(self.GAME_WIDTH, self.preview_rect.right)
        boundary_y = min(self.GAME_HEIGHT, self.preview_rect.bottom)
        pygame.draw.rect(self.screen, (100, 100, 120),
                        (0, 0, boundary_x, boundary_y), 2)

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

        # Draw portal indicator at custom position
        portal_x = self.portal_position["x"]
        portal_y = self.portal_position["y"]
        pygame.draw.rect(self.screen, (100, 200, 255), (portal_x, portal_y, 80, 60))
        pygame.draw.rect(self.screen, (255, 255, 255), (portal_x, portal_y, 80, 60), 2)
        portal_text = self.font.render("PORTAL", True, (255, 255, 255))
        self.screen.blit(portal_text, (portal_x + 10, portal_y + 20))

        # Draw monsters
        monster_colors = {
            "walker": (200, 50, 50),
            "flyer": (150, 50, 200),
            "spider": (40, 40, 40),
            "blob": (100, 200, 100),
            "taterbug": (80, 80, 90),
            "chompy": (200, 80, 80),
            "snake": (100, 180, 60),
            "shriek": (60, 20, 80)
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
        elif self.show_new_dialog:
            self._draw_new_dialog()
        elif self.show_monster_editor:
            self._draw_monster_editor()

    def _draw_tool_panel(self):
        """Draw the tool selection panel"""
        panel_x = self.preview_rect.right

        if self.tool_panel_collapsed:
            # Draw collapsed panel with expand button
            panel_width = self.collapsed_panel_width
            pygame.draw.rect(self.screen, (40, 45, 55),
                            (panel_x, 0, panel_width, self.screen_height))
            pygame.draw.line(self.screen, (80, 85, 95),
                            (panel_x, 0), (panel_x, self.screen_height), 2)

            # Expand button (arrow pointing left)
            btn_rect = pygame.Rect(panel_x + 3, 5, 24, 24)
            pygame.draw.rect(self.screen, (60, 65, 75), btn_rect)
            pygame.draw.rect(self.screen, (100, 105, 115), btn_rect, 1)
            # Draw arrow <<
            arrow_text = self.font.render("<<", True, (200, 200, 220))
            self.screen.blit(arrow_text, (panel_x + 5, 8))

            # Show current tool indicator vertically
            tool_colors = self._get_tool_colors()
            for i, tool in enumerate(self.tools):
                y = 40 + i * 25
                color = tool_colors.get(tool, (100, 100, 100))
                if i == self.selected_tool:
                    pygame.draw.rect(self.screen, (255, 255, 100),
                                   (panel_x + 5, y, 20, 20), 2)
                pygame.draw.rect(self.screen, color, (panel_x + 7, y + 2, 16, 16))
            return

        panel_width = self.tool_panel_width

        # Panel background
        pygame.draw.rect(self.screen, (40, 45, 55),
                        (panel_x, 0, panel_width, self.screen_height))
        pygame.draw.line(self.screen, (80, 85, 95),
                        (panel_x, 0), (panel_x, self.screen_height), 2)

        # Collapse button (arrow pointing right)
        btn_rect = pygame.Rect(panel_x + 3, 5, 20, 20)
        pygame.draw.rect(self.screen, (60, 65, 75), btn_rect)
        pygame.draw.rect(self.screen, (100, 105, 115), btn_rect, 1)
        arrow_text = self.small_font.render(">>", True, (200, 200, 220))
        self.screen.blit(arrow_text, (panel_x + 5, 7))

        # Title
        title = self.title_font.render("TOOLS", True, (200, 200, 220))
        self.screen.blit(title, (panel_x + 35, 15))

        # Tool buttons
        self._draw_tool_buttons(panel_x, panel_width)

    def _get_tool_colors(self):
        """Get color mapping for tools"""
        return {
            "platform": (100, 80, 60),
            "spawn": (50, 150, 255),
            "portal": (100, 200, 255),
            "walker": (200, 50, 50),
            "flyer": (150, 50, 200),
            "spider": (40, 40, 40),
            "blob": (100, 200, 100),
            "taterbug": (80, 80, 90),
            "chompy": (200, 80, 80),
            "snake": (100, 180, 60),
            "shriek": (60, 20, 80),
            "delete": (200, 50, 50)
        }

    def _draw_tool_buttons(self, panel_x, panel_width):
        """Draw tool buttons in expanded panel"""
        tool_colors = self._get_tool_colors()

        for i, tool in enumerate(self.tools):
            y = 45 + i * 32
            color = tool_colors.get(tool, (100, 100, 100))

            # Highlight selected
            if i == self.selected_tool:
                pygame.draw.rect(self.screen, (80, 85, 95),
                               (panel_x + 5, y - 2, panel_width - 10, 28))
                pygame.draw.rect(self.screen, (255, 255, 100),
                               (panel_x + 5, y - 2, panel_width - 10, 28), 2)

            # Tool color indicator
            pygame.draw.rect(self.screen, color, (panel_x + 10, y + 2, 18, 18))

            # Tool name
            text = self.small_font.render(tool.capitalize(), True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 33, y + 4))

            # Keyboard shortcut hint
            if i < 9:
                key_hint = self.small_font.render(str(i + 1), True, (100, 100, 120))
                self.screen.blit(key_hint, (panel_x + panel_width - 20, y + 4))
            elif i == 9:
                key_hint = self.small_font.render("0", True, (100, 100, 120))
                self.screen.blit(key_hint, (panel_x + panel_width - 20, y + 4))

    def _draw_status_bar(self):
        """Draw the status bar"""
        bar_y = self.screen_height - self.status_bar_height

        pygame.draw.rect(self.screen, (30, 35, 45),
                        (0, bar_y, self.screen_width, self.status_bar_height))
        pygame.draw.line(self.screen, (80, 85, 95),
                        (0, bar_y), (self.screen_width, bar_y), 2)

        # File name and dirty indicator
        filename_display = self.current_filename or "Untitled"
        if self.is_dirty:
            filename_display += " *"
            dirty_color = (255, 200, 100)
        else:
            dirty_color = (180, 180, 200)

        file_text = self.font.render(filename_display, True, dirty_color)
        self.screen.blit(file_text, (10, bar_y + 10))

        # Status text
        grid_status = "ON" if self.grid_snap else "OFF"
        status = f"Grid: {grid_status} | Platforms: {len(self.platforms)} | Monsters: {len(self.monsters)}"
        text = self.font.render(status, True, (180, 180, 200))
        self.screen.blit(text, (200, bar_y + 10))

        # Controls hint
        hint = "Ctrl+N: New | Ctrl+S: Save | Ctrl+O: Load | P: Test"
        hint_text = self.small_font.render(hint, True, (120, 120, 140))
        self.screen.blit(hint_text, (self.screen_width - 320, bar_y + 12))

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
        """Draw load file dialog with scrollable file list"""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Dialog box - taller to fit more files
        dialog_w, dialog_h = 400, 450
        dialog_x = (self.screen_width - dialog_w) // 2
        dialog_y = (self.screen_height - dialog_h) // 2

        pygame.draw.rect(self.screen, (50, 55, 65),
                        (dialog_x, dialog_y, dialog_w, dialog_h))
        pygame.draw.rect(self.screen, (100, 105, 115),
                        (dialog_x, dialog_y, dialog_w, dialog_h), 2)

        # Title
        title = self.title_font.render("Load Level", True, (255, 255, 255))
        self.screen.blit(title, (dialog_x + 150, dialog_y + 15))

        # File list with scrolling
        if self.available_files:
            # Get visible slice of files
            visible_files = self.available_files[self.load_scroll_offset:
                                                  self.load_scroll_offset + self.load_visible_items]

            for i, filename in enumerate(visible_files):
                actual_index = i + self.load_scroll_offset
                y = dialog_y + 60 + i * 28

                if actual_index == self.selected_element:
                    pygame.draw.rect(self.screen, (80, 85, 95),
                                   (dialog_x + 20, y - 2, dialog_w - 60, 26))
                    color = (255, 255, 100)
                else:
                    color = (200, 200, 200)

                text = self.font.render(filename, True, color)
                self.screen.blit(text, (dialog_x + 30, y))

            # Draw scroll indicators if needed
            total_files = len(self.available_files)
            if total_files > self.load_visible_items:
                # Scroll bar background
                scrollbar_x = dialog_x + dialog_w - 25
                scrollbar_y = dialog_y + 60
                scrollbar_h = self.load_visible_items * 28
                pygame.draw.rect(self.screen, (40, 45, 55),
                               (scrollbar_x, scrollbar_y, 10, scrollbar_h))

                # Scroll bar thumb
                thumb_h = max(20, scrollbar_h * self.load_visible_items // total_files)
                max_offset = total_files - self.load_visible_items
                if max_offset > 0:
                    thumb_y = scrollbar_y + (scrollbar_h - thumb_h) * self.load_scroll_offset // max_offset
                else:
                    thumb_y = scrollbar_y
                pygame.draw.rect(self.screen, (100, 105, 115),
                               (scrollbar_x, thumb_y, 10, thumb_h))

                # Show file count
                count_text = self.small_font.render(f"{total_files} files", True, (150, 150, 150))
                self.screen.blit(count_text, (dialog_x + dialog_w - 60, dialog_y + 420))
        else:
            no_files = self.font.render("No saved levels found", True, (150, 150, 150))
            self.screen.blit(no_files, (dialog_x + 120, dialog_y + 200))

        # Hint
        hint = self.font.render("UP/DOWN: Select | ENTER: Load | ESC: Cancel",
                               True, (150, 150, 150))
        self.screen.blit(hint, (dialog_x + 55, dialog_y + 420))

    def _draw_new_dialog(self):
        """Draw unsaved changes confirmation dialog"""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 450, 180
        dialog_x = (self.screen_width - dialog_w) // 2
        dialog_y = (self.screen_height - dialog_h) // 2

        pygame.draw.rect(self.screen, (50, 55, 65),
                        (dialog_x, dialog_y, dialog_w, dialog_h))
        pygame.draw.rect(self.screen, (255, 200, 100),
                        (dialog_x, dialog_y, dialog_w, dialog_h), 2)

        # Warning icon area
        pygame.draw.rect(self.screen, (80, 60, 30),
                        (dialog_x, dialog_y, 60, dialog_h))

        # Warning symbol
        warning_text = self.title_font.render("!", True, (255, 200, 100))
        self.screen.blit(warning_text, (dialog_x + 23, dialog_y + 70))

        # Title
        title = self.title_font.render("Unsaved Changes", True, (255, 200, 100))
        self.screen.blit(title, (dialog_x + 80, dialog_y + 20))

        # Message
        msg1 = self.font.render("You have unsaved changes.", True, (200, 200, 200))
        msg2 = self.font.render("Do you want to save before continuing?", True, (200, 200, 200))
        self.screen.blit(msg1, (dialog_x + 80, dialog_y + 60))
        self.screen.blit(msg2, (dialog_x + 80, dialog_y + 85))

        # Buttons
        btn_y = dialog_y + 130

        # Yes button
        pygame.draw.rect(self.screen, (60, 120, 60), (dialog_x + 80, btn_y, 100, 30))
        pygame.draw.rect(self.screen, (100, 180, 100), (dialog_x + 80, btn_y, 100, 30), 2)
        yes_text = self.font.render("(Y)es Save", True, (255, 255, 255))
        self.screen.blit(yes_text, (dialog_x + 90, btn_y + 6))

        # No button
        pygame.draw.rect(self.screen, (120, 60, 60), (dialog_x + 195, btn_y, 100, 30))
        pygame.draw.rect(self.screen, (180, 100, 100), (dialog_x + 195, btn_y, 100, 30), 2)
        no_text = self.font.render("(N)o Discard", True, (255, 255, 255))
        self.screen.blit(no_text, (dialog_x + 200, btn_y + 6))

        # Cancel button
        pygame.draw.rect(self.screen, (60, 60, 80), (dialog_x + 310, btn_y, 100, 30))
        pygame.draw.rect(self.screen, (100, 100, 140), (dialog_x + 310, btn_y, 100, 30), 2)
        cancel_text = self.font.render("(C)ancel", True, (255, 255, 255))
        self.screen.blit(cancel_text, (dialog_x + 330, btn_y + 6))

    def _draw_monster_editor(self):
        """Draw monster editor dialog"""
        if not self.editing_monster:
            return

        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Field definitions - base fields for all monsters
        fields = [
            ("Patrol Range", "patrol_range", 0, 500),
            ("Speed", "speed", 1, 10),
            ("Health", "health", 1, 50)
        ]

        # Add aggro_duration field for Snake and Shriek
        has_aggro = self.editing_monster.get("type") in ["snake", "shriek"]
        if has_aggro:
            fields.append(("Aggro Duration", "aggro_duration", 30, 600))

        # Dialog box - taller for monsters with aggro
        dialog_w = 350
        dialog_h = 265 if has_aggro else 220
        dialog_x = (self.screen_width - dialog_w) // 2
        dialog_y = (self.screen_height - dialog_h) // 2

        pygame.draw.rect(self.screen, (50, 55, 65),
                        (dialog_x, dialog_y, dialog_w, dialog_h))
        pygame.draw.rect(self.screen, (100, 150, 200),
                        (dialog_x, dialog_y, dialog_w, dialog_h), 2)

        # Title with monster type
        monster_type = self.editing_monster["type"].capitalize()
        title = self.title_font.render(f"Edit {monster_type}", True, (255, 255, 255))
        self.screen.blit(title, (dialog_x + 20, dialog_y + 15))

        # Draw fields
        for i, (label, key, min_val, max_val) in enumerate(fields):
            y = dialog_y + 60 + i * 45
            is_selected = (i == self.monster_editor_field)

            # Highlight selected field
            if is_selected:
                pygame.draw.rect(self.screen, (70, 75, 85),
                               (dialog_x + 15, y - 5, dialog_w - 30, 40))
                pygame.draw.rect(self.screen, (100, 150, 200),
                               (dialog_x + 15, y - 5, dialog_w - 30, 40), 2)

            # Label - show seconds for aggro_duration
            display_label = label
            if key == "aggro_duration":
                display_label = "Aggro (frames)"
            label_color = (255, 255, 100) if is_selected else (200, 200, 200)
            label_text = self.font.render(display_label, True, label_color)
            self.screen.blit(label_text, (dialog_x + 25, y + 5))

            # Value with arrows
            value = self.editing_monster.get(key, min_val)
            # Show seconds equivalent for aggro_duration
            if key == "aggro_duration":
                value_str = f"{value} ({value/60:.1f}s)"
            else:
                value_str = str(value)

            # Left arrow
            arrow_color = (150, 150, 150) if is_selected else (80, 80, 80)
            left_arrow = self.font.render("<", True, arrow_color)
            self.screen.blit(left_arrow, (dialog_x + 200, y + 5))

            # Value
            value_text = self.font.render(value_str, True, (255, 255, 255))
            value_x = dialog_x + 250 - value_text.get_width() // 2
            self.screen.blit(value_text, (value_x, y + 5))

            # Right arrow
            right_arrow = self.font.render(">", True, arrow_color)
            self.screen.blit(right_arrow, (dialog_x + 310, y + 5))

        # Hint - position at bottom of dialog
        hint = self.small_font.render("UP/DOWN: Select | LEFT/RIGHT: Adjust | ENTER: Done",
                                      True, (150, 150, 150))
        self.screen.blit(hint, (dialog_x + 25, dialog_y + dialog_h - 30))
