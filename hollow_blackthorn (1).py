
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

# ----------------------------- Assets ----------------------------------------
SCENE_IMAGES = {}
SCENE_FILES = {
    "road": "road.png",
    "hall": "hall.png",
    "dining": "dining.png",
    "study": "study.png",
    "basement": "basement.png",
    "yard": "yard.png",
}
for key, filename in SCENE_FILES.items():
    try:
        img = pygame.image.load(str(ASSET_DIR / filename)).convert()
        SCENE_IMAGES[key] = pygame.transform.smoothscale(img, SCENE_RECT.size)
    except (pygame.error, FileNotFoundError):
        pass

# Each room has its own 20-second seamless-style ambience loop. Two dedicated
# mixer channels crossfade between rooms; interaction sounds play separately.
AMBIENCE_FILES = {
    "road": "road_ambience.wav",
    "hall": "hall_ambience.wav",
    "dining": "dining_ambience.wav",
    "study": "study_ambience.wav",
    "basement": "basement_ambience.wav",
    "yard": "yard_ambience.wav",
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
            {"label": "Footprints", "rect": (365, 320, 110, 210), "hint": "Bootprints lead from the road toward the estate.", "action": "tracks"},
            {"label": "Gate", "rect": (575, 120, 175, 235), "hint": "The Blackthorn gate stands open toward the mansion.", "action": "gate"},
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
            {"label": "Staircase", "rect": (460, 110, 260, 285), "hint": "The staircase looks old, broad, and treacherously loud.", "action": "stairs"},
            {"label": "Portrait", "rect": (635, 70, 140, 200), "hint": "Someone slashed every face in the family portrait.", "action": "portrait"},
            {"label": "Note", "rect": (610, 410, 155, 100), "hint": "A folded note lies on the narrow table below the portrait.", "action": "read_note"},
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
            {"label": "Pantry", "rect": (350, 85, 140, 165), "hint": "A warm crack of light spills from the pantry beyond.", "action": "pantry"},
            {"label": "Window", "rect": (580, 70, 185, 260), "hint": "Moonlight pours through the rain-streaked window.", "action": "window"},
            {"label": "Scratched message", "rect": (420, 300, 230, 130), "hint": "Fresh scratches mark the polished tabletop.", "action": "message"},
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
            {"label": "Desk ledger", "rect": (330, 250, 260, 145), "hint": "The open maintenance ledger is lit by a warm lamp.", "action": "ledger"},
            {"label": "Desk drawer", "rect": (530, 360, 210, 160), "hint": "A lower desk drawer is jammed partway open.", "action": "drawer"},
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
            {"label": "Generator", "rect": (560, 215, 215, 210), "hint": "The generator coughs, rattles, and spits sparks.", "action": "generator"},
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
            {"label": "Service gate", "rect": (560, 110, 220, 290), "hint": "The iron service gate is chained shut.", "action": "service_gate"},
        ],
    },
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
        "scene": "road",
        "decisions": SCENES["road"]["limit"],
        "inventory": [],
        "clues": set(),
        "flags": set(),
        "health": 100,
        "message": "Click an object in the scene or use an action card below.",
        "hover_hint": "",
        "game_over": False,
        "ending": "",
        "visited": {"road"},
        "popup": new_popup("Blackthorn", "The storm drives you toward the estate.", GOLD),
        "last_action": None,
    }

def current_character(state):
    return CHARACTERS[state["character"]]

def set_feedback(state, title, text, color=CYAN):
    state["message"] = text
    state["popup"] = new_popup(title, text, color)

def enter_scene(state, scene_id, feedback=None):
    state["scene"] = scene_id
    SCENE_AUDIO.enter(scene_id)
    state["decisions"] = SCENES[scene_id]["limit"]
    state["visited"].add(scene_id)
    if feedback is None:
        feedback = f"You enter: {SCENES[scene_id]['title']}."
    set_feedback(state, SCENES[scene_id]["title"], feedback, GOLD)

