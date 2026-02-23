#!/usr/bin/env python3
"""
Menu bar app for audio input source switching.

Two modes:
  - Dictation: enforce priority input device (Yeti X > Blue Snowball)
  - Meeting:   input follows output device (e.g. both AirPods)

Requires: brew install switchaudio-osx
          pip install rumps
"""

from __future__ import annotations

import subprocess
from typing import Optional

import rumps

SWITCH_AUDIO_SOURCE = "SwitchAudioSource"
PRIORITY_INPUTS = ["Yeti X", "Blue Snowball"]
POLL_INTERVAL = 5
STATE_FILE = "/tmp/input_source_mode"

MODE_DICTATION = "dictation"
MODE_MEETING = "meeting"


def run_sas(*args: str) -> str:
    result = subprocess.run(
        [SWITCH_AUDIO_SOURCE, *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def get_connected_inputs() -> list[str]:
    output = run_sas("-t", "input", "-a")
    return [line for line in output.splitlines() if line]


def get_current_input() -> str:
    return run_sas("-t", "input", "-c")


def get_current_output() -> str:
    return run_sas("-t", "output", "-c")


def set_input(device: str) -> None:
    run_sas("-t", "input", "-s", device)


def pick_prioritized_input(connected: list[str]) -> Optional[str]:
    for preferred in PRIORITY_INPUTS:
        if preferred in connected:
            return preferred
    for preferred in PRIORITY_INPUTS:
        for device in connected:
            if preferred in device:
                return device
    return None


def is_continuity_camera(device: str) -> bool:
    return "continuity camera" in device.lower()


def find_matching_input(output_device: str, connected_inputs: list[str]) -> Optional[str]:
    """Find a connected input device whose name matches the current output."""
    for inp in connected_inputs:
        if inp == output_device:
            return inp
    for inp in connected_inputs:
        if output_device in inp or inp in output_device:
            return inp
    return None


def read_mode() -> str:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            mode = f.read().strip()
            if mode in (MODE_DICTATION, MODE_MEETING):
                return mode
    except FileNotFoundError:
        pass
    return MODE_DICTATION


def write_mode(mode: str) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(mode)


class InputSourceApp(rumps.App):
    def __init__(self):
        super().__init__("Input Source")
        self.mode = read_mode()

        self.dictation_item = rumps.MenuItem(
            "Dictation Mode", callback=self.set_dictation
        )
        self.meeting_item = rumps.MenuItem(
            "Meeting Mode", callback=self.set_meeting
        )
        self.input_info = rumps.MenuItem("Input: —")
        self.input_info.set_callback(None)
        self.output_info = rumps.MenuItem("Output: —")
        self.output_info.set_callback(None)

        self.menu = [
            self.dictation_item,
            self.meeting_item,
            None,
            self.input_info,
            self.output_info,
        ]
        self._apply_mode_ui()

        self.timer = rumps.Timer(self._poll, POLL_INTERVAL)
        self.timer.start()

    def _apply_mode_ui(self):
        is_dictation = self.mode == MODE_DICTATION
        self.dictation_item.state = is_dictation
        self.meeting_item.state = not is_dictation
        self.title = "Dictation" if is_dictation else "Meeting"

    def set_dictation(self, _sender=None):
        if self.mode == MODE_DICTATION:
            return
        self.mode = MODE_DICTATION
        write_mode(self.mode)
        self._apply_mode_ui()
        rumps.notification(
            "Input Source",
            "Switched to Dictation Mode",
            "Microphone follows priority list",
            sound=False,
        )

    def set_meeting(self, _sender=None):
        if self.mode == MODE_MEETING:
            return
        self.mode = MODE_MEETING
        write_mode(self.mode)
        self._apply_mode_ui()
        self._sync_meeting_input()

        rumps.notification(
            "Input Source",
            "Switched to Meeting Mode",
            "Microphone follows output device",
            sound=False,
        )

    def _poll(self, _timer):
        try:
            connected = get_connected_inputs()
            current_input = get_current_input()
            current_output = get_current_output()

            self.input_info.title = f"Input: {current_input or '—'}"
            self.output_info.title = f"Output: {current_output or '—'}"

            if is_continuity_camera(current_input):
                return

            if self.mode == MODE_DICTATION:
                self._poll_dictation(connected, current_input)
            else:
                self._poll_meeting(connected, current_input, current_output)
        except (subprocess.SubprocessError, OSError, ValueError) as exc:
            # Keep timer alive; surface failures for debugging.
            print(f"[input_source_menubar] poll error: {exc}", flush=True)

    def _poll_dictation(self, connected: list[str], current_input: str):
        priority = pick_prioritized_input(connected)
        if priority and current_input != priority:
            set_input(priority)

    def _poll_meeting(
        self,
        connected: list[str],
        current_input: str,
        current_output: str,
    ):
        match = find_matching_input(current_output, connected)
        if match and current_input != match:
            set_input(match)

    def _sync_meeting_input(self):
        current_output = get_current_output()
        connected = get_connected_inputs()
        current_input = get_current_input()
        match = find_matching_input(current_output, connected)
        if match and current_input != match:
            set_input(match)


if __name__ == "__main__":
    InputSourceApp().run()
