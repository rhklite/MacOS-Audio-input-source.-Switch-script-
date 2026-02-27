# Script

macOS audio input source switcher with a menu bar app.

## What it does

- **Dictation mode**: Keeps microphone on a priority device (Yeti X, then Blue Snowball)
- **Meeting mode**: Input follows output (e.g. both use AirPods when selected)
- Polls every 5 seconds and switches input as devices or modes change

## Requirements

- macOS
- [switchaudio-osx](https://github.com/deweller/switchaudio-osx): `brew install switchaudio-osx`
- [rumps](https://github.com/jaredks/rumps): `pip install rumps`
- Python 3

## Usage

```bash
./Input_source.sh [--list | --current | --set | "Device Name"]
```

| Flag | Description |
|------|-------------|
| `--list` | List all input devices |
| `--current` | Show current input device |
| `--set` | Launch menu bar app (default) |
| `"Device Name"` | Switch to that device |

## Login at startup

Add `Input_source.sh` (or a symlink to it) to **Login Items** so the menu bar app starts with your session.

## Files

- `Input_source.sh` — CLI and launcher
- `input_source_menubar.py` — Menu bar app (Dictation / Meeting toggle, device menus)
