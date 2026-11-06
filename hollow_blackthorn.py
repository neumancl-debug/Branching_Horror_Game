
"""
THE HOLLOW AT BLACKTHORN
A mouse-driven, 2D point-and-click horror adventure.

Requirements:
    Python 3.10+
    pygame 2.5+

Run:
    python -m pip install pygame
    python hollow_blackthorn.py
"""
import sys
from pathlib import Path
import pygame
import math

pygame.init()
pygame.display.set_caption("The Hollow at Blackthorn")

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets"

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    AUDIO_ENABLED = True
except pygame.error:
    AUDIO_ENABLED = False

# ----------------------------- Display / palette -----------------------------
W, H = 1280, 800
FPS = 60
SCREEN = pygame.display.set_mode((W, H))
CLOCK = pygame.time.Clock()

INK = (5, 11, 18)
PANEL = (7, 19, 29)
PANEL2 = (10, 28, 40)
LINE = (37, 111, 139)
CYAN = (95, 210, 239)
PALE = (208, 228, 238)
MUTED = (130, 163, 180)
RED = (194, 63, 67)
GOLD = (207, 167, 103)
GREEN = (91, 202, 162)
WHITE = (241, 244, 239)
DARK = (4, 10, 17)

FONT = pygame.font.SysFont("consolas", 17)
SMALL = pygame.font.SysFont("consolas", 14)
TINY = pygame.font.SysFont("consolas", 12)
TITLE = pygame.font.SysFont("consolas", 25, bold=True)
BIG = pygame.font.SysFont("consolas", 34, bold=True)

# Layout
HEADER_H = 48
SCENE_RECT = pygame.Rect(250, 58, 780, 570)
SIDEBAR = pygame.Rect(16, 58, 218, 570)
NARRATIVE = pygame.Rect(1046, 58, 218, 570)
BOTTOM = pygame.Rect(16, 642, 1248, 142)
POPUP_RECT = pygame.Rect(460, 455, 360, 120)
MAP_POPUP_RECT = pygame.Rect(132, 70, 1016, 660)

# ----------------------------- Assets ----------------------------------------
SCENE_IMAGES = {}
SCENE_FILES = {
    "road": "road.png",
    "hall": "hall.png",
    "dining": "dining.png",
    "study": "study.png",
    "basement": "basement.png",
    "yard": "yard.png",
    "landing": "landing.png",
    "nursery": "nursery.png",
    "greenhouse": "greenhouse.png",
    "chapel": "chapel.png",
    "crypt": "crypt.png",
}
for key, filename in SCENE_FILES.items():
    try:
        img = pygame.image.load(str(ASSET_DIR / filename)).convert()
        SCENE_IMAGES[key] = pygame.transform.smoothscale(img, SCENE_RECT.size)
    except (pygame.error, FileNotFoundError):
        pass

MAP_IMAGE = None
try:
    MAP_IMAGE = pygame.image.load(str(ASSET_DIR / "estate_map.png")).convert_alpha()
except (pygame.error, FileNotFoundError):
    pass

MAP_NODE_RECTS = {
    "road": (46, 806, 262, 158),
    "dining": (262, 610, 248, 134),
    "hall": (574, 550, 242, 163),
    "study": (886, 610, 238, 130),
    "basement": (569, 820, 228, 147),
    "crypt": (948, 832, 248, 150),
    "landing": (560, 370, 243, 142),
    "nursery": (868, 386, 229, 130),
    "yard": (557, 188, 252, 122),
    "greenhouse": (171, 162, 241, 135),
    "chapel": (1082, 166, 259, 142),
}
MAP_LABELS = {
    "road": "Road", "hall": "Entrance Hall", "dining": "Dining Room", "study": "Study",
    "basement": "Basement", "yard": "Yard", "landing": "Upper Landing", "nursery": "Nursery",
    "greenhouse": "Greenhouse", "chapel": "Chapel", "crypt": "Crypt",
}

PORTRAITS = {}  # Populated after the character definitions below.

KILLER_IMAGE = None
try:
    KILLER_IMAGE = pygame.image.load(str(ASSET_DIR / "the_watcher.png")).convert_alpha()
except (pygame.error, FileNotFoundError):
    pass

ITEM_IMAGES = {}
ITEM_ICON_FILES = {
    "Flashlight": "item_flashlight.png", "Victim's Note": "item_victim_s_note.png",
    "Kitchen Knife": "item_kitchen_knife.png", "Small Screwdriver": "item_small_screwdriver.png",
    "Maintenance Log": "item_maintenance_log.png", "Brass Key": "item_brass_key.png",
    "Bolt Cutters": "item_bolt_cutters.png", "Bandage": "item_bandage.png",
    "Silver Locket": "item_silver_locket.png", "Ritual Page": "item_ritual_page.png",
    "Garden Shears": "item_garden_shears.png", "Chapel Candle": "item_chapel_candle.png",
}
for item_name, filename in ITEM_ICON_FILES.items():
    try:
        ITEM_IMAGES[item_name] = pygame.image.load(str(ASSET_DIR / filename)).convert_alpha()
    except (pygame.error, FileNotFoundError):
        pass

# Position and scale in each original scene illustration, in local scene pixels.
KILLER_PLACEMENTS = {
    "road": (600, 126, 115, 235),
    "hall": (365, 148, 133, 259),
    "dining": (480, 110, 141, 276),
    "study": (292, 140, 154, 304),
    "basement": (360, 127, 178, 346),
    "yard": (515, 137, 145, 290),
    "landing": (396, 145, 132, 286),
    "nursery": (492, 136, 148, 312),
    "greenhouse": (466, 145, 136, 295),
    "chapel": (528, 112, 138, 300),
    "crypt": (520, 126, 145, 314),
}

# Each room has its own 20-second seamless-style ambience loop. Two dedicated
# mixer channels crossfade between rooms; interaction sounds play separately.
AMBIENCE_FILES = {
    "road": "road_ambience.wav",
    "hall": "hall_ambience.wav",
    "dining": "dining_ambience.wav",
    "study": "study_ambience.wav",
    "basement": "basement_ambience.wav",
    "yard": "yard_ambience.wav",
    "landing": "landing_ambience.wav",
    "nursery": "nursery_ambience.wav",
    "greenhouse": "greenhouse_ambience.wav",
    "chapel": "chapel_ambience.wav",
    "crypt": "crypt_ambience.wav",
}

SFX = {}
AMBIENCE = {}
MUSIC_BED = None
if AUDIO_ENABLED:
    pygame.mixer.set_num_channels(max(8, pygame.mixer.get_num_channels()))
    try:
        SFX["click"] = pygame.mixer.Sound(str(ASSET_DIR / "interact.wav"))
        SFX["click"].set_volume(0.35)
    except (pygame.error, FileNotFoundError):
        pass

    try:
        # Retain the original low background drone underneath the new room sounds.
        MUSIC_BED = pygame.mixer.Sound(str(ASSET_DIR / "ambient_drone.wav"))
    except (pygame.error, FileNotFoundError):
        pass

    for room, filename in AMBIENCE_FILES.items():
        try:
            AMBIENCE[room] = pygame.mixer.Sound(str(ASSET_DIR / filename))
        except (pygame.error, FileNotFoundError):
            # Missing ambience files do not stop the game from running.
            pass


class SceneAudio:
    """Crossfade distinct looped room ambience with independent SFX channels."""

    FADE_SECONDS = 1.8
    VOLUME = 0.67

    def __init__(self):
        self.enabled = AUDIO_ENABLED
        self.channels = [pygame.mixer.Channel(4), pygame.mixer.Channel(5)] if self.enabled else []
        self.music_channel = pygame.mixer.Channel(6) if self.enabled else None
        self.active_slot = None
        self.fading_slot = None
        self.active_scene = None
        self.fade_elapsed = 0.0
        self.muted = False

    def enter(self, scene):
        if not self.enabled or scene == self.active_scene:
            return
        sound = AMBIENCE.get(scene)
        if self.music_channel is not None and MUSIC_BED is not None and not self.music_channel.get_busy():
            self.music_channel.set_volume(0.0 if self.muted else 0.095)
            self.music_channel.play(MUSIC_BED, loops=-1)
        if sound is None:
            self.stop()
            return

        next_slot = 0 if self.active_slot is None else 1 - self.active_slot
        self.fading_slot = self.active_slot
        self.active_slot = next_slot
        self.active_scene = scene
        self.fade_elapsed = 0.0
        channel = self.channels[next_slot]
        channel.stop()
        channel.set_volume(0.0)
        channel.play(sound, loops=-1)

        # For a fresh game, start the first room gently instead of abruptly.
        if self.fading_slot is None:
            self.fade_elapsed = 0.0

    def update(self, seconds):
        if self.active_slot is None:
            return
        self.fade_elapsed = min(self.FADE_SECONDS, self.fade_elapsed + seconds)
        amount = self.fade_elapsed / self.FADE_SECONDS
        target_volume = 0.0 if self.muted else self.VOLUME
        if self.music_channel is not None:
            self.music_channel.set_volume(0.0 if self.muted else 0.095)
        self.channels[self.active_slot].set_volume(target_volume * amount)
        if self.fading_slot is not None:
            other = self.channels[self.fading_slot]
            other.set_volume(target_volume * (1.0 - amount))
            if amount >= 1.0:
                other.stop()
                self.fading_slot = None

    def toggle_mute(self):
        self.muted = not self.muted
        # Apply the change immediately, including to sound being crossfaded.
        self.update(0.0)

    def stop(self):
        for channel in self.channels:
            channel.stop()
        if self.music_channel is not None:
            self.music_channel.stop()
        self.active_slot = None
        self.fading_slot = None
        self.active_scene = None
        self.fade_elapsed = 0.0


SCENE_AUDIO = SceneAudio()


def play_sfx(name="click"):
    if AUDIO_ENABLED and name in SFX:
        SFX[name].play()

# ----------------------------- Game content ----------------------------------
CHARACTERS = {
    "Marcus": {
        "role": "THE ATHLETE",
        "traits": {"Strength": 3, "Perception": 1, "Stealth": 1, "Technical": 1},
        "bio": "Protective, competitive, and quick to act.",
        "special": "Force weak barriers and cross physical obstacles."
    },
    "Evelyn": {
        "role": "THE OBSERVER",
        "traits": {"Strength": 1, "Perception": 3, "Stealth": 2, "Technical": 1},
        "bio": "Analytical, skeptical, and prone to overthinking.",
        "special": "Spot hidden evidence and notice inconsistencies."
    },
    "Noah": {
        "role": "THE TECHNICIAN",
        "traits": {"Strength": 1, "Perception": 2, "Stealth": 1, "Technical": 3},
        "bio": "Practical, resourceful, and cautious.",
        "special": "Work with basic locks, panels, and mechanisms."
    },
    "Sofia": {
        "role": "THE SURVIVOR",
        "traits": {"Strength": 1, "Perception": 2, "Stealth": 3, "Technical": 1},
        "bio": "Independent, adaptable, and hard to frighten.",
        "special": "Move quietly and conceal herself under pressure."
    }
}

