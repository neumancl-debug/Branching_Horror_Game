"""Pygame presentation, input, and main loop for The Hollow at Blackthorn.

Story rules live in story.py. Map positions are local to the world surface;
buttons use logical canvas coordinates. The canvas scales to fit the window,
and mouse positions are converted back to those same logical coordinates.
"""

import argparse
import math
import os
import random
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from story import CHARACTERS, MAX_THREAT, SCENES, GameState
from ui import (
    EDGE,
    GOLD,
    INK,
    MUTED,
    PANEL,
    RED,
    load_fonts,
    make_background,
    manor,
    panel,
    portrait,
    seal,
)

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 820
WORLD_RECT = pygame.Rect(30, 130, 740, 460)
Color = tuple[int, int, int]
Point = tuple[float, float] | pygame.Vector2
UIAction = tuple[str, str | int | None]
TARGET_FPS = 60
MAX_FRAME_SECONDS = 0.05  # Cap movement after a stall or window drag.
PLAYER_SPEED = 190  # Map pixels per second, independent of frame rate.
PLAYER_RADIUS = 11
INTERACTION_RADIUS = 85
PLAYER_SPAWN = (355, 395)

# Furniture uses map-local coordinates, just like the scene interaction markers.
SCENE_OBSTACLES = {
    "road": ((170, 260, 180, 90),),
    "hall": ((105, 155, 110, 40), (500, 60, 145, 80)),
    "dining": ((245, 165, 225, 125),),
    "basement": ((90, 140, 150, 35), (495, 135, 125, 45)),
    "yard": ((95, 285, 110, 60),),
}


