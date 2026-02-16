#!/bin/zsh

# Audio microphone input source switcher using SwitchAudioSource
# Note: LaunchAgent runs from ~/bin/Input_source.sh — copy edits there for login behavior.
# Requires: brew install switchaudio-osx
# Switches to the highest-priority connected input device from PRIORITY_INPUTS.
# Runs as daemon when no args/--set: stays in background and polls for
# prioritized devices to be connected or reconnected.

SWITCH_AUDIO_SOURCE="SwitchAudioSource"
# Ordered by priority (first item is highest priority).
PRIORITY_INPUTS=(
  "Yeti X"
  "Blue Snowball"
)
POLL_INTERVAL=5
NOTIFY_STATE_FILE="/tmp/input_source_notify_state"
NOTIFY_DEDUP_WINDOW=30

should_send_startup_notification() {
  local now last_ts
  now=$(date +%s)
  if [[ -f "$NOTIFY_STATE_FILE" ]]; then
    last_ts=$(<"$NOTIFY_STATE_FILE")
    if [[ "$last_ts" == <-> ]] && (( now - last_ts < NOTIFY_DEDUP_WINDOW )); then
      return 1
    fi
  fi
  print -r -- "$now" > "$NOTIFY_STATE_FILE"
  return 0
}

pick_prioritized_input() {
  local connected_inputs="$1"
  local preferred
  local device

  # Exact-name match first.
  for preferred in "${PRIORITY_INPUTS[@]}"; do
    while IFS= read -r device; do
      if [[ "$device" == "$preferred" ]]; then
        echo "$device"
        return 0
      fi
    done <<< "$connected_inputs"
  done

  # Optional safe fallback: partial-name match.
  for preferred in "${PRIORITY_INPUTS[@]}"; do
    while IFS= read -r device; do
      if [[ "$device" == *"$preferred"* ]]; then
        echo "$device"
        return 0
      fi
    done <<< "$connected_inputs"
  done

  return 1
}

is_continuity_camera_device() {
  local device_name="$1"
  local normalized_name="${(L)device_name}"
  [[ "$normalized_name" == *"continuity camera"* ]]
}

if ! command -v "$SWITCH_AUDIO_SOURCE" &>/dev/null; then
  echo "Error: SwitchAudioSource is not installed." >&2
  echo "Install it with: brew install switchaudio-osx" >&2
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
    echo "  --set       Daemon: poll priority list and switch to highest connected device (default)"
    echo "  \"Device\"    Switch to the specified input device"
    exit 0
    ;;
  --set)
    # Wait for session/audio to be ready after login
    sleep 15
    connected_inputs=$($SWITCH_AUDIO_SOURCE -t input -a)
    startup_device=$(pick_prioritized_input "$connected_inputs")
    if [[ -n "$startup_device" ]]; then
      startup_message="Polling device: $startup_device"
    else
      startup_message="Polling device: none detected"
    fi
    if should_send_startup_notification; then
      osascript -e "display notification \"$startup_message\" with title \"Input Source\"" 2>/dev/null
    fi
    while true; do
      connected_inputs=$($SWITCH_AUDIO_SOURCE -t input -a)
      device=$(pick_prioritized_input "$connected_inputs")
      if [[ -n "$device" ]]; then
        current_device=$($SWITCH_AUDIO_SOURCE -t input -c)
        if ! is_continuity_camera_device "$current_device" && [[ "$current_device" != "$device" ]]; then
          $SWITCH_AUDIO_SOURCE -t input -s "$device"
        fi
      fi
      sleep "$POLL_INTERVAL"
    done
    ;;
  *)
    # Device name argument: switch to specified device
    $SWITCH_AUDIO_SOURCE -t input -s "$1"
    ;;
esac