SCENES = {
    "road": {
        "title": "The Stranded Car",
        "number": 1,
        "limit": 3,
        "description": [
            "Rain lashes the windshield. The engine has died,",
            "and your phone has no signal. An iron gate hangs",
            "open beside a stone pillar marked BLACKTHORN.",
            " ",
            "Muddy footprints lead through the gate. Behind",
            "the car, a branch cracks in the darkness."
        ],
        "hotspots": [
            {"label": "Car", "rect": (20, 230, 280, 240), "hint": "The old sedan may still hide something useful.", "action": "glovebox"},
            {"label": "Footprints", "rect": (330, 355, 175, 190), "hint": "Bootprints lead from the road toward the estate.", "action": "tracks"},
            {"label": "Gate", "rect": (390, 138, 230, 220), "hint": "The Blackthorn gate stands open toward the mansion.", "action": "gate"},
            {"label": "Tree line", "rect": (0, 60, 250, 170), "hint": "The woods behind the car are very still.", "action": "listen"},
        ],
    },
    "hall": {
        "title": "The Entrance Hall",
        "number": 2,
        "limit": 2,
        "description": [
            "The front door swings inward before you touch it.",
            "Cold ash and wet plaster fill the air.",
            "A crooked chandelier taps softly overhead.",
            " ",
            "Muddy footprints stop near the staircase. A family",
            "portrait has been slashed. A folded note rests on",
            "the table beneath it."
        ],
        "hotspots": [
            {"label": "Double doors", "rect": (0, 120, 240, 260), "hint": "The double doors to the left lead deeper into the house.", "action": "dining"},
            {"label": "Staircase", "rect": (460, 115, 230, 380), "hint": "The staircase looks old, broad, and treacherously loud.", "action": "stairs"},
            {"label": "Portrait", "rect": (670, 30, 105, 268), "hint": "Someone slashed every face in the family portrait.", "action": "portrait"},
            {"label": "Note", "rect": (645, 360, 130, 155), "hint": "A folded note lies on the narrow table below the portrait.", "action": "read_note"},
        ],
    },
    "dining": {
        "title": "The Dining Room",
        "number": 3,
        "limit": 2,
        "description": [
            "Dusty plates line a table long enough to vanish",
            "into shadow. One chair is pulled back neatly.",
            "The pantry door stands slightly ajar.",
            " ",
            "A swollen window rattles in the rain. A message",
            "has been scratched into the tabletop."
        ],
        "hotspots": [
            {"label": "Pantry", "rect": (215, 95, 140, 200), "hint": "A warm crack of light spills from the pantry beyond.", "action": "pantry"},
            {"label": "Window", "rect": (580, 70, 185, 260), "hint": "Moonlight pours through the rain-streaked window.", "action": "window"},
            {"label": "Scratched message", "rect": (300, 320, 290, 150), "hint": "Fresh scratches mark the polished tabletop.", "action": "message"},
            {"label": "Sideboard", "rect": (0, 130, 265, 230), "hint": "A carved sideboard sits beneath an old portrait.", "action": "sideboard"},
        ],
    },
    "study": {
        "title": "The Study",
        "number": 4,
        "limit": 2,
        "description": [
            "The study smells of mildew and hot copper.",
            "A desk lamp burns over an open ledger.",
            "A fuse panel hangs open on the wall.",
            " ",
            "The floor near the bookcase is oddly clean, as if",
            "the shelf has been moved recently."
        ],
        "hotspots": [
            {"label": "Bookcase", "rect": (0, 0, 300, 520), "hint": "The heavy shelves are dense with books and dust.", "action": "bookcase"},
            {"label": "Desk ledger", "rect": (415, 300, 230, 105), "hint": "The open maintenance ledger is lit by a warm lamp.", "action": "ledger"},
            {"label": "Desk drawer", "rect": (515, 385, 235, 155), "hint": "A lower desk drawer is jammed partway open.", "action": "drawer"},
            {"label": "Fuse panel", "rect": (640, 100, 135, 190), "hint": "The exposed panel hums faintly behind loose wires.", "action": "panel"},
        ],
    },
    "basement": {
        "title": "The Basement",
        "number": 5,
        "limit": 2,
        "description": [
            "The cellar is wet and cold. Pipes tick behind the",
            "walls. A steel door stands on the left with a keypad.",
            "A generator judders on the right.",
            " ",
            "Tallies gouged into the brick suggest other people",
            "counted time here before you arrived."
        ],
        "hotspots": [
            {"label": "Steel door", "rect": (45, 135, 195, 245), "hint": "The steel door is rusted shut behind a keypad lock.", "action": "steeldoor"},
            {"label": "Tally marks", "rect": (330, 170, 175, 200), "hint": "Dozens of tally marks are scratched into the bricks.", "action": "tallies"},
            {"label": "Generator", "rect": (560, 235, 215, 260), "hint": "The generator coughs, rattles, and spits sparks.", "action": "generator"},
        ],
    },
    "yard": {
        "title": "The Rear Yard",
        "number": 6,
        "limit": 2,
        "description": [
            "Cold rain strikes a walled rear yard behind the",
            "estate. A chained service gate faces the tree line.",
            "A small shed leans against the wall.",
            " ",
            "Footprints crisscross the mud. Some lead to the",
            "gate. Others circle back toward the house."
        ],
        "hotspots": [
            {"label": "Shed", "rect": (0, 110, 240, 270), "hint": "The shed window glows faintly in the rain.", "action": "shed"},
            {"label": "Footprints", "rect": (220, 330, 245, 150), "hint": "Fresh and older tracks overlap in the muddy yard.", "action": "yard_tracks"},
            {"label": "Service gate", "rect": (600, 110, 175, 305), "hint": "The iron service gate is chained shut.", "action": "service_gate"},
        ],
    },
}



# Optional branches are actual locations, each with an illustrated background.
SCENES.update({
    "landing": {
        "title":"The Upper Landing", "number":7, "limit":3,
        "description":["The upper landing groans softly over the foyer below.", "Moonlight cuts through stained glass across the warped floorboards.", "A teddy-painted nursery door waits to the right.", "Every loose board threatens to carry your steps through the whole house."],
        "hotspots":[
            {"label":"Loose floorboard","rect":(500,385,240,125),"hint":"A broken section of floorboard flexes dangerously near the runner.","action":"landing_floor"},
            {"label":"Banister","rect":(160,170,315,315),"hint":"The railing overlooks the entrance hall below.","action":"landing_rail"},
            {"label":"Linen cabinet","rect":(555,220,155,185),"hint":"A cobwebbed cabinet sits beneath the family portrait.","action":"landing_cabinet"},
            {"label":"Nursery door","rect":(642,95,132,338),"hint":"A worn child's door marked with a teddy bear leads into the nursery.","action":"landing_door"},
        ]
    },
    "nursery": {
        "title":"The Locked Nursery", "number":8, "limit":3,
        "description":["Moonlight settles over a nursery left exactly as someone abandoned it.","The lace canopy over the crib stirs though no breeze reaches the room.","A child's diary rests on the writing desk.","An open music box glitters on the lace table by the window."],
        "hotspots":[
            {"label":"Canopy cradle","rect":(282,140,250,255),"hint":"An ornate crib rests beneath a decayed lace canopy.","action":"nursery_cradle"},
            {"label":"Child's diary","rect":(0,298,240,182),"hint":"A faded diary lies closed on the writing desk.","action":"nursery_diary"},
            {"label":"Music box","rect":(610,295,150,170),"hint":"An open gilded music box waits on the lace table.","action":"nursery_music"},
            {"label":"Moonlit window","rect":(480,55,225,270),"hint":"The window overlooks the roof and inner garden.","action":"nursery_window"},
        ]
    },
    "greenhouse": {
        "title":"The Glass Conservatory", "number":9, "limit":3,
        "description":["The conservatory glass sweats with rain and moonlit condensation.","Roots have burst through the paving stones around the central bed.","A workbench glows by lantern light beneath the mansion windows.","On the right, the heating pipes rattle around a shattered exit."],
        "hotspots":[
            {"label":"Workbench","rect":(0,286,308,250),"hint":"Rusted tools lie across the lantern-lit workbench.","action":"greenhouse_tools"},
            {"label":"Heating pipes","rect":(605,100,160,355),"hint":"The greenhouse heating pipes strain and hiss beside the boiler.","action":"greenhouse_heat"},
            {"label":"Broken glass","rect":(480,105,170,255),"hint":"Broken glazing and the torn roof suggest a desperate escape route.","action":"greenhouse_glass"},
            {"label":"Strange roots","rect":(260,132,250,345),"hint":"The roots have wrapped themselves around a carved stone base.","action":"greenhouse_roots"},
        ]
    },
    "chapel": {
        "title":"The Ruined Chapel", "number":10, "limit":4,
        "description":["The estate chapel opens in cold moonlight and guttering candlefire.","Broken stained glass frames the manor beyond the altar.","A bell rope hangs beside the right archway.","An old prayer book waits on a carved lectern."],
        "hotspots":[
            {"label":"Stone altar","rect":(290,248,250,220),"hint":"An old altar bears a circular silver indentation.","action":"chapel_altar"},
            {"label":"Candles","rect":(15,248,185,188),"hint":"A bank of guttering candles burns on the side table.","action":"chapel_candle"},
            {"label":"Bell rope","rect":(622,58,118,230),"hint":"A torn bell rope hangs beside the archway.","action":"chapel_bell"},
            {"label":"Prayer book","rect":(574,255,180,162),"hint":"A weathered prayer book rests open on the lectern.","action":"chapel_prayer"},
        ]
    },
    "crypt": {
        "title":"The Family Crypt", "number":11, "limit":3,
        "description":["A stone effigy sleeps atop the family sarcophagus.","A ritual table lies in the candlelit dark to one side.","Names of the dead cover the wall beside the gate.","An ancient seal mechanism is set into the far stonework."],
        "hotspots":[
            {"label":"Stone coffin","rect":(350,210,300,250),"hint":"A heavy lid bears the family coat of arms.","action":"crypt_coffin"},
            {"label":"Ritual manuscript","rect":(10,360,220,155),"hint":"A loose ritual page lies open on the wooden table.","action":"crypt_page"},
            {"label":"Name wall","rect":(28,82,200,315),"hint":"Rows of names and memorial plaques line the damp wall.","action":"crypt_names"},
            {"label":"Stone seal","rect":(622,122,140,260),"hint":"The circular stone seal can be opened or closed at a price.","action":"crypt_seal"},
        ]
    }
})

# Each route is navigation rather than an investigation. Movement never spends a
# room's limited decisions, and routes can return to earlier locations.
ROUTES = {
    "road":[("hall", "Enter the estate")],
    "hall":[("dining", "Through the dining doors"),("landing_quiet", "Creep upstairs quietly"),
            ("landing_loud", "Run up the creaking stairs"),("chapel", "Investigate the east wing")],
    "dining":[("hall", "Return to entrance hall"),("study", "Enter the private study"),("greenhouse", "Follow pantry to conservatory")],
    "landing":[("hall", "Descend the staircase"),("nursery", "Open the nursery door"),("study", "Cross to the study")],
    "nursery":[("landing", "Back to the upper landing"),("chapel", "Take the narrow chapel stairs")],
    "study":[("dining", "Back to the dining room"),("landing", "Step onto the landing"),
             ("basement", "Down the service stairs"),("chapel_secret", "Use the hidden passage")],
    "basement":[("study", "Climb to the study"),("crypt", "Through the stone arch"),("yard", "Unlock the rear service door")],
    "crypt":[("basement", "Back to the basement"),("chapel", "Up the burial stairs")],
    "chapel":[("hall", "Return to the entrance hall"),("crypt", "Descend into the crypt"),("nursery", "Take the narrow stairs upstairs")],
    "greenhouse":[("dining", "Return by the pantry"),("yard", "Step into the rear yard")],
    "yard":[("basement", "Return through the cellar"),("greenhouse", "Enter the conservatory")],
}

def normalize_scene_id(scene_id):
    if scene_id.startswith("landing_"):
        return "landing"
    if scene_id == "chapel_secret":
        return "chapel"
    return scene_id

# High-resolution promotional character headshots, shown on all three UI screens.
for _person in CHARACTERS:
    try:
        _file = ASSET_DIR / ("portrait_" + _person.lower() + ".png")
        PORTRAITS[_person] = pygame.image.load(str(_file)).convert()
    except (pygame.error, FileNotFoundError):
        pass

CHARACTER_DETAILS = {
    "Marcus": {"name": "Marcus Reed", "summary": "A former college athlete with a protective instinct and a habit of rushing toward danger. He can overpower obstacles but often misses the warning signs.", "strengths": "Heavy doors, direct confrontation, physical escapes", "weaknesses": "Subtle clues, technical locks, quiet approaches"},
    "Evelyn": {"name": "Evelyn Shaw", "summary": "An observant student who notices patterns others overlook. Careful, inquisitive, and reluctant to trust easy answers, she discovers secrets hidden in plain sight.", "strengths": "Spotting clues, deciphering warnings, reading tracks", "weaknesses": "Physical struggle, improvised mechanisms"},
    "Noah": {"name": "Noah Vale", "summary": "A pragmatic technician who understands machines, locks, and power systems. He thinks before he acts, but hesitation is costly when the killer closes in.", "strengths": "Generators, fuse panels, tools, simple lockwork", "weaknesses": "Fistfights, sprinting, evading pursuit"},
    "Sofia": {"name": "Sofia Reyes", "summary": "An independent survivor who keeps moving when everyone else panics. Her instinct for silence and escape can save her life, though some mysteries remain unsolved.", "strengths": "Sneaking, hiding, avoiding pursuit, escape routes", "weaknesses": "Breaking barriers, working with electrical equipment"},
}

# ----------------------------- Helpers ---------------------------------------
def draw_text(surface, text, x, y, font=FONT, color=PALE):
    surface.blit(font.render(str(text), True, color), (x, y))

def wrap_text(text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines, line = [], ""
    for word in words:
        test = word if not line else line + " " + word
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def draw_wrapped(surface, text, rect, font=FONT, color=PALE, line_gap=3, max_lines=None):
    y = rect.y
    count = 0
    for line in wrap_text(text, font, rect.width):
        if max_lines is not None and count >= max_lines:
            break
        surface.blit(font.render(line, True, color), (rect.x, y))
        y += font.get_linesize() + line_gap
        count += 1
    return y

def panel(surface, rect, fill=PANEL, border=LINE, radius=6):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 1, border_radius=radius)

