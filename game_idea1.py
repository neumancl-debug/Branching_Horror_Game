
import tkinter as tk
from tkinter import messagebox


# ==========================================================
# THE LAST WING
# A mouse-controlled branching horror story game
# ==========================================================

class LastWingGame:

    def __init__(self, window):
        self.window = window
        self.window.title("The Last Wing")
        self.window.geometry("850x720")
        self.window.minsize(700, 600)
        self.window.configure(bg="#151515")

        self.character = None
        self.inventory = []
        self.clues = []
        self.flags = set()

        self.scene = "intro"
        self.actions = 0
        self.game_finished = False
        self.message = ""

        # Character information and starting items.
        self.characters = {
            "Morgan": {
                "description": (
                    "The Observer\n"
                    "Notices hidden details and remembers small clues.\n"
                    "Weakness: struggles with heavy physical obstacles.\n"
                    "Starting item: Flashlight."
                ),
                "items": ["Flashlight"]
            },
            "Eli": {
                "description": (
                    "The Technician\n"
                    "Understands electronics, machinery, and locks.\n"
                    "Weakness: struggles with heavy physical obstacles.\n"
                    "Starting item: Multitool."
                ),
                "items": ["Multitool"]
            },
            "Riley": {
                "description": (
                    "The Athlete\n"
                    "Can move heavy objects and overcome physical obstacles.\n"
                    "Weakness: can overlook small clues.\n"
                    "Starting item: Athletic Gloves."
                ),
                "items": ["Athletic Gloves"]
            },
            "Avery": {
                "description": (
                    "The Empath\n"
                    "Understands behavior and recognizes deception.\n"
                    "Weakness: struggles with technical challenges.\n"
                    "Starting item: Old Journal."
                ),
                "items": ["Old Journal"]
            }
        }

        # Scene descriptions.
        self.scenes = {
            "room": {
                "title": "SCENE 1: THE PATIENT ROOM",
                "actions": 3,
                "description": (
                    "You awaken on a freezing tile floor. A fluorescent "
                    "light buzzes above you, casting a pale glow across "
                    "peeling wallpaper and a narrow metal bed.\n\n"
                    "A heavy steel door stands opposite you. Its keypad "
                    "has several worn buttons. Beside it, an old window "
                    "rattles in a corroded frame. A folded note is wedged "
                    "beneath the bed.\n\n"
                    "Then you hear footsteps outside. They stop directly "
                    "outside your door. Three slow knocks follow.\n\n"
                    "You have three actions before you must move on."
                )
            },

            "corridor": {
                "title": "SCENE 2: THE NORTH CORRIDOR",
                "actions": 3,
                "description": (
                    "The corridor stretches into darkness. Ceiling lights "
                    "flicker above abandoned wheelchairs and open doorways. "
                    "The air smells of wet concrete and old medicine.\n\n"
                    "A red EXIT sign hangs above a locked security door. "
                    "Farther down the hall, a records room stands open. "
                    "Something scrapes against the floor around the corner.\n\n"
                    "On the wall, someone has written: "
                    "'HE KNOWS WHEN THE LIGHTS GO OUT.'"
                )
            },

            "records": {
                "title": "SCENE 3: THE RECORDS ROOM",
                "actions": 2,
                "description": (
                    "Dust hangs in the beam of your light. Filing cabinets "
                    "lean at strange angles, and hundreds of patient files "
                    "cover the floor.\n\n"
                    "A cracked computer terminal blinks on a desk. One "
                    "drawer is jammed shut. On the wall is a list of "
                    "security incidents, the last entry dated only "
                    "three days ago.\n\n"
                    "A stairwell leads down to the basement. From below "
                    "comes the steady hum of an electrical generator."
                )
            },

            "maintenance": {
                "title": "SCENE 4: MAINTENANCE",
                "actions": 2,
                "description": (
                    "The maintenance room is hot and smells of burnt "
                    "plastic. A large breaker panel hums unevenly. Several "
                    "warning lights flash above a diagram of the building.\n\n"
                    "A heavy emergency door stands at the far end. A "
                    "workbench is covered with old supplies. Through a "
                    "small reinforced window, you see a shadow move "
                    "across the corridor behind you.\n\n"
                    "The building's emergency power is failing."
                )
            },

            "basement": {
                "title": "SCENE 5: THE BASEMENT",
                "actions": 2,
                "description": (
                    "Concrete stairs descend into a basement filled with "
                    "pipes and thick electrical cables. Water drips into "
                    "a shallow puddle beneath a broken light.\n\n"
                    "A security terminal stands beside a steel door. "
                    "An emergency exit sign points toward a narrow "
                    "passage. The terminal screen displays a warning:\n\n"
                    "'SECURITY LOCKDOWN ACTIVE. ACCESS REQUIRED.'\n\n"
                    "You hear a door slam somewhere above."
                )
            },

            "final": {
                "title": "SCENE 6: THE FINAL CHAMBER",
                "actions": 2,
                "description": (
                    "The basement passage opens into a wide concrete "
                    "chamber. A security control room sits to your left. "
                    "Straight ahead is an emergency exit with a small "
                    "card reader.\n\n"
                    "At the other end of the chamber, the killer steps "
                    "into the light. Their face is hidden behind a "
                    "dark mask. They have followed you through the "
                    "building.\n\n"
                    "There is no time to search for more supplies. "
                    "Your earlier decisions will determine your options."
                )
            }
        }

        # Each scene automatically advances to the next one when
        # the player uses all available actions.
        self.next_scene = {
            "room": "corridor",
            "corridor": "records",
            "records": "maintenance",
            "maintenance": "basement",
            "basement": "final"
        }

        self.show_intro()

    # ------------------------------------------------------
    # BASIC INTERFACE
    # ------------------------------------------------------

    def clear_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def make_label(self, parent, text, size=12, bold=False,
                   color="#eeeeee", justify="left"):
        font_style = "bold" if bold else "normal"

        label = tk.Label(
            parent,
            text=text,
            font=("Georgia", size, font_style),
            fg=color,
            bg="#151515",
            wraplength=770,
            justify=justify,
            anchor="w"
        )

        label.pack(fill="x", padx=22, pady=7)
        return label

    def make_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 11),
            fg="#ffffff",
            bg="#343434",
            activebackground="#555555",
            activeforeground="#ffffff",
            relief="raised",
            cursor="hand2",
            wraplength=720,
            padx=12,
            pady=9
        )

        button.pack(fill="x", padx=22, pady=4)
        return button

    def add_item(self, item):
        if item not in self.inventory:
            self.inventory.append(item)

    def add_clue(self, clue):
        if clue not in self.clues:
            self.clues.append(clue)

    # ------------------------------------------------------
    # INTRODUCTION AND CHARACTER SELECTION
    # ------------------------------------------------------

    def show_intro(self):
        self.clear_screen()

        self.make_label(
            self.window,
            "THE LAST WING",
            size=27,
            bold=True,
            color="#c0392b",
            justify="center"
        )

        self.make_label(
            self.window,
            "A branching survival horror story",
            size=14,
            color="#aaaaaa",
            justify="center"
        )

        story = (
            "BLACKTHORN MEDICAL INSTITUTE\n\n"
            "The hospital was closed after several patients and "
            "employees mysteriously disappeared. Official reports "
            "claimed the building was unsafe. Former employees "
            "whispered about something much worse.\n\n"
            "Tonight, you wake up inside one of its locked rooms. "
            "You remember being taken from a parking lot, but "
            "everything after that is a blur.\n\n"
            "A speaker crackles above you.\n\n"
            "'Patient recovered. Begin the final observation.'\n\n"
            "Footsteps approach from the corridor. You must search "
            "for clues, manage your limited actions, and decide "
            "whether to escape or stop the person hunting you.\n\n"
            "Your decisions matter. Some opportunities will not "
            "return, and some mistakes will end the story."
        )

        self.make_label(self.window, story, size=12)

        self.make_button(
            self.window,
            "BEGIN",
            self.show_character_select
        )

    def show_character_select(self):
        self.clear_screen()

        self.make_label(
            self.window,
            "CHOOSE YOUR CHARACTER",
            size=21,
            bold=True,
            color="#c0392b"
        )

        self.make_label(
            self.window,
            "Each character has different strengths and starting items."
        )

        for name, info in self.characters.items():
            self.make_label(
                self.window,
                name.upper() + "\n" + info["description"],
                size=11
            )

            self.make_button(
                self.window,
                "Play as " + name,
                lambda selected=name: self.start_game(selected)
            )

    def start_game(self, name):
        self.character = name
        self.inventory = self.characters[name]["items"].copy()
        self.clues = []
        self.flags = set()
        self.game_finished = False
        self.message = ""

        self.show_scene("room")

    # ------------------------------------------------------
    # SCENE DISPLAY
    # ------------------------------------------------------

    def show_scene(self, scene_name):
        self.scene = scene_name
        self.clear_screen()

        if scene_name in ("escape", "victory", "death"):
            self.show_ending(scene_name)
            return

        scene = self.scenes[scene_name]
        self.actions = scene["actions"]

        self.make_label(
            self.window,
            scene["title"],
            size=19,
            bold=True,
            color="#c0392b"
        )

        self.make_label(
            self.window,
            scene["description"],
            size=12
        )

        if self.message:
            self.make_label(
                self.window,
                self.message,
                size=11,
                bold=True,
                color="#e6c76a"
            )

        # Keep the inventory visible.
        inventory_text = (
            "INVENTORY: " +
            (", ".join(self.inventory) if self.inventory else "Empty")
        )

        clues_text = (
            "CLUES: " +
            (", ".join(self.clues) if self.clues else "None found")
        )

        self.make_label(
            self.window,
            inventory_text,
            size=10,
            color="#8ecae6"
        )

        self.make_label(
            self.window,
            clues_text,
            size=10,
            color="#a8d5a2"
        )

        self.status_label = self.make_label(
            self.window,
            "Actions remaining: " + str(self.actions),
            size=11,
            bold=True,
            color="#e6c76a"
        )

        # Use a frame so choices can be scrolled if needed.
        self.choice_frame = tk.Frame(
            self.window,
            bg="#151515"
        )
        self.choice_frame.pack(fill="both", expand=True, pady=5)

        self.show_choices()

    # ------------------------------------------------------
    # AVAILABLE CHOICES
    # ------------------------------------------------------

    def show_choices(self):
        # Remove old choice buttons.
        for widget in self.choice_frame.winfo_children():
            widget.destroy()

        choices = {
            "room": [
                ("Read the note beneath the bed", self.read_note),
                ("Inspect the keypad", self.inspect_keypad),
                ("Try to open the old window", self.open_window),
                ("Hide beneath the bed", self.hide),
                ("Call out into the corridor", self.call_out)
            ],

            "corridor": [
                ("Examine the writing on the wall", self.read_wall),
                ("Search the abandoned nurse station", self.search_station),
                ("Inspect the security door", self.inspect_security_door),
                ("Move quietly toward the records room",
                 self.enter_records)
            ],

            "records": [
                ("Read the patient files", self.read_records),
                ("Inspect the computer terminal", self.inspect_terminal),
                ("Force the jammed filing cabinet", self.open_cabinet),
                ("Go to the maintenance room", self.enter_maintenance)
            ],

            "maintenance": [
                ("Search the workbench", self.search_workbench),
                ("Inspect the breaker panel", self.inspect_breaker),
                ("Restore the emergency power", self.restore_power),
                ("Continue to the basement", self.enter_basement)
            ],

            "basement": [
                ("Use the security terminal", self.use_terminal),
                ("Search the security desk", self.search_security_desk),
                ("Try the emergency passage", self.try_passage),
                ("Enter the final chamber", self.enter_final)
            ],

            "final": [
                ("Try to escape through the emergency exit",
                 self.try_escape),
                ("Use the security controls against the killer",
                 self.stop_killer),
                ("Try to distract the killer and run",
                 self.distract_killer),
                ("Hide in the control room",
                 self.hide_final)
            ]
        }

        for label, command in choices.get(self.scene, []):
            self.make_button(
                self.choice_frame,
                label,
                command
            )

        self.make_button(
            self.choice_frame,
            "View collected notes",
            self.view_notes
        )

    # ------------------------------------------------------
    # ACTION SYSTEM
    # ------------------------------------------------------

    def take_action(self, result, item=None, clue=None,
                    flag=None, next_scene=None, fatal=False):
        if self.game_finished:
            return

        if item:
            self.add_item(item)

        if clue:
            self.add_clue(clue)

        if flag:
            self.flags.add(flag)

        self.message = result

        if fatal:
            self.show_scene("death")
            return

        # A choice can move the story forward immediately.
        if next_scene:
            self.show_scene(next_scene)
            return

        self.actions -= 1

        if self.actions <= 0:
            # The last action can be used, but there is no
            # additional action available in this scene.
            following_scene = self.next_scene.get(self.scene)

            if following_scene:
                self.message += (
                    "\n\nYou have used all your actions. "
                    "You must move forward."
                )
                self.show_scene(following_scene)
            else:
                self.show_scene("death")
        else:
            self.show_scene_same_scene()

    def show_scene_same_scene(self):
        old_scene = self.scene
        remaining = self.actions

        self.clear_screen()

        scene = self.scenes[old_scene]

        self.make_label(
            self.window,
            scene["title"],
            size=19,
            bold=True,
            color="#c0392b"
        )

        self.make_label(
            self.window,
            scene["description"],
            size=12
        )

        self.make_label(
            self.window,
            self.message,
            size=11,
            bold=True,
            color="#e6c76a"
        )

        self.make_label(
            self.window,
            "INVENTORY: " +
            (", ".join(self.inventory) if self.inventory else "Empty"),
            size=10,
            color="#8ecae6"
        )

        self.make_label(
            self.window,
            "CLUES: " +
            (", ".join(self.clues) if self.clues else "None found"),
            size=10,
            color="#a8d5a2"
        )

        self.make_label(
            self.window,
            "Actions remaining: " + str(remaining),
            size=11,
            bold=True,
            color="#e6c76a"
        )

        self.choice_frame = tk.Frame(
            self.window,
            bg="#151515"
        )
        self.choice_frame.pack(fill="both", expand=True, pady=5)

        self.show_choices()

    # ------------------------------------------------------
    # SCENE 1: PATIENT ROOM
    # ------------------------------------------------------

    def read_note(self):
        if "Victim's Note" in self.inventory:
            self.take_action(
                "You have already collected the note. "
                "It warns that the basement locks during power failures."
            )
            return

        self.take_action(
            "The paper is damp and creased. It reads:\n"
            "'The killer watches the cameras. The basement doors "
            "lock when the power fails. Find another way out.'",
            item="Victim's Note",
            clue="Basement doors lock during power failures",
            flag="read_note"
        )

    def inspect_keypad(self):
        if self.character == "Morgan":
            self.take_action(
                "You notice that three keypad buttons are more worn "
                "than the others. Someone repeatedly entered the "
                "same code. You record the pattern for later.",
                clue="Worn keypad buttons",
                flag="keypad_clue"
            )
        elif self.character == "Eli":
            self.take_action(
                "You recognize the keypad model. It connects to the "
                "building's central security system. A recovered "
                "access code could open connected doors.",
                clue="Electronic security system",
                flag="keypad_clue"
            )
        else:
            self.take_action(
                "The keypad is old, but its buttons still respond. "
                "Without a code, you cannot open the door."
            )

    def open_window(self):
        if self.character == "Riley":
            self.take_action(
                "You grip the rusted frame and force the window "
                "open enough to examine the outside wall. The drop "
                "is too far to climb down safely, but you discover "
                "a narrow exterior ledge.",
                clue="Exterior ledge",
                flag="ledge_found"
            )
        else:
            self.take_action(
                "You pull at the window frame. It barely moves. "
                "The rust has fused the frame to the wall, and "
                "you cannot open it."
            )

    def hide(self):
        self.take_action(
            "You squeeze beneath the bed and remain still. "
            "Footsteps pass the door. For now, you are safe, "
            "but you discover nothing useful."
        )

    def call_out(self):
        self.take_action(
            "Your voice echoes down the corridor. The footsteps "
            "stop. A moment later, the handle begins to turn. "
            "You retreat as the footsteps approach.",
            flag="killer_alerted"
        )

    # ------------------------------------------------------
    # SCENE 2: CORRIDOR
    # ------------------------------------------------------

    def read_wall(self):
        self.take_action(
            "The writing was scratched into the paint with "
            "something sharp. Beneath it, smaller letters read: "
            "'The cameras have blind spots near the nurse station.'",
            clue="Camera blind spots",
            flag="camera_clue"
        )

    def search_station(self):
        if "Keycard" in self.inventory:
            self.take_action(
                "The nurse station is empty. You already took "
                "the keycard from its drawer."
            )
        else:
            self.take_action(
                "You search beneath a stack of rotting folders "
                "and find an old staff keycard. Its magnetic strip "
                "is scratched, but it may still work.",
                item="Keycard",
                clue="Staff keycard"
            )

    def inspect_security_door(self):
        self.take_action(
            "The security door has an electronic reader. "
            "A small label says that staff keycards are accepted. "
            "You also see a mechanical release panel nearby.",
            clue="Security door needs access"
        )

    def enter_records(self):
        self.take_action(
            "You slip through the open records-room doorway "
            "and pull it almost shut behind you.",
            next_scene="records"
        )

    # ------------------------------------------------------
    # SCENE 3: RECORDS ROOM
    # ------------------------------------------------------

    def read_records(self):
        self.take_action(
            "The files describe repeated security failures. "
            "One report says the emergency exit remains powered "
            "even when the main building loses electricity. "
            "Another mentions a maintenance access code.",
            item="Patient Records",
            clue="Emergency exit has backup power",
            flag="records_read"
        )

    def inspect_terminal(self):
        if self.character == "Eli":
            self.take_action(
                "You reconnect a loose cable and recover a code "
                "from the damaged terminal. The screen warns that "
                "the code only works while the system is powered.",
                item="Access Code",
                clue="Terminal access code",
                flag="terminal_repaired"
            )
        elif self.character == "Morgan":
            self.take_action(
                "You notice the terminal's recent activity log. "
                "A maintenance employee accessed the basement "
                "shortly before the hospital was closed.",
                clue="Recent basement access",
                flag="terminal_clue"
            )
        else:
            self.take_action(
                "The terminal flickers and displays an error. "
                "You cannot get it working."
            )

    def open_cabinet(self):
        if self.character == "Riley":
            self.take_action(
                "You brace yourself and pull the jammed drawer "
                "open. Inside, you find a building map with "
                "the emergency route marked in pencil.",
                item="Building Map",
                clue="Marked emergency route",
                flag="map_found"
            )
        else:
            self.take_action(
                "The cabinet barely moves. The metal frame is "
                "wedged against the wall, and forcing it further "
                "would make too much noise."
            )

    def enter_maintenance(self):
        self.take_action(
            "You leave the records room and follow the service "
            "signs toward the maintenance area.",
            next_scene="maintenance"
        )

    # ------------------------------------------------------
    # SCENE 4: MAINTENANCE ROOM
    # ------------------------------------------------------

    def search_workbench(self):
        if "Fuse" in self.inventory:
            self.take_action(
                "The workbench has nothing else useful."
            )
        else:
            self.take_action(
                "Among the scattered tools, you find a replacement "
                "fuse in an unopened supply box.",
                item="Fuse",
                clue="Replacement fuse"
            )

    def inspect_breaker(self):
        if self.character == "Eli":
            self.take_action(
                "You inspect the panel and identify the failed "
                "circuit. Replacing the fuse should restore "
                "power to the security terminal.",
                clue="Failed power circuit",
                flag="breaker_understood"
            )
        else:
            self.take_action(
                "The panel carries several electrical warnings. "
                "You cannot tell which circuit has failed."
            )

    def restore_power(self):
        if self.character != "Eli":
            self.take_action(
                "The panel is too complicated to repair safely. "
                "You need someone who understands the system."
            )
        elif "Fuse" not in self.inventory:
            self.take_action(
                "You identify the failed circuit, but it needs "
                "a replacement fuse. You will have to search "
                "the workbench first."
            )
        else:
            self.take_action(
                "You replace the failed fuse and restore power. "
                "Lights flicker throughout the basement. The "
                "security terminal should now be operational.",
                flag="power_restored",
                clue="Emergency power restored"
            )

    def enter_basement(self):
        self.take_action(
            "You descend the concrete staircase toward the "
            "security terminal.",
            next_scene="basement"
        )

    # ------------------------------------------------------
    # SCENE 5: BASEMENT
    # ------------------------------------------------------

    def use_terminal(self):
        if self.character != "Eli":
            self.take_action(
                "You try the terminal, but its error messages "
                "are difficult to interpret. You need technical "
                "knowledge or a working access code."
            )
        elif "Access Code" not in self.inventory:
            self.take_action(
                "The terminal is working, but it requests an "
                "access code. You need to find one in the records."
            )
        elif "power_restored" not in self.flags:
            self.take_action(
                "You enter the code, but the terminal has no "
                "reliable power. Restore the emergency circuit first."
            )
        else:
            self.take_action(
                "The code works. You disable the basement lockdown "
                "and unlock the emergency passage.",
                flag="lockdown_disabled",
                clue="Basement lockdown disabled"
            )

    def search_security_desk(self):
        if "Emergency Key" in self.inventory:
            self.take_action(
                "The desk is empty. You already found the emergency key."
            )
        elif self.character == "Morgan":
            self.take_action(
                "You notice a loose panel under the desk. Inside "
                "is a small emergency key taped to a maintenance log.",
                item="Emergency Key",
                clue="Hidden emergency key"
            )
        else:
            self.take_action(
                "You search the desk but find only blank forms "
                "and a broken pen."
            )

    def try_passage(self):
        if (
            "lockdown_disabled" in self.flags
            or "Emergency Key" in self.inventory
        ):
            self.take_action(
                "The emergency passage opens. You move toward "
                "the final chamber.",
                next_scene="final"
            )
        elif "basement doors lock during power failures" in self.clues:
            self.take_action(
                "You remember the victim's warning. The security "
                "lock is active, and the passage will not open "
                "until you disable it or find the emergency key."
            )
        else:
            self.take_action(
                "The passage is locked. A warning light indicates "
                "that security clearance is required."
            )

    def enter_final(self):
        self.take_action(
            "You leave the terminal behind and enter the final "
            "chamber. Footsteps echo from the opposite doorway.",
            next_scene="final"
        )

    # ------------------------------------------------------
    # SCENE 6: FINAL CHAMBER
    # ------------------------------------------------------

    def try_escape(self):
        has_key = "Emergency Key" in self.inventory
        has_card = "Keycard" in self.inventory
        has_code = "Access Code" in self.inventory
        has_power = "power_restored" in self.flags
        lockdown_off = "lockdown_disabled" in self.flags

        if has_key or lockdown_off or (has_card and has_power):
            self.show_scene("escape")

        elif has_code and has_power:
            self.show_scene("escape")

        else:
            self.take_action(
                "The card reader flashes red. The emergency exit "
                "needs a valid access item and an available security "
                "system. The killer is getting closer."
            )

    def stop_killer(self):
        # The player uses the building's security system to
        # stop the killer rather than fighting directly.
        if (
            self.character == "Eli"
            and "Access Code" in self.inventory
            and "power_restored" in self.flags
        ):
            self.show_scene("victory")

        elif (
            "lockdown_disabled" in self.flags
            and "camera_clue" in self.clues
        ):
            self.show_scene("victory")

        else:
            self.take_action(
                "You reach for the control panel, but the system "
                "is locked. You need the right access, working "
                "power, or information about the security cameras."
            )

    def distract_killer(self):
        if (
            self.character == "Avery"
            or "Camera blind spots" in self.clues
        ):
            self.take_action(
                "You exploit a moment of hesitation and move "
                "through a camera blind spot. The killer loses "
                "sight of you, giving you one chance to escape.",
                next_scene="escape"
            )
        else:
            self.show_scene("death")

    def hide_final(self):
        if (
            "Camera blind spots" in self.clues
            or self.character == "Avery"
        ):
            self.take_action(
                "You identify a blind spot near the control room "
                "and stay out of sight. The killer passes the "
                "doorway. You slip through the emergency exit.",
                next_scene="escape"
            )
        else:
            self.show_scene("death")

    # ------------------------------------------------------
    # INVENTORY AND CLUE VIEWER
    # ------------------------------------------------------

    def view_notes(self):
        self.clear_screen()

        self.make_label(
            self.window,
            "INVENTORY AND CASE NOTES",
            size=20,
            bold=True,
            color="#c0392b"
        )

        self.make_label(
            self.window,
            "Character: " + str(self.character)
        )

        self.make_label(
            self.window,
            "ITEMS\n" +
            ("\n".join("- " + item for item in self.inventory)
             if self.inventory else "No items collected.")
        )

        self.make_label(
            self.window,
            "CLUES\n" +
            ("\n".join("- " + clue for clue in self.clues)
             if self.clues else "No clues collected.")
        )

        self.make_button(
            self.window,
            "Return to the current scene",
            self.return_to_scene
        )

    def return_to_scene(self):
        # Rebuild the current scene without restoring spent actions.
        self.show_scene_same_scene()

    # ------------------------------------------------------
    # ENDINGS AND RESTART
    # ------------------------------------------------------

    def show_ending(self, ending):
        self.game_finished = True
        self.clear_screen()

        if ending == "escape":
            title = "ENDING 1: OUTSIDE"
            description = (
                "The emergency door finally opens. Cold night air "
                "rushes across your face as you stumble out into "
                "the darkness.\n\n"
                "Behind you, Blackthorn Institute disappears "
                "into the fog. You survived, carrying the clues "
                "that may explain what happened inside."
            )

        elif ending == "victory":
            title = "ENDING 2: THE LAST PATIENT"
            description = (
                "The security system responds to your commands. "
                "The chamber's heavy security doors close, cutting "
                "off the killer's route through the building.\n\n"
                "The alarms begin to sound. You escape the chamber "
                "while security systems contain the threat.\n\n"
                "For the first time in years, Blackthorn is silent."
            )

        else:
            title = "ENDING 3: ANOTHER VICTIM"
            description = (
                "The footsteps stop behind you. You realize too "
                "late that you have run out of time and options.\n\n"
                "The lights flicker out. The last thing you hear "
                "is the old speaker crackling overhead:\n\n"
                "'Patient observation complete.'\n\n"
                "Blackthorn Institute claims another victim."
            )

        self.make_label(
            self.window,
            title,
            size=23,
            bold=True,
            color="#c0392b",
            justify="center"
        )

        self.make_label(
            self.window,
            description,
            size=13
        )

        self.make_label(
            self.window,
            "Character: " + str(self.character) +
            "\nItems collected: " + str(len(self.inventory)) +
            "\nClues discovered: " + str(len(self.clues)),
            size=11,
            color="#8ecae6"
        )

        self.make_button(
            self.window,
            "Play Again",
            self.restart
        )

        self.make_button(
            self.window,
            "Quit Game",
            self.window.destroy
        )

    def restart(self):
        self.character = None
        self.inventory = []
        self.clues = []
        self.flags = set()
        self.actions = 0
        self.message = ""
        self.game_finished = False

        self.show_intro()


# ==========================================================
# START THE GAME
# ==========================================================

if __name__ == "__main__":
    root = tk.Tk()
    game = LastWingGame(root)
    root.mainloop()