def end_game(state, ending, fatal=False):
    state["game_over"] = True
    state["ending"] = ending
    state["message"] = ending
    state["popup"] = new_popup("Game Over" if fatal else "Ending", ending, RED if fatal else GOLD)
    if fatal:
        state["health"] = 0

def spend_decision(state):
    if state["decisions"] <= 0:
        set_feedback(state, "No Decisions Left", "You have no decisions left in this scene. Click Continue to move on.", GOLD)
        return False
    state["decisions"] -= 1
    return True

def add_item(state, item):
    if item not in state["inventory"]:
        state["inventory"].append(item)

def add_clue(state, clue):
    state["clues"].add(clue)

def auto_advance(state):
    if state["scene"] == "road":
        enter_scene(state, "hall", "You hurry inside the manor before whatever is in the trees reaches the road.")
    elif state["scene"] == "hall":
        enter_scene(state, "dining", "The double doors give way and the dining room yawns open beyond them.")
    elif state["scene"] == "dining":
        enter_scene(state, "study", "A quieter passage leads you from the dining room into a private study.")
    elif state["scene"] == "study":
        enter_scene(state, "basement", "A hidden route and a service stair carry you down into the basement.")
    elif state["scene"] == "basement":
        enter_scene(state, "yard", "A final door releases you into the rear yard behind the house.")
    elif state["scene"] == "yard":
        if "Maintenance Log" in state["inventory"] and "victim_count" in state["clues"]:
            set_feedback(state, "Final Choice", "You have enough evidence to confront the killer—or flee through the storm.", GOLD)
        else:
            set_feedback(state, "No More Time", "The yard is your last chance. Escape now or prepare to face the killer.", GOLD)


def act(state, action):
    if state["game_over"]:
        return
    if action == "continue":
        auto_advance(state)
        return

    if not spend_decision(state):
        return

    char = current_character(state)
    scene = state["scene"]
    state["last_action"] = action

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
                add_clue(state, "pipe_clicking")
                set_feedback(state, "Pantry Searched", "The clicking comes from a loose pipe. Behind a crate, you recover a stained kitchen knife.", GREEN)
            else:
                set_feedback(state, "Pantry Empty", "Only dusty jars and the same rattling pipe wait in the pantry now.", MUTED)
        elif action == "window":
            if char["traits"]["Strength"] >= 3:
                state["flags"].add("window_broken")
                state["health"] = max(0, state["health"] - 10)
                set_feedback(state, "Window Forced", "You wrench the swollen frame apart, cutting your palm. The drop outside is steep and littered with broken stone.", RED)
            else:
                state["flags"].add("killer_alerted")
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
                add_clue(state, "power_routes")
                set_feedback(state, "Panel Isolated", "You isolate a live wire. Lights die elsewhere in the manor, and far below you hear a magnetic lock release.", GREEN)
            else:
                state["health"] -= 15
                state["flags"].add("killer_alerted")
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
                set_feedback(state, "Wrong Lever", "The machine snarls louder when you touch it. Somewhere upstairs, something answers.", RED)
        elif action == "steeldoor":
            if "generator_disabled" in state["flags"] or "Brass Key" in state["inventory"]:
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
            if "Bolt Cutters" in state["inventory"] or "Kitchen Knife" in state["inventory"] or "Small Screwdriver" in state["inventory"] or char["traits"]["Strength"] >= 3:
                if "killer_alerted" in state["flags"] and char["traits"]["Stealth"] < 3:
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
                end_game(state, "You confront the killer with records, dates, and evidence. He emerges from the dark—no longer myth, no longer hidden—and the truth leaves Blackthorn with you.")
            else:
                state["health"] -= 50
                if state["health"] <= 0:
                    end_game(state, "You step into the yard and call for him. He answers from just behind you.", True)
                else:
                    end_game(state, "You survive the confrontation, but flee without proof of what happened at Blackthorn.")
        return

