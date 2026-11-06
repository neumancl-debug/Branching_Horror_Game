THE HOLLOW AT BLACKTHORN — BRANCHING EDITION
============================================================

Python 3.10+ • Pygame 2.5+

RUN (Windows PowerShell)
------------------------
1. Extract hollow_blackthorn_branching_edition.zip.
2. Open the extracted hollow_blackthorn_branching_edition folder.
3. Run:
      python -m pip install pygame
      python hollow_blackthorn.py
   Or double-click START_GAME.bat.

RUN (macOS or Linux)
--------------------
      python3 -m pip install pygame
      python3 hollow_blackthorn.py

CONTROLS
--------
• Mouse: inspect and interact with visible objects.
• PATHS: open the available routes from the current location.
• BACK: return to your previous location (free).
• Space: open the PATHS menu.
• Esc: close the path menu, or return to the title screen.
• M: mute / unmute ambient audio.
• Click inventory items to inspect or use them. A bandage heals and disappears.

NEW FEATURES
------------
• 11 illustrated locations (six original rooms + upper landing, nursery,
  conservatory, chapel, and family crypt) with individual ambient loops.
• Branching room map with multiple distinct survival, escape and ghost endings.
• Room decision budgets persist: leaving and returning NEVER replenishes a room.
• Moving to a room and back does not use an investigation decision.
• Killer appearances depend on noise and earlier actions, rather than occurring
  automatically in every room. A room can only have one Watcher encounter per run.
• The opening road encounter happens only after TWO room investigations. Search
  the glove box first for a flashlight, then choose to use it in the encounter.
• Sprinting up the noisy stairs attracts the Watcher upstairs after a delay.
  Quietly climbing the stairs can avoid his attention.
• New item and clue routes: nursery locket, crypt manuscript, chapel candle,
  garden shears, ritual endings, and an optional greenhouse escape.
• Ghost figure renders only during encounters, and disappears completely after.

BRANCH MAP
----------
Road -> Entrance Hall
Entrance Hall -> Dining Room, Upper Landing (quiet/loud), Ruined Chapel
Dining Room -> Private Study, Glass Conservatory
Upper Landing -> Nursery, Study, Entrance Hall
Nursery -> Chapel (once diary discovered), Upper Landing
Study -> Basement, Upper Landing, Dining Room, hidden Chapel passage
Basement -> Family Crypt, Rear Yard (locked until you find a way through)
Family Crypt <-> Chapel, Basement
Conservatory <-> Dining Room, Rear Yard
Rear Yard <-> Basement, Conservatory

Note: Some paths are blocked until you find the appropriate clues or tools.
Not every game follows the same branch or reaches the same ending.

FILES
-----
• hollow_blackthorn.py — game source code
• assets/ — all image and audio files; keep beside the Python file
• requirements.txt — pygame dependency
• START_GAME.bat — Windows starter

QUALITY CHECKS
--------------
Python syntax compiled; scripted logic tests verify the room graph, backtracking,
persistent decisions, four character stat profiles, conditional Watcher encounters,
flashlight timing, inventory consumption and distinct endings. Live graphical
Pygame testing was not available in the creation environment.


Map controls:
- Click MAP in the bottom-right controls, or press TAB, to open the estate map.
- The map marks your current room in red, visited rooms in gold, and unvisited rooms with ?.
