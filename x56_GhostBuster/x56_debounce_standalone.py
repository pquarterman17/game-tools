"""
X56 HOTAS Standalone Debounce Filter
======================================
A self-contained ghost input filter that reads your physical X56,
applies debounce filtering, and outputs clean signals to a vJoy
virtual joystick. No Joystick Gremlin required.

Requirements:
  pip install pygame pyvjoy
  + vJoy driver installed (https://github.com/njz3/vJoy/releases)

Usage:
  1. Install vJoy and configure at least 1 virtual device with enough buttons
  2. pip install pygame pyvjoy
  3. python x56_debounce_standalone.py
  4. Use HidHide to hide the physical X56 from games
  5. Map your game to the vJoy device

Configuration:
  Edit the settings below, or run the diagnostic tool first to find
  which buttons need filtering and what debounce threshold to use.
"""

import pygame
import pyvjoy
import time
import sys
import threading
from collections import defaultdict
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
#  CONFIGURATION — Edit these to match your setup
# ══════════════════════════════════════════════════════════════════

# Debounce threshold in milliseconds.
# Ghost inputs are typically <30ms. Real presses are >80ms.
# Start at 60ms; increase if ghosts still get through.
DEBOUNCE_MS = 60

# vJoy device ID (usually 1 unless you have multiple virtual devices)
VJOY_DEVICE_ID = 1

# Set to True to also pass through axis data (throttle, stick axes)
PASS_THROUGH_AXES = True

# Axis deadzone — small axis movements below this % are ignored
AXIS_DEADZONE_PERCENT = 3

# Set to filter only specific buttons (empty list = filter ALL buttons)
# Use the diagnostic tool to find which buttons ghost, then list them here.
# Example: FILTER_ONLY_BUTTONS = [4, 7, 12]
FILTER_ONLY_BUTTONS = []

# Poll rate in Hz
POLL_RATE_HZ = 500

# ══════════════════════════════════════════════════════════════════


class DebounceFilter:
    """Manages debounce state for all buttons on a joystick."""

    def __init__(self, debounce_ms, filter_buttons=None):
        self.debounce_sec = debounce_ms / 1000.0
        self.filter_buttons = set(filter_buttons) if filter_buttons else None
        self.press_times = {}       # button -> time of press
        self.confirmed = set()      # buttons confirmed as real presses
        self.output_state = {}      # button -> current output state (0 or 1)
        self.ghost_count = defaultdict(int)
        self.total_filtered = 0
        self.total_forwarded = 0

    def should_filter(self, button):
        """Check if this button should be debounced."""
        if self.filter_buttons is None:
            return True
        return button in self.filter_buttons

    def update(self, button, raw_state):
        """
        Process a raw button state. Returns the filtered output state.
        """
        prev_output = self.output_state.get(button, 0)

        # If not filtering this button, pass through directly
        if not self.should_filter(button):
            self.output_state[button] = raw_state
            return raw_state

        now = time.time()

        if raw_state == 1:
            # Button is pressed
            if button not in self.press_times:
                # New press — start debounce timer
                self.press_times[button] = now

            # Check if debounce period has elapsed
            if now - self.press_times[button] >= self.debounce_sec:
                if button not in self.confirmed:
                    self.confirmed.add(button)
                    self.total_forwarded += 1
                self.output_state[button] = 1
                return 1
            else:
                # Still in debounce window — don't forward yet
                self.output_state[button] = 0
                return 0

        else:
            # Button is released
            if button in self.press_times:
                if button not in self.confirmed:
                    # Released before debounce expired → ghost!
                    self.ghost_count[button] += 1
                    self.total_filtered += 1
                    elapsed_ms = (now - self.press_times[button]) * 1000
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    print(f"  ⚡ FILTERED ghost: Button {button} ({elapsed_ms:.1f}ms) [{timestamp}]")

                # Clean up
                self.press_times.pop(button, None)
                self.confirmed.discard(button)

            self.output_state[button] = 0
            return 0


def apply_deadzone(value, deadzone_pct):
    """Apply deadzone to a -1.0 to 1.0 axis value."""
    threshold = deadzone_pct / 100.0
    if abs(value) < threshold:
        return 0.0
    # Rescale remaining range
    sign = 1 if value > 0 else -1
    return sign * (abs(value) - threshold) / (1.0 - threshold)


def axis_to_vjoy(value):
    """Convert pygame axis (-1.0 to 1.0) to vJoy range (1 to 32767)."""
    return int((value + 1.0) / 2.0 * 32766) + 1