# ----------------------------- UI rendering ----------------------------------
def draw_header(state):
    pygame.draw.rect(SCREEN, DARK, (0, 0, W, HEADER_H))
    pygame.draw.line(SCREEN, LINE, (0, HEADER_H-1), (W, HEADER_H-1), 1)
    draw_text(SCREEN, "◈  THE HOLLOW AT BLACKTHORN", 18, 12, TITLE, CYAN)
    scene = SCENES[state["scene"]]
    draw_text(SCREEN, "M: UNMUTE" if SCENE_AUDIO.muted else "M: MUTE", 728, 17, SMALL, MUTED)
    draw_text(SCREEN, f"SCENE {scene['number']}: {scene['title']}", 850, 15, FONT, PALE)

def draw_sidebar(state):
    panel(SCREEN, SIDEBAR)
    name = state["character"]
    c = CHARACTERS[name]
    draw_text(SCREEN, name.upper(), SIDEBAR.x+14, SIDEBAR.y+14, TITLE, CYAN)
    draw_text(SCREEN, c["role"], SIDEBAR.x+14, SIDEBAR.y+47, SMALL, GOLD)
    y = SIDEBAR.y+78
    for trait, value in c["traits"].items():
        draw_text(SCREEN, trait, SIDEBAR.x+14, y, SMALL, MUTED)
        draw_text(SCREEN, str(value), SIDEBAR.right-28, y, SMALL, PALE)
        y += 23
    pygame.draw.line(SCREEN, LINE, (SIDEBAR.x+12,y+2),(SIDEBAR.right-12,y+2),1)
    y += 14
    draw_text(SCREEN, "INVENTORY", SIDEBAR.x+14, y, FONT, CYAN)
    y += 25
    if not state["inventory"]:
        draw_text(SCREEN, "— empty —", SIDEBAR.x+14, y, SMALL, MUTED)
        y += 20
    else:
        for item in state["inventory"][-6:]:
            for line in wrap_text("▪ " + item, SMALL, SIDEBAR.width - 28):
                draw_text(SCREEN, line, SIDEBAR.x+14, y, SMALL, PALE)
                y += 17
    y += 8
    pygame.draw.line(SCREEN, LINE, (SIDEBAR.x+12,y),(SIDEBAR.right-12,y),1)
    y += 12
    draw_text(SCREEN, "CLUES", SIDEBAR.x+14, y, FONT, CYAN)
    y += 25
    if not state["clues"]:
        draw_text(SCREEN, "— none found —", SIDEBAR.x+14, y, SMALL, MUTED)
    else:
        for clue in list(sorted(state["clues"]))[-5:]:
            label = clue.replace("_", " ")
            for line in wrap_text("▪ " + label, SMALL, SIDEBAR.width - 28):
                draw_text(SCREEN, line, SIDEBAR.x+14, y, SMALL, PALE)
                y += 17
            y += 2
    draw_text(SCREEN, "HEALTH", SIDEBAR.x+14, SIDEBAR.bottom-57, SMALL, CYAN)
    pygame.draw.rect(SCREEN, (27, 40, 48), (SIDEBAR.x+14,SIDEBAR.bottom-33,SIDEBAR.width-28,11), border_radius=3)
    hw = max(0, int((SIDEBAR.width-28)*state["health"]/100))
    pygame.draw.rect(SCREEN, GREEN if state["health"] > 35 else RED,
                     (SIDEBAR.x+14,SIDEBAR.bottom-33,hw,11), border_radius=3)
    draw_text(SCREEN, f"{state['health']}%", SIDEBAR.right-50, SIDEBAR.bottom-58, TINY, PALE)

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
    pygame.draw.rect(SCREEN, LINE, SCENE_RECT, 1)

def draw_hotspots(state):
    mouse = pygame.mouse.get_pos()
    state["hover_hint"] = ""
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
    y = draw_wrapped(SCREEN, latest, pygame.Rect(NARRATIVE.x+14, y, NARRATIVE.width-28, 132), SMALL, PALE, 3, max_lines=10)
    draw_text(SCREEN, f"DECISIONS LEFT: {state['decisions']}", NARRATIVE.x+14, NARRATIVE.bottom-30, FONT, CYAN)

