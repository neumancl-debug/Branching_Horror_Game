# The Hollow at Blackthorn

A mouse-driven 2D point-and-click horror game made with Python and Pygame.

## Requirements
- Python 3.10 or newer
- Pygame 2.5 or newer

## Run on Windows
1. Extract `hollow_blackthorn_game_final.zip`.
2. Open the extracted `hollow_blackthorn_game_final` folder.
3. Click the address bar, type `cmd`, and press Enter.
4. Install Pygame if needed:
   ```
   python -m pip install pygame
   ```
5. Start the game:
   ```
   python hollow_blackthorn.py
   ```

If `python` does not work, try:
```
py hollow_blackthorn.py
```

## Run on macOS / Linux
Open a terminal in the extracted folder and run:
```
python3 -m pip install pygame
python3 hollow_blackthorn.py
```

## Controls
- Hover over highlighted objects in the scene to identify them.
- Click an object or one of the action cards at the bottom.
- Every interaction uses one decision.
- Click **Continue** at any time to advance to the next scene.
- Press **Space** as a shortcut for Continue.
- Press **M** to mute/unmute scene ambience (interaction clicks remain audible).
- Press **Esc** to quit.

## Included in this build
- Illustrated backgrounds for **all six scenes**.
- Six unique looping ambient soundscapes, one for each room:
  - **Stranded Car:** Rain, wind, thunder, and dripping water.
  - **Entrance Hall:** Drafts, old wood creaks, and distant taps.
  - **Dining Room:** Rain at the windows, ticking, and faint glass clinks.
  - **Study:** Electrical hum, relay buzz, and subtle paper noises.
  - **Basement:** Generator rumbles, pipe rattles, and water drips.
  - **Rear Yard:** Gusty rain, distant thunder, and rattling iron.
- 1.8-second crossfades between scenes so room ambience changes smoothly.
- Original quiet musical drone remains beneath the room ambience.
- Separate button/interact sound that plays over the environment.
- On-screen popup messages after interactions so you can see what happened.
- Mouse cursor enabled for normal point-and-click play.

## Important
Keep the `assets` folder in the same directory as `hollow_blackthorn.py`.
