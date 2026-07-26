# X56 HOTAS Ghost Input Fix

## What's Included

| File | Purpose |
|------|---------|
| `x56_ghost_diagnostic.py` | Identifies which buttons are ghosting and how often |
| `x56_debounce_standalone.py` | Standalone filter — reads X56, outputs clean signals to vJoy |
| `x56_debounce_gremlin.py` | Joystick Gremlin plugin (if you already use Gremlin) |

## Quick Start

### Step 1: Run the Diagnostic

This tells you exactly which buttons are ghosting and recommends a debounce threshold.

```
pip install pygame
python x56_ghost_diagnostic.py
```

**Keep your hands off the HOTAS** for the full 2-minute scan. Any button activity detected is a ghost input. The tool will report which buttons are worst and suggest a debounce value.

### Step 2: Install the Filter

**Option A — Standalone (Recommended)**

This is the simplest path. It runs as a Python script that sits between your X56 and your games.

1. **Install vJoy** — download from [github.com/njz3/vJoy/releases](https://github.com/njz3/vJoy/releases)
   - Run "Configure vJoy" and set up 1 device with 128 buttons and 8 axes
2. **Install HidHide** — download from [github.com/nefarius/HidHide/releases](https://github.com/nefarius/HidHide/releases)
   - This hides the physical X56 from games so they only see the clean vJoy output
   - In HidHide, add your X56 devices to the hidden list
   - Add `python.exe` to the application whitelist (so the filter script can still see the X56)
3. **Install Python dependencies:**
   ```
   pip install pygame pyvjoy
   ```
4. **Edit the config** in `x56_debounce_standalone.py`:
   - Set `DEBOUNCE_MS` to the value the diagnostic recommended (start with 60)
   - Optionally set `FILTER_ONLY_BUTTONS` to target specific buttons
5. **Run the filter:**
   ```
   python x56_debounce_standalone.py
   ```
6. **Map your games to the vJoy device** instead of the X56 directly

**Option B — Joystick Gremlin Plugin**

If you already use Joystick Gremlin:

1. Make sure vJoy is installed
2. Copy `x56_debounce_gremlin.py` to your Gremlin user plugins folder
3. Open Gremlin → Plugins tab → enable the X56 Debounce plugin
4. Set your debounce threshold in the plugin settings
5. You'll need to edit the script to add your device GUIDs and button mappings (see comments in the file)

### Step 3: Tune the Threshold

- **Too low** (e.g., 20ms): Some ghosts still get through
- **Sweet spot** (40-80ms): Ghosts filtered, no noticeable input lag
- **Too high** (e.g., 200ms+): Real quick-taps might get eaten

Start at 60ms. If you still see ghosts, increase by 10ms increments. For flight sims, even 100ms of debounce is imperceptible.

## How It Works

Ghost inputs on the X56 are typically caused by electrical noise on the USB connection. They manifest as extremely brief button presses (usually under 30ms) — far shorter than any real human press.

The debounce filter works by holding every button press in a buffer. Only if the button is **still pressed** after the debounce threshold does it count as real and get forwarded to the virtual joystick. If the button releases before the timer expires, it's silently discarded as a ghost.

## Bonus Hardware Tips

While the software filter solves the symptom, these hardware steps can reduce the root cause:

- **Use a powered USB hub** — the X56 is power-hungry; underpowered USB ports cause noise
- **Separate stick and throttle onto different USB controllers** — not just different ports, different controllers
- **Add ferrite cores** to both USB cables (clip-on ferrite beads, ~$5 on Amazon)
- **Avoid USB 3.0 ports** — try USB 2.0 ports, which have less electrical interference
- **Shorten cable runs** — use the shortest USB cables possible
