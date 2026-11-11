#!/usr/bin/env python3
"""
Dynamic Island - Feature Test Suite & Simulation Runner
Test all features of Linux Dynamic Island:
- Desktop & App Notifications
- Volume & OSD Toasts
- MPRIS Music Player Simulation (Album Art, Song Title, Controls, Animations)
- GSettings Configuration Toggling (Expand on Click/Hover, Margin, Height)
- Automated Smoke Tests

Usage:
    python3 tests/test_features.py
    python3 tests/test_features.py --test notification
    python3 tests/test_features.py --test volume
    python3 tests/test_features.py --test music
    python3 tests/test_features.py --test all
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log(msg, symbol="ℹ️"):
    print(f"{symbol} {msg}")


def test_notification():
    """Send desktop and app notifications to test Dynamic Island toast."""
    log("Sending standard Desktop Notification via notify-send...", "🔔")
    subprocess.run([
        'notify-send',
        'Dynamic Island Test',
        'Hello from Linux Dynamic Island test suite!',
        '-i', 'dialog-information',
        '-t', '3000'
    ])
    time.sleep(1.5)

    log("Sending App Notification (Spotify style)...", "🎵")
    subprocess.run([
        'notify-send',
        'Spotify',
        'Now Playing: The Weeknd - Blinding Lights',
        '-i', 'spotify',
        '-t', '3500'
    ])
    time.sleep(1.5)

    log("Sending System Notification (Warning style)...", "⚠️")
    subprocess.run([
        'notify-send',
        'Battery Warning',
        'Battery level is at 20%. Please plug in charger.',
        '-i', 'battery-caution-symbolic',
        '-u', 'critical',
        '-t', '3000'
    ])
    log("Notifications dispatched! Check your Dynamic Island on the screen.", "✅")


def test_volume():
    """Trigger volume change to test Dynamic Island OSD toast and level bar."""
    log("Testing Volume OSD Toast...", "🔊")
    tool = None
    if shutil.which('wpctl'):
        tool = 'wpctl'
    elif shutil.which('pactl'):
        tool = 'pactl'

    if not tool:
        log("Neither wpctl nor pactl found. Cannot trigger audio volume change.", "⚠️")
        return

    log(f"Using {tool} to step volume up and down...", "🎛️")
    if tool == 'wpctl':
        subprocess.run(['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%+'])
        time.sleep(1.2)
        subprocess.run(['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%-'])
    else:
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%'])
        time.sleep(1.2)
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%'])

    log("Volume change triggered! Check the volume toast and progress bar on Dynamic Island.", "✅")


def test_music():
    """Launch the MPRIS mock music player simulation."""
    mpris_script = os.path.join(REPO_ROOT, 'tests', 'simulate_mpris.py')
    log("Starting MPRIS Music Player Simulation...", "🎶")
    subprocess.run([sys.executable, mpris_script])


def test_settings():
    """Test GSettings reading and setting changes."""
    schema = 'org.gnome.shell.extensions.dynamic-island'
    log("Testing GSettings Configuration Keys...", "⚙️")

    # Read current settings
    res = subprocess.run(['gsettings', 'get', schema, 'expand-on'], capture_output=True, text=True)
    current_expand = res.stdout.strip().replace("'", "")
    log(f"Current 'expand-on': {current_expand}")

    # Toggle test
    new_expand = 'hover' if current_expand == 'click' else 'click'
    log(f"Switching 'expand-on' to '{new_expand}'...")
    subprocess.run(['gsettings', 'set', schema, 'expand-on', new_expand])
    time.sleep(0.5)

    res_check = subprocess.run(['gsettings', 'get', schema, 'expand-on'], capture_output=True, text=True)
    log(f"Verified 'expand-on': {res_check.stdout.strip()}")

    # Restore
    log(f"Restoring 'expand-on' to '{current_expand}'...")
    subprocess.run(['gsettings', 'set', schema, 'expand-on', current_expand])
    log("GSettings key read/write test completed successfully!", "✅")


def test_code_quality():
    """Run automated unit tests for schemas, metadata, and JS syntax."""
    log("Running Code Quality & Integrity Unit Tests...", "🧪")
    test_path = os.path.join(REPO_ROOT, 'tests', 'test_code_quality.py')
    res = subprocess.run([sys.executable, test_path])
    if res.returncode == 0:
        log("All code quality tests passed!", "✅")
    else:
        log("Code quality tests reported issues.", "❌")


def run_all_tests():
    """Run a complete automated smoke test."""
    print("\n=======================================================")
    print("🚀 RUNNING COMPREHENSIVE DYNAMIC ISLAND SMOKE TEST")
    print("=======================================================\n")
    test_code_quality()
    print()
    test_settings()
    print()
    test_notification()
    print()
    test_volume()
    print("\n=======================================================")
    print("✨ ALL SMOKE TESTS COMPLETED!")
    print("To test the interactive Music Player, run:")
    print("    python3 tests/test_features.py --test music")
    print("=======================================================\n")


def interactive_menu():
    while True:
        print("\n" + "=" * 55)
        print("🏝️  DYNAMIC ISLAND FEATURE TEST RUNNER")
        print("=" * 55)
        print(" [1] Test Desktop & App Notifications (notify-send)")
        print(" [2] Test Volume OSD Toast (wpctl / pactl)")
        print(" [3] Simulate Music Player (MPRIS: Art, Track, Controls)")
        print(" [4] Test Settings & Configuration Keys (GSettings)")
        print(" [5] Run Code Quality & Syntax Unit Tests")
        print(" [6] Run Full Smoke Test (All non-blocking tests)")
        print(" [0] Exit")
        print("=" * 55)
        try:
            choice = input("Enter choice [0-6]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == '1':
            test_notification()
        elif choice == '2':
            test_volume()
        elif choice == '3':
            test_music()
        elif choice == '4':
            test_settings()
        elif choice == '5':
            test_code_quality()
        elif choice == '6':
            run_all_tests()
        elif choice in ('0', 'q', 'exit'):
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 0-6.")


def main():
    parser = argparse.ArgumentParser(description="Test Dynamic Island features.")
    parser.add_argument(
        '--test',
        choices=['notification', 'volume', 'music', 'settings', 'quality', 'all'],
        help="Run a specific test directly without interactive menu"
    )
    args = parser.parse_args()

    if args.test == 'notification':
        test_notification()
    elif args.test == 'volume':
        test_volume()
    elif args.test == 'music':
        test_music()
    elif args.test == 'settings':
        test_settings()
    elif args.test == 'quality':
        test_code_quality()
    elif args.test == 'all':
        run_all_tests()
    else:
        interactive_menu()


if __name__ == '__main__':
    main()
