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

SWITCH_AUDIO_SOURCE = "/opt/homebrew/bin/SwitchAudioSource"
PRIORITY_INPUTS = ["Yeti X", "Blue Snowball"]
HIDDEN_DEVICE_KEYWORDS = ["nomachine audio adapter", "nomachine microphone adapter"]
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


def get_connected_outputs() -> list[str]:
    output = run_sas("-t", "output", "-a")
    return [line for line in output.splitlines() if line]


def set_input(device: str) -> None:
    run_sas("-t", "input", "-s", device)


def set_input_background(device: str) -> None:
    subprocess.Popen(
        [SWITCH_AUDIO_SOURCE, "-t", "input", "-s", device],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def set_output(device: str) -> None:
    run_sas("-t", "output", "-s", device)


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


def is_airpods(device: str) -> bool:
    name = device.lower()
    return "airpods" in name or ("ellie" in name and "ears" in name)


def is_hidden_device(device: str) -> bool:
    name = device.lower()
    return any(keyword in name for keyword in HIDDEN_DEVICE_KEYWORDS)


def get_connected_airpods_name() -> Optional[str]:
    devices = get_connected_inputs() + get_connected_outputs()
    for d in devices:
        if is_airpods(d):
            return d
    return None


def open_sound_settings() -> None:
    subprocess.run(
        ["open", "x-apple.systempreferences:com.apple.Sound-Settings.extension"],
        check=False,
    )


def open_airpods_settings() -> None:
    subprocess.run(
        ["open", "x-apple.systempreferences:com.apple.BluetoothSettings"],
        check=False,
    )


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
        self.last_connected_inputs: list[str] = []
        self.last_connected_outputs: list[str] = []
        self.last_current_input: str = ""
        self.last_current_output: str = ""

        self.dictation_item = rumps.MenuItem(
            "Dictation Mode", callback=self.set_dictation
        )
        self.meeting_item = rumps.MenuItem(
            "Meeting Mode", callback=self.set_meeting
        )

        self.input_submenu = rumps.MenuItem("Input")
        self.output_submenu = rumps.MenuItem("Output")

        self.sound_settings_item = rumps.MenuItem(
            "Sound Settings...", callback=self._open_sound_settings
        )
        self.airpods_settings_item = rumps.MenuItem(
            "AirPods Settings...", callback=self._open_airpods_settings
        )

        self._populate_initial_devices()

        self.menu = [
            self.dictation_item,
            self.meeting_item,
            None,
            self.input_submenu,
            self.output_submenu,
            None,
            self.sound_settings_item,
            self.airpods_settings_item,
        ]
        self._apply_mode_ui()
        self._update_airpods_visibility()

        self.timer = rumps.Timer(self._poll, POLL_INTERVAL)
        self.timer.start()

    def _populate_initial_devices(self):
        current_input = get_current_input()
        current_output = get_current_output()
        connected_inputs = get_connected_inputs()
        connected_outputs = get_connected_outputs()
        self.last_connected_inputs = connected_inputs
        self.last_connected_outputs = connected_outputs
        self.last_current_input = current_input
        self.last_current_output = current_output
        self._update_submenu(
            self.input_submenu, connected_inputs, current_input, self._select_input
        )
        self._update_submenu(
            self.output_submenu, connected_outputs, current_output, self._select_output
        )

    def _rebuild_device_menus(
        self,
        connected_inputs: Optional[list[str]] = None,
        connected_outputs: Optional[list[str]] = None,
        current_input: Optional[str] = None,
        current_output: Optional[str] = None,
    ):
        if connected_inputs is None:
            connected_inputs = get_connected_inputs()
        if connected_outputs is None:
            connected_outputs = get_connected_outputs()
        if current_input is None:
            current_input = get_current_input()
        if current_output is None:
            current_output = get_current_output()

        self._update_submenu(
            self.input_submenu, connected_inputs, current_input, self._select_input
        )
        self._update_submenu(
            self.output_submenu, connected_outputs, current_output, self._select_output
        )

    def _update_submenu(self, submenu, devices, current, callback):
        filtered_devices = [d for d in devices if not is_hidden_device(d)]
        existing = {item.title: item for item in submenu.values()}
        new_set = set(filtered_devices)
        old_set = set(existing.keys())

        for name in old_set - new_set:
            del submenu[name]

        for device in filtered_devices:
            if device in existing:
                existing[device].state = device == current
            else:
                item = rumps.MenuItem(device, callback=callback)
                item.state = device == current
                submenu.add(item)

    def _select_input(self, sender):
        set_input(sender.title)
        self.last_current_input = sender.title
        self._rebuild_device_menus()

    def _select_output(self, sender):
        set_output(sender.title)
        self.last_current_output = sender.title
        if self.mode == MODE_MEETING:
            self._sync_meeting_input()
        self._rebuild_device_menus()

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
        # Apply dictation behavior immediately when switching modes.
        connected = self.last_connected_inputs or get_connected_inputs()
        current_input = self.last_current_input or get_current_input()
        new_input = self._poll_dictation(connected, current_input, background=True)
        self.last_current_input = new_input
        self._set_input_menu_state(new_input)
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
        new_input = self._sync_meeting_input(background=True)
        self.last_current_input = new_input
        self._set_input_menu_state(new_input)

        rumps.notification(
            "Input Source",
            "Switched to Meeting Mode",
            "Microphone follows output device",
            sound=False,
        )

    def _poll(self, _timer):
        try:
            connected = get_connected_inputs()
            connected_outputs = get_connected_outputs()
            current_input = get_current_input()
            current_output = get_current_output()
            self.last_connected_inputs = connected
            self.last_connected_outputs = connected_outputs
            self.last_current_input = current_input
            self.last_current_output = current_output

            self._rebuild_device_menus(
                connected_inputs=connected,
                connected_outputs=connected_outputs,
                current_input=current_input,
                current_output=current_output,
            )
            self._update_airpods_visibility(connected, connected_outputs)

            if is_continuity_camera(current_input):
                return

            if self.mode == MODE_DICTATION:
                self._poll_dictation(connected, current_input)
            else:
                self._poll_meeting(connected, current_input, current_output)
        except (subprocess.SubprocessError, OSError, ValueError) as exc:
            print(f"[input_source_menubar] poll error: {exc}", flush=True)

    def _poll_dictation(
        self, connected: list[str], current_input: str, background: bool = False
    ) -> str:
        priority = pick_prioritized_input(connected)
        if priority and current_input != priority:
            if background:
                set_input_background(priority)
            else:
                set_input(priority)
            return priority
        return current_input

    def _poll_meeting(
        self,
        connected: list[str],
        current_input: str,
        current_output: str,
    ):
        self._sync_input_to_output(connected, current_input, current_output)

    def _sync_meeting_input(self, background: bool = False) -> str:
        current_output = self.last_current_output or get_current_output()
        connected = self.last_connected_inputs or get_connected_inputs()
        current_input = self.last_current_input or get_current_input()
        return self._sync_input_to_output(
            connected, current_input, current_output, background=background
        )

    @staticmethod
    def _sync_input_to_output(
        connected_inputs: list[str],
        current_input: str,
        current_output: str,
        background: bool = False,
    ) -> str:
        match = find_matching_input(current_output, connected_inputs)
        if match and current_input != match:
            if background:
                set_input_background(match)
            else:
                set_input(match)
            return match
        return current_input

    def _set_input_menu_state(self, selected_input: str) -> None:
        for item in self.input_submenu.values():
            item.state = item.title == selected_input

    def _update_airpods_visibility(
        self,
        connected_inputs: Optional[list[str]] = None,
        connected_outputs: Optional[list[str]] = None,
    ):
        if connected_inputs is None:
            connected_inputs = self.last_connected_inputs or get_connected_inputs()
        if connected_outputs is None:
            connected_outputs = self.last_connected_outputs or get_connected_outputs()
        airpods_name = None
        for device in [*connected_inputs, *connected_outputs]:
            if is_airpods(device):
                airpods_name = device
                break
        if airpods_name:
            self.airpods_settings_item.title = f"{airpods_name} Settings..."
            self.airpods_settings_item.hidden = False
        else:
            self.airpods_settings_item.hidden = True

    def _open_sound_settings(self, _sender=None):
        open_sound_settings()

    def _open_airpods_settings(self, _sender=None):
        open_airpods_settings()


def hide_dock_icon():
    """Hide the Python icon from the Dock (LSUIElement=1 equivalent)."""
    try:
        import AppKit

        AppKit.NSApplication.sharedApplication().setActivationPolicy_(  # type: ignore[attr-defined]
            AppKit.NSApplicationActivationPolicyAccessory  # type: ignore[attr-defined]
        )
    except ImportError:
        pass


if __name__ == "__main__":
    hide_dock_icon()
    InputSourceApp().run()