def action_cards_for_scene(state):
    scene = state["scene"]
    if scene == "road":
        actions = [("Inspect footprints", "tracks"), ("Search glove box", "glovebox"), ("Approach gate", "gate"), ("Hide and listen", "listen")]
    elif scene == "hall":
        actions = [("Read the note", "read_note"), ("Inspect portrait", "portrait"), ("Open double doors", "dining"), ("Try staircase", "stairs")]
    elif scene == "dining":
        actions = [("Investigate pantry", "pantry"), ("Check window", "window"), ("Read message", "message"), ("Search sideboard", "sideboard")]
    elif scene == "study":
        actions = [("Read maintenance log", "ledger"), ("Inspect fuse panel", "panel"), ("Search bookcase", "bookcase"), ("Open desk drawer", "drawer")]
    elif scene == "basement":
        actions = [("Inspect generator", "generator"), ("Try steel door", "steeldoor"), ("Count tally marks", "tallies")]
    else:
        actions = [("Break service gate", "service_gate"), ("Search shed", "shed"), ("Read footprints", "yard_tracks")]
        if "Maintenance Log" in state["inventory"] and "victim_count" in state["clues"]:
            actions.append(("Confront killer", "confront"))
    return actions

def draw_bottom(state, button_rects):
    panel(SCREEN, BOTTOM)
    draw_text(SCREEN, "AVAILABLE ACTIONS", BOTTOM.x+18, BOTTOM.y+15, FONT, CYAN)
    draw_text(SCREEN, "Hover over objects in the scene or click a card below.", BOTTOM.x+18, BOTTOM.y+46, SMALL, PALE)
    hint = state["hover_hint"] or "Every interaction uses one decision. Continue always advances the story."
    draw_wrapped(SCREEN, hint, pygame.Rect(BOTTOM.x+18, BOTTOM.y+69, 255, 48), SMALL, MUTED, 2, max_lines=3)

    actions = action_cards_for_scene(state)
    mouse = pygame.mouse.get_pos()
    bw, bh, gap = 150, 88, 9
    start_x = BOTTOM.x + 290
    y = BOTTOM.y + 34
    for i, (label, action) in enumerate(actions[:5]):
        rect = pygame.Rect(start_x + i * (bw + gap), y, bw, bh)
        hovered = rect.collidepoint(mouse)
        button(SCREEN, rect, label, hovered, (state["decisions"] > 0 and not state["game_over"]))
        button_rects.append((rect, action))

    rect = pygame.Rect(BOTTOM.right-145, BOTTOM.y+34, 125, 88)
    hovered = rect.collidepoint(mouse)
    button(SCREEN, rect, "PLAY AGAIN" if state["game_over"] else "CONTINUE", hovered, True)
    button_rects.append((rect, "restart" if state["game_over"] else "continue"))

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

def draw_character_select():
    SCREEN.fill(INK)
    draw_text(SCREEN, "THE HOLLOW AT BLACKTHORN", 65, 55, BIG, CYAN)
    draw_text(SCREEN, "A point-and-click horror story", 68, 105, FONT, PALE)
    draw_text(SCREEN, "Choose who enters the house. Their traits change which actions are safest.", 68, 145, FONT, MUTED)
    cards = []
    names = list(CHARACTERS.keys())
    for i, name in enumerate(names):
        rect = pygame.Rect(65+i*295, 220, 260, 365)
        cards.append((rect, name))
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        panel(SCREEN, rect, PANEL2 if hovered else PANEL, CYAN if hovered else LINE, 7)
        c = CHARACTERS[name]
        draw_text(SCREEN, name.upper(), rect.x+18, rect.y+18, TITLE, CYAN)
        draw_text(SCREEN, c["role"], rect.x+18, rect.y+55, SMALL, GOLD)
        y = rect.y+95
        for trait, value in c["traits"].items():
            draw_text(SCREEN, trait, rect.x+18, y, SMALL, MUTED)
            draw_text(SCREEN, "●" * value, rect.x+145, y, SMALL, CYAN)
            y += 25
        y += 8
        for line in wrap_text(c["bio"], SMALL, rect.width-36):
            draw_text(SCREEN, line, rect.x+18, y, SMALL, PALE)
            y += 19
        y += 10
        for line in wrap_text(c["special"], SMALL, rect.width-36):
            draw_text(SCREEN, line, rect.x+18, y, SMALL, GOLD)
            y += 18
        button(SCREEN, pygame.Rect(rect.x+18, rect.bottom-55, rect.width-36, 38), "PLAY AS " + name, hovered)
    draw_text(SCREEN, "Controls: hover/click to interact • SPACE to continue • M to mute ambience • ESC to quit", 68, 660, FONT, MUTED)
    draw_text(SCREEN, "Each of the six rooms has its own atmospheric soundtrack and transitions smoothly.", 68, 692, FONT, PALE)
    return cards

