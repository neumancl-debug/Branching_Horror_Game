"""Procedural Victorian horror artwork and shared UI styling.

All artwork is drawn with Pygame, so the game has no external images, fonts,
downloads, or asset paths to manage. Fonts use a platform fallback list and then
Pygame's bundled default. Decorative textures are built once, not every frame.
"""

import math
import random

import pygame

INK = (232, 224, 203)
MUTED = (147, 158, 148)
GOLD = (197, 158, 92)
RED = (184, 82, 71)
BACKGROUND = (12, 20, 20)
PANEL = (20, 29, 28)
EDGE = (61, 74, 65)


def load_fonts() -> dict[int, pygame.font.Font]:
    """Use readable body text and serif headings, with portable fallbacks."""
    body = pygame.font.match_font("trebuchetms,dejavusans,liberationsans")
    heading = pygame.font.match_font("georgia,dejavuserif,liberationserif")
    sizes = (12, 13, 14, 16, 18, 20, 24, 28, 30, 34, 38, 40, 46, 58, 72)
    return {size: pygame.font.Font(heading if size >= 24 else body, size) for size in sizes}


def make_background(size: tuple[int, int]) -> pygame.Surface:
    """Cache a subtle paper grain and an ink-green vertical gradient."""
    surface = pygame.Surface(size)
    width, height = size
    for y in range(height):
        fade = y / height
        pygame.draw.line(
            surface,
            (int(22 - fade * 12), int(33 - fade * 14), int(30 - fade * 10)),
            (0, y),
            (width, y),
        )
    rng = random.Random(1874)
    for _ in range(4500):
        x, y = rng.randrange(width), rng.randrange(height)
        color = surface.get_at((x, y))
        delta = rng.choice((-4, -2, 2, 4))
        surface.set_at((x, y), tuple(max(0, channel + delta) for channel in color[:3]))
    pygame.draw.rect(surface, (49, 63, 53), (15, 15, width - 30, height - 30), 1)
    pygame.draw.line(surface, GOLD, (35, 15), (120, 15))
    pygame.draw.line(surface, GOLD, (width - 120, height - 16), (width - 35, height - 16))
    return surface


def panel(
    surface: pygame.Surface,
    bounds: pygame.Rect | tuple[int, int, int, int],
    fill: tuple[int, int, int] = PANEL,
    edge: tuple[int, int, int] = EDGE,
) -> None:
    """Draw a clipped-corner panel with small brass corner details."""
    rect = pygame.Rect(bounds)
    cut = 8
    points = [
        (rect.left + cut, rect.top),
        (rect.right - cut, rect.top),
        (rect.right, rect.top + cut),
        (rect.right, rect.bottom - cut),
        (rect.right - cut, rect.bottom),
        (rect.left + cut, rect.bottom),
        (rect.left, rect.bottom - cut),
        (rect.left, rect.top + cut),
    ]
    pygame.draw.polygon(surface, fill, points)
    pygame.draw.polygon(surface, edge, points, 1)
    for x, y, dx, dy in (
        (rect.left + 5, rect.top + 5, 1, 1),
        (rect.right - 5, rect.bottom - 5, -1, -1),
    ):
        pygame.draw.line(surface, edge, (x, y), (x + dx * 15, y))
        pygame.draw.line(surface, edge, (x, y), (x, y + dy * 15))


def seal(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int = 16,
    color: tuple[int, int, int] = GOLD,
) -> None:
    """Draw the estate's geometric thorn-and-diamond crest."""
    x, y = center
    pygame.draw.polygon(
        surface,
        color,
        [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)],
        1,
    )
    pygame.draw.line(surface, color, (x, y - radius + 5), (x, y + radius - 5))
    for offset in (-5, 3):
        pygame.draw.line(surface, color, (x, y + offset), (x - 5, y + offset - 4))
        pygame.draw.line(surface, color, (x, y + offset + 4), (x + 5, y + offset))


