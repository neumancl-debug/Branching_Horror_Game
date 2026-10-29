# Developer guide

This is an AI-assisted class prototype. It demonstrates a small decision-based
game; its killer logic uses deterministic rules, not machine learning or a live
AI service. No network access or API key is needed to play.

## File responsibilities

| File | Responsibility |
| --- | --- |
| `story.py` | Character/scene data and all decision rules |
| `main.py` | Pygame drawing, keyboard/mouse input, movement, and application loop |
| `ui.py` | Shared palette, portable fonts, cached background, panels, portraits, and manor artwork |
| `test_story.py` | Story paths, character abilities, and state invariants |
| `test_ui.py` | Input handling, modal behavior, and resized-window hit detection |
| `requirements.txt` | Runtime dependency |
| `requirements-dev.txt` | Runtime dependency plus optional formatter/linter |
| `pyproject.toml` | Shared formatting and lint settings |

The story module does not import Pygame. This separation lets us test outcomes
without graphics and change the interface without rewriting the game rules.
The renderer still has one `Game` class: adding a full scene framework, database,
or inheritance tree would add complexity without helping this prototype.

Styling helpers in `ui.py` draw original artwork with Pygame primitives. The
background texture is cached when the UI starts; animated rain and nearby
interaction rings use elapsed time. Heading and body fonts have platform fallback
lists, with Pygame's bundled default as a final fallback. The artwork does not
change action IDs, decision budgets, collision bounds, or story outcomes.

## Data model

`Character`, `Action`, and `Scene` are frozen dataclasses: named fields make their
meaning visible, and instances cannot be changed accidentally during a run.
The dictionaries containing them are module-level content definitions.

`GameState` is a mutable dataclass representing a single playthrough:

- `character` and `scene` identify the current survivor and room.
- `decisions` is the current room's remaining action budget. The constructor
  accepts `None` and immediately replaces it with that scene's default.
- `inventory` is a set of collected physical items; duplicates are unnecessary.
- `clues` maps internal clue IDs to text for the journal.
- `used` prevents repeating an action in the same scene.
- `gate_override_disabled` records a persistent world change, separate from items.
- `threat` tracks danger, with the limit defined once as `MAX_THREAT`.
- `pending_scene` postpones a scene change until its outcome has been read.
- `ending` and `ending_text` describe a completed run.
- `history` records the complete outcome text returned by accepted actions.

Mutable collections use `field(default_factory=...)`, giving each run its own
containers. The constructor rejects unknown characters, scenes, and invalid
decision/threat ranges. Type hints describe expected inputs; they do not replace
runtime checks. These dataclasses are internal game data, not an untrusted save
file format.

## What happens when a player chooses an action?

1. The UI checks that gameplay is active and no overlay is blocking input.
2. It passes an action ID to `GameState.choose()`.
3. `choose()` rejects invalid, repeated, or unavailable actions without mutation.
4. An accepted action consumes exactly one decision, even if the attempt fails.
5. A scene-specific private method applies its items, clues, threat, or ending.
6. Fatal danger cancels any pending scene change. An action that already resolves
   an ending keeps that ending.
7. If decisions run out without an ending or explicit exit, threat increases and
   the next scene is queued. In the courtyard, exhaustion ends the run instead.
8. The complete message is recorded and displayed in a result modal.
9. After acknowledgement, `enter_pending()` changes scene, resets the budget,
   clears used actions, and keeps inventory and clues.

The UI intentionally cannot skip the outcome to change rooms immediately.
Walking and opening the journal never call `choose()`, so neither costs a turn.
If threat reaches its limit, the run ends before a queued transition is committed.

## UI and movement

The three screen modes are `title`, `play`, and `ending`. During play, result
messages, the journal, and pause are overlays that block decisions and movement.
`handle()` processes discrete events; `update(dt)` handles held movement keys;
`draw()` renders the current view.

The game draws to a fixed 1200 by 820 canvas and scales it into the window with
side or top borders as needed. `mouse()` reverses that transform for accurate
button clicks. Scene action positions and furniture collision rectangles are
relative to the world surface, rather than the whole window.

Movement uses pixels per second multiplied by elapsed time. Direction vectors
are normalized so diagonal movement is not faster. Horizontal and vertical
collision checks are separate so the player can slide along furniture. A capped
frame interval prevents a large jump after dragging or stalling the window.
Pygame cleanup runs in `finally` so the display is released after an exception.

## Extending the prototype

To add an action to an existing scene:

1. Add an `Action` with a unique ID within that scene, a label, map position, and hint.
2. Add its outcome to that scene's `_resolve_*` method. These methods are private;
   callers should use `choose()` so validation and decision costs are applied.
3. Use inventory for objects, clues for learned information, and state fields for
   persistent world changes. Avoid encoding state flags as fake items.
4. Add a behavioral test covering its outcome and relevant failure conditions.
5. Check the rendered text and journal for overflow.

For a new room, also add scene data, a rule handler in `_resolve()`'s dispatch
table, its scenery in `draw_world()`, and bounds in `SCENE_OBSTACLES`. Connect its
route from another room. The UI currently supports four actions per scene;
larger action lists or longer journals require a layout/scrolling change.

## Verification and limitations

`python -m unittest -v` checks story and input behavior. UI tests use SDL's dummy
display, so they do not open a window. The CLI smoke check renders all rooms and
overlays and can save a preview. Automated checks do not judge text readability,
art quality, story balance, or replace a manual playthrough.

Ruff checks imports, unused code, common errors, and formatting. Run the commands
in the README before submitting changes. Comments explain design decisions and
non-obvious operations; docstrings describe classes and method contracts rather
than repeating each line of code.

The project intentionally has no save system, sound, enemy pathfinding, combat
simulation, or online services. Threat is driven by choices. Story IDs and item
names remain simple strings, appropriate to this small fixed set of content.