def draw_game_over(state):
    overlay = pygame.Surface((W,H), pygame.SRCALPHA)
    overlay.fill((0,0,0,185))
    SCREEN.blit(overlay,(0,0))
    rect = pygame.Rect(230, 230, 820, 300)
    panel(SCREEN, rect, (6, 15, 23), RED if state["health"] <= 0 else GOLD, 8)
    title = "GAME OVER" if state["health"] <= 0 else "ENDING"
    img = BIG.render(title, True, RED if state["health"] <= 0 else GOLD)
    SCREEN.blit(img, (rect.centerx-img.get_width()//2, rect.y+34))
    lines = wrap_text(state["ending"] or state["message"], FONT, rect.width-80)
    y = rect.y+105
    for line in lines[:6]:
        img = FONT.render(line, True, PALE)
        SCREEN.blit(img, (rect.centerx-img.get_width()//2,y))
        y += 27
    draw_text(SCREEN, "Click PLAY AGAIN in the lower-right corner to choose another character.", rect.x+125, rect.bottom-50, SMALL, MUTED)

STATE = None
MODE = "select"
BUTTON_RECTS = []
CHAR_CARDS = []

def main():
    global STATE, MODE, BUTTON_RECTS, CHAR_CARDS
    running = True
    while running:
        dt = CLOCK.tick(FPS) / 1000.0
        SCENE_AUDIO.update(dt)

        # Click detection uses buttons drawn on the PREVIOUS frame. Clearing
        # the list here would make Continue and other button clicks do nothing.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    SCENE_AUDIO.toggle_mute()
                elif MODE == "game" and event.key == pygame.K_SPACE and not STATE["game_over"]:
                    act(STATE, "continue")
                    play_sfx()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if MODE == "select":
                    for rect, name in CHAR_CARDS:
                        if rect.collidepoint(event.pos):
                            STATE = new_game(name)
                            MODE = "game"
                            play_sfx()
                            break
                elif MODE == "game":
                    clicked = False
                    for rect, action in BUTTON_RECTS:
                        if rect.collidepoint(event.pos):
                            if action == "restart":
                                SCENE_AUDIO.stop()
                                MODE = "select"
                                STATE = None
                            else:
                                act(STATE, action)
                            play_sfx()
                            clicked = True
                            break
                    if clicked:
                        continue
                    if not STATE["game_over"]:
                        for spot in SCENES[STATE["scene"]]["hotspots"]:
                            x, y, w, h = spot["rect"]
                            rect = pygame.Rect(SCENE_RECT.x+x, SCENE_RECT.y+y, w, h)
                            if rect.collidepoint(event.pos):
                                act(STATE, spot["action"])
                                play_sfx()
                                break

        if MODE == "game" and STATE and STATE.get("popup") and STATE["popup"].get("ttl", 0) > 0:
            STATE["popup"]["ttl"] -= 1

        SCREEN.fill(INK)
        if MODE == "select":
            CHAR_CARDS = draw_character_select()
        else:
            draw_header(STATE)
            draw_sidebar(STATE)
            draw_scene_background(STATE)
            draw_hotspots(STATE)
            draw_narrative(STATE)
            # Rebuild clickable button hitboxes only AFTER processing events.
            BUTTON_RECTS = []
            draw_bottom(STATE, BUTTON_RECTS)
            draw_popup(STATE)
            if STATE["game_over"]:
                draw_game_over(STATE)
        pygame.display.flip()

    SCENE_AUDIO.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
