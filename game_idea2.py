
import tkinter as tk
from tkinter import messagebox


class HollowAtBlackthorn:

    def __init__(self, root):
        self.root = root
        self.root.title("The Hollow at Blackthorn")
        self.root.geometry("900x760")
        self.root.minsize(720, 600)
        self.root.configure(bg="#171717")

        self.characters = {
            "Marcus": {
                "description": (
                    "THE ATHLETE\n"
                    "Strong, competitive, and protective.\n"
                    "Strength: Forces weak obstacles and climbs.\n"
                    "Weakness: Impulsive and poor with delicate machinery.\n"
                    "Starting item: Flashlight"
                ),
                "items": ["Flashlight"]
            },
            "Evelyn": {
                "description": (
                    "THE OBSERVER\n"
                    "Analytical, skeptical, and detail-oriented.\n"
                    "Strength: Finds hidden clues and notices patterns.\n"
                    "Weakness: Struggles with physical obstacles.\n"
                    "Starting item: Notebook"
                ),
                "items": ["Notebook"]
            },
            "Noah": {
                "description": (
                    "THE TECHNICIAN\n"
                    "Practical, cautious, and resourceful.\n"
                    "Strength: Repairs machinery and electronic locks.\n"
                    "Weakness: Less physically capable.\n"
                    "Starting item: Multitool"
                ),
                "items": ["Multitool"]
            },
            "Sofia": {
                "description": (
                    "THE SURVIVOR\n"
                    "Quiet, independent, and adaptable.\n"
                    "Strength: Sneaks past threats and hides effectively.\n"
                    "Weakness: Cannot force heavy obstacles.\n"
                    "Starting item: Bandage"
                ),
                "items": ["Bandage"]
            }
        }

        self.scene_data = {
            "road": {
                "title": "SCENE 1 — THE STRANDED CAR",
                "limit": 3,
                "description": (
                    "Rain lashes the windshield as your car rolls to a "
                    "stop on a narrow forest road. The engine gives one "
                    "final cough and dies. Your phone displays NO SERVICE.\n\n"
                    "Beyond the headlights, an iron gate hangs open beside "
                    "a stone pillar. The name BLACKTHORN is barely visible "
                    "beneath thick moss. A muddy trail leads toward a huge "
                    "estate hidden between the trees.\n\n"
                    "The footprints in the mud are unusually deep at the "
                    "heel, as if someone was carrying something heavy. "
                    "Behind the car, a branch snaps. The sound is followed "
                    "by complete silence.\n\n"
                    "You have THREE decisions before you must leave."
                )
            },

            "hall": {
                "title": "SCENE 2 — THE ENTRANCE HALL",
                "limit": 2,
                "description": (
                    "The front door swings inward before anyone touches it. "
                    "Cold air rolls across the stone floor. A chandelier "
                    "hangs crookedly above a row of muddy footprints.\n\n"
                    "The footprints stop at the staircase. A family portrait "
                    "has been slashed across every face. Beside it stands "
                    "a narrow table holding a folded scrap of paper.\n\n"
                    "Above you, a floorboard groans. Then another. Someone "
                    "is slowly moving toward the staircase.\n\n"
                    "Two decisions remain before you must choose a route."
                )
            },

            "dining": {
                "title": "SCENE 3 — THE DINING ROOM",
                "limit": 2,
                "description": (
                    "The dining room stretches into darkness. Dust covers "
                    "a long table set with twelve plates. Eleven chairs "
                    "are overturned, but one has been pulled neatly away "
                    "from the table.\n\n"
                    "A narrow window is swollen from years of damp. Its "
                    "rusted latch is fused to the frame. Outside, the "
                    "ground drops into a ditch tangled with thorns.\n\n"
                    "At the opposite end of the room, a pantry door hangs "
                    "slightly open. Something clicks irregularly inside.\n\n"
                    "Beneath a broken glass, words have been scratched "
                    "into the table: 'THE DOOR IS NOT LOCKED. IT IS WAITING.'"
                )
            },

            "study": {
                "title": "SCENE 4 — THE STUDY",
                "limit": 2,
                "description": (
                    "The study smells of wet paper and extinguished candles. "
                    "Books have been ripped from the shelves and scattered "
                    "across the floor. A desk faces a rain-streaked window.\n\n"
                    "On the desk rests a leather maintenance log. Several "
                    "pages have been torn out. A bookcase stands slightly "
                    "away from the wall, leaving a thin black gap behind it.\n\n"
                    "From somewhere below comes the steady throb of an "
                    "old generator. A door beside the desk leads downstairs."
                )
            },

            "basement": {
                "title": "SCENE 5 — THE BASEMENT",
                "limit": 2,
                "description": (
                    "Concrete stairs lead into a basement crowded with "
                    "pipes and electrical cables. Water drips into a "
                    "shallow puddle beneath a flickering bulb.\n\n"
                    "A security panel sits beside a steel door. Red lights "
                    "flash across its surface. A nearby maintenance shelf "
                    "holds a few dusty tools and a small electrical fuse.\n\n"
                    "Someone has written on the wall in faded pencil:\n\n"
                    "'IF THE GENERATOR STOPS, THE EXIT LOCKS.'\n\n"
                    "The footsteps upstairs have stopped."
                )
            },

            "generator": {
                "title": "SCENE 6 — THE GENERATOR ROOM",
                "limit": 2,
                "description": (
                    "The generator room vibrates with a low mechanical "
                    "rumble. The machine is old and uneven, and a warning "
                    "light blinks above an open electrical panel.\n\n"
                    "A replacement fuse may solve the problem, but the "
                    "exposed wiring looks dangerous. A heavy metal cabinet "
                    "stands against the opposite wall. Behind it, a narrow "
                    "service passage disappears into darkness.\n\n"
                    "A maintenance log lies beside the panel. Its last "
                    "legible line reads: 'The west passage bypasses the "
                    "front security system.'"
                )
            },

            "garden": {
                "title": "ALTERNATE ROUTE — THE THORN GARDEN",
                "limit": 2,
                "description": (
                    "You climb through the dining room window and drop "
                    "onto a narrow exterior ledge. Below, a thorn-covered "
                    "garden slopes toward a stone wall.\n\n"
                    "The rain has turned the ground into mud. An iron "
                    "gate stands at the far end, but its chain is wrapped "
                    "around a rusted post. A greenhouse door hangs open "
                    "nearby.\n\n"
                    "Behind you, the window creaks. A shadow moves "
                    "across the curtain."
                )
            },

            "final": {
                "title": "SCENE 7 — THE FINAL CHAMBER",
                "limit": 2,
                "description": (
                    "The passage opens into a concrete chamber beneath "
                    "the estate. A security control room sits to the left. "
                    "Straight ahead is an emergency exit with a card reader.\n\n"
                    "At the far end, the masked killer steps into the light. "
                    "One gloved hand rests against the wall. The other "
                    "holds a ring of keys.\n\n"
                    "The killer tilts their head as if recognizing you. "
                    "Then the chamber lights begin to flicker.\n\n"
                    "You have TWO decisions. Your earlier discoveries "
                    "may determine whether you escape, expose the killer, "
                    "or become the next victim."
                )
            }
        }

        self.next_scene = {
            "road": "hall",
            "hall": "dining",
            "dining": "study",
            "study": "basement",
            "basement": "generator",
            "generator": "final",
            "garden": "final"
        }

        self.character = None
        self.inventory = []
        self.clues = set()
        self.flags = set()
        self.scene = None
        self.actions = 0
        self.message = ""
        self.finished = False

        self.show_intro()

    # --------------------------------------------------
    # INTERFACE
    # --------------------------------------------------

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def label(self, parent, text, size=12, color="#eeeeee",
              bold=False, center=False):
        label = tk.Label(
            parent,
            text=text,
            font=("Georgia", size, "bold" if bold else "normal"),
            fg=color,
            bg="#171717",
            wraplength=810,
            justify="center" if center else "left",
            anchor="center" if center else "w"
        )
        label.pack(fill="x", padx=22, pady=7)
        return label

    def button(self, parent, text, command):
        tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 11),
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            cursor="hand2",
            wraplength=760,
            padx=10,
            pady=8
        ).pack(fill="x", padx=22, pady=3)

    # --------------------------------------------------
    # INTRODUCTION AND CHARACTERS
    # --------------------------------------------------

    def show_intro(self):
        self.clear()

        self.label(
            self.root,
            "THE HOLLOW AT BLACKTHORN",
            size=27,
            color="#b33a3a",
            bold=True,
            center=True
        )

        self.label(
            self.root,
            "A branching survival horror game",
            size=14,
            color="#aaaaaa",
            center=True
        )

        self.label(
            self.root,
            "Four university friends are driving through a rural "
            "forest when their car breaks down during a storm. With "
            "no phone signal and no other buildings in sight, they "
            "seek shelter at Blackthorn Estate.\n\n"
            "The front door is open. A fire burns in a room upstairs. "
            "A table is set for dinner, although the house appears "
            "to have been abandoned for years.\n\n"
            "Then they discover a room full of photographs showing "
            "previous visitors. Every photograph has a date and a "
            "single word written underneath: FOUND.\n\n"
            "Someone has been living in the estate. Someone who "
            "does not want visitors to leave.\n\n"
            "Choose one character and explore the house. Search "
            "for clues, collect useful items, and make your decisions "
            "carefully. Some opportunities disappear permanently."
        )

        self.button(
            self.root,
            "START GAME",
            self.character_select
        )

    def character_select(self):
        self.clear()

        self.label(
            self.root,
            "CHOOSE YOUR CHARACTER",
            size=22,
            color="#b33a3a",
            bold=True
        )

        self.label(
            self.root,
            "Each character has a different skill and starting item."
        )

        for name, info in self.characters.items():
            self.label(
                self.root,
                name.upper() + "\n" + info["description"],
                size=11
            )
            self.button(
                self.root,
                "Play as " + name,
                lambda n=name: self.start_game(n)
            )

    def start_game(self, name):
        self.character = name
        self.inventory = self.characters[name]["items"].copy()
        self.clues = set()
        self.flags = set()
        self.finished = False
        self.message = ""
        self.enter_scene("road")

    # --------------------------------------------------
    # SCENE MANAGEMENT
    # --------------------------------------------------

    def enter_scene(self, name, message=""):
        self.scene = name
        self.actions = self.scene_data[name]["limit"]
        self.message = message
        self.render_scene()

    def render_scene(self):
        self.clear()

        data = self.scene_data[self.scene]

        self.label(
            self.root,
            data["title"],
            size=20,
            color="#b33a3a",
            bold=True
        )

        self.label(self.root, data["description"])

        if self.message:
            self.label(
                self.root,
                self.message,
                size=11,
                color="#e4c66a",
                bold=True
            )

        self.label(
            self.root,
            "CHARACTER: " + self.character,
            size=10,
            color="#aaaaaa"
        )

        self.label(
            self.root,
            "INVENTORY: " + (
                ", ".join(self.inventory)
                if self.inventory else "Empty"
            ),
            size=10,
            color="#8ecae6"
        )

        self.label(
            self.root,
            "CLUES: " + (
                ", ".join(sorted(self.clues))
                if self.clues else "None"
            ),
            size=10,
            color="#a8d5a2"
        )

        self.label(
            self.root,
            "DECISIONS REMAINING: " + str(self.actions),
            size=11,
            color="#e4c66a",
            bold=True
        )

        self.choices = tk.Frame(self.root, bg="#171717")
        self.choices.pack(fill="both", expand=True, pady=5)

        if self.actions > 0:
            self.show_choices()
        else:
            self.button(
                self.choices,
                "Continue to the next area",
                self.advance_scene
            )

        self.button(
            self.root,
            "Read collected notes and inventory",
            self.show_inventory
        )

    def show_choices(self):
        options = {
            "road": [
                ("Inspect the muddy footprints", self.inspect_tracks),
                ("Search the glove compartment", self.search_car),
                ("Hide behind the car and listen", self.listen),
                ("Run toward the estate", self.run_to_estate)
            ],

            "hall": [
                ("Read the folded scrap of paper", self.read_hall_note),
                ("Inspect the chandelier and wall", self.inspect_hall),
                ("Open the dining room doors", self.enter_dining),
                ("Take the staircase upstairs", self.take_stairs)
            ],

            "dining": [
                ("Investigate the clicking pantry", self.investigate_pantry),
                ("Try to force the swollen window", self.force_window),
                ("Examine the message on the table", self.read_table),
                ("Enter the study", self.enter_study)
            ],

            "study": [
                ("Read the maintenance log", self.read_log),
                ("Examine the suspicious bookcase", self.inspect_bookcase),
                ("Search the desk drawers", self.search_desk),
                ("Descend into the basement", self.enter_basement)
            ],

            "basement": [
                ("Search the maintenance shelf", self.search_shelf),
                ("Inspect the security panel", self.inspect_panel),
                ("Go to the generator room", self.enter_generator)
            ],

            "generator": [
                ("Inspect the electrical panel", self.inspect_generator),
                ("Repair the generator", self.repair_generator),
                ("Move the heavy cabinet", self.move_cabinet),
                ("Enter the service passage", self.enter_final)
            ],

            "garden": [
                ("Search the greenhouse", self.search_greenhouse),
                ("Try to open the chained gate", self.open_garden_gate),
                ("Hide and wait for the shadow to pass", self.garden_hide)
            ],

            "final": [
                ("Unlock the emergency exit", self.escape_attempt),
                ("Use the security control room", self.confront),
                ("Distract the killer and run", self.distract),
                ("Hide from the killer", self.hide_final)
            ]
        }

        for text, function in options.get(self.scene, []):
            self.button(self.choices, text, function)

    # --------------------------------------------------
    # ACTION AND INVENTORY HELPERS
    # --------------------------------------------------

    def has(self, item):
        return item in self.inventory

    def collect(self, item):
        if item not in self.inventory:
            self.inventory.append(item)

    def clue(self, item):
        self.clues.add(item)

    def flag(self, item):
        self.flags.add(item)

    def act(self, result, item=None, clue=None, flag=None,
            next_scene=None, ending=None):
        if self.finished:
            return

        if item:
            self.collect(item)

        if clue:
            self.clue(clue)

        if flag:
            self.flag(flag)

        if ending:
            self.show_ending(ending)
            return

        if next_scene:
            self.enter_scene(next_scene, result)
            return

        self.actions -= 1
        self.message = result

        if self.actions <= 0:
            self.render_scene()
            return

        self.render_scene()

    def advance_scene(self):
        next_name = self.next_scene.get(self.scene)

        if next_name:
            self.enter_scene(
                next_name,
                "You leave the area and move deeper into Blackthorn."
            )
        else:
            self.show_ending("death")

    # --------------------------------------------------
    # SCENE 1: STRANDED CAR
    # --------------------------------------------------

    def inspect_tracks(self):
        if self.character == "Evelyn":
            self.act(
                "You notice two different sets of footprints. One "
                "leads toward the house. The other circles back "
                "toward the road, as though someone followed you.",
                clue="Two sets of footprints",
                flag="tracks_examined"
            )
        else:
            self.act(
                "The rain is washing the prints away. You can tell "
                "they lead toward the estate, but not who made them."
            )

    def search_car(self):
        if self.has("Flashlight"):
            self.act(
                "The glove compartment is empty except for a faded "
                "road map. Your flashlight is already the most useful "
                "thing you have."
            )
        else:
            self.act(
                "You find a flashlight wedged beneath the owner's "
                "manual. Its beam is weak, but it still works.",
                item="Flashlight"
            )

    def listen(self):
        if self.character == "Sofia":
            self.act(
                "You stay low and listen. The footsteps stop, then "
                "move away from the road. Whoever is following you "
                "does not seem to know exactly where you are.",
                clue="Footsteps move away",
                flag="quiet_approach"
            )
        else:
            self.act(
                "You hear something moving between the trees, "
                "but the storm makes it impossible to judge its distance."
            )

    def run_to_estate(self):
        if self.character == "Marcus":
            self.act(
                "You sprint through the mud and reach the gate quickly. "
                "You are safely ahead of the others, but the noise "
                "of your footsteps echoes through the trees.",
                flag="killer_alerted",
                next_scene="hall"
            )
        else:
            self.act(
                "You hurry toward the estate. The mud slows you down, "
                "and a branch snaps beneath your foot. Something moves "
                "in the trees behind you.",
                flag="killer_alerted",
                next_scene="hall"
            )

    # --------------------------------------------------
    # SCENE 2: ENTRANCE HALL
    # --------------------------------------------------

    def read_hall_note(self):
        self.act(
            "The note reads: 'He hears the stairs. Don't use them "
            "when the house is quiet. The west hall has another way.'",
            clue="Stairs are noisy",
            flag="stairs_warning"
        )

    def inspect_hall(self):
        if self.character == "Evelyn":
            self.act(
                "You notice that the dust beneath the chandelier "
                "has been disturbed. A section of the wall behind "
                "the portrait is cleaner than the rest, as though "
                "a piece of furniture has recently been moved.",
                clue="Recently moved wall panel",
                flag="hidden_panel"
            )
        else:
            self.act(
                "The chandelier is old and unstable. The portrait "
                "has been slashed repeatedly, but you cannot tell "
                "why the wall beneath it looks different."
            )

    def enter_dining(self):
        self.act(
            "You push through the double doors. The hinges squeal, "
            "and the sound travels through the silent house.",
            flag="killer_alerted",
            next_scene="dining"
        )

    def take_stairs(self):
        if "Stairs are noisy" in self.clues:
            self.act(
                "Remembering the warning, you avoid the loose boards "
                "and reach the upper landing without alerting anyone.",
                next_scene="study"
            )
        elif self.character == "Sofia":
            self.act(
                "You step around the loose boards and move quietly "
                "upstairs. A shadow passes the landing, but you "
                "slip into the study.",
                next_scene="study"
            )
        else:
            self.act(
                "The staircase groans under your weight. A door "
                "slams upstairs. Heavy footsteps rush toward you.",
                ending="death"
            )

    # --------------------------------------------------
    # SCENE 3: DINING ROOM
    # --------------------------------------------------

    def investigate_pantry(self):
        if self.has("Kitchen Knife"):
            self.act(
                "The pantry contains broken dishes and empty jars. "
                "You have already taken the useful item."
            )
        elif self.character == "Evelyn":
            self.act(
                "You identify the clicking as a loose pipe. Behind "
                "a stack of pans, you find a kitchen knife wrapped "
                "in a cloth. Someone has scratched initials into "
                "the handle.",
                item="Kitchen Knife",
                clue="Initials on the knife"
            )
        else:
            self.act(
                "You open the pantry. A loose pipe clicks against "
                "the wall. You find a kitchen knife beneath a towel.",
                item="Kitchen Knife"
            )

    def force_window(self):
        if self.character == "Marcus":
            self.act(
                "You force the swollen frame open. The drop is "
                "awkward, but you climb onto the exterior ledge "
                "and descend into the thorn garden.",
                flag="garden_route",
                next_scene="garden"
            )
        else:
            self.act(
                "You pull at the swollen window. The rusted latch "
                "does not move. The frame is too stubborn to force "
                "without making a great deal of noise."
            )

    def read_table(self):
        self.act(
            "The message has been scratched over older writing. "
            "You can make out the words 'WEST PASSAGE' underneath. "
            "Someone tried to leave through a route hidden in the house.",
            clue="Hidden west passage",
            flag="passage_hint"
        )

    def enter_study(self):
        self.act(
            "You leave the dining room and enter the study. "
            "The door closes behind you with a quiet click.",
            next_scene="study"
        )

    # --------------------------------------------------
    # SCENE 4: STUDY
    # --------------------------------------------------

    def read_log(self):
        self.act(
            "The maintenance log contains a warning: 'The west "
            "generator controls the security system. If the generator "
            "fails, the front exit locks. The west passage bypasses "
            "the front security door.'",
            item="Maintenance Log",
            clue="Generator controls security",
            flag="log_read"
        )

    def inspect_bookcase(self):
        if self.character == "Evelyn":
            self.act(
                "You spot scratches on the floor beneath the bookcase. "
                "Pushing a hidden latch shifts the shelves aside, "
                "revealing a narrow service passage.",
                clue="Hidden passage discovered",
                flag="hidden_passage"
            )
        else:
            self.act(
                "The bookcase is heavy. There is a narrow gap behind "
                "it, but you cannot see what is hidden there."
            )

    def search_desk(self):
        if self.has("Maintenance Key"):
            self.act(
                "The desk contains old paperwork, but you already "
                "found the useful key."
            )
        else:
            self.act(
                "Inside the bottom drawer, you find a maintenance "
                "key marked WEST WING. It may fit a service door.",
                item="Maintenance Key"
            )

    def enter_basement(self):
        self.act(
            "You descend the stairs into the basement. The generator "
            "is louder down here, and the air grows warmer.",
            next_scene="basement"
        )

    # --------------------------------------------------
    # SCENE 5: BASEMENT
    # --------------------------------------------------

    def search_shelf(self):
        if self.has("Fuse"):
            self.act(
                "You search the shelf again, but there are no more "
                "replacement fuses."
            )
        else:
            self.act(
                "Behind a dusty toolbox, you find a replacement fuse "
                "and a short note: 'Only Noah understood the panel.'",
                item="Fuse",
                clue="Replacement fuse available"
            )

    def inspect_panel(self):
        if self.character == "Noah":
            self.act(
                "You recognize the panel's wiring layout. The system "
                "needs a replacement fuse before it can restore power. "
                "You also identify a manual override.",
                clue="Panel manual override",
                flag="panel_understood"
            )
        else:
            self.act(
                "The panel has several warning lights. A label says "
                "that tampering with the wiring could disable the exits."
            )

    def enter_generator(self):
        self.act(
            "You follow the thick power cables into the generator room.",
            next_scene="generator"
        )

    # --------------------------------------------------
    # SCENE 6: GENERATOR ROOM
    # --------------------------------------------------

    def inspect_generator(self):
        if self.character == "Noah":
            self.act(
                "You trace the faulty circuit and discover a blown fuse. "
                "The generator can be repaired if you have a replacement.",
                clue="Generator fault identified",
                flag="generator_understood"
            )
        else:
            self.act(
                "The generator rattles unevenly. A warning light flashes "
                "beside an open electrical panel. You cannot tell which "
                "component has failed."
            )

    def repair_generator(self):
        if self.character != "Noah":
            self.act(
                "The electrical panel is too complicated to repair "
                "safely. You need someone with technical experience."
            )
        elif not self.has("Fuse"):
            self.act(
                "You identify the failed component, but you do not "
                "have a replacement fuse. Search the basement shelf."
            )
        else:
            self.act(
                "You replace the fuse and restart the generator. "
                "The lights return, and the security system begins "
                "to reboot. A green indicator appears on the exit panel.",
                flag="power_restored",
                clue="Generator repaired"
            )

    def move_cabinet(self):
        if self.character == "Marcus":
            self.act(
                "You push the heavy cabinet aside. Behind it is "
                "a narrow service passage marked WEST EXIT. It "
                "leads directly to the final chamber.",
                flag="service_passage",
                clue="West exit passage",
                next_scene="final"
            )
        else:
            self.act(
                "The cabinet barely moves. It is too heavy to shift "
                "without help, and scraping it across the concrete "
                "would alert anyone nearby."
            )

    def enter_final(self):
        if "Hidden passage discovered" in self.clues:
            self.act(
                "You follow the passage hidden behind the bookcase. "
                "It descends into a concrete chamber beneath the estate.",
                next_scene="final"
            )
        elif "West exit passage" in self.clues:
            self.act(
                "You follow the west exit passage into the final chamber.",
                next_scene="final"
            )
        elif "Maintenance Key" in self.inventory:
            self.act(
                "The maintenance key opens a narrow service door. "
                "Beyond it lies the final chamber.",
                next_scene="final"
            )
        else:
            self.act(
                "You find a locked service door. You need a maintenance "
                "key or another way to reach the passage."
            )

    # --------------------------------------------------
    # ALTERNATE ROUTE: GARDEN
    # --------------------------------------------------

    def search_greenhouse(self):
        if self.has("Garden Key"):
            self.act(
                "The greenhouse contains only broken pots and dead plants."
            )
        else:
            self.act(
                "Inside the greenhouse, you find a small key beneath "
                "a cracked flowerpot. A handwritten note says the "
                "west gate leads toward an old service tunnel.",
                item="Garden Key",
                clue="West gate leads to service tunnel"
            )

    def open_garden_gate(self):
        if self.has("Garden Key"):
            self.act(
                "The key opens the chained gate. You follow a narrow "
                "stone path to a service entrance beneath the estate.",
                next_scene="final"
            )
        elif self.character == "Marcus":
            self.act(
                "You try to break the chain, but it is secured with "
                "a heavy industrial lock. You need the key.",
            )
        else:
            self.act(
                "The chain is too thick to break. You need to find "
                "another way through the garden."
            )

    def garden_hide(self):
        if self.character == "Sofia":
            self.act(
                "You hide beneath the greenhouse bench and remain "
                "still. The shadow passes the window without seeing "
                "you. You find a service path behind the greenhouse.",
                next_scene="final"
            )
        else:
            self.act(
                "You crouch behind a planter. The rain hides some "
                "of your movement, but the garden offers little cover."
            )

    # --------------------------------------------------
    # SCENE 7: FINAL CHAMBER
    # --------------------------------------------------

    def escape_attempt(self):
        if "Garden Key" in self.inventory:
            self.show_ending("escape_evidence")
        elif "power_restored" in self.flags:
            self.show_ending("escape")
        elif "Maintenance Key" in self.inventory:
            self.show_ending("escape")
        elif "service_passage" in self.flags:
            self.show_ending("escape")
        else:
            self.act(
                "The card reader flashes red. The emergency exit "
                "remains locked. You need the right key or restored "
                "power to release the lock."
            )

    def confront(self):
        if (
            self.character == "Noah"
            and "power_restored" in self.flags
            and "panel_understood" in self.flags
        ):
            self.show_ending("victory")

        elif (
            "Hidden passage discovered" in self.clues
            and "Maintenance Log" in self.inventory
        ):
            self.show_ending("victory")

        else:
            self.act(
                "The control room is locked behind an electronic "
                "panel. You cannot access the security system "
                "without the right knowledge or clues."
            )

    def distract(self):
        if self.character == "Sofia":
            self.act(
                "You use the flickering lights and your knowledge "
                "of the estate to slip out of the killer's line of "
                "sight. You reach an exterior service path.",
                ending="escape"
            )
        elif "Hidden west passage" in self.clues:
            self.act(
                "You distract the killer and slip through the west "
                "passage while they search the wrong corridor.",
                ending="escape"
            )
        else:
            self.act(
                "You make a run for the doorway, but the killer "
                "blocks your path. You have nowhere left to go.",
                ending="death"
            )

    def hide_final(self):
        if (
            self.character == "Sofia"
            or "Two sets of footprints" in self.clues
        ):
            self.act(
                "You wait for the killer to pass the control room. "
                "The footsteps fade, and you slip through an "
                "unwatched doorway toward the outside.",
                ending="escape"
            )
        else:
            self.act(
                "You hide behind the control-room door. The footsteps "
                "stop. The handle begins to turn.",
                ending="death"
            )

    # --------------------------------------------------
    # INVENTORY AND NOTES
    # --------------------------------------------------

    def show_inventory(self):
        self.clear()

        self.label(
            self.root,
            "YOUR INVENTORY",
            size=22,
            color="#b33a3a",
            bold=True
        )

        self.label(
            self.root,
            "Character: " + str(self.character)
        )

        self.label(
            self.root,
            "ITEMS\n" + (
                "\n".join("- " + item for item in self.inventory)
                if self.inventory else "No items collected."
            )
        )

        self.label(
            self.root,
            "CLUES\n" + (
                "\n".join("- " + clue for clue in sorted(self.clues))
                if self.clues else "No clues collected."
            )
        )

        self.button(
            self.root,
            "Return to the current scene",
            self.render_scene
        )

    # --------------------------------------------------
    # ENDINGS
    # --------------------------------------------------

    def show_ending(self, ending):
        self.finished = True
        self.clear()

        endings = {
            "escape": (
                "ENDING 1 — THE ESCAPE\n\n"
                "The exit opens, and cold rain hits your face. "
                "You stumble away from the estate and follow "
                "the road toward the distant lights of a town.\n\n"
                "Behind you, Blackthorn disappears into the fog. "
                "You survived, but you still do not know how many "
                "people never made it out."
            ),

            "escape_evidence": (
                "ENDING 2 — THE TRUTH ESCAPES\n\n"
                "The garden gate opens onto an old service tunnel. "
                "You emerge beyond the estate walls with evidence "
                "that someone has been living inside the house.\n\n"
                "By morning, authorities arrive at Blackthorn. "
                "The photographs, the maintenance records, and "
                "the hidden rooms reveal what happened to the "
                "missing visitors. The killer is no longer hidden."
            ),

            "victory": (
                "ENDING 3 — THE LAST VISITOR\n\n"
                "You reach the security controls and activate the "
                "estate's emergency lockdown. Heavy doors seal "
                "the chamber, preventing the killer from following.\n\n"
                "Alarms echo through the house. You escape while "
                "the security system contains the threat. The "
                "estate's secrets will finally be investigated."
            ),

            "death": (
                "ENDING 4 — THE HOLLOW CLAIMS ANOTHER\n\n"
                "The footsteps stop behind you. You realize that "
                "the route ahead is blocked and your remaining "
                "options have disappeared.\n\n"
                "The lights go out. Somewhere in the house, an "
                "old clock begins to chime.\n\n"
                "Another photograph will soon be added to the wall."
            )
        }

        self.label(
            self.root,
            "THE HOLLOW AT BLACKTHORN",
            size=24,
            color="#b33a3a",
            bold=True,
            center=True
        )

        self.label(
            self.root,
            endings[ending],
            size=13
        )

        self.label(
            self.root,
            "Character: " + str(self.character) +
            "\nItems collected: " + str(len(self.inventory)) +
            "\nClues discovered: " + str(len(self.clues)),
            size=11,
            color="#8ecae6"
        )

        self.button(
            self.root,
            "PLAY AGAIN",
            self.restart
        )

        self.button(
            self.root,
            "QUIT",
            self.root.destroy
        )

    def restart(self):
        self.character = None
        self.inventory = []
        self.clues = set()
        self.flags = set()
        self.scene = None
        self.actions = 0
        self.message = ""
        self.finished = False

        self.show_intro()


# ------------------------------------------------------
# RUN THE GAME
# ------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    game = HollowAtBlackthorn(root)
    root.mainloop()