def manor(surface: pygame.Surface, bounds: pygame.Rect, time: float = 0.0) -> None:
    """Draw an original estate silhouette, moon, rain, and drifting ground mist."""
    art = pygame.Surface(bounds.size, pygame.SRCALPHA)
    width, height = bounds.size
    moon = (int(width * 0.74), int(height * 0.24))
    for radius in range(65, 27, -6):
        pygame.draw.circle(art, (162, 172, 145, 5), moon, radius)
    pygame.draw.circle(art, (153, 168, 149, 150), moon, 28)
    base = int(height * 0.80)
    left, right = int(width * 0.17), int(width * 0.84)
    roof = int(height * 0.40)
    pygame.draw.rect(art, (8, 16, 18), (left, roof + 30, right - left, base - roof))
    pygame.draw.polygon(
        art,
        (8, 16, 18),
        [
            (left - 17, roof + 35),
            (int(width * 0.37), roof - 31),
            (int(width * 0.55), roof + 35),
        ],
    )
    tower = int(width * 0.62)
    pygame.draw.rect(art, (8, 16, 18), (tower - 27, roof - 36, 54, base - roof + 36))
    pygame.draw.polygon(
        art,
        (8, 16, 18),
        [
            (tower - 37, roof - 35),
            (tower, roof - 90),
            (tower + 37, roof - 35),
        ],
    )
    pygame.draw.line(art, (59, 73, 64), (tower, roof - 91), (tower, roof - 112), 2)
    for column in range(5):
        x = left + 24 + column * max(24, (right - left - 40) // 5)
        for row in range(2):
            y = roof + 52 + row * 49
            glow = (170, 119, 57, 150) if (column + row) % 4 == 0 else (54, 78, 72, 150)
            pygame.draw.rect(
                art, glow, (x, y, 15, 26), border_top_left_radius=7, border_top_right_radius=7
            )
            pygame.draw.line(art, (8, 16, 18), (x + 7, y), (x + 7, y + 26), 2)
    pygame.draw.rect(art, (4, 10, 13), (int(width * 0.46), base - 48, 27, 57))
    # Bare branches frame the house without requiring a bitmap background.
    for side in (0, width):
        sign = 1 if side == 0 else -1
        trunk = side + sign * 20
        pygame.draw.line(art, (20, 35, 32), (trunk, height), (trunk + sign * 17, 8), 9)
        for i in range(5):
            y = 50 + i * 37
            end = (trunk + sign * (65 + (i % 2) * 24), y - 43)
            pygame.draw.line(art, (20, 35, 32), (trunk, y + 40), end, 3)
            pygame.draw.line(art, (20, 35, 32), end, (end[0] + sign * 26, end[1] + 4), 2)
    for i in range(5):
        drift = int(math.sin(time * 0.15 + i) * 17)
        pygame.draw.ellipse(
            art, (88, 121, 108, 12), (-40 + drift + i * 33, base + i * 8, width, 32)
        )
    for i in range(45):
        x = (i * 83 - int(time * 22)) % width
        y = (i * 47 + int(time * 115)) % height
        pygame.draw.line(art, (106, 130, 123, 35), (x, y), (x - 4, y + 15))
    surface.blit(art, bounds)


def portrait(
    surface: pygame.Surface,
    center: tuple[int, int],
    color: tuple[int, int, int],
    name: str,
) -> None:
    """Draw a small, stylized survivor bust with a distinct identifying detail."""
    x, y = center
    dark = tuple(int(channel * 0.35) for channel in color)
    pygame.draw.circle(surface, (28, 40, 36), (x, y), 37)
    pygame.draw.circle(surface, (62, 73, 60), (x, y), 37, 1)
    pygame.draw.polygon(
        surface, dark, [(x - 28, y + 27), (x - 20, y + 5), (x + 20, y + 5), (x + 28, y + 27)]
    )
    pygame.draw.polygon(surface, color, [(x - 9, y + 4), (x, y + 21), (x + 10, y + 4), (x, y + 8)])
    pygame.draw.ellipse(surface, (159, 144, 118), (x - 12, y - 23, 24, 32))
    pygame.draw.arc(surface, (29, 33, 30), (x - 14, y - 26, 28, 29), 0, math.pi, 8)
    pygame.draw.line(surface, (106, 91, 74), (x + 5, y - 12), (x + 5, y + 1), 2)
    if name == "Evelyn":
        for dx in (-6, 6):
            pygame.draw.circle(surface, (62, 70, 61), (x + dx, y - 9), 5, 1)
        pygame.draw.line(surface, (62, 70, 61), (x - 1, y - 9), (x + 1, y - 9))
    elif name == "Noah":
        pygame.draw.line(surface, GOLD, (x - 12, y - 17), (x + 12, y - 17), 4)
    elif name == "Sofia":
        pygame.draw.arc(surface, dark, (x - 18, y - 28, 36, 43), 0, math.pi, 6)
    else:
        pygame.draw.line(surface, color, (x - 12, y - 17), (x + 12, y - 17), 3)
