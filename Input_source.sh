#!/bin/zsh

# Audio microphone input source switcher using SwitchAudioSource
# If you start this at login, ensure Login Items points here (or symlink ~/bin/Input_source.sh).
# Requires: brew install switchaudio-osx
#           pip install rumps
# The --set mode launches a menu bar app (input_source_menubar.py) that handles
# polling and switching with Dictation / Meeting mode toggle.

SWITCH_AUDIO_SOURCE="SwitchAudioSource"
SCRIPT_DIR="${0:A:h}"
MENUBAR_APP="$SCRIPT_DIR/input_source_menubar.py"

if ! command -v "$SWITCH_AUDIO_SOURCE" &>/dev/null; then
  echo "Error: SwitchAudioSource is not installed." >&2
  echo "Install it with: brew install switchaudio-osx" >&2
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is not installed." >&2
  exit 1
fi

case "${1:---set}" in
  --list)
    $SWITCH_AUDIO_SOURCE -t input -a
    ;;
  --current)
    $SWITCH_AUDIO_SOURCE -t input -c
    ;;
  --help|-h)
    echo "Usage: $0 [--list | --current | --set | \"Device Name\"]"
    echo ""
    echo "  --list      List all available input devices"
    echo "  --current   Show currently selected input device"
    echo "  --set       Launch menu bar app with Dictation/Meeting mode (default)"
    echo "  \"Device\"    Switch to the specified input device"
    exit 0
    ;;
  --set)
    if [[ ! -f "$MENUBAR_APP" ]]; then
      echo "Error: Menu bar app not found at $MENUBAR_APP" >&2
      exit 1
    fi
    exec python3 "$MENUBAR_APP"
    ;;
  *)
    $SWITCH_AUDIO_SOURCE -t input -s "$1"
    ;;
esac
