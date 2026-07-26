"""
X56 HOTAS Ghost Input Diagnostic Tool
======================================
Monitors your Logitech X56 for phantom button presses and logs them.
Run this with the HOTAS plugged in but hands off to identify which
buttons are firing ghost inputs and how frequently.

Requirements: pip install pygame
Usage:       python x56_ghost_diagnostic.py
"""

import pygame
import time
import sys
from datetime import datetime
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────────
MONITOR_DURATION_SECONDS = 120   # How long to monitor (default: 2 min)
POLL_RATE_HZ = 500               # How often to check inputs (Hz)
# ───────────────────────────────────────────────────────────────────

def find_x56_devices(joysticks):
    """Identify X56 stick and throttle from connected joysticks."""
    x56_devices = []
    for i, js in enumerate(joysticks):
        name = js.get_name().lower()
        if "x56" in name or "x-56" in name or "saitek" in name:
            x56_devices.append((i, js))
    return x56_devices

def main():
    pygame.init()
    pygame.joystick.init()

    num_joysticks = pygame.joystick.get_count()
    if num_joysticks == 0:
        print("ERROR: No joysticks detected. Is your X56 plugged in?")
        sys.exit(1)

    # Initialize all joysticks
    joysticks = []
    for i in range(num_joysticks):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

    # Find X56 devices
    x56_devices = find_x56_devices(joysticks)

    if not x56_devices:
        print("WARNING: Could not auto-detect X56 by name. Listing all devices:\n")
        for i, js in enumerate(joysticks):
            print(f"  [{i}] {js.get_name()} — {js.get_numbuttons()} buttons, {js.get_numaxes()} axes")
        print("\nMonitoring ALL connected joysticks.\n")
        x56_devices = list(enumerate(joysticks))
    else:
        print("Detected X56 devices:")
        for i, js in x56_devices:
            print(f"  [{i}] {js.get_name()} — {js.get_numbuttons()} buttons")
        print()

    # Record initial button states
    button_states = {}
    for idx, js in x56_devices:
        for b in range(js.get_numbuttons()):
            button_states[(idx, b)] = js.get_button(b)

    # Ghost tracking
    ghost_log = []          # list of (timestamp, device_idx, button, duration_ms)
    ghost_counts = defaultdict(int)  # (device_idx, button) -> count
    press_start = {}        # (device_idx, button) -> time of press

    print("=" * 60)
    print("  GHOST INPUT DIAGNOSTIC — HANDS OFF THE HOTAS!")
    print("=" * 60)
    print(f"  Monitoring for {MONITOR_DURATION_SECONDS} seconds at {POLL_RATE_HZ} Hz")
    print(f"  Started at {datetime.now().strftime('%H:%M:%S')}")
    print("  Any button activity below is a ghost input.")
    print("=" * 60)
    print()

    start_time = time.time()
    poll_interval = 1.0 / POLL_RATE_HZ
    total_ghosts = 0

    try:
        while time.time() - start_time < MONITOR_DURATION_SECONDS:
            pygame.event.pump()

            for idx, js in x56_devices:
                for b in range(js.get_numbuttons()):
                    current = js.get_button(b)
                    prev = button_states[(idx, b)]

                    if current != prev:
                        now = time.time()
                        device_name = js.get_name()

                        if current == 1:
                            # Button pressed — record start
                            press_start[(idx, b)] = now
                            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                            print(f"  ⚡ GHOST PRESS   [{timestamp}]  {device_name}  Button {b}")
                            total_ghosts += 1
                            ghost_counts[(idx, b)] += 1
                        else:
                            # Button released — calculate duration
                            if (idx, b) in press_start:
                                duration_ms = (now - press_start[(idx, b)]) * 1000
                                ghost_log.append((datetime.now(), idx, b, duration_ms))
                                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                                print(f"  ⚡ GHOST RELEASE [{timestamp}]  {device_name}  Button {b}  (held {duration_ms:.1f} ms)")
                                del press_start[(idx, b)]

                        button_states[(idx, b)] = current

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\n  Stopped early by user.")

    elapsed = time.time() - start_time

    # ── Report ─────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  DIAGNOSTIC REPORT")
    print("=" * 60)
    print(f"  Duration monitored: {elapsed:.0f} seconds")
    print(f"  Total ghost presses: {total_ghosts}")
    print()

    if total_ghosts == 0:
        print("  No ghost inputs detected during this session.")
        print("  Try running again for a longer duration, or wiggle the")
        print("  USB cable gently to provoke intermittent contacts.")
    else:
        print("  Ghost inputs by button (sorted by frequency):")
        print("  " + "-" * 50)
        sorted_ghosts = sorted(ghost_counts.items(), key=lambda x: -x[1])
        for (idx, btn), count in sorted_ghosts:
            device_name = dict(x56_devices)[idx].get_name()
            avg_dur = 0
            durations = [d for (_, di, bi, d) in ghost_log if di == idx and bi == btn]
            if durations:
                avg_dur = sum(durations) / len(durations)
            print(f"    {device_name} — Button {btn}: {count} ghosts (avg duration: {avg_dur:.1f} ms)")

        print()
        print("  RECOMMENDATIONS:")
        print("  " + "-" * 50)

        short_ghosts = [d for (_, _, _, d) in ghost_log if d < 50]
        if len(short_ghosts) > len(ghost_log) * 0.5:
            print("  • Most ghost presses are very short (<50ms).")
            print("    → A debounce filter of 50-80ms should eliminate them.")
        else:
            print("  • Some ghost presses have longer durations.")
            print("    → Use a debounce filter of 80-150ms.")
            print("    → Also consider hardware fixes (powered USB hub, ferrite cores).")

        # Which buttons to filter
        problem_buttons = [btn for (_, btn), count in sorted_ghosts if count >= 2]
        if problem_buttons:
            btn_str = ", ".join(str(b) for b in problem_buttons)
            print(f"  • Worst offending buttons: {btn_str}")
            print(f"    → Focus your debounce filter on these buttons.")

    print()
    print("=" * 60)

    # Save log to file
    if total_ghosts > 0:
        log_filename = f"x56_ghost_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_filename, 'w') as f:
            f.write(f"X56 Ghost Input Log — {datetime.now()}\n")
            f.write(f"Duration: {elapsed:.0f}s | Total ghosts: {total_ghosts}\n\n")
            for ts, idx, btn, dur in ghost_log:
                device_name = dict(x56_devices)[idx].get_name()
                f.write(f"{ts.strftime('%H:%M:%S.%f')[:-3]}  {device_name}  Button {btn}  {dur:.1f}ms\n")
        print(f"  Log saved to: {log_filename}")
        print()

    pygame.quit()

if __name__ == "__main__":
    main()