def main():
    pygame.init()
    pygame.joystick.init()

    num_joysticks = pygame.joystick.get_count()
    if num_joysticks == 0:
        print("ERROR: No joysticks detected.")
        sys.exit(1)

    # Initialize joysticks
    joysticks = []
    for i in range(num_joysticks):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

    # Find X56 devices
    x56_devices = []
    for i, js in enumerate(joysticks):
        name = js.get_name().lower()
        if "x56" in name or "x-56" in name or "saitek" in name:
            x56_devices.append((i, js))

    if not x56_devices:
        print("Could not auto-detect X56. Available devices:")
        for i, js in enumerate(joysticks):
            print(f"  [{i}] {js.get_name()}")
        print("\nUsing all devices.")
        x56_devices = list(enumerate(joysticks))
    else:
        print("Detected X56 devices:")
        for i, js in x56_devices:
            print(f"  [{i}] {js.get_name()}")

    # Initialize vJoy
    try:
        vjoy = pyvjoy.VJoyDevice(VJOY_DEVICE_ID)
        print(f"\nvJoy device {VJOY_DEVICE_ID} connected.")
    except Exception as e:
        print(f"\nERROR: Could not connect to vJoy device {VJOY_DEVICE_ID}.")
        print(f"  Make sure vJoy is installed and device {VJOY_DEVICE_ID} is configured.")
        print(f"  Error: {e}")
        sys.exit(1)

    # Create debounce filters (one per device)
    filters = {}
    for idx, js in x56_devices:
        filters[idx] = DebounceFilter(DEBOUNCE_MS, FILTER_ONLY_BUTTONS or None)

    # Calculate total buttons across all devices for vJoy mapping
    button_offset = {}
    offset = 0
    for idx, js in x56_devices:
        button_offset[idx] = offset
        offset += js.get_numbuttons()

    print()
    print("=" * 60)
    print("  X56 DEBOUNCE FILTER — ACTIVE")
    print("=" * 60)
    print(f"  Debounce threshold: {DEBOUNCE_MS}ms")
    if FILTER_ONLY_BUTTONS:
        print(f"  Filtering buttons:  {FILTER_ONLY_BUTTONS}")
    else:
        print(f"  Filtering:          ALL buttons")
    print(f"  Axes passthrough:   {'Yes' if PASS_THROUGH_AXES else 'No'}")
    print(f"  Axis deadzone:      {AXIS_DEADZONE_PERCENT}%")
    print(f"  Output:             vJoy device {VJOY_DEVICE_ID}")
    print(f"  Poll rate:          {POLL_RATE_HZ} Hz")
    print()
    print("  Press Ctrl+C to stop and see statistics.")
    print("=" * 60)
    print()

    poll_interval = 1.0 / POLL_RATE_HZ
    start_time = time.time()

    try:
        while True:
            pygame.event.pump()

            for idx, js in x56_devices:
                debounce = filters[idx]
                base_btn = button_offset[idx]

                # Process buttons
                for b in range(js.get_numbuttons()):
                    raw = js.get_button(b)
                    filtered = debounce.update(b, raw)
                    vjoy_btn_id = base_btn + b + 1  # vJoy buttons are 1-indexed
                    try:
                        vjoy.set_button(vjoy_btn_id, filtered)
                    except Exception:
                        pass  # vJoy may not have enough buttons configured

                # Pass through axes
                if PASS_THROUGH_AXES:
                    axis_map = [
                        pyvjoy.HID_USAGE_X,
                        pyvjoy.HID_USAGE_Y,
                        pyvjoy.HID_USAGE_Z,
                        pyvjoy.HID_USAGE_RX,
                        pyvjoy.HID_USAGE_RY,
                        pyvjoy.HID_USAGE_RZ,
                        pyvjoy.HID_USAGE_SL0,
                        pyvjoy.HID_USAGE_SL1,
                    ]
                    for a in range(min(js.get_numaxes(), len(axis_map))):
                        raw_axis = js.get_axis(a)
                        filtered_axis = apply_deadzone(raw_axis, AXIS_DEADZONE_PERCENT)
                        vjoy_value = axis_to_vjoy(filtered_axis)
                        try:
                            vjoy.set_axis(axis_map[a], vjoy_value)
                        except Exception:
                            pass

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        pass

    # ── Session Statistics ─────────────────────────────────────────
    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print("  SESSION STATISTICS")
    print("=" * 60)
    print(f"  Runtime: {elapsed:.0f} seconds")

    for idx, js in x56_devices:
        debounce = filters[idx]
        print(f"\n  {js.get_name()}:")
        print(f"    Ghost inputs filtered: {debounce.total_filtered}")
        print(f"    Real presses forwarded: {debounce.total_forwarded}")
        if debounce.ghost_count:
            print(f"    Worst offenders:")
            sorted_ghosts = sorted(debounce.ghost_count.items(), key=lambda x: -x[1])
            for btn, count in sorted_ghosts[:10]:
                print(f"      Button {btn}: {count} ghosts filtered")

    print()
    print("=" * 60)
    pygame.quit()


if __name__ == "__main__":
    main()
