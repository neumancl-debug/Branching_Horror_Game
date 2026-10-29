"""Story data and decision rules, independent of Pygame.

The UI calls ``choose()`` once per attempted action, displays its returned text,
then calls ``enter_pending()`` after the player dismisses the result. Keeping
these steps separate ensures that a scene change never hides an unread outcome.
"""

from dataclasses import dataclass, field

MAX_THREAT = 6
SURVIVAL_ENDINGS = frozenset(
    {
        "THROUGH THE THORNS",
        "THE TRUTH GETS OUT",
        "OUT OF BLACKTHORN",
        "THE HOUSE TURNS ON HIM",
    }
)


@dataclass(frozen=True)
class Character:
    """Read-only character details shared by selection and gameplay screens."""

    role: str
    biography: str
    traits: str
    color: tuple[int, int, int]


CHARACTERS = {
    "Marcus": Character(
        "THE ATHLETE",
        "Broad shoulders, a sprinter's legs, and a habit of acting first.",
        "Strength: forces obstacles. Weakness: noisy and impulsive.",
        (205, 153, 93),
    ),
    "Evelyn": Character(
        "THE OBSERVER",
        "Slight, sharp-eyed, and always watching the edges of a room.",
        "Perception: discovers extra evidence. Weakness: little strength.",
        (139, 180, 181),
    ),
    "Noah": Character(
        "THE TECHNICIAN",
        "Oil-stained fingers and a cautious, methodical mind.",
        "Mechanics: bypasses the power panel. Weakness: little strength.",
        (150, 166, 124),
    ),
    "Sofia": Character(
        "THE SURVIVOR",
        "Light on her feet, steady-handed, and difficult to frighten.",
        "Stealth: crosses darkness quietly. Weakness: no technical training.",
        (179, 143, 173),
    ),
}


@dataclass(frozen=True)
class Action:
    """An action ID, UI label, map-local pixel position, and nearby hint."""

    id: str
    label: str
    position: tuple[int, int]
    hint: str


@dataclass(frozen=True)
class Scene:
    """Read-only scene content; next_scene is the route used on timeout."""

    title: str
    subtitle: str
    description: str
    decisions: int
    actions: tuple[Action, ...]
    next_scene: str | None


