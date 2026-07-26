"""
X56 HOTAS Debounce Filter — Joystick Gremlin Plugin
=====================================================
This is a Joystick Gremlin user plugin that filters ghost button presses
on the Logitech X56 HOTAS by applying a configurable debounce timer.

A button press is only forwarded to the virtual joystick (vJoy) if it
stays pressed for longer than the debounce threshold. Ghost inputs are
typically <30ms, while real presses are >80ms.

SETUP:
  1. Install vJoy:          https://github.com/njz3/vJoy/releases
  2. Install Joystick Gremlin: https://whitemagic.github.io/JoystickGremlin/
  3. Place this file in your Joystick Gremlin user plugins folder
  4. In Gremlin, go to Plugins tab → enable this plugin
  5. Use HidHide to hide the physical X56 from games (Gremlin can do this)
  6. Map your games to the vJoy virtual device instead

HOW IT WORKS:
  - Every X56 button press starts a debounce timer
  - Only if the button is STILL pressed after the threshold does it
    register on the vJoy output
  - Releases are forwarded immediately
  - A log counts filtered ghost inputs per session
"""

import gremlin
from gremlin.user_plugin import *
import time
import threading
from collections import defaultdict

# ── User-Configurable Parameters (shown in Gremlin UI) ────────────

mode = ModeVariable("Mode", "Default")

debounce_ms = IntegerVariable(
    "Debounce threshold (ms)",
    "Button presses shorter than this are filtered as ghosts. "
    "Start with 60ms and increase if ghosts still get through.",
    60,       # default
    10,       # min
    500       # max
)

log_filtered = BoolVariable(
    "Log filtered ghost inputs",
    "Print filtered ghost presses to the Gremlin log window.",
    True
)

# ── Internal State ─────────────────────────────────────────────────

# Track pending presses: button_id -> timer thread
_pending_timers = {}
_lock = threading.Lock()
_ghost_count = defaultdict(int)
_total_filtered = 0

# ── Debounce Logic ─────────────────────────────────────────────────

def make_debounce_press(button_id, vjoy_btn, device_name):
    """
    Returns a callback for button press events that applies debounce.
    """

    def on_press(event):
        global _total_filtered

        if event.is_pressed:
            # Button pressed — start debounce timer
            def confirm_press():
                """Called after debounce delay — forward if still pressed."""
                with _lock:
                    if button_id in _pending_timers:
                        del _pending_timers[button_id]
                        vjoy_btn.is_pressed = True

            timer = threading.Timer(debounce_ms.value / 1000.0, confirm_press)
            with _lock:
                # Cancel any existing timer for this button
                if button_id in _pending_timers:
                    _pending_timers[button_id].cancel()
                _pending_timers[button_id] = timer
            timer.start()

        else:
            # Button released
            with _lock:
                if button_id in _pending_timers:
                    # Release came before debounce expired → ghost!
                    _pending_timers[button_id].cancel()
                    del _pending_timers[button_id]
                    _total_filtered += 1
                    _ghost_count[button_id] += 1
                    if log_filtered.value:
                        gremlin.util.log(
                            f"[X56 Debounce] FILTERED ghost: {device_name} "
                            f"Button {button_id} "
                            f"(total filtered: {_total_filtered})"
                        )
                else:
                    # Normal release — forward it
                    vjoy_btn.is_pressed = False

    return on_press


# ── Plugin Registration ────────────────────────────────────────────
#
# NOTE: Joystick Gremlin's plugin API requires you to set up decorators
# for each button you want to filter. The example below shows the pattern.
#
# You will need to customize the device GUID and button numbers for YOUR
# specific X56. To find your GUIDs:
#   1. Open Joystick Gremlin
#   2. Go to the Device tab
#   3. Your X56 Stick and Throttle will each have a GUID shown
#
# TEMPLATE — Copy and adjust for each button you want to debounce:
#
# stick = gremlin.input_devices.JoystickDecorator(
#     "X56 Rhino Stick",               # Device name as shown in Gremlin
#     "{YOUR-STICK-GUID-HERE}",        # Device GUID
#     mode.value
# )
#
# @stick.button(1)    # Button number
# def stick_btn1(event, vjoy):
#     handler = make_debounce_press(
#         button_id="stick_1",
#         vjoy_btn=vjoy[1].button(1),   # vJoy device 1, button 1
#         device_name="Stick"
#     )
#     handler(event)
#
# Repeat the @stick.button(N) block for each button that ghosts.
# The diagnostic tool will tell you exactly which buttons to target.
# ───────────────────────────────────────────────────────────────────