class Game:
    """Coordinate UI state, movement, rendering, and one story-state instance.

    ``mode`` is title, play, or ending. During play, a result modal, journal, or
    pause screen blocks decisions and movement. Drawing rebuilds the clickable
    button list for the current screen, including only the topmost overlay.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        """Create rendering surfaces and begin on character selection."""
        self.screen = screen
        self.canvas = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.world = pygame.Surface(WORLD_RECT.size)
        self.fonts = load_fonts()
        self.background = make_background((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True
        self.selected = "Evelyn"
        self.state = GameState(self.selected)
        self.mode = "title"
        self.modal = None
        self.journal = False
        self.paused = False
        self.player = pygame.Vector2(PLAYER_SPAWN)
        self.time = 0.0
        self.buttons = []
        self.rng = random.Random(350)  # Repeatable rain layout for visual checks.
        self.rain = [
            (self.rng.randrange(740), self.rng.randrange(460), self.rng.randrange(100, 260))
            for _ in range(80)
        ]

    def text(
        self,
        text: str,
        x: float,
        y: float,
        size: int = 18,
        color: Color = INK,
        surface: pygame.Surface | None = None,
    ) -> None:
        """Draw one line on the canvas, or on a supplied map surface."""
        surface = surface if surface is not None else self.canvas
        surface.blit(self.fonts[size].render(text, True, color), (x, y))

    def wrap(
        self,
        text: str,
        x: float,
        y: float,
        width: int,
        size: int = 18,
        color: Color = INK,
        line_height: int | None = None,
        surface: pygame.Surface | None = None,
    ) -> float:
        """Word-wrap paragraphs and return the y position below the final line."""
        line_height = line_height or size + 7
        for paragraph in text.split("\n"):
            line = ""
            for word in paragraph.split():
                candidate = f"{line} {word}".strip()
                if self.fonts[size].size(candidate)[0] > width and line:
                    self.text(line, x, y, size, color, surface)
                    y += line_height
                    line = word
                else:
                    line = candidate
            self.text(line, x, y, size, color, surface)
            y += line_height
        return y

    def mouse(self, point: Point) -> tuple[float, float]:
        """Map window coordinates to the fixed canvas, including letterboxing."""
        sw, sh = self.screen.get_size()
        scale = min(sw / WINDOW_WIDTH, sh / WINDOW_HEIGHT)
        return (
            (point[0] - (sw - WINDOW_WIDTH * scale) / 2) / scale,
            (point[1] - (sh - WINDOW_HEIGHT * scale) / 2) / scale,
        )

    def label(self, text: str, x: int, y: int, color: Color = GOLD) -> None:
        """Draw a small uppercase section label with generous letter spacing."""
        for character in text.upper():
            glyph = self.fonts[12].render(character, True, color)
            self.canvas.blit(glyph, (x, y))
            x += glyph.get_width() + 2

    def rule(self, x: int, y: int, width: int) -> None:
        """Separate sections with a fine brass-and-ink rule."""
        pygame.draw.line(self.canvas, EDGE, (x, y), (x + width, y))
        pygame.draw.line(self.canvas, GOLD, (x, y), (x + 28, y))

    def button(
        self,
        rect: tuple[int, int, int, int] | pygame.Rect,
        label: str,
        action: UIAction,
        enabled: bool = True,
        accent: bool = False,
    ) -> None:
        """Draw a button and register its hit area for the next input event."""
        rect = pygame.Rect(rect)
        hover = rect.collidepoint(self.mouse(pygame.mouse.get_pos()))
        highlighted = enabled and (hover or accent)
        fill = (40, 48, 38) if highlighted else PANEL if enabled else (17, 24, 24)
        edge = GOLD if highlighted else EDGE if enabled else (37, 47, 41)
        panel(self.canvas, rect, fill, edge)
        text_y = rect.y + (rect.height - self.fonts[16].get_height()) // 2
        text_color = INK if enabled else (107, 118, 108)
        if action[0] == "choice":
            number = str(action[1] + 1)
            badge = pygame.Rect(rect.x + 7, rect.y + 5, 26, rect.height - 10)
            pygame.draw.rect(self.canvas, (54, 57, 42) if highlighted else (28, 39, 34), badge)
            self.text(number if enabled else "-", badge.x + 8, text_y, 14, edge)
            clean_label = label.split("  ", 1)[1].replace("  [done]", "")
            self.text(clean_label, rect.x + 47, text_y, 16, text_color)
            self.text(
                "USED" if not enabled else ">",
                rect.right - (48 if not enabled else 27),
                text_y + 2,
                12,
                edge,
            )
        else:
            if highlighted:
                pygame.draw.line(
                    self.canvas, GOLD, (rect.x + 8, rect.y + 12), (rect.x + 8, rect.bottom - 12), 2
                )
            self.text(label, rect.x + 20, text_y, 16, text_color)
        self.buttons.append((rect, action, enabled))

    def start(self) -> None:
        """Start a fresh run with the selected survivor and clear overlays."""
        self.state = GameState(self.selected)
        self.mode = "play"
        self.modal = None
        self.journal = self.paused = False
        self.player.update(PLAYER_SPAWN)

    def choose(self, index: int) -> None:
        """Convert a visible action index into a story decision and result modal."""
        if self.mode != "play" or self.modal or self.paused or self.journal or self.state.ending:
            return
        actions = SCENES[self.state.scene].actions
        if 0 <= index < len(actions):
            result = self.state.choose(actions[index].id)
            if result:
                self.modal = result

    def continue_result(self) -> None:
        """Dismiss a result before committing its ending or scene transition."""
        if self.modal is None:
            return
        self.modal = None
        if self.state.ending:
            self.mode = "ending"
        elif self.state.pending_scene:
            self.state.enter_pending()
            self.player.update(PLAYER_SPAWN)

    def handle(self, event: pygame.event.Event) -> None:
        """Route discrete keyboard and mouse events according to UI priority."""
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            key = event.key
            if self.mode == "title":
                if pygame.K_1 <= key <= pygame.K_4:
                    self.selected = list(CHARACTERS)[key - pygame.K_1]
                elif key == pygame.K_RETURN:
                    self.start()
                elif key == pygame.K_ESCAPE:
                    self.running = False
            elif self.mode == "ending":
                if key in (pygame.K_RETURN, pygame.K_r):
                    self.mode = "title"
                elif key == pygame.K_ESCAPE:
                    self.running = False
            elif self.modal:
                if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self.continue_result()
            elif key == pygame.K_j:
                self.journal = not self.journal
            elif key in (pygame.K_ESCAPE, pygame.K_p):
                if self.journal:
                    self.journal = False
                else:
                    self.paused = not self.paused
            elif not self.paused and not self.journal:
                if pygame.K_1 <= key <= pygame.K_4:
                    self.choose(key - pygame.K_1)
                elif key == pygame.K_e:
                    index = self.nearest()
                    if index is not None:
                        self.choose(index)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            point = self.mouse(event.pos)
            for rect, action, enabled in reversed(self.buttons):
                if rect.collidepoint(point) and enabled:
                    self.activate(action)
                    break

    def activate(self, action: UIAction) -> None:
        """Apply a named UI command stored with a clicked button."""
        kind, value = action
        if kind == "select" and isinstance(value, str):
            self.selected = value
        elif kind == "start":
            self.start()
        elif kind == "choice" and isinstance(value, int):
            self.choose(value)
        elif kind == "continue":
            self.continue_result()
        elif kind == "journal":
            self.journal = not self.journal
        elif kind == "resume":
            self.paused = False
        elif kind == "title":
            self.mode = "title"
            self.modal = None
            self.journal = self.paused = False
        elif kind == "quit":
            self.running = False

    def nearest(self) -> int | None:
        """Return the closest unused action index within interaction range."""
        candidates = [
            (self.player.distance_to(a.position), i)
            for i, a in enumerate(SCENES[self.state.scene].actions)
            if a.id not in self.state.used
        ]
        if candidates:
            distance, index = min(candidates)
            if distance < INTERACTION_RADIUS:
                return index
        return None

    def blockers(self) -> list[pygame.Rect]:
        """Return solid furniture rectangles for the active scene."""
        return [pygame.Rect(bounds) for bounds in SCENE_OBSTACLES[self.state.scene]]

    def update(self, dt: float) -> None:
        """Advance rain animation and move the player using elapsed seconds."""
        self.time += dt
        if self.mode != "play" or self.modal or self.journal or self.paused:
            return
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN])
            - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if direction.length_squared():
            direction = direction.normalize()
            step = direction * PLAYER_SPEED * dt
            obstacles = self.blockers()
            # Resolve each axis independently so the player slides along furniture.
            for axis in (0, 1):
                test = self.player.copy()
                test[axis] += step[axis]
                body = pygame.Rect(
                    test.x - PLAYER_RADIUS,
                    test.y - PLAYER_RADIUS,
                    PLAYER_RADIUS * 2,
                    PLAYER_RADIUS * 2,
                )
                if not any(body.colliderect(rect) for rect in obstacles):
                    self.player = test
            self.player.x = max(22, min(718, self.player.x))
            self.player.y = max(26, min(432, self.player.y))

    def draw_world(self) -> None:
        """Draw scene furniture, lighting, interaction markers, and characters."""
        world_surface = self.world
        scene = self.state.scene
        outside = scene in ("road", "yard")
        world_surface.fill((25, 34, 33) if outside else (37, 35, 32))
        if outside:
            for i in range(90):
                x, y = (i * 137 + 19) % 740, (i * 73 + 31) % 460
                pygame.draw.line(world_surface, (35, 45, 39), (x, y), (x + 8, y - 9), 2)
        else:
            for y in range(0, 460, 36):
                pygame.draw.line(world_surface, (47, 43, 38), (0, y), (740, y))
                for x in range((y // 36 % 2) * 70, 740, 140):
                    pygame.draw.line(world_surface, (47, 43, 38), (x, y), (x, y + 36))
            pygame.draw.rect(world_surface, (69, 63, 54), (6, 6, 728, 448), 10)
        if scene == "road":
            pygame.draw.polygon(
                world_surface, (43, 47, 44), [(115, 460), (370, 460), (640, 100), (520, 95)]
            )
            for x in (26, 76, 675, 715):
                pygame.draw.rect(world_surface, (15, 24, 23), (x, 0, 14, 455))
                pygame.draw.circle(world_surface, (18, 29, 26), (x + 7, 50), 57)
            pygame.draw.rect(world_surface, (76, 89, 85), (170, 260, 180, 90), border_radius=20)
            pygame.draw.rect(world_surface, (23, 41, 45), (220, 269, 70, 72), border_radius=5)
            pygame.draw.polygon(
                world_surface, (76, 74, 51), [(345, 275), (510, 205), (510, 390), (345, 335)]
            )
            self.text("BLACKTHORN", 516, 65, 18, MUTED, world_surface)
        elif scene == "hall":
            pygame.draw.rect(world_surface, (70, 43, 42), (300, 40, 110, 410))
            for y in range(60, 150, 15):
                pygame.draw.rect(world_surface, (100, 89, 72), (500, y, 145, 10))
            pygame.draw.rect(world_surface, (76, 60, 46), (105, 155, 110, 40))
            pygame.draw.rect(world_surface, (106, 83, 56), (117, 45, 85, 85), 5)
            pygame.draw.line(world_surface, (119, 66, 57), (126, 55), (188, 116), 5)
            pygame.draw.circle(world_surface, (131, 115, 76), (355, 165), 40, 3)
            for x in (330, 355, 380):
                pygame.draw.circle(world_surface, GOLD, (x, 165), 4)
        elif scene == "dining":
            pygame.draw.rect(world_surface, (90, 68, 49), (245, 165, 225, 125), border_radius=12)
            for x in range(265, 465, 36):
                for y in (182, 268):
                    pygame.draw.circle(world_surface, (160, 152, 125), (x, y), 10, 2)
            for x in (280, 350, 420):
                pygame.draw.circle(world_surface, GOLD, (x, 226), 3)
            pygame.draw.rect(world_surface, (54, 73, 75), (555, 50, 80, 85))
            pygame.draw.line(world_surface, (105, 97, 77), (595, 50), (595, 135), 7)
            pygame.draw.rect(world_surface, (22, 25, 24), (95, 50, 105, 85))
        elif scene == "basement":
            for x in (30, 55, 675):
                pygame.draw.line(world_surface, (82, 82, 68), (x, 0), (x, 460), 7)
            pygame.draw.rect(world_surface, (88, 70, 50), (90, 140, 150, 35))
            pygame.draw.rect(world_surface, (81, 89, 82), (495, 135, 125, 45))
            for i, color in enumerate((RED, GOLD, MUTED)):
                pygame.draw.line(world_surface, color, (520 + i * 25, 142), (520 + i * 25, 173), 3)
            pygame.draw.rect(world_surface, (9, 16, 19), (560, 390, 100, 70))
        else:
            for x in range(500, 680, 18):
                pygame.draw.line(world_surface, (107, 117, 109), (x, 30), (x, 150), 5)
            for y in (55, 120):
                pygame.draw.line(world_surface, (107, 117, 109), (500, y), (675, y), 5)
            for x in (120, 175):
                pygame.draw.circle(world_surface, (67, 66, 53), (x, 315), 27)
                pygame.draw.circle(world_surface, (110, 100, 73), (x, 315), 27, 2)
            pygame.draw.line(world_surface, (149, 124, 81), (350, 0), (350, 162), 4)
            self.person(world_surface, (590, 390), (29, 25, 27), True)
        self.draw_scene_details()
        # A dark overlay pools around the player; a flashlight widens visibility.
        shade = pygame.Surface(WORLD_RECT.size, pygame.SRCALPHA)
        shade.fill((0, 4, 10, 125))
        radius = 225 if "Flashlight" in self.state.inventory else 145
        for r in range(radius, 15, -10):
            alpha = int(115 * (1 - r / radius))
            pygame.draw.circle(shade, (0, 4, 9, 110 - alpha), self.player, r)
        world_surface.blit(shade, (0, 0))
        near = self.nearest()
        for i, action in enumerate(SCENES[scene].actions):
            done = action.id in self.state.used
            point = action.position
            color = (78, 91, 79) if done else GOLD if i == near else (167, 176, 147)
            if i == near:
                pulse = 25 + int(math.sin(self.time * 2) * 2)
                pygame.draw.circle(world_surface, (73, 79, 52), point, pulse, 1)
            pygame.draw.circle(world_surface, (12, 23, 23), point, 16)
            pygame.draw.circle(world_surface, color, point, 16, 1)
            pygame.draw.line(
                world_surface, color, (point[0] - 23, point[1]), (point[0] - 18, point[1])
            )
            pygame.draw.line(
                world_surface, color, (point[0] + 18, point[1]), (point[0] + 23, point[1])
            )
            self.text(
                "-" if done else str(i + 1), point[0] - 5, point[1] - 10, 16, color, world_surface
            )
        self.person(world_surface, self.player, CHARACTERS[self.state.character].color)
        if outside:
            for x, y, speed in self.rain:
                yy = int((y + self.time * speed) % 480) - 10
                xx = int((x - self.time * 40) % 760)
                pygame.draw.line(world_surface, (83, 103, 110), (xx, yy), (xx - 4, yy + 12))
        self.canvas.blit(world_surface, WORLD_RECT)
        pygame.draw.rect(self.canvas, EDGE, WORLD_RECT, 1)
        for x, y, dx, dy in ((30, 130, 1, 1), (770, 590, -1, -1)):
            pygame.draw.line(self.canvas, GOLD, (x, y), (x + 32 * dx, y))
            pygame.draw.line(self.canvas, GOLD, (x, y), (x, y + 24 * dy))

    def draw_scene_details(self) -> None:
        """Add visual story cues without changing collision or interaction rules."""
        surface = self.world
        scene = self.state.scene
        if scene == "road":
            for x in (193, 302):
                for y in (253, 344):
                    pygame.draw.rect(surface, (10, 18, 20), (x, y, 28, 12), border_radius=3)
            pygame.draw.line(surface, (155, 168, 145), (175, 306), (343, 306))
            for i in range(7):
                pygame.draw.ellipse(surface, (21, 29, 27), (418 + i * 17, 352 - i * 24, 6, 11))
            for x in range(535, 676, 21):
                pygame.draw.line(surface, (73, 88, 76), (x, 67), (x, 130), 3)
        elif scene == "hall":
            pygame.draw.rect(surface, (123, 93, 62), (307, 46, 96, 400), 1)
            pygame.draw.rect(surface, (85, 55, 45), (313, 52, 84, 388), 1)
            pygame.draw.polygon(
                surface, (198, 185, 145), [(145, 163), (169, 165), (168, 185), (144, 181)]
            )
            for y in (169, 174, 179):
                pygame.draw.line(surface, (99, 87, 65), (149, y), (163, y + 1))
            for x in (330, 355, 380):
                pygame.draw.line(surface, (142, 117, 71), (x, 145), (x, 161), 2)
                pygame.draw.ellipse(surface, (230, 188, 101), (x - 2, 138, 5, 9))
            pygame.draw.line(surface, (109, 88, 58), (355, 115), (355, 16), 2)
            for i in range(6):
                pygame.draw.ellipse(surface, (27, 28, 25), (450 + i * 13, 340 - i * 27, 6, 11))
        elif scene == "dining":
            for x in range(264, 456, 46):
                for y in (142, 301):
                    pygame.draw.rect(surface, (47, 40, 32), (x, y, 28, 17), border_radius=3)
                    pygame.draw.line(surface, (105, 80, 52), (x, y), (x + 28, y))
            pygame.draw.rect(surface, (99, 53, 41), (342, 195, 25, 60))
            pygame.draw.rect(surface, GOLD, (345, 198, 19, 54), 1)
            for x in range(306, 335, 6):
                pygame.draw.line(surface, (153, 133, 96), (x, 242), (x + 8, 252))
            pygame.draw.line(surface, (133, 152, 145), (566, 62), (581, 91), 2)
        elif scene == "basement":
            pygame.draw.rect(surface, (183, 166, 122), (135, 145, 37, 23))
            pygame.draw.line(surface, (83, 82, 59), (153, 146), (153, 167))
            for x in (140, 158):
                for y in (151, 156, 161):
                    pygame.draw.line(surface, (100, 98, 71), (x, y), (x + 9, y))
            pygame.draw.circle(
                surface, GOLD if self.state.gate_override_disabled else RED, (604, 148), 3
            )
            for x in range(560, 650, 17):
                pygame.draw.line(surface, (83, 85, 67), (x, 360), (x + 9, 369), 2)
        else:
            for x in (70, 224, 460, 694):
                pygame.draw.rect(surface, (66, 73, 60), (x, 20, 18, 105))
                pygame.draw.polygon(surface, (80, 85, 67), [(x - 4, 20), (x + 9, 5), (x + 23, 20)])
            for y in (304, 322):
                for x in (120, 175):
                    pygame.draw.line(surface, (115, 106, 77), (x - 22, y), (x + 22, y), 2)
            pygame.draw.line(surface, (93, 96, 74), (350, 33), (593, 369), 1)

    @staticmethod
    def person(surface: pygame.Surface, point: Point, color: Color, killer: bool = False) -> None:
        """Draw a simple top-down survivor or masked killer sprite."""
        x, y = int(point[0]), int(point[1])
        pygame.draw.ellipse(surface, (9, 15, 17), (x - 17, y + 9, 34, 13))
        pygame.draw.circle(surface, color, (x, y), 15)
        pygame.draw.circle(surface, (194, 192, 166) if killer else (181, 163, 134), (x, y - 7), 9)
        if killer:
            for dx in (-4, 4):
                pygame.draw.circle(surface, (20, 24, 24), (x + dx, y - 8), 2)
            pygame.draw.line(surface, (150, 160, 152), (x + 17, y + 3), (x + 27, y + 19), 4)

    def draw_title(self) -> None:
        """Draw the four character cards and the start button."""
        manor(self.canvas, pygame.Rect(730, 22, 420, 290), self.time)
        self.label("BLACKTHORN ESTATE  /  A SURVIVAL TALE", 64, 43)
        self.text("THE HOLLOW", 58, 70, 72)
        self.text("AT BLACKTHORN", 64, 155, 34, GOLD)
        self.wrap(
            "Four friends. A stalled car. A house that is listening.\nSome doors should stay closed.",
            66,
            214,
            650,
            18,
            MUTED,
            line_height=26,
        )
        self.rule(64, 291, 1070)
        self.label("CHOOSE YOUR SURVIVOR", 64, 306)
        self.text("01 - 04  /  EACH STRENGTH OPENS A DIFFERENT WAY", 715, 306, 12, MUTED)
        mouse = self.mouse(pygame.mouse.get_pos())
        for i, (name, character) in enumerate(CHARACTERS.items()):
            color = character.color
            rect = pygame.Rect(62 + i * 280, 335, 260, 296)
            selected = name == self.selected
            panel(
                self.canvas,
                rect,
                (29, 39, 33) if selected else PANEL,
                GOLD if selected else color if rect.collidepoint(mouse) else EDGE,
            )
            self.label(f"SURVIVOR 0{i + 1}", rect.x + 20, 354, color)
            portrait(self.canvas, (rect.right - 53, 405), color, name)
            self.text(name, rect.x + 20, 390, 28, INK)
            self.text(character.role, rect.x + 20, 430, 12, GOLD)
            y = self.wrap(character.biography, rect.x + 20, 466, 220, 16, line_height=21)
            self.wrap(character.traits, rect.x + 20, y + 13, 220, 13, MUTED, line_height=18)
            if selected:
                pygame.draw.line(self.canvas, GOLD, (rect.x + 20, 618), (rect.x + 64, 618), 2)
                self.text("SELECTED", rect.right - 84, 606, 12, GOLD)
            self.buttons.append((rect, ("select", name), True))
        self.button(
            (62, 661, 340, 54), "ENTER THE ESTATE     [Enter]", ("start", None), accent=True
        )
        seal(self.canvas, (452, 687), 15)
        self.text(
            "Read the room. Trust your instincts. Every decision matters.", 485, 677, 16, MUTED
        )
        self.rule(64, 744, 1070)
        self.text(
            "WASD  Move     E  Interact     1-4  Choose     J  Journal     Esc  Pause",
            64,
            762,
            14,
            MUTED,
        )
        self.label("TAKE YOUR TIME. THE HOUSE CAN WAIT.", 790, 765, MUTED)

    def draw_play(self) -> None:
        """Draw the map, scene text, inventory, threat meter, and action list."""
        state = self.state
        scene = SCENES[state.scene]
        self.label("THE HOLLOW  /  BLACKTHORN ESTATE", 32, 26)
        chapter, _, title = scene.title.partition(" / ")
        self.text(title.title(), 30, 50, 34)
        self.text(scene.subtitle, 32, 101, 16, MUTED)
        panel(self.canvas, (790, 24, 378, 91))
        self.text(str(state.decisions), 811, 29, 46, GOLD)
        self.label("DECISIONS", 861, 43)
        self.text(f"of {scene.decisions} in this scene", 861, 68, 12, MUTED)
        self.label("THREAT", 1015, 38, RED if state.threat >= 4 else MUTED)
        for i in range(MAX_THREAT):
            pygame.draw.rect(
                self.canvas,
                RED if i < state.threat else (43, 53, 45),
                (1015 + i * 22, 62, 15, 8),
            )
        self.text(
            "CLOSING IN" if state.threat >= 4 else "LISTENING" if state.threat else "UNSEEN",
            1015,
            82,
            12,
            RED if state.threat >= 4 else MUTED,
        )
        self.draw_world()
        panel(self.canvas, (790, 130, 378, 657))
        self.label(f"CHAPTER {chapter}  /  FIELD OBSERVATIONS", 812, 151)
        self.rule(812, 179, 334)
        self.wrap(scene.description, 812, 198, 333, 18, line_height=25)
        self.rule(812, 477, 334)
        self.label("CARRIED WITH YOU", 812, 497)
        x, y = 812, 528
        if not state.inventory:
            self.text("Empty pockets. Keep your eyes open.", x, y, 14, MUTED)
        for item in sorted(state.inventory):
            width = self.fonts[14].size(item)[0] + 22
            if x + width > 1146:
                x, y = 812, y + 31
            pygame.draw.rect(self.canvas, (29, 40, 34), (x, y, width, 25), border_radius=3)
            self.text(item, x + 11, y + 4, 14, INK)
            x += width + 7
        if state.gate_override_disabled:
            self.text("GATE OVERRIDE DISABLED", 812, y + 38, 12, GOLD)
        self.rule(812, 636, 334)
        character = CHARACTERS[state.character]
        portrait(self.canvas, (842, 674), character.color, state.character)
        self.text(state.character, 892, 645, 24)
        self.text(character.role, 892, 680, 12, MUTED)
        self.button(
            (812, 721, 334, 42),
            f"OPEN JOURNAL  /  {len(state.clues)} clues     [J]",
            ("journal", None),
        )
        near = self.nearest()
        self.label("WHAT WILL YOU DO?", 32, 606)
        self.text("1-4 or click  /  walking costs nothing", 452, 603, 13, MUTED)
        for i, action in enumerate(scene.actions):
            enabled = action.id not in state.used
            self.button(
                (30, 630 + 40 * i, 740, 34),
                f"{i + 1}  {action.label}" + ("  [done]" if not enabled else ""),
                ("choice", i),
                enabled,
                i == near,
            )
        if near is not None:
            panel(self.canvas, (WORLD_RECT.x + 12, WORLD_RECT.y + 12, 716, 62), edge=GOLD)
            self.wrap(
                "[E]  " + scene.actions[near].hint,
                WORLD_RECT.x + 27,
                WORLD_RECT.y + 25,
                682,
                16,
                INK,
                line_height=21,
            )

    def overlay(self, title: str, text: str, button_label: str, action: UIAction) -> None:
        """Dim the play screen and replace its hit areas with one modal button."""
        veil = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        veil.fill((3, 9, 12, 218))
        self.canvas.blit(veil, (0, 0))
        panel(self.canvas, (190, 196, 820, 426), edge=GOLD)
        seal(self.canvas, (233, 238), 16, RED if self.state.ending else GOLD)
        self.label("BLACKTHORN  /  A MOMENT IN THE DARK", 265, 228, MUTED)
        self.text(title.title(), 230, 268, 30, GOLD)
        self.rule(230, 316, 736)
        self.wrap(text, 230, 340, 730, 18, line_height=27)
        self.buttons.clear()
        self.button((230, 550, 736, 44), button_label, action, accent=True)

    def draw_journal(self) -> None:
        """Display learned clues without spending a story decision."""
        veil = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        veil.fill((2, 8, 12, 225))
        self.canvas.blit(veil, (0, 0))
        paper, ink, faded = (187, 182, 151), (44, 56, 47), (91, 91, 66)
        panel(self.canvas, (124, 62, 952, 700), paper, GOLD)
        self.label("PRIVATE RECORD  /  BLACKTHORN ESTATE", 164, 97, faded)
        self.text("Collected testimony", 162, 123, 40, ink)
        self.text(f"{len(self.state.clues):02} CLUES", 908, 99, 18, faded)
        pygame.draw.line(self.canvas, (137, 137, 107), (164, 185), (1034, 185))
        pygame.draw.line(self.canvas, (156, 151, 119), (194, 209), (194, 670))
        y = 210
        if not self.state.clues:
            self.wrap(
                "No testimony yet. Look for the things someone left behind.",
                218,
                y + 26,
                770,
                20,
                faded,
            )
        for index, (name, clue) in enumerate(self.state.clues.items()):
            pygame.draw.circle(self.canvas, paper, (194, y + 10), 11)
            pygame.draw.circle(self.canvas, faded, (194, y + 10), 11, 1)
            self.text(str(index + 1), 190, y + 1, 13, faded)
            self.label(name.replace("_", " "), 220, y, faded)
            y = self.wrap(clue, 220, y + 25, 786, 18, ink, line_height=25) + 23
        self.buttons.clear()
        self.button((164, 700, 872, 43), "CLOSE THE JOURNAL     [J / Esc]", ("journal", None))

    def draw_ending(self) -> None:
        """Display the final outcome and offer replay or quit."""
        won = self.state.survived
        color = GOLD if won else RED
        manor(self.canvas, pygame.Rect(765, 28, 360, 280), self.time)
        seal(self.canvas, (111, 105), 22, color)
        self.label("DAWN BREAKS" if won else "THE ESTATE CLAIMS ANOTHER", 154, 99, color)
        self.wrap(self.state.ending.title(), 88, 157, 1020, 40, INK, line_height=54)
        panel(self.canvas, (90, 281, 1020, 245), edge=color)
        self.label("THE LAST PAGE", 120, 305, color)
        self.wrap(self.state.ending_text, 120, 345, 954, 20, line_height=31)
        self.label(
            f"{self.state.character}  /  {self.state.actions_taken} decisions  /  {len(self.state.clues)} clues",
            122,
            492,
            MUTED,
        )
        self.button(
            (90, 569, 485, 55), "CHOOSE ANOTHER SURVIVOR     [Enter]", ("title", None), accent=True
        )
        self.button((601, 569, 180, 55), "QUIT", ("quit", None))
        self.rule(90, 720, 1020)
        self.text(
            "Another survivor. Another choice. Another way through the dark.", 90, 742, 16, MUTED
        )

    def draw(self) -> None:
        """Render the active screen and scale it to the current window size."""
        self.canvas.blit(self.background, (0, 0))
        self.buttons.clear()
        if self.mode == "title":
            self.draw_title()
        elif self.mode == "ending":
            self.draw_ending()
        else:
            self.draw_play()
            if self.modal:
                self.overlay(
                    "THE CONSEQUENCE", self.modal, "CONTINUE   [Enter / Space]", ("continue", None)
                )
            elif self.journal:
                self.draw_journal()
            elif self.paused:
                self.overlay(
                    "PAUSED",
                    "Every attempted action costs a decision, including a failed attempt. Walking and reading your journal are free. Used actions cannot be repeated.\n\nThe killer advances through decisions, not elapsed time.",
                    "RESUME   [Esc / P]",
                    ("resume", None),
                )
                self.button((730, 634, 275, 42), "RETURN TO TITLE", ("title", None))
        sw, sh = self.screen.get_size()
        scale = min(sw / WINDOW_WIDTH, sh / WINDOW_HEIGHT)
        size = (max(1, int(WINDOW_WIDTH * scale)), max(1, int(WINDOW_HEIGHT * scale)))
        self.screen.fill((5, 9, 12))
        self.screen.blit(
            pygame.transform.smoothscale(self.canvas, size),
            ((sw - size[0]) // 2, (sh - size[1]) // 2),
        )
        pygame.display.flip()


def smoke_test(game: Game, screenshot: Path | None) -> None:
    """Exercise the actual renderer and input handlers without opening a window."""
    game.draw()
    game.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert game.mode == "play"
    game.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
    assert "Flashlight" in game.state.inventory and game.modal
    game.draw()
    game.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    for scene in SCENES:
        game.state.scene = scene
        game.state.decisions = SCENES[scene].decisions
        game.state.used.clear()
        game.draw()
    game.journal = True
    game.draw()
    game.journal = False
    game.paused = True
    game.draw()
    game.paused = False
    game.state.scene = "hall"
    game.state.decisions = 2
    game.state.used.clear()
    game.state.clues["stairs"] = "He hears the stairs. Do not use them when the house is quiet."
    game.draw()
    if screenshot:
        pygame.image.save(game.canvas, screenshot)
    game.state.finish("THE TRUTH GETS OUT", "You escaped with the evidence.")
    game.mode = "ending"
    game.draw()
    print(
        "Smoke test passed: menu, keyboard actions, results, all five scenes, journal, pause, ending."
    )


def main() -> None:
    """Parse command-line options, initialize Pygame, and run at a capped FPS."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    try:
        pygame.display.init()
        pygame.font.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("The Hollow at Blackthorn | CIS350 Prototype")
        game = Game(screen)
        if args.smoke_test:
            smoke_test(game, args.screenshot)
        else:
            clock = pygame.time.Clock()
            game.draw()
            while game.running:
                dt = min(clock.tick(TARGET_FPS) / 1000, MAX_FRAME_SECONDS)
                for event in pygame.event.get():
                    game.handle(event)
                    # Refresh hit areas after each event so two queued clicks
                    # cannot activate controls from different screens.
                    if game.running and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        game.draw()
                game.update(dt)
                game.draw()
    finally:
        # Release the display even if initialization or an unexpected rule fails.
        pygame.quit()


if __name__ == "__main__":
    main()