SCENES = {
    "road": Scene(
        "01 / THE STRANDED CAR",
        "Blackthorn Road · 11:47 PM",
        (
            "Rain swallows the engine's last sputter. Your phone has no service. Beyond "
            "the headlights, an iron gate hangs open beneath the name BLACKTHORN. Deep "
            "footprints lead toward the estate. Behind the car, a branch snaps."
        ),
        3,
        (
            Action(
                "glovebox",
                "Search the glove compartment",
                (245, 300),
                "A small compartment catches the light inside the stalled car.",
            ),
            Action(
                "tracks",
                "Inspect the muddy footprints",
                (460, 335),
                "Two trails overlap in the mud; one seems to circle back.",
            ),
            Action(
                "listen",
                "Hide behind the car and listen",
                (225, 410),
                "The rain conceals movement. Patience might reveal what follows you.",
            ),
            Action(
                "estate",
                "Follow the path to the estate",
                (605, 170),
                "The front door is the only shelter in sight. This leaves the road.",
            ),
        ),
        "hall",
    ),
    "hall": Scene(
        "02 / THE ENTRANCE HALL",
        "Something upstairs is listening",
        (
            "Wet plaster, cold ash, and a metallic smell fill the hall. A crooked "
            "chandelier hangs above a strangely clean patch of floor. A folded note rests"
            " below a slashed portrait. Slow footsteps approach the warped staircase."
        ),
        2,
        (
            Action(
                "note",
                "Read the folded note",
                (160, 230),
                "The paper is damp, but someone pressed hard enough to tear it.",
            ),
            Action(
                "chandelier",
                "Examine the chandelier",
                (355, 250),
                "A frayed suspension rope runs toward the service rooms.",
            ),
            Action(
                "stairs",
                "Try the warped staircase",
                (575, 190),
                "The boards bow under their own weight. The footsteps are above you.",
            ),
            Action(
                "dining",
                "Open the dining-room doors",
                (600, 425),
                "Tarnished hinges look painfully dry. This leaves the hall.",
            ),
        ),
        "dining",
    ),
    "dining": Scene(
        "03 / THE DINING ROOM",
        "A place has been set for you",
        (
            "Twelve plates line a table beneath dead candles. One chair is neatly pulled "
            "out. The window frame is swollen shut; beyond it lies a thorn-filled ditch. "
            "Scratches beneath a broken glass catch your eye. A pantry door clicks in the"
            " draft; service stairs descend beside it."
        ),
        3,
        (
            Action(
                "pantry",
                "Search the pantry",
                (150, 190),
                "A key glints beside a kitchen knife on a low shelf.",
            ),
            Action(
                "scratches",
                "Read the scratched message",
                (360, 330),
                "Fresh words cross out older writing. A dark ledger lies nearby.",
            ),
            Action(
                "window",
                "Force the swollen window",
                (590, 210),
                "The heavy frame is fused shut. The ditch below looks deep.",
            ),
            Action(
                "basement",
                "Take the service stairs down",
                (605, 435),
                "A cold draft rises from the maintenance rooms. This leaves the room.",
            ),
        ),
        "basement",
    ),
    "basement": Scene(
        "04 / THE WINDOWLESS ROOM",
        "The generator hums behind the wall",
        (
            "Copper pipes sweat above a maintenance bench. A logbook lies open beside a "
            "fuse panel marked GATE OVERRIDE. A light switch gleams beside the door. A "
            "narrow passage vanishes into blackness. Through the ceiling comes the slow "
            "scrape of a blade."
        ),
        3,
        (
            Action(
                "log",
                "Read the maintenance log",
                (160, 210),
                "A diagram connects the gate override to an alarm circuit.",
            ),
            Action(
                "panel",
                "Bypass the gate override",
                (550, 230),
                "Three wires feed a latched relay. Knowledge could keep it quiet.",
            ),
            Action(
                "switch",
                "Turn on the overhead light",
                (135, 415),
                "Fresh wiring leads from this switch into the alarm housing.",
            ),
            Action(
                "passage",
                "Enter the unlit passage",
                (600, 430),
                "The air smells of rain. A loose chain drags across the floor.",
            ),
        ),
        "yard",
    ),
    "yard": Scene(
        "05 / THE REAR COURTYARD",
        "The last gate",
        (
            "Rain needles the courtyard. The iron gate has a brass emergency lock linked "
            "to an electric bolt. Behind you, a figure in a pale mask fills the doorway. "
            "Above him, the chandelier's service rope passes over a rusted hook. He takes"
            " one deliberate step toward you."
        ),
        2,
        (
            Action(
                "gate",
                "Open the rear gate and escape",
                (590, 200),
                "A brass key, brute strength, or a disabled override could open a way.",
            ),
            Action(
                "hide",
                "Slip behind the rain barrels",
                (155, 390),
                "Deep shadows offer cover, but he will not be fooled twice.",
            ),
            Action(
                "trap",
                "Cut the chandelier service rope",
                (350, 190),
                "The rope is within reach. A blade and knowledge of the rig could turn it against him.",
            ),
            Action(
                "fight",
                "Rush the masked figure",
                (590, 435),
                "His blade is longer than your reach. He is waiting for you.",
            ),
        ),
        None,
    ),
}