def button(surface, rect, label, hovered=False, enabled=True, font=FONT):
    fill = (15, 45, 59) if hovered else (7, 24, 35)
    edge = CYAN if hovered else LINE
    if not enabled:
        fill, edge = (8, 15, 21), (43, 59, 66)
    pygame.draw.rect(surface, fill, rect, border_radius=5)
    pygame.draw.rect(surface, edge, rect, 1, border_radius=5)
    lines = wrap_text(label, font, rect.width - 16)
    total_h = len(lines) * font.get_linesize()
    y = rect.centery - total_h // 2
    for line in lines:
        img = font.render(line, True, PALE if enabled else MUTED)
        surface.blit(img, (rect.centerx - img.get_width() // 2, y))
        y += font.get_linesize()

# ----------------------------- Game state ------------------------------------
def new_popup(title, text, color=CYAN):
    return {"title": title, "text": text, "color": color, "ttl": 240}

def new_game(character_name):
    SCENE_AUDIO.enter("road")
    return {
        "character": character_name,
        "scene": "road", "decisions":SCENES["road"]["limit"],
        "room_remaining":{"road":SCENES["road"]["limit"]},
        "room_actions":{}, "used_actions":set(),
        "back_stack":[], "navigation_open":False, "map_open":False,
        "inventory":[], "clues":set(), "flags":set(),
        "health":100, "noise":0, "pursuit_active":False,
        "message":"Search the car before entering the house; the woods are still.",
        "hover_hint":"", "game_over":False, "ending":"", "ending_title":"",
        "visited":{"road"},
        "popup":new_popup("The Blackthorn Gate", "Something moved among the trees. Search the car first if you need supplies.", GOLD),
        "last_action":None, "threat":0,
        "encounter":None, "encounter_pending":None, "encounter_delay":0.0,
        "encounter_warning":None, "encounter_warned":False,
        "encountered":set(), "actions_in_scene":0, "killer_visible":False,
        "inventory_message":"Click items to inspect them. Bandages heal and are consumed.",
    }


def current_character(state):
    return CHARACTERS[state["character"]]

def set_feedback(state, title, text, color=CYAN):
    state["message"] = text
    state["popup"] = new_popup(title, text, color)

def queue_encounter(state, scene, delay=3.0, warning=None):
    if state["game_over"] or scene in state["encountered"] or state["encounter"]:
        return False
    if state["scene"] != scene or state.get("encounter_pending") == scene:
        return False
    state["encounter_pending"] = scene
    state["encounter_delay"] = float(delay)
    state["encounter_warning"] = warning
    state["encounter_warned"] = False
    # Keep the interaction result visible before warning the player.
    return True


def enter_scene(state, scene_id, feedback=None, backtracking=False):
    if scene_id not in SCENES or scene_id == state["scene"]:
        return
    old_scene=state["scene"]
    already_visited = scene_id in state["visited"]
    state["room_remaining"][old_scene]=state["decisions"]
    state["room_actions"][old_scene]=state["actions_in_scene"]
    if not backtracking:
        state["back_stack"].append(old_scene)
    state["scene"]=scene_id
    state["navigation_open"]=False
    state["map_open"] = False
    state["encounter"]=None
    state["encounter_pending"]=None
    state["encounter_delay"]=0.0
    state["encounter_warning"]=None
    state["encounter_warned"]=False
    state["killer_visible"]=False
    state["decisions"]=state["room_remaining"].setdefault(scene_id,SCENES[scene_id]["limit"])
    state["actions_in_scene"]=state["room_actions"].get(scene_id,0)
    state["visited"].add(scene_id)
    SCENE_AUDIO.enter(scene_id)
    if feedback is None:
        feedback = "You return to " + SCENES[scene_id]["title"] + "." if already_visited else "You enter " + SCENES[scene_id]["title"] + "."
    if already_visited:
        feedback += f" Decisions here remain at {state['decisions']}; used actions do not refresh."
    set_feedback(state, SCENES[scene_id]["title"], feedback, GOLD)
    if not already_visited and state["pursuit_active"] and scene_id in ("landing","nursery","study"):
        queue_encounter(state,scene_id,delay=4.6,
            warning="The staircase groans behind you. Slow, dragging steps are following you into this room. Hide or prepare for the Watcher.")
    elif not already_visited and scene_id=="basement" and state["noise"]>=4:
        queue_encounter(state,scene_id,delay=4.0,
            warning="Your earlier noise echoes down the service shafts. A metal scrape answers from the dark.")
    elif not already_visited and scene_id=="yard" and state["noise"]>=5:
        queue_encounter(state,scene_id,delay=5.0,
            warning="A shadow slips along the wet wall outside. Your noisy passage through the house was not forgotten.")


def go_back(state):
    if state.get("encounter"):
        return
    if not state["back_stack"]:
        set_feedback(state,"No Previous Room","This is the first location. Use PATHS to move into the estate.",MUTED)
        return
    dest=state["back_stack"].pop()
    enter_scene(state,dest,backtracking=True,feedback="You retrace your route, watching for familiar hazards.")


def use_route(state, route_id):
    if state["game_over"] or state["encounter"]:
        return
    route_ids = [key for key, _ in ROUTES[state["scene"]]]
    if route_id not in route_ids:
        return
    target=route_id
    if route_id in ("landing_quiet","landing_loud"):
        target="landing"
        if route_id=="landing_loud":
            state["noise"]+=3
            state["flags"].add("stair_noise")
            state["pursuit_active"]=True
            warning="You sprint up the old stairs. Each step cracks like a gunshot; footsteps start climbing behind you."
        else:
            if "stairs_are_noisy" in state["clues"] or current_character(state)["traits"]["Stealth"]>=2:
                warning="You keep to the quiet edges of the stairs. Nothing follows you up."
            else:
                state["noise"]+=1
                warning="You try to creep, but a weak tread groans. The darkness below seems to listen."
        enter_scene(state,target,feedback=warning)
        return
    if route_id=="chapel_secret":
        target="chapel"
        if "passage_open" not in state["flags"]:
            set_feedback(state,"Hidden Passage Shut","You have to discover the bookcase catch before you can take this passage.",MUTED)
            return
    if state["scene"]=="basement" and route_id=="yard":
        if not ({"generator_disabled","panel_open"}&state["flags"]) and not ({"Maintenance Log","Brass Key"}&set(state["inventory"])):
            set_feedback(state,"The Rear Door Is Locked","You need the maintenance code, a brass key, or the generator override to open it.",MUTED)
            return
        if "Brass Key" in state["inventory"] and "Maintenance Log" not in state["inventory"] and "generator_disabled" not in state["flags"]:
            remove_item(state,"Brass Key")
    if state["scene"]=="nursery" and route_id=="chapel" and "nursery_diary" not in state["clues"]:
        set_feedback(state,"Narrow Staircase","The panel door has no handle. The diary may reveal its latch.",MUTED)
        return
    if state["scene"]=="yard" and route_id=="basement" and "yard" not in state["visited"]:
        return
    enter_scene(state,target)


def end_game(state, ending, fatal=False, title=None):
    state["game_over"] = True
    state["ending"] = ending
    state["ending_title"] = title or ("GAME OVER" if fatal else "ESCAPED BLACKTHORN")
    state["message"] = ending
    state["popup"] = None
    state["navigation_open"] = False
    state["map_open"] = False
    state["encounter"] = None
    state["killer_visible"] = False
    if fatal:
        state["health"] = 0


def spend_decision(state):
    if state["decisions"] <= 0:
        set_feedback(state,"No Decisions Left","This room is exhausted. Use PATHS or BACK to explore other places; revisiting will not restore decisions.",GOLD)
        return False
    state["decisions"]-=1
    state["room_remaining"][state["scene"]]=state["decisions"]
    return True


def add_item(state, item):
    if item not in state["inventory"]:
        state["inventory"].append(item)

def remove_item(state, item):
    if item in state["inventory"]:
        state["inventory"].remove(item)
        return True
    return False

def use_item(state, item):
    if item not in state["inventory"]:
        return
    if item == "Bandage":
        if state["health"] >= 100:
            set_feedback(state, "Not Needed", "You're unhurt. Save the bandage for a real injury.", GOLD)
        else:
            healed = min(30, 100-state["health"])
            state["health"] += healed
            remove_item(state, item)
            set_feedback(state, "Bandage Used", f"You dress the wound and recover {healed} health. The bandage is removed from inventory.", GREEN)
    elif item == "Victim's Note":
        set_feedback(state, "Victim's Note", "He hears the stairs. Don't use them when the house is quiet. The handwriting ends in a desperate scrawl.", CYAN)
    elif item == "Maintenance Log":
        set_feedback(state, "Maintenance Log", "The basement override code is 0417. Handwritten dates suggest someone carefully counted each disappearance.", CYAN)
    elif item == "Brass Key" and state["scene"] == "basement":
        use_route(state, "yard")
    else:
        set_feedback(state, "Inventory", f"{item} is ready. Some items are consumed automatically when you use them in an encounter or on a lock.", MUTED)

def add_clue(state, clue):
    state["clues"].add(clue)


ENCOUNTERS = {
    "road": ("Movement in the Pines", "A pale figure condenses out of the rain beside the pines. The Watcher was never entirely human.",
             ["Hide behind the car", "Dash toward the gate", "Shine your flashlight"]),
    "hall": ("A Shape on the Landing", "A spectral killer forms on the upper landing, coat drifting like smoke as a blade taps the banister.",
             ["Stay perfectly still", "Charge across the hall", "Duck behind the banister"]),
    "dining": ("The Chair Moves", "The chair at the far end drags backward. A ghostly figure gathers behind it, knife lowered.",
             ["Hide under the table", "Block him with a chair", "Fight with your knife"]),
    "study": ("He Found the Study", "Cold mist leaks under the study door. The Watcher's skull-like face forms in the gap beside the bookcase.",
             ["Jam the door", "Dash past the desk", "Blind him with flashlight"]),
    "basement": ("The Watcher in the Dark", "The generator flickers and a hooded apparition coalesces in the aisle, blade scraping concrete.",
             ["Hide behind the pipes", "Kill the lights", "Push straight through"]),
    "yard": ("One Last Pursuit", "A tall ghostly figure rises beside the iron gate, phasing through sheets of rain to cut you off.",
             ["Sprint for the wall", "Fight with your knife", "Stand your ground"]),
    "landing": ("Something Climbs the Stairs", "Each creak is answered from below. Pale hands appear between the banister posts, followed by the Watcher.",
               ["Hide behind the rail", "Dash toward the nursery", "Flash the hallway light"]),
    "nursery": ("The Music Box Stops", "The melody falters. A ghostly hood slowly forms beside the cradle, its eyes empty and fixed on you.",
               ["Duck beneath the crib", "Throw the music box", "Hold the silver locket"]),
    "greenhouse": ("Footsteps in Glass", "Condensation blooms across the greenhouse panes as the Watcher phases through the glass wall.",
               ["Hide among the vines", "Shatter a glass pane", "Turn out the lamp"]),
    "chapel": ("The Bell Answers", "After the bell echoes, the Watcher appears beneath the ruined cross. Its mist avoids the candle flame.",
               ["Step behind the altar", "Hold up the candle", "Run for the crypt"]),
    "crypt": ("The Stone Seal Breaks", "A cold voice speaks from the coffin. The Watcher rises in the doorway before the seal is restored.",
               ["Hide between coffins", "Read the ritual page", "Force the stone seal shut"]),
}

def trigger_encounter(state, scene=None):
    scene = scene or state["scene"]
    if state["game_over"] or scene in state["encountered"]:
        return
    state["encountered"].add(scene)
    state["encounter"] = scene
    state["encounter_pending"] = None
    state["encounter_delay"] = 0.0
    state["encounter_warning"] = None
    state["encounter_warned"] = False
    state["navigation_open"] = False
    state["map_open"] = False
    state["killer_visible"] = True
    state["threat"] += 1
    state["popup"] = None
    state["message"] = ENCOUNTERS[scene][1]


def hurt(state, damage, narrative):
    state["health"] = max(0, state["health"]-damage)
    state["flags"].add("injured")
    if damage:
        state["threat"] += 1
    if state["health"] <= 0:
        end_game(state, narrative + " You collapse before reaching safety.", True)
    else:
        set_feedback(state, "INJURED  -" + str(damage) + " HP", narrative, RED)


def encounter_choice(state, index):
    scene = state.get("encounter")
    if scene is None or index not in (0, 1, 2):
        return
    c = current_character(state)["traits"]
    inv = state["inventory"]
    state["encounter"] = None
    state["killer_visible"] = False
    state["flags"].add("killer_alerted")
    damage = 0
    note = ""
    if scene == "road":
        if index == 0:
            damage = 0 if c["Stealth"] >= 2 else 12
            note = "You crouch low behind the car as the Watcher drifts by. Its blade brushes the metal inches from your face." if not damage else "The Watcher phases around the trunk and slashes your leg before slipping back into the rain."
        elif index == 1:
            damage = 8 if c["Strength"] >= 3 else 15
            note = "You sprint through the muddy gate. An icy blade catches your coat before the apparition thins into the storm."
        elif "Flashlight" in inv:
            remove_item(state, "Flashlight")
            note = "You flare the flashlight into its hollow mask. The battery dies, and the spectral figure peels apart into mist. The flashlight is gone."
        else:
            damage = 17
            note = "You reach for a flashlight you never found. The Watcher closes the gap and cuts your shoulder before vanishing into the trees."
    elif scene == "hall":
        if index == 0:
            damage = 0 if c["Stealth"] >= 2 else 14
            note = "You don't move. The Watcher studies you from the landing, then unravels into smoke upstairs." if not damage else "You shift your weight on a creaking floorboard. The Watcher charges and wounds your arm before fading from the staircase."
        elif index == 1:
            damage = 8 if c["Strength"] >= 3 else 24
            note = "You shoulder past the apparition toward the dining wing. Its blade glances off you before the figure scatters into ash-like vapor."
        else:
            damage = 0 if c["Perception"] >= 2 else 16
            note = "You find a narrow hiding space beside the stair rail and watch the ghost pass through the banister, then dissolve." if not damage else "You crouch in the wrong shadow. A spectral boot strikes your ribs before the Watcher flickers away."
    elif scene == "dining":
        if index == 0:
            damage = 0 if c["Stealth"] >= 2 else 17
            note = "You slide soundlessly under the table while the Watcher's hem drifts past inches away, then disappears." if not damage else "A chair snaps loudly beneath you. The Watcher reaches under the table and slices your calf before withdrawing into the dark."
        elif index == 1:
            damage = 3 if c["Strength"] >= 3 else 21
            note = "You topple a heavy chair into its path. It slows the specter long enough for you to escape, though a glancing blow opens your side."
        elif "Kitchen Knife" in inv:
            remove_item(state, "Kitchen Knife")
            note = "You block its strike with the kitchen knife. The blade snaps in two, and the ghost recoils into a blur of smoke. The knife is gone."
        else:
            damage = 25
            note = "You reach for a weapon you don't have. The Watcher drives you against the table before melting back into shadow."
    elif scene == "study":
        if index == 0:
            if c["Technical"] >= 2:
                note = "You wedge the study door shut with a quick adjustment of its lock. Frost spreads under the frame as the handle rattles, then falls still."
            elif "Small Screwdriver" in inv:
                remove_item(state, "Small Screwdriver")
                note = "You sacrifice the screwdriver to jam the latch. Metal bends behind the door, and when the pressure stops, the ghost is gone."
            else:
                damage = 19
                note = "You slam the study door, but the warped latch gives way. A spectral blade catches your wrist before the Watcher recedes."
        elif index == 1:
            damage = 6 if c["Strength"] >= 3 else 21
            note = "You vault the desk as the Watcher lunges. Broken glass bites into your palm before the apparition dissolves behind you."
        elif "Flashlight" in inv:
            remove_item(state, "Flashlight")
            note = "You blast its mask with the flashlight and hurl it. The final charge tears the Watcher apart into white mist. The flashlight is gone."
        else:
            damage = 24
            note = "You fumble in your bag for a light. The Watcher is already within arm's reach when it rakes your shoulder and flickers away."
    elif scene == "basement":
        if index == 0:
            damage = 0 if c["Stealth"] >= 2 else 25
            note = "You slip behind the exposed pipes and hold your breath as the Watcher glides past and evaporates into the generator haze." if not damage else "Your boot strikes a pipe and the Watcher drives its blade into your side before breaking into cold vapor."
        elif index == 1:
            damage = 0 if ("generator_override" in state["clues"] or c["Technical"] >= 3) else 22
            if not damage:
                state["flags"].add("generator_disabled")
                note = "You flip the correct breaker. The generator dies, and the apparition loses its outline, dissolving into the sudden darkness."
            else:
                note = "You grab an unmarked switch. The generator erupts in sparks, scorching your hands as the Watcher closes in and then vanishes."
        else:
            damage = 9 if c["Strength"] >= 3 else 32
            note = "You barrel through the Watcher and reach the opposite wall, but its knife catches you on the way through before it disperses."
    elif scene == "yard":
        if index == 0:
            damage = 2 if c["Stealth"] >= 3 else 26
            note = "You vault the low wall behind the shed. The Watcher scrapes you with its blade but loses shape in the rain."
        elif index == 1:
            if "Kitchen Knife" in inv:
                remove_item(state, "Kitchen Knife")
                note = "The knives clash. Your kitchen blade breaks as you force the ghost back; it unravels into fog and the knife is gone."
            else:
                damage = 31
                note = "You swing an empty hand. The Watcher counters brutally, leaving you barely able to stand before it melts into darkness."
        else:
            damage = 11 if c["Strength"] >= 3 else 28
            note = "You hold your ground long enough to drive the Watcher back, but not without paying for it in blood before it dissipates."
    elif scene == "landing":
        if index==0:
            damage=0 if c["Stealth"]>=2 else 18
            note="You stay motionless behind the rail as the Watcher dissolves into drifting dust." if not damage else "The banister cracks beneath you. An icy hand tears your shoulder before fading away."
        elif index==1:
            damage=4 if c["Strength"]>=3 else 19
            note="You race across the gallery. A blade catches you, but the spectral killer loses its form before reaching the door."
        elif "Flashlight" in inv:
            remove_item(state,"Flashlight")
            note="The flashlight floods the landing with white light. The Watcher tears apart into fog; the dead flashlight is discarded."
        else:
            damage=22
            note="You fumble for a missing flashlight. The Watcher strikes, then vanishes through the floor."
    elif scene == "nursery":
        if index==0:
            damage=0 if c["Stealth"]>=2 else 15
            note="You slip under the cradle. The Watcher's feet hover above the floor, then dissolve into candle-smoke." if not damage else "The crib rocks violently and splinters against your arm before the spirit goes."
        elif index==1:
            damage=8
            note="The music box breaks against the door. The ghost shivers apart, but the flying metal cuts your hand."
        elif "Silver Locket" in inv:
            note="You raise the silver locket. The Watcher recoils as if recognizing it, fading without a sound."
        else:
            damage=26
            note="Your hands are empty. The ghost rushes you and a supernatural chill seizes your chest before it fades."
    elif scene == "greenhouse":
        if index==0:
            damage=0 if c["Stealth"]>=2 else 16
            note="You crouch behind the thick vines while the Watcher glides past and slips through glass." if not damage else "The thorny vines snap as you move. A sudden icy strike bruises your ribs."
        elif index==1:
            damage=18
            state["noise"]+=1
            note="The window shatters. You escape the grasp but glass slices your palms before the apparition fades."
        else:
            damage=0 if "Chapel Candle" in inv or "Flashlight" in inv else 20
            note="The light goes out; with no light left to bind it, the Watcher unravels." if not damage else "You reach for a light you cannot find. The ghost cuts your forearm before retreating."
    elif scene == "chapel":
        if index==0:
            damage=0 if c["Stealth"]>=2 else 15
            note="Behind the altar you feel the Watcher glide past, unable to cross the worn blessing." if not damage else "The old altar splinters. Its flying stone chips wound your leg before the ghost disappears."
        elif index==1:
            damage=0 if "Chapel Candle" in inv else 22
            note="You hold the chapel candle aloft. A ring of warm light drives the spirit back into the floor." if not damage else "You cannot find a candle; the ghost answers with a blade of freezing air."
        else:
            damage=7 if c["Strength"]>=3 else 19
            note="You tumble down the burial stairs with the Watcher at your heels, but it loses shape before catching you."
    elif scene == "crypt":
        if index==0:
            damage=0 if c["Stealth"]>=2 else 18
            note="You press against a stone coffin until the ghost floats away, leaving only damp air." if not damage else "Your foot slips on stone. The Watcher catches you before it vanishes between the tombs."
        elif index==1:
            damage=0 if "Ritual Page" in inv else 24
            note="You speak the old words. The Watcher recoils and retreats behind the crypt's closed stone doors." if not damage else "You have no words to speak. The spirit attacks before thinning to mist."
        else:
            damage=9 if c["Strength"]>=3 else 26
            note="You shove the seal closed. It costs you blood and breath, but the apparition is driven out of the room."
    state["pursuit_active"]=False
    if damage:
        hurt(state, damage, note)
    else:
        state["threat"] = max(0, state["threat"]-1)
        set_feedback(state, "THE WATCHER FADES", note, GREEN)
    if not state["game_over"] and state["health"] < 30:
        state["flags"].add("limping")


def after_player_action(state, old_scene, old_decisions, action=None):
    if state["game_over"] or state["encounter"] or state["scene"]!=old_scene:
        return
    if state["decisions"]>=old_decisions:
        return
    scene=state["scene"]
    state["actions_in_scene"]+=1
    state["room_actions"][scene]=state["actions_in_scene"]
    state["used_actions"].add((scene,action))
    if scene in state["encountered"] or state.get("encounter_pending"):
        return
    if scene=="road" and state["actions_in_scene"]>=2:
        queue_encounter(state,scene,4.0,"The footprints stop at the tree line. Pale mist is gathering beyond your headlights; something is coming closer.")
    elif scene in ("hall","dining","study") and state["noise"]>=2 and state["actions_in_scene"]>=1:
        queue_encounter(state,scene,3.8,"Your earlier noise has traveled through the house. A slow scraping sound answers from the corridor.")
    elif scene=="nursery" and action=="nursery_music":
        queue_encounter(state,scene,3.4,"The music box starts playing by itself. Something cold is taking shape beside the cradle.")
    elif scene=="greenhouse" and (action=="greenhouse_heat" or state["noise"]>=4):
        queue_encounter(state,scene,3.5,"Condensation spreads in the shape of a handprint. The Watcher has heard you among the glass.")
    elif scene=="chapel" and action=="chapel_bell":
        queue_encounter(state,scene,3.6,"The bell reverberates deep below the chapel. A cold shape is climbing toward the sound.")
    elif scene=="crypt" and action=="crypt_coffin" and state["noise"]>=3:
        queue_encounter(state,scene,3.6,"The heavy lid echoes off the stone walls. The breathing sound comes from outside the crypt door.")


def perform_action(state,action):
    if state["game_over"] or state.get("encounter"):
        return
    if action in ("continue","paths","stairs"):
        state["navigation_open"]=True
        state["map_open"] = False
        state["popup"]=None
        return
    if action=="map":
        state["map_open"] = not state.get("map_open", False)
        state["navigation_open"] = False
        state["popup"] = None
        return
    if action=="back":
        state["map_open"] = False
        go_back(state)
        return
    if action=="close_paths":
        state["navigation_open"]=False
        return
    if action=="close_map":
        state["map_open"] = False
        return
    if action.startswith("route:"):
        use_route(state,action.split(":",1)[1])
        return
    # Existing door hotspots remain clickable, but traveling is free.
    if action in ("gate","dining","steeldoor"):
        use_route(state,{"gate":"hall","dining":"dining","steeldoor":"yard"}[action])
        return
    if action=="watch_killer":
        return
    oldscene,olddec=state["scene"],state["decisions"]
    act(state,action)
    after_player_action(state,oldscene,olddec,action)


def auto_advance(state):
    # The old six-room linear jump has been replaced by a path selection menu.
    state["navigation_open"]=True


def act(state, action):
    if state["game_over"]:
        return
    if action == "continue":
        auto_advance(state)
        return
    if action == "watch_killer":
        if state["scene"] not in state["encountered"]:
            trigger_encounter(state)
        else:
            set_feedback(state, "He Is Still Here", "The masked watcher waits at the edge of the light, holding his blade without a word. He knows where you are.", RED)
        return

    if not spend_decision(state):
        return

    char = current_character(state)
    scene = state["scene"]
    state["last_action"] = action
    # The same actions cannot duplicate unique clues/items when revisited.
    # Actions still cost a decision, but room decisions never regenerate.

    # ROAD
    if scene == "road":
        if action == "tracks":
            if char["traits"]["Perception"] >= 2:
                add_clue(state, "two_trails")
                set_feedback(state, "Clue Found", "You spot a second trail of prints turning back toward the road. Something walked in and then returned.", CYAN)
            else:
                set_feedback(state, "Tracks Blurred", "Rain has softened the edges of the footprints. You can tell they lead in, but not what returned.", MUTED)
        elif action == "glovebox":
            if "Flashlight" not in state["inventory"]:
                add_item(state, "Flashlight")
                set_feedback(state, "Item Found", "Inside the glove box is a flashlight. The beam flickers, but it still works.", GREEN)
            else:
                set_feedback(state, "Already Searched", "You check the glove compartment again. Nothing else useful remains inside.", MUTED)
        elif action == "gate":
            enter_scene(state, "hall", "You pass through the iron gate and force your way into the estate.")
        elif action == "listen":
            if char["traits"]["Stealth"] >= 3:
                add_clue(state, "stopped_footsteps")
                set_feedback(state, "You Hear Something", "The distant footsteps stop the moment you stop breathing. Whatever is out there is listening too.", CYAN)
            else:
                state["flags"].add("killer_alerted")
                state["noise"]+=1
                set_feedback(state, "Too Much Noise", "A shape shifts in the darkness behind the car. Your movement gives away your position.", RED)
        return

    # HALL
    if scene == "hall":
        if action == "read_note":
            if "Victim's Note" not in state["inventory"]:
                add_clue(state, "stairs_are_noisy")
                add_item(state, "Victim's Note")
                set_feedback(state, "Note Read", "The note warns: 'He hears the stairs. Don't use them when the house is quiet.'", CYAN)
            else:
                set_feedback(state, "Nothing New", "It is the same note. The warning about the stairs still chills you.", MUTED)
        elif action == "stairs":
            if "stairs_are_noisy" in state["clues"] and char["traits"]["Stealth"] >= 2:
                enter_scene(state, "study", "You test the outer edge of each step and manage to climb the staircase in eerie silence.")
            elif char["traits"]["Strength"] >= 3:
                state["flags"].add("killer_alerted")
                enter_scene(state, "study", "You bound up the steps before caution can stop you. The staircase groans loud enough to wake the house.")
            else:
                state["flags"].add("killer_alerted")
                state["health"] -= 25
                if state["health"] <= 0:
                    end_game(state, "A rotted tread splits beneath you. The fall is bad—but what reaches you in the dark is worse.", True)
                else:
                    enter_scene(state, "study", "A board snaps under your weight. You escape upward, but not before something below turns toward the noise.")
        elif action == "dining":
            enter_scene(state, "dining", "The double doors yield with a dry groan and open into the dining room.")
        elif action == "portrait":
            if char["traits"]["Perception"] >= 2:
                add_clue(state, "portrait_scratches")
                set_feedback(state, "Fresh Damage", "The slashes are newer than the dust around the frame. Someone defaced the portrait recently.", CYAN)
            else:
                set_feedback(state, "Disturbing Sight", "The ruined portrait tells you only one thing for certain: rage still lives in this house.", MUTED)
        return

    # DINING
    if scene == "dining":
        if action == "pantry":
            if "pantry_checked" not in state["flags"]:
                state["flags"].add("pantry_checked")
                add_item(state, "Kitchen Knife")
                add_item(state, "Bandage")
                add_clue(state, "pipe_clicking")
                set_feedback(state, "Pantry Searched", "Behind a crate, you recover a kitchen knife and a clean bandage. Click the bandage in inventory to heal an injury.", GREEN)
            else:
                set_feedback(state, "Pantry Empty", "Only dusty jars and the same rattling pipe wait in the pantry now.", MUTED)
        elif action == "window":
            if char["traits"]["Strength"] >= 3:
                state["flags"].add("window_broken")
                state["noise"]+=2
                state["health"] = max(0, state["health"] - 10)
                set_feedback(state, "Window Forced", "You wrench the swollen frame apart, cutting your palm. The drop outside is steep and littered with broken stone.", RED)
            else:
                state["flags"].add("killer_alerted")
                state["noise"]+=2
                set_feedback(state, "No Good", "The frame barely shifts. All you gain is a burst of noise and a stronger fear that something heard it.", RED)
        elif action == "message":
            if char["traits"]["Perception"] >= 2:
                add_clue(state, "hidden_passage_hint")
                set_feedback(state, "Clue Found", "Beneath the scratched warning, you make out older letters: 'BEHIND THE BOOKS.'", CYAN)
            else:
                set_feedback(state, "Half a Clue", "The carved warning is obvious, but the older writing underneath refuses to resolve into words.", MUTED)
        elif action == "sideboard":
            if char["traits"]["Technical"] >= 2:
                add_item(state, "Small Screwdriver")
                set_feedback(state, "Tool Found", "A loose panel in the sideboard reveals a small screwdriver wrapped in cloth.", GREEN)
            else:
                set_feedback(state, "Warped Shut", "The sideboard drawers are warped shut. You suspect there is something hidden there, but forcing it would take more than bare hands.", MUTED)
        return

    # STUDY
    if scene == "study":
        if action == "ledger":
            if "Maintenance Log" not in state["inventory"]:
                add_clue(state, "generator_override")
                add_item(state, "Maintenance Log")
                set_feedback(state, "Record Found", "The maintenance log mentions a basement override and a margin code: 0417.", CYAN)
            else:
                set_feedback(state, "Old Record", "The ledger still shows the same note about the basement override and the code 0417.", MUTED)
        elif action == "panel":
            if char["traits"]["Technical"] >= 2 or "Small Screwdriver" in state["inventory"]:
                state["flags"].add("panel_open")
                if char["traits"]["Technical"] < 2:
                    remove_item(state, "Small Screwdriver")
                add_clue(state, "power_routes")
                set_feedback(state, "Panel Isolated", "You isolate a live wire. Lights die elsewhere in the manor, and far below you hear a magnetic lock release.", GREEN)
            else:
                state["health"] -= 15
                state["flags"].add("killer_alerted")
                state["noise"]+=2
                if state["health"] <= 0:
                    end_game(state, "The fuse panel erupts in a flash of white fire. Your last sight is your own shadow burning across the wall.", True)
                else:
                    set_feedback(state, "Shock", "The panel bites your hand and spits sparks into the room. The flash is bright enough to betray your position.", RED)
        elif action == "bookcase":
            if "hidden_passage_hint" in state["clues"] or char["traits"]["Perception"] >= 3:
                state["flags"].add("passage_open")
                add_clue(state, "hidden_passage")
                set_feedback(state, "Passage Found", "A catch behind the books gives way. The shelf shifts, revealing a narrow service passage.", GREEN)
            else:
                set_feedback(state, "Almost Something", "The dust pattern on the floor suggests the bookcase moves, but you cannot find the release.", MUTED)
        elif action == "drawer":
            if char["traits"]["Technical"] >= 2:
                add_item(state, "Brass Key")
                set_feedback(state, "Key Found", "You ease the jammed drawer open and find a tarnished brass key tucked inside.", GREEN)
            else:
                set_feedback(state, "Jammed Drawer", "The drawer catches hard on swollen wood. You need a tool or steadier hands to free it.", MUTED)
        return

    # BASEMENT
    if scene == "basement":
        if action == "generator":
            if "generator_override" in state["clues"] or char["traits"]["Technical"] >= 3:
                state["flags"].add("generator_disabled")
                add_clue(state, "generator_disabled")
                set_feedback(state, "Power Cut", "You use the override and kill the generator. The basement falls into a deeper, more dangerous silence.", GREEN)
            else:
                state["flags"].add("killer_alerted")
                state["noise"]+=2
                set_feedback(state, "Wrong Lever", "The machine snarls louder when you touch it. Somewhere upstairs, something answers.", RED)
        elif action == "steeldoor":
            if "generator_disabled" in state["flags"] or "Brass Key" in state["inventory"]:
                if "generator_disabled" not in state["flags"]:
                    remove_item(state, "Brass Key")
                enter_scene(state, "yard", "The steel door unlocks with a reluctant clank and opens onto the rear yard.")
            elif "Maintenance Log" in state["inventory"]:
                enter_scene(state, "yard", "You tap in 0417. The keypad accepts it, and the steel door opens into the night.")
            else:
                set_feedback(state, "Locked", "The keypad flashes red. You need a code, a key, or a way to kill the power feeding the lock.", MUTED)
        elif action == "tallies":
            add_clue(state, "victim_count")
            set_feedback(state, "A Count of the Lost", "There are forty-seven tally marks here. The newest scratches are pale and recent.", CYAN)
        return

    # YARD
    if scene == "yard":
        if action == "service_gate":
            if "Bolt Cutters" in state["inventory"] or char["traits"]["Strength"] >= 3:
                if "Bolt Cutters" in state["inventory"]:
                    remove_item(state, "Bolt Cutters")
                if state["noise"] >= 4 and char["traits"]["Stealth"] < 3:
                    state["health"] -= 35
                    if state["health"] <= 0:
                        end_game(state, "The chain gives, but a figure crashes into you from the dark before you can reach the trees.", True)
                    else:
                        end_game(state, "You force the gate and escape into the forest, wounded and breathless, with only fragments of the truth.")
                else:
                    end_game(state, "You slip through the service gate and vanish into the storm. Blackthorn remains behind you—for now.")
            else:
                set_feedback(state, "Too Strong", "The chain is too thick to break by hand. You need better leverage, a cutting tool, or far more strength.", MUTED)
        elif action == "shed":
            if "Bolt Cutters" not in state["inventory"] and char["traits"]["Perception"] >= 2:
                add_item(state, "Bolt Cutters")
                set_feedback(state, "Tool Found", "Behind rotting boards in the shed, you uncover a pair of rusted but usable bolt cutters.", GREEN)
            else:
                set_feedback(state, "Nothing Else", "The shed is damp, cramped, and full of rust. If anything useful was here, you already found it.", MUTED)
        elif action == "yard_tracks":
            if "two_trails" in state["clues"]:
                add_clue(state, "escape_route")
                set_feedback(state, "Tracks Read", "The freshest prints match the ones by the road. One trail avoids the light and skirts the broken wall.", CYAN)
            else:
                set_feedback(state, "Tracks Confused", "The rain and overlapping prints make the yard hard to read. Too many paths begin here and fail.", MUTED)
        elif action == "confront":
            if "Maintenance Log" in state["inventory"] and "victim_count" in state["clues"]:
                end_game(state, "You call out the forty-seven names from the maintenance records. The Watcher rises in the yard, but each name strips away a layer of its mask. The spirit retreats, and you carry its history into daylight.", title="ENDING: THE NAMES REMEMBERED")
            else:
                state["health"] = max(0,state["health"] - 50)
                if state["health"] <= 0:
                    end_game(state, "You step into the yard and call for the ghost. It answers from just behind you.", True)
                else:
                    end_game(state, "The Watcher nearly claims you. You escape the yard battered, with no proof that anyone will believe.",title="ENDING: THE WOUNDED WITNESS")
        return


    # UPPER LANDING
    if scene=="landing":
        if action=="landing_floor":
            add_clue(state,"old_stairwell")
            set_feedback(state,"A Hidden Passage","Under the warped board is a pencil drawing of the chapel stairs. Someone once used them to avoid the Watcher.",CYAN)
        elif action=="landing_rail":
            if char["traits"]["Stealth"]>=2:
                set_feedback(state,"Quiet View","From here, you can watch the whole hall unseen. The railing has a narrow path along the wall.",GREEN)
            else:
                state["noise"]+=1
                set_feedback(state,"Creaking Rail","The loose railing protests when you lean on it. A sound answers from below.",RED)
        elif action=="landing_cabinet":
            if "landing_bandage_taken" not in state["flags"]:
                state["flags"].add("landing_bandage_taken")
                add_item(state,"Bandage")
                set_feedback(state,"Item Found","A clean bandage lies among the old linen. It can heal you when used from inventory.",GREEN)
            else:
                set_feedback(state,"Empty Cabinet","Only dust and yellow linen remain inside.",MUTED)
        elif action=="landing_door":
            set_feedback(state,"Nursery Door","The old child's room is at the end of the landing. Use PATHS to enter it.",GOLD)
        return

    # NURSERY
    if scene=="nursery":
        if action=="nursery_cradle":
            if "nursery_locket_taken" not in state["flags"]:
                state["flags"].add("nursery_locket_taken")
                add_item(state,"Silver Locket")
                set_feedback(state,"Silver Locket Found","A tarnished locket rests under the cradle mattress. A child's picture has been folded inside.",GREEN)
            else:
                set_feedback(state,"Empty Cradle","The locket is gone. A slow rocking motion carries on for another moment.",MUTED)
        elif action=="nursery_diary":
            add_clue(state,"nursery_diary")
            set_feedback(state,"Diary Fragment","The caretaker wrote: 'Her room connects to the chapel through a narrow stair. The locket belonged to the lost daughter.'",CYAN)
        elif action=="nursery_music":
            state["noise"]+=3
            set_feedback(state,"The Music Box Starts","A broken lullaby echoes through the nursery. The tune travels down the hall—and something follows the sound.",RED)
        elif action=="nursery_window":
            add_clue(state,"greenhouse_roof")
            set_feedback(state,"A Way Out","You glimpse the conservatory roof through the rain. One glass panel is broken near the outer wall.",CYAN)
        return

    # GREENHOUSE
    if scene=="greenhouse":
        if action=="greenhouse_tools":
            if "garden_shears_taken" not in state["flags"]:
                state["flags"].add("garden_shears_taken")
                add_item(state,"Garden Shears")
                set_feedback(state,"Garden Shears Found","Sharp shears lie beneath a pot. They may be strong enough to cut the garden netting.",GREEN)
            else:
                set_feedback(state,"Empty Workbench","Broken pots, soil, and rust are all that remain.",MUTED)
        elif action=="greenhouse_heat":
            state["noise"]+=2
            if char["traits"]["Technical"]>=2:
                add_clue(state,"conservatory_vent")
                set_feedback(state,"Pipe Valve Open","You vent the steam safely. Outside air rushes through a narrow escape gap.",GREEN)
            else:
                hurt(state,13,"Hot steam erupts from the pipe and burns your arm. The valve shrieks loudly.")
        elif action=="greenhouse_glass":
            if "Garden Shears" in state["inventory"] or "Bolt Cutters" in state["inventory"] or char["traits"]["Strength"]>=3:
                if "Garden Shears" in state["inventory"]:
                    remove_item(state,"Garden Shears")
                elif "Bolt Cutters" in state["inventory"]:
                    remove_item(state,"Bolt Cutters")
                end_game(state,"You cut through the tangled wire and climb through the fractured conservatory roof. At dawn, you find the road and leave Blackthorn without ever learning what stalked you.",title="ENDING: THE GLASS ESCAPE")
            else:
                state["noise"]+=1
                set_feedback(state,"Still Sealed","The glass is cracked, but a heavy trellis bars the opening. You need shears, cutters, or unusual strength.",MUTED)
        elif action=="greenhouse_roots":
            add_clue(state,"roots_of_the_curse")
            set_feedback(state,"A Family Sigil","The roots have coiled around a ritual stone carved with the Blackthorn family crest. The same symbol appears on chapel records.",CYAN)
        return

    # CHAPEL
    if scene=="chapel":
        if action=="chapel_candle":
            if "chapel_candle_taken" not in state["flags"]:
                state["flags"].add("chapel_candle_taken")
                add_item(state,"Chapel Candle")
                set_feedback(state,"Chapel Candle Found","You shield the last votive flame and take it with you. A faint warmth pushes back the cold.",GREEN)
            else:
                set_feedback(state,"No Candle Left","You took the only candle. The altar looks darker now.",MUTED)
        elif action=="chapel_prayer":
            add_clue(state,"chapel_prayer")
            set_feedback(state,"The Binding Prayer","The stone reads: 'Return the daughter's silver, light a flame, and speak the words from below. The house will release her.'",CYAN)
        elif action=="chapel_bell":
            state["noise"]+=3
            set_feedback(state,"The Bell Rings","A harsh bell echoes through the walls. Something restless beneath the floor has heard it.",RED)
        elif action=="chapel_altar":
            needs={"Silver Locket","Ritual Page","Chapel Candle"}
            if needs.issubset(state["inventory"]):
                remove_item(state,"Silver Locket")
                remove_item(state,"Ritual Page")
                remove_item(state,"Chapel Candle")
                end_game(state,"At the altar, the locket opens as you speak the ritual words. The Watcher's mask fractures, and the lost daughter finally leaves Blackthorn in a column of silver light. The curse ends; you survive with the truth.",title="ENDING: THE CURSE BROKEN")
            else:
                missing=', '.join(sorted(needs-set(state["inventory"])))
                set_feedback(state,"An Unfinished Rite","The altar will not answer yet. You still need: "+missing+". Find the missing pieces, then return if you have decisions remaining.",MUTED)
        return

    # CRYPT
    if scene=="crypt":
        if action=="crypt_page":
            if "ritual_page_taken" not in state["flags"]:
                state["flags"].add("ritual_page_taken")
                add_item(state,"Ritual Page")
                set_feedback(state,"Ritual Page Found","You recover a brittle page describing the silver locket and candle that can release the restless dead.",GREEN)
            else:
                set_feedback(state,"The Page Is Gone","You already removed the ritual manuscript from under the lid.",MUTED)
        elif action=="crypt_names":
            add_clue(state,"buried_names")
            set_feedback(state,"The Forgotten Family","The carved names show the Watcher was a grieving caretaker, bound by a ritual after the daughter's death.",CYAN)
        elif action=="crypt_coffin":
            state["noise"]+=2
            if char["traits"]["Strength"]>=3:
                add_clue(state,"the_watchers_grief")
                set_feedback(state,"A Hidden Portrait","You force the coffin lid open. Inside is a photograph of the child, wrapped in black fabric.",CYAN)
            else:
                hurt(state,12,"The stone lid slips and crushes your fingertips. Its grinding echo rolls through the chamber.")
        elif action=="crypt_seal":
            if "Ritual Page" in state["inventory"] and "Maintenance Log" in state["inventory"]:
                end_game(state,"You recite the binding and seal the Watcher inside the crypt. The doors lock behind you. Blackthorn is safe for the living, but you will never leave the tomb.",title="ENDING: THE LAST WARDEN")
            else:
                set_feedback(state,"Seal Not Understood","The stone shudders under your touch, but you lack the page and maintenance records to bind it permanently.",MUTED)
        return

# ----------------------------- UI rendering ----------------------------------
def draw_header(state):
    pygame.draw.rect(SCREEN, DARK, (0, 0, W, HEADER_H))
    pygame.draw.line(SCREEN, LINE, (0, HEADER_H-1), (W, HEADER_H-1), 1)
    draw_text(SCREEN, "◈  THE HOLLOW AT BLACKTHORN", 18, 12, TITLE, CYAN)
    scene = SCENES[state["scene"]]
    draw_text(SCREEN, "M: UNMUTE" if SCENE_AUDIO.muted else "M: MUTE", 728, 17, SMALL, MUTED)
    draw_text(SCREEN, f"SCENE {scene['number']}: {scene['title']}", 850, 15, FONT, PALE)

def blit_cover(surface, image, rect):
    iw, ih = image.get_size()
    scale = max(rect.width / iw, rect.height / ih)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    scaled = pygame.transform.smoothscale(image, new_size)
    sx = max(0, (scaled.get_width() - rect.width) // 2)
    sy = max(0, (scaled.get_height() - rect.height) // 2)
    surface.blit(scaled, rect.topleft, area=pygame.Rect(sx, sy, rect.width, rect.height))


def draw_portrait(surface, person, rect):
    img = PORTRAITS.get(person)
    if img:
        blit_cover(surface, img, rect)
    else:
        pygame.draw.rect(surface, (16, 37, 48), rect)
        draw_text(surface, person, rect.x+16, rect.y+rect.height//2, SMALL, GOLD)
    pygame.draw.rect(surface, LINE, rect, 1, border_radius=4)


def draw_sidebar(state, inventory_rects):
    panel(SCREEN, SIDEBAR)
    name=state["character"]
    c=CHARACTERS[name]
    draw_portrait(SCREEN,name,pygame.Rect(SIDEBAR.x+12,SIDEBAR.y+11,194,145))
    draw_text(SCREEN,CHARACTER_DETAILS[name]["name"],SIDEBAR.x+13,SIDEBAR.y+163,FONT,CYAN)
    draw_text(SCREEN,c["role"],SIDEBAR.x+13,SIDEBAR.y+187,SMALL,GOLD)
    y=SIDEBAR.y+209
    for trait,value in c["traits"].items():
        draw_text(SCREEN,trait,SIDEBAR.x+14,y,SMALL,MUTED)
        draw_text(SCREEN,str(value),SIDEBAR.right-28,y,SMALL,PALE)
        y+=20
    pygame.draw.line(SCREEN,LINE,(SIDEBAR.x+12,y+1),(SIDEBAR.right-12,y+1),1)
    y+=10
    draw_text(SCREEN,"INVENTORY",SIDEBAR.x+14,y,FONT,CYAN)
    y+=23
    # Only physical items are in inventory. Each item gets its own artwork icon.
    if not state["inventory"]:
        draw_text(SCREEN,"(empty)",SIDEBAR.x+14,y,SMALL,MUTED)
    for item in state["inventory"][-8:]:
        rect=pygame.Rect(SIDEBAR.x+12,y-1,SIDEBAR.width-24,19)
        if rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(SCREEN,(28,51,60),rect,border_radius=3)
        img=ITEM_IMAGES.get(item)
        if img:
            SCREEN.blit(pygame.transform.smoothscale(img,(18,18)),(SIDEBAR.x+15,y-1))
        else:
            pygame.draw.rect(SCREEN,GOLD,(SIDEBAR.x+16,y+3,14,14),1)
        draw_text(SCREEN,item,SIDEBAR.x+38,y+1,TINY,PALE)
        inventory_rects.append((rect,item))
        y+=17
    # Keep the inventory and health areas separated as items are added.
    clue_y = SIDEBAR.bottom-108
    pygame.draw.line(SCREEN,LINE,(SIDEBAR.x+12,clue_y),(SIDEBAR.right-12,clue_y),1)
    draw_text(SCREEN,f"CLUES FOUND: {len(state['clues'])}",SIDEBAR.x+14,clue_y+10,SMALL,CYAN)
    if state["clues"]:
        clue=sorted(state["clues"])[-1].replace("_"," ")
        draw_text(SCREEN,clue[:26],SIDEBAR.x+14,clue_y+31,TINY,PALE)
    draw_text(SCREEN,"WOUNDED" if state["health"]<50 else "HEALTH",SIDEBAR.x+14,SIDEBAR.bottom-57,SMALL,RED if state["health"]<50 else CYAN)
    pygame.draw.rect(SCREEN,(27,40,48),(SIDEBAR.x+14,SIDEBAR.bottom-33,SIDEBAR.width-28,11),border_radius=3)
    hw=max(0,int((SIDEBAR.width-28)*state["health"]/100))
    if hw:
        pygame.draw.rect(SCREEN,GREEN if state["health"]>35 else RED,(SIDEBAR.x+14,SIDEBAR.bottom-33,hw,11),border_radius=3)
    draw_text(SCREEN,f"{state['health']}%",SIDEBAR.right-50,SIDEBAR.bottom-58,TINY,PALE)

def draw_scene_background(state):
    panel(SCREEN, SCENE_RECT)
    img = SCENE_IMAGES.get(state["scene"])
    if img:
        SCREEN.blit(img, SCENE_RECT.topleft)
        wash = pygame.Surface(SCENE_RECT.size, pygame.SRCALPHA)
        wash.fill((0,0,0,28))
        SCREEN.blit(wash, SCENE_RECT.topleft)
    else:
        pygame.draw.rect(SCREEN, (12,24,35), SCENE_RECT)
    draw_killer(state)
    pygame.draw.rect(SCREEN, LINE, SCENE_RECT, 1)


def killer_screen_rect(state):
    x,y,w,h=KILLER_PLACEMENTS[state["scene"]]
    return pygame.Rect(SCENE_RECT.x+x,SCENE_RECT.y+y,w,h)


def draw_killer(state):
    if KILLER_IMAGE is None or not state.get("killer_visible") or state.get("encounter") is None:
        return
    rect = killer_screen_rect(state)
    halo = pygame.Surface((rect.width+80, rect.height+70), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, (210, 230, 255, 42), halo.get_rect())
    SCREEN.blit(halo, (rect.x-40, rect.y-35))
    scaled = pygame.transform.smoothscale(KILLER_IMAGE, rect.size)
    scaled.set_alpha(238)
    SCREEN.blit(scaled, rect.topleft)
    draw_text(SCREEN, "THE WATCHER", rect.x-2, max(SCENE_RECT.y+5, rect.y-24), SMALL, WHITE)


def draw_hotspots(state):
    mouse = pygame.mouse.get_pos()
    state["hover_hint"] = ""
    if state.get("killer_visible") and state.get("encounter") is not None and killer_screen_rect(state).collidepoint(mouse):
        state["hover_hint"] = "The Watcher is in front of you now. Pick a response in the encounter panel."
        draw_text(SCREEN, "THE WATCHER", killer_screen_rect(state).x, max(SCENE_RECT.y+4, killer_screen_rect(state).y-24), SMALL, WHITE)
    for spot in SCENES[state["scene"]]["hotspots"]:
        x, y, w, h = spot["rect"]
        rect = pygame.Rect(SCENE_RECT.x+x, SCENE_RECT.y+y, w, h)
        if rect.collidepoint(mouse):
            pygame.draw.rect(SCREEN, CYAN, rect, 2, border_radius=5)
            label_w = min(210, FONT.size(spot["label"])[0] + 18)
            label_rect = pygame.Rect(rect.centerx-label_w//2, max(SCENE_RECT.y+6, rect.y-28), label_w, 23)
            pygame.draw.rect(SCREEN, (4, 13, 21), label_rect, border_radius=4)
            pygame.draw.rect(SCREEN, CYAN, label_rect, 1, border_radius=4)
            draw_text(SCREEN, spot["label"], label_rect.x+8, label_rect.y+3, SMALL, WHITE)
            state["hover_hint"] = spot["hint"]


def draw_narrative(state):
    panel(SCREEN, NARRATIVE)
    draw_text(SCREEN, "FIELD NOTES", NARRATIVE.x+14, NARRATIVE.y+13, FONT, CYAN)
    y = NARRATIVE.y + 42
    for paragraph in SCENES[state["scene"]]["description"]:
        if paragraph.strip():
            y = draw_wrapped(SCREEN, paragraph, pygame.Rect(NARRATIVE.x+14, y, NARRATIVE.width-28, 80), SMALL, PALE, 3) + 6
        else:
            y += 6
    pygame.draw.line(SCREEN, LINE, (NARRATIVE.x+12, y+4), (NARRATIVE.right-12, y+4), 1)
    y += 16
    draw_text(SCREEN, "LATEST RESULT", NARRATIVE.x+14, y, TINY, GOLD)
    y += 18
    latest = state["message"]
    usable_h=max(0,NARRATIVE.bottom-63-y)
    max_lines=max(0,min(9,int(usable_h/(SMALL.get_linesize()+3))))
    if max_lines:
        draw_wrapped(SCREEN, latest, pygame.Rect(NARRATIVE.x+14,y,NARRATIVE.width-28,usable_h),SMALL,PALE,3,max_lines=max_lines)
    pygame.draw.rect(SCREEN,PANEL,(NARRATIVE.x+9,NARRATIVE.bottom-46,NARRATIVE.width-18,37))
    draw_text(SCREEN,f"DECISIONS LEFT: {state['decisions']}",NARRATIVE.x+14,NARRATIVE.bottom-30,FONT,CYAN)

def action_cards_for_scene(state):
    choices={
        "road":[("Inspect footprints","tracks"),("Search glove box","glovebox"),("Enter the estate","gate"),("Hide and listen","listen")],
        "hall":[("Read the note","read_note"),("Inspect portrait","portrait"),("Go to dining room","dining"),("Take staircase","stairs")],
        "dining":[("Search pantry","pantry"),("Check window","window"),("Read message","message"),("Search sideboard","sideboard")],
        "study":[("Read ledger","ledger"),("Inspect fuse panel","panel"),("Search bookcase","bookcase"),("Open desk drawer","drawer")],
        "basement":[("Inspect generator","generator"),("Try steel door","steeldoor"),("Count tally marks","tallies")],
        "yard":[("Break service gate","service_gate"),("Search shed","shed"),("Read footprints","yard_tracks")],
        "landing":[("Check floorboard","landing_floor"),("Inspect railing","landing_rail"),("Open cabinet","landing_cabinet"),("Try nursery door","landing_door")],
        "nursery":[("Inspect cradle","nursery_cradle"),("Read child's diary","nursery_diary"),("Wind music box","nursery_music"),("Check window","nursery_window")],
        "greenhouse":[("Search workbench","greenhouse_tools"),("Adjust pipes","greenhouse_heat"),("Escape via roof","greenhouse_glass"),("Inspect roots","greenhouse_roots")],
        "chapel":[("Inspect altar","chapel_altar"),("Take candle","chapel_candle"),("Ring old bell","chapel_bell"),("Read prayer","chapel_prayer")],
        "crypt":[("Open sarcophagus","crypt_coffin"),("Take ritual page","crypt_page"),("Read names","crypt_names"),("Seal the tomb","crypt_seal")],
    }
    actions=choices[state["scene"]][:]
    if state["scene"]=="yard" and "Maintenance Log" in state["inventory"] and "victim_count" in state["clues"]:
        actions.append(("Confront the ghost","confront"))
    return actions


def draw_bottom(state, button_rects):
    panel(SCREEN, BOTTOM)
    draw_text(SCREEN, "AVAILABLE ACTIONS", BOTTOM.x+18, BOTTOM.y+15, FONT, CYAN)
    info=pygame.Rect(BOTTOM.x+16,BOTTOM.y+36,285,90)
    pygame.draw.rect(SCREEN,(11,27,38),info,border_radius=6)
    pygame.draw.rect(SCREEN,LINE,info,1,border_radius=6)
    draw_text(SCREEN,"SCENE HINT",info.x+12,info.y+9,TINY,GOLD)
    hint=state["hover_hint"] or "Use PATHS to explore, MAP to track rooms, and BACK to retrace your steps. Decisions do not reset."
    draw_wrapped(SCREEN,hint,pygame.Rect(info.x+12,info.y+28,info.width-24,48),SMALL,PALE,2,max_lines=3)
    actions=action_cards_for_scene(state)
    mouse=pygame.mouse.get_pos()
    bw,bh,gap=128,88,8
    start_x=BOTTOM.x+330
    for i,(label,action) in enumerate(actions[:5]):
        rect=pygame.Rect(start_x+i*(bw+gap),BOTTOM.y+34,bw,bh)
        hovered=rect.collidepoint(mouse)
        travel=action in ("gate","dining","stairs","steeldoor")
        button(SCREEN,rect,label,hovered,travel or state["decisions"]>0)
        button_rects.append((rect,action))
    rpaths=pygame.Rect(BOTTOM.right-145,BOTTOM.y+34,125,26)
    rmap=pygame.Rect(BOTTOM.right-145,BOTTOM.y+64,125,26)
    rback=pygame.Rect(BOTTOM.right-145,BOTTOM.y+94,125,28)
    if state["game_over"]:
        button(SCREEN,rpaths,"PLAY AGAIN",rpaths.collidepoint(mouse),True,font=SMALL)
        button_rects.append((rpaths,"restart"))
    else:
        button(SCREEN,rpaths,"PATHS",rpaths.collidepoint(mouse),True,font=SMALL)
        button(SCREEN,rmap,"MAP",rmap.collidepoint(mouse),True,font=SMALL)
        button(SCREEN,rback,"BACK",rback.collidepoint(mouse),True,font=SMALL)
        button_rects.append((rpaths,"paths"))
        button_rects.append((rmap,"map"))
        button_rects.append((rback,"back"))


def draw_routes(state):
    """Modal path chooser. Every row is independently clickable without costs."""
    veil=pygame.Surface(SCENE_RECT.size,pygame.SRCALPHA)
    veil.fill((2,9,16,202))
    SCREEN.blit(veil,SCENE_RECT.topleft)
    rect=pygame.Rect(330,109,620,470)
    panel(SCREEN,rect,fill=(8,21,31),border=GOLD,radius=8)
    draw_text(SCREEN,"CHOOSE YOUR NEXT PATH",rect.x+27,rect.y+25,TITLE,GOLD)
    draw_text(SCREEN,"Travel is free. Used decisions stay used when you return.",rect.x+27,rect.y+62,SMALL,MUTED)
    mouse=pygame.mouse.get_pos()
    buttons=[]
    for i,(dest,label) in enumerate(ROUTES[state["scene"]]):
        item=pygame.Rect(rect.x+27,rect.y+103+i*62,rect.width-54,52)
        visited_scene = normalize_scene_id(dest)
        status=" [VISITED]" if visited_scene in state["visited"] else " [NEW]"
        button(SCREEN,item,label+status,item.collidepoint(mouse),True,font=SMALL)
        buttons.append((item,"route:"+dest))
    close=pygame.Rect(rect.x+27,rect.bottom-57,rect.width-54,38)
    button(SCREEN,close,"CLOSE PATHS",close.collidepoint(mouse),True,font=SMALL)
    buttons.append((close,"close_paths"))
    return buttons


def draw_map_overlay(state):
    veil = pygame.Surface((W, H), pygame.SRCALPHA)
    veil.fill((2, 8, 14, 212))
    SCREEN.blit(veil, (0, 0))
    rect = MAP_POPUP_RECT
    panel(SCREEN, rect, fill=(8,21,31), border=GOLD, radius=10)
    draw_text(SCREEN, "BLACKTHORN ESTATE MAP", rect.x+28, rect.y+20, TITLE, GOLD)
    draw_text(SCREEN, "Visited rooms remain revealed. Unvisited rooms stay obscured until you reach them.", rect.x+28, rect.y+55, SMALL, MUTED)
    inner = pygame.Rect(rect.x+18, rect.y+88, rect.width-36, rect.height-144)
    mouse = pygame.mouse.get_pos()
    buttons = []
    if MAP_IMAGE is not None:
        SCREEN.blit(pygame.transform.smoothscale(MAP_IMAGE, inner.size), inner.topleft)
    else:
        pygame.draw.rect(SCREEN, (20,30,40), inner)
    sx = inner.width / 1448.0
    sy = inner.height / 1086.0
    for scene_id, base in MAP_NODE_RECTS.items():
        bx, by, bw, bh = base
        node = pygame.Rect(int(inner.x + bx*sx), int(inner.y + by*sy), max(32, int(bw*sx)), max(24, int(bh*sy)))
        status = "current" if state["scene"] == scene_id else ("visited" if scene_id in state["visited"] else "unknown")
        if status == "current":
            fill = pygame.Surface(node.size, pygame.SRCALPHA)
            fill.fill((120, 42, 45, 95))
            SCREEN.blit(fill, node.topleft)
            pygame.draw.rect(SCREEN, RED, node, 3, border_radius=10)
            draw_text(SCREEN, MAP_LABELS[scene_id], node.x+10, node.y+node.height-30, SMALL, WHITE)
        elif status == "visited":
            fill = pygame.Surface(node.size, pygame.SRCALPHA)
            fill.fill((196, 162, 101, 45))
            SCREEN.blit(fill, node.topleft)
            pygame.draw.rect(SCREEN, GOLD, node, 2, border_radius=10)
            draw_text(SCREEN, MAP_LABELS[scene_id], node.x+10, node.y+node.height-28, SMALL, PALE)
        else:
            overlay = pygame.Surface(node.size, pygame.SRCALPHA)
            overlay.fill((3, 9, 15, 212))
            SCREEN.blit(overlay, node.topleft)
            pygame.draw.rect(SCREEN, (103, 114, 123), node, 2, border_radius=10)
            qx = node.centerx - FONT.size("?")[0] // 2
            qy = node.centery - FONT.get_linesize() // 2 - 4
            draw_text(SCREEN, "?", qx, qy, TITLE, PALE)
            draw_text(SCREEN, "UNVISITED", node.x+8, node.bottom-25, TINY, MUTED)
    footer = pygame.Rect(rect.x+18, rect.bottom-44, rect.width-36, 28)
    pygame.draw.rect(SCREEN, (10,20,29), footer, border_radius=5)
    draw_text(SCREEN, f"CURRENT ROOM: {MAP_LABELS[state['scene']]}    •    Press TAB or click CLOSE to dismiss the map.", footer.x+12, footer.y+6, SMALL, PALE)
    close = pygame.Rect(rect.right-165, rect.y+18, 140, 34)
    button(SCREEN, close, "CLOSE MAP", close.collidepoint(mouse), True, font=SMALL)
    buttons.append((close, "close_map"))
    return buttons

def draw_popup(state):
    popup = state.get("popup")
    if not popup or popup.get("ttl", 0) <= 0:
        return
    overlay = pygame.Surface(POPUP_RECT.size, pygame.SRCALPHA)
    overlay.fill((4, 10, 17, 230))
    SCREEN.blit(overlay, POPUP_RECT.topleft)
    pygame.draw.rect(SCREEN, popup["color"], POPUP_RECT, 2, border_radius=8)
    draw_text(SCREEN, popup["title"], POPUP_RECT.x+16, POPUP_RECT.y+14, TITLE, popup["color"])
    draw_wrapped(SCREEN, popup["text"], pygame.Rect(POPUP_RECT.x+16, POPUP_RECT.y+48, POPUP_RECT.width-32, POPUP_RECT.height-60), FONT, PALE, 3, max_lines=4)

def draw_menu_backdrop(darken=162):
    bg=SCENE_IMAGES.get("road")
    if bg:
        SCREEN.blit(pygame.transform.smoothscale(bg,(W,H)),(0,0))
    else:
        SCREEN.fill(INK)
    overlay=pygame.Surface((W,H),pygame.SRCALPHA)
    overlay.fill((1,8,14,darken))
    SCREEN.blit(overlay,(0,0))


def draw_main_menu():
    draw_menu_backdrop(143)
    panel(SCREEN,pygame.Rect(275,125,730,530),fill=(6,16,25),border=GOLD,radius=11)
    draw_text(SCREEN,"THE HOLLOW AT",418,175,BIG,PALE)
    draw_text(SCREEN,"BLACKTHORN",448,235,BIG,GOLD)
    draw_wrapped(SCREEN,"An illustrated, branching point-and-click survival horror story",pygame.Rect(395,311,510,80),FONT,MUTED)
    mouse=pygame.mouse.get_pos()
    entries=[(pygame.Rect(430,410,420,63),"BEGIN STORY","select"),
             (pygame.Rect(430,488,420,60),"QUIT","quit")]
    for rect,label,_ in entries:
        button(SCREEN,rect,label,rect.collidepoint(mouse),font=TITLE)
    draw_text(SCREEN,"11 illustrated locations  •  4 playable survivors  •  Multiple endings",315,599,SMALL,MUTED)
    return [(r,a) for r,_,a in entries]


def draw_character_select():
    draw_menu_backdrop(192)
    draw_text(SCREEN,"CHOOSE YOUR SURVIVOR",330,55,BIG,PALE)
    draw_text(SCREEN,"Select a character to examine their traits before confirming.",305,109,FONT,MUTED)
    cards=[]
    for i,name in enumerate(CHARACTERS):
        rect=pygame.Rect(62+i*305,164,269,485)
        hovered=rect.collidepoint(pygame.mouse.get_pos())
        panel(SCREEN,rect,(11,27,38) if hovered else PANEL,CYAN if hovered else LINE,7)
        draw_portrait(SCREEN,name,pygame.Rect(rect.x+10,rect.y+10,249,249))
        details=CHARACTER_DETAILS[name]
        draw_text(SCREEN,details["name"],rect.x+13,rect.y+268,TITLE,PALE)
        draw_text(SCREEN,CHARACTERS[name]["role"],rect.x+14,rect.y+300,SMALL,GOLD)
        y=rect.y+334
        for trait,value in CHARACTERS[name]["traits"].items():
            draw_text(SCREEN,trait,rect.x+14,y,SMALL,MUTED)
            draw_text(SCREEN,"■ "*value,rect.x+142,y,SMALL,CYAN)
            y+=24
        button(SCREEN,pygame.Rect(rect.x+13,rect.bottom-48,rect.width-26,36),"VIEW CHARACTER",hovered)
        cards.append((rect,name))
    back=pygame.Rect(62,698,165,48)
    button(SCREEN,back,"BACK",back.collidepoint(pygame.mouse.get_pos()))
    return cards,[(back,"title")]


def draw_character_confirm(name):
    draw_menu_backdrop(203)
    panel(SCREEN,pygame.Rect(55,110,1170,590),fill=(7,19,29),border=GOLD,radius=8)
    draw_text(SCREEN,"CONFIRM YOUR CHARACTER",410,55,BIG,PALE)
    draw_portrait(SCREEN,name,pygame.Rect(83,147,350,420))
    details=CHARACTER_DETAILS[name]
    c=CHARACTERS[name]
    draw_text(SCREEN,details["name"],470,146,BIG,CYAN)
    draw_text(SCREEN,c["role"],470,193,FONT,GOLD)
    draw_text(SCREEN,"BACKSTORY",470,250,FONT,GOLD)
    draw_wrapped(SCREEN,details["summary"],pygame.Rect(470,284,700,125),FONT,PALE,6,max_lines=5)
    draw_text(SCREEN,"ATTRIBUTES",470,401,FONT,GOLD)
    y=438
    for trait,value in c["traits"].items():
        draw_text(SCREEN,trait,470,y,FONT,PALE)
        for dot in range(3):
            pygame.draw.rect(SCREEN,CYAN if dot<value else (45,65,72),(640+dot*41,y,30,14),border_radius=3)
        draw_text(SCREEN,f"{value}/3",785,y,SMALL,PALE)
        y+=33
    draw_text(SCREEN,"STRENGTHS",865,412,SMALL,GREEN)
    draw_wrapped(SCREEN,details["strengths"],pygame.Rect(865,440,300,76),SMALL,PALE,max_lines=3)
    draw_text(SCREEN,"WEAKNESSES",865,522,SMALL,RED)
    draw_wrapped(SCREEN,details["weaknesses"],pygame.Rect(865,548,300,80),SMALL,PALE,max_lines=3)
    back=pygame.Rect(100,608,280,62)
    go=pygame.Rect(740,608,426,62)
    mouse=pygame.mouse.get_pos()
    button(SCREEN,back,"CHANGE CHARACTER",back.collidepoint(mouse),font=FONT)
    button(SCREEN,go,"START AS "+name.upper(),go.collidepoint(mouse),font=TITLE)
    return [(back,"select"),(go,"start")]

def draw_encounter(state):
    scene=state.get("encounter")
    if scene is None:
        return []
    title,desc,choices=ENCOUNTERS[scene]
    x,y,w,h=315,414,650,198
    shade=pygame.Surface((w,h),pygame.SRCALPHA)
    shade.fill((7,13,23,239))
    SCREEN.blit(shade,(x,y))
    pygame.draw.rect(SCREEN,RED,(x,y,w,h),2,border_radius=7)
    draw_text(SCREEN,"!  "+title.upper(),x+18,y+15,TITLE,RED)
    draw_wrapped(SCREEN,desc,pygame.Rect(x+18,y+54,w-36,56),SMALL,PALE,2,max_lines=2)
    boxes=[]
    for i,label in enumerate(choices):
        rect=pygame.Rect(x+15+i*210,y+117,201,64)
        button(SCREEN,rect,label,rect.collidepoint(pygame.mouse.get_pos()),font=SMALL)
        boxes.append((rect,i))
    return boxes

def draw_game_over(state):
    overlay = pygame.Surface((W,H), pygame.SRCALPHA)
    overlay.fill((0,0,0,185))
    SCREEN.blit(overlay,(0,0))
    rect = pygame.Rect(230, 230, 820, 300)
    panel(SCREEN, rect, (6, 15, 23), RED if state["health"] <= 0 else GOLD, 8)
    title = state.get("ending_title") or ("GAME OVER" if state["health"] <= 0 else "ENDING")
    img = BIG.render(title, True, RED if state["health"] <= 0 else GOLD)
    SCREEN.blit(img, (rect.centerx-img.get_width()//2, rect.y+34))
    lines = wrap_text(state["ending"] or state["message"], FONT, rect.width-80)
    y = rect.y+105
    for line in lines[:6]:
        img = FONT.render(line, True, PALE)
        SCREEN.blit(img, (rect.centerx-img.get_width()//2,y))
        y += 27
    restart_rect=pygame.Rect(rect.centerx-150,rect.bottom-76,300,49)
    button(SCREEN,restart_rect,"RETURN TO MAIN MENU",restart_rect.collidepoint(pygame.mouse.get_pos()),True,SMALL)
    BUTTON_RECTS.append((restart_rect,"restart"))

STATE = None
MODE = "title"
SELECTED = None
BUTTON_RECTS = []
CHAR_CARDS = []
MENU_BUTTONS = []
INVENTORY_BUTTONS = []
ENCOUNTER_BUTTONS = []
ROUTE_BUTTONS = []
MAP_BUTTONS = []

def main():
    global STATE, MODE, SELECTED, BUTTON_RECTS, CHAR_CARDS, MENU_BUTTONS, INVENTORY_BUTTONS, ENCOUNTER_BUTTONS, ROUTE_BUTTONS, MAP_BUTTONS
    running=True
    while running:
        dt=CLOCK.tick(FPS)/1000.0
        SCENE_AUDIO.update(dt)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if MODE=="game" and STATE and STATE.get("map_open"):
                        STATE["map_open"] = False
                    elif MODE=="game" and STATE and STATE.get("navigation_open"):
                        STATE["navigation_open"]=False
                    elif MODE=="game" and STATE and STATE.get("encounter") is None:
                        MODE="title"; STATE=None; SCENE_AUDIO.stop()
                    elif MODE=="confirm":
                        MODE="select"
                    elif MODE=="select":
                        MODE="title"
                    else:
                        running=False
                elif event.key==pygame.K_m:
                    SCENE_AUDIO.toggle_mute()
                elif event.key==pygame.K_TAB and MODE=="game" and STATE and not STATE["game_over"] and not STATE.get("encounter"):
                    perform_action(STATE,"map");play_sfx()
                elif event.key==pygame.K_SPACE and MODE=="game" and STATE and not STATE["game_over"] and not STATE.get("encounter"):
                    perform_action(STATE,"paths");play_sfx()
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if MODE=="title":
                    for rect,action in MENU_BUTTONS:
                        if rect.collidepoint(event.pos):
                            if action=="quit":running=False
                            elif action=="select":MODE="select"
                            play_sfx();break
                elif MODE=="select":
                    handled=False
                    for rect,action in MENU_BUTTONS:
                        if rect.collidepoint(event.pos):
                            MODE=action;play_sfx();handled=True;break
                    if not handled:
                        for rect,name in CHAR_CARDS:
                            if rect.collidepoint(event.pos):
                                SELECTED=name;MODE="confirm";play_sfx();break
                elif MODE=="confirm":
                    for rect,action in MENU_BUTTONS:
                        if rect.collidepoint(event.pos):
                            if action=="start" and SELECTED:
                                STATE=new_game(SELECTED);MODE="game"
                            elif action=="select":MODE="select"
                            play_sfx();break
                elif MODE=="game" and STATE:
                    if STATE["game_over"]:
                        for rect,action in BUTTON_RECTS:
                            if action=="restart" and rect.collidepoint(event.pos):
                                SCENE_AUDIO.stop();STATE=None;MODE="title";play_sfx();break
                        continue
                    # Encounters are a modal: normal buttons and hotspots cannot
                    # be activated until the urgent choice is resolved.
                    if STATE.get("encounter") is not None:
                        for rect,idx in ENCOUNTER_BUTTONS:
                            if rect.collidepoint(event.pos):
                                encounter_choice(STATE,idx);play_sfx();break
                        continue
                    if STATE.get("map_open"):
                        for rect,action in MAP_BUTTONS:
                            if rect.collidepoint(event.pos):
                                perform_action(STATE,action);play_sfx();break
                        continue
                    if STATE.get("navigation_open"):
                        for rect,action in ROUTE_BUTTONS:
                            if rect.collidepoint(event.pos):
                                perform_action(STATE,action);play_sfx();break
                        continue
                    used=False
                    for rect,item in INVENTORY_BUTTONS:
                        if rect.collidepoint(event.pos):
                            use_item(STATE,item);play_sfx();used=True;break
                    if used:continue
                    for rect,action in BUTTON_RECTS:
                        if rect.collidepoint(event.pos):
                            perform_action(STATE,action);play_sfx();used=True;break
                    if used:continue
                    for spot in SCENES[STATE["scene"]]["hotspots"]:
                        x,y,w,h=spot["rect"]
                        rect=pygame.Rect(SCENE_RECT.x+x,SCENE_RECT.y+y,w,h)
                        if rect.collidepoint(event.pos):
                            perform_action(STATE,spot["action"]);play_sfx();break
        if MODE=="game" and STATE and not STATE["game_over"] and STATE.get("encounter_pending"):
            STATE["encounter_delay"]-=dt
            if STATE["encounter_delay"]<=1.8 and not STATE.get("encounter_warned"):
                STATE["encounter_warned"]=True
                if STATE.get("encounter_warning"):
                    set_feedback(STATE,"THE WATCHER IS NEAR",STATE["encounter_warning"],RED)
            if STATE["encounter_delay"]<=0:
                trigger_encounter(STATE,STATE["encounter_pending"])
        if MODE=="game" and STATE and STATE.get("popup") and STATE["popup"].get("ttl",0)>0:
            STATE["popup"]["ttl"]-=1
        SCREEN.fill(INK)
        if MODE=="title":
            MENU_BUTTONS=draw_main_menu()
        elif MODE=="select":
            CHAR_CARDS,MENU_BUTTONS=draw_character_select()
        elif MODE=="confirm":
            MENU_BUTTONS=draw_character_confirm(SELECTED)
        elif MODE=="game" and STATE:
            draw_header(STATE)
            INVENTORY_BUTTONS=[]
            draw_sidebar(STATE,INVENTORY_BUTTONS)
            draw_scene_background(STATE)
            draw_hotspots(STATE)
            draw_narrative(STATE)
            BUTTON_RECTS=[]
            draw_bottom(STATE,BUTTON_RECTS)
            if STATE["game_over"]:
                draw_game_over(STATE)
            elif STATE.get("encounter"):
                ENCOUNTER_BUTTONS=draw_encounter(STATE)
            else:
                ENCOUNTER_BUTTONS=[]
                if STATE.get("map_open"):
                    MAP_BUTTONS = draw_map_overlay(STATE)
                    ROUTE_BUTTONS=[]
                elif STATE.get("navigation_open"):
                    MAP_BUTTONS=[]
                    ROUTE_BUTTONS=draw_routes(STATE)
                else:
                    MAP_BUTTONS=[]
                    ROUTE_BUTTONS=[]
                    draw_popup(STATE)
        pygame.display.flip()
    SCENE_AUDIO.stop()
    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()