@dataclass
class GameState:
    """Mutable state for one run, including items, clues, and pending outcomes.

    ``used`` records action IDs for the current scene only. Inventory and clues
    persist between scenes. Each container uses a factory so separate runs never
    share mutable data. A missing decision count uses the scene's default budget.
    """

    character: str
    scene: str = "road"
    decisions: int | None = None
    inventory: set[str] = field(default_factory=set)
    clues: dict[str, str] = field(default_factory=dict)
    used: set[str] = field(default_factory=set)
    threat: int = 0
    ending: str | None = None
    ending_text: str = ""
    pending_scene: str | None = None
    history: list[str] = field(default_factory=list)
    actions_taken: int = 0
    gate_override_disabled: bool = False

    def __post_init__(self) -> None:
        """Reject invalid starting data and use the selected scene's budget."""
        if self.character not in CHARACTERS:
            raise ValueError(f"Unknown character: {self.character}")
        if self.scene not in SCENES:
            raise ValueError(f"Unknown scene: {self.scene}")
        if self.decisions is None:
            self.decisions = SCENES[self.scene].decisions
        if not 0 <= self.decisions <= SCENES[self.scene].decisions:
            raise ValueError("Decisions must be within the scene's action budget")
        if not 0 <= self.threat <= MAX_THREAT:
            raise ValueError(f"Threat must be between 0 and {MAX_THREAT}")

    @property
    def survived(self) -> bool:
        """Whether the current ending is a successful survival outcome."""
        return self.ending in SURVIVAL_ENDINGS

    def finish(self, title: str, message: str) -> None:
        """End the run and cancel any queued scene change."""
        self.ending, self.ending_text = title, message
        self.pending_scene = None

    def enter_pending(self) -> None:
        """Commit a queued transition after its result has been read."""
        if self.pending_scene and not self.ending:
            self.scene = self.pending_scene
            self.pending_scene = None
            self.decisions = SCENES[self.scene].decisions
            self.used.clear()

    def choose(self, action_id: str) -> str | None:
        """Spend one decision and return the complete outcome for a valid action.

        Return None without modifying state for an unavailable, repeated, or
        invalid action. Fatal outcomes take priority over queued transitions.
        """
        # __post_init__ always initializes this optional constructor argument.
        assert self.decisions is not None
        if self.ending or self.pending_scene or self.decisions <= 0 or action_id in self.used:
            return None
        if action_id not in {action.id for action in SCENES[self.scene].actions}:
            return None
        self.used.add(action_id)
        self.decisions -= 1
        self.actions_taken += 1
        message = self._resolve(action_id)
        if not self.ending and self.threat >= MAX_THREAT:
            self.finish(
                "FOUND IN THE DARK",
                (
                    "Too much noise. Too many wasted moments. The mask emerges from the nearest "
                    "doorway before you can move."
                ),
            )
        if not self.ending and self.decisions == 0 and not self.pending_scene:
            if self.scene == "yard":
                self.finish(
                    "NOWHERE LEFT TO HIDE",
                    "The gate is still shut. Your last moment of hesitation belongs to him.",
                )
            else:
                self.threat += 1
                if self.threat >= MAX_THREAT:
                    self.finish(
                        "FOUND IN THE DARK",
                        "Your last delay gives him time to reach the doorway. There is no path past the pale mask.",
                    )
                    message += "\n\nTime runs out. The approaching footsteps reach you. Threat +1."
                else:
                    self.pending_scene = SCENES[self.scene].next_scene
                    message += (
                        "\n\nTime runs out. Approaching footsteps force you onward. Threat +1."
                    )
        self.history.append(message)
        return message

    def _resolve(self, action_id: str) -> str:
        """Dispatch a validated action to its scene-specific rule handler."""
        handlers = {
            "road": self._resolve_road,
            "hall": self._resolve_hall,
            "dining": self._resolve_dining,
            "basement": self._resolve_basement,
            "yard": self._resolve_yard,
        }
        return handlers[self.scene](action_id)

    def _resolve_road(self, action_id: str) -> str:
        """Collect starting information and supplies before entering the house."""
        character = self.character
        if action_id == "glovebox":
            self.inventory.add("Flashlight")
            return "You find a small flashlight. Its beam is weak, but steady. Added to inventory: Flashlight."
        if action_id == "tracks":
            self.clues["tracks"] = "One trail circles back to the road. Someone is hunting here."
            if character == "Evelyn":
                self.clues["rig"] = (
                    "A victim was dragged by a rope. The house contains a rigged trap."
                )
                return (
                    "You distinguish a second trail. Evelyn also spots rope fibers in the mud: "
                    "someone has been using a rig to drag victims. Two clues recorded."
                )
            return (
                "One trail enters the estate; another circles behind the car. This was no "
                "accident. Clue recorded: The second trail."
            )
        if action_id == "listen":
            if character == "Sofia":
                return (
                    "Sofia holds her breath until a shape passes behind the trees. She slips away"
                    " without making a sound."
                )
            self.threat += 1
            return (
                "You hear breathing on the other side of the car. You stumble away, kicking "
                "loose gravel. Threat +1."
            )
        if action_id == "estate":
            self.pending_scene = "hall"
            return "You follow the path. The front door opens before your hand reaches it."
        raise ValueError(f"Unhandled road action: {action_id}")

    def _resolve_hall(self, action_id: str) -> str:
        """Reveal warnings and the trap, or punish a dangerous staircase choice."""
        if action_id == "note":
            self.clues["stairs"] = "He hears the stairs. Do not use them when the house is quiet."
            return (
                'The note reads: "He hears the stairs. Do not use them when the house is '
                'quiet." You keep the warning in your journal.'
            )
        if action_id == "chandelier":
            self.clues["rig"] = (
                "The chandelier hangs from a service rope accessible in the rear courtyard."
            )
            return (
                "The chandelier is attached to a pulley. Its service rope runs all the way to"
                " the rear courtyard. A sharp blade could sever it. Clue recorded: The rig."
            )
        if action_id == "stairs":
            if "stairs" in self.clues:
                self.threat += 1
                return (
                    "Remembering the note, you stop at the first creak and retreat. The delay "
                    "still costs you. Threat +1."
                )
            self.finish(
                "THE STAIRCASE",
                (
                    "The third step screams beneath you. The footsteps stop. A pale mask appears "
                    "at the landing; there is nowhere to turn."
                ),
            )
            return "A board gives way with a sound like a gunshot. He was listening."
        if action_id == "dining":
            self.threat += 1
            self.pending_scene = "dining"
            return (
                "The hinges shriek as you push through. Upstairs, the footsteps quicken. Threat +1."
            )
        raise ValueError(f"Unhandled hall action: {action_id}")

    def _resolve_dining(self, action_id: str) -> str:
        """Provide tools and evidence, plus Marcus's alternate escape route."""
        character = self.character
        if action_id == "pantry":
            self.inventory.update(("Brass key", "Kitchen knife"))
            return (
                "The clicking is a loose pipe. Beneath it you find a brass key and a kitchen "
                "knife. Both go into your inventory."
            )
        if action_id == "scratches":
            self.clues["warning"] = "In the room with no windows, do not turn on the light."
            self.inventory.add("Victims' ledger")
            return (
                'Under the newer scratches: "In the room with no windows, do not turn on the '
                'light." The ledger lists missing visitors. You take it as evidence.'
            )
        if action_id == "window":
            if character == "Marcus":
                evidence = "Victims' ledger" in self.inventory
                self.finish(
                    "THROUGH THE THORNS",
                    (
                        "Marcus tears the frame loose and drops into the ditch. Thorns cut his arms, "
                        "but the road is close."
                    )
                    + (
                        " The ledger survives the fall. Now someone will know what happened here."
                        if evidence
                        else " You survive, but leave the truth inside Blackthorn."
                    ),
                )
                return "Wood splits. Rain pours through the opening. You jump."
            self.threat += 2
            return (
                "The waterlogged frame will not move. You strain until the latch clangs "
                "against the glass. Threat +2. Your character lacks Marcus's strength."
            )
        if action_id == "basement":
            self.pending_scene = "basement"
            return "You take the narrow service stairs. These boards are solid. Below, a generator hums."
        raise ValueError(f"Unhandled dining action: {action_id}")

    def _resolve_basement(self, action_id: str) -> str:
        """Handle the wiring puzzle and the passage to the courtyard."""
        character = self.character
        if action_id == "log":
            self.clues["wiring"] = "Disconnect the red alarm lead before lowering the gate relay."
            return (
                "The diagram is clear: disconnect the red alarm lead, then lower the gate "
                "relay. The courtyard bolt will release. Clue recorded: Gate wiring."
            )
        if action_id == "panel":
            if character == "Noah" or "wiring" in self.clues:
                self.gate_override_disabled = True
                return (
                    "You isolate the alarm and lower the relay. Somewhere outside, a heavy bolt "
                    "slides open. The rear gate can now be opened."
                )
            self.threat += 2
            return (
                "You pull the wrong lead. A bell rings once before you reconnect it. The "
                "override stays locked. Threat +2. A diagram or technical skill would help."
            )
        if action_id == "switch":
            self.finish(
                "THE LIGHT IS A SIGNAL",
                (
                    "The bulb flares. A bell screams behind the wall. The only doorway fills with"
                    " a pale mask. The previous victims tried to warn you."
                ),
            )
            return "The switch is wired to an alarm. You understand one second too late."
        if action_id == "passage":
            self.pending_scene = "yard"
            if "Flashlight" in self.inventory or character == "Sofia":
                return "You step over the chain and follow the draft. The passage opens into a rain-soaked courtyard."
            self.threat += 1
            return "In the dark you trip over a loose chain. Its rattle follows you into the courtyard. Threat +1."
        raise ValueError(f"Unhandled basement action: {action_id}")

    def _resolve_yard(self, action_id: str) -> str:
        """Resolve escape or confrontation using the run's accumulated state."""
        character = self.character
        if action_id == "gate":
            if (
                "Brass key" in self.inventory
                or self.gate_override_disabled
                or character == "Marcus"
            ):
                evidence = "Victims' ledger" in self.inventory
                self.finish(
                    "THE TRUTH GETS OUT" if evidence else "OUT OF BLACKTHORN",
                    "The gate gives way. You run until the house vanishes behind the trees."
                    + (
                        " At dawn, you hand the victims' ledger to the police. This time, the missing have names."
                        if evidence
                        else " You are alive. Behind you, Blackthorn keeps its secrets."
                    ),
                )
                return "One final pull. The gate swings open into the rain."
            self.threat += 1
            return (
                "The lock holds. You need the brass key, Marcus's strength, or the gate "
                "override. He draws closer. Threat +1."
            )
        if action_id == "hide":
            if character == "Sofia" or "tracks" in self.clues:
                self.threat = max(0, self.threat - 2)
                return (
                    "You anticipate his approach and slip behind the barrels. He turns toward the"
                    " wrong shadow. Threat -2. Make your next choice count."
                )
            self.threat += 1
            return (
                "Your shoulder catches a barrel. He turns toward the sound. Threat +1. You "
                "have one last opportunity."
            )
        if action_id == "trap":
            if "Kitchen knife" in self.inventory and "rig" in self.clues:
                self.finish(
                    "THE HOUSE TURNS ON HIM",
                    (
                        "You cut the service rope. A crash tears through the doorway as the "
                        "chandelier falls. The masked figure goes down. You take the road at dawn, "
                        "leaving Blackthorn silent at last."
                    ),
                )
                return "You wait until he stands beneath the doorway, then draw the knife across the frayed rope."
            self.finish(
                "A MOMENT TOO LATE",
                (
                    "Without a blade and a clear understanding of the rig, you fumble at the "
                    "rope. He closes the distance before you can free it."
                ),
            )
            return "The rope refuses to break in your hands."
        if action_id == "fight":
            self.finish(
                "HIS REACH IS LONGER",
                "You charge. He has been waiting for exactly this. The courtyard falls quiet again.",
            )
            return "You step out of cover and rush him."
        raise ValueError(f"Unhandled yard action: {action_id}")
