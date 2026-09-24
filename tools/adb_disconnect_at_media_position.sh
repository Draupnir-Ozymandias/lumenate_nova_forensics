#!/usr/bin/env bash
set -euo pipefail

target_ms="${1:-45000}"
timeout_seconds="${2:-180}"
post_disconnect_seconds="${3:-35}"

if ! [[ "$target_ms" =~ ^[0-9]+$ && "$timeout_seconds" =~ ^[0-9]+$ && "$post_disconnect_seconds" =~ ^[0-9]+$ ]]; then
  echo "usage: $0 [target_ms] [timeout_seconds] [post_disconnect_seconds]" >&2
  exit 2
fi

device_count="$(adb devices | awk 'NR > 1 && $2 == "device" {count++} END {print count+0}')"
if [[ "$device_count" -ne 1 ]]; then
  echo "expected exactly one authorized ADB device; found $device_count" >&2
  exit 1
fi

adb shell cmd bluetooth_manager wait-for-state:STATE_ON >/dev/null
adb shell log -t LUMENATE_FORENSICS \
  "DISCONNECT_HOLD_WATCHER_ARMED_TARGET_${target_ms}MS"

deadline_epoch="$(( $(date +%s) + timeout_seconds ))"
seen_fresh_start=0
poll_count=0

while [[ "$(date +%s)" -lt "$deadline_epoch" ]]; do
  state_line="$(adb shell dumpsys media_session | grep -m 1 'state=PlaybackState' || true)"
  position_ms="$(printf '%s\n' "$state_line" | sed -nE \
    's/.*state=PlaybackState \{state=[^,]+, position=([0-9]+),.*/\1/p')"

  if [[ "$state_line" == *"state=PLAYING(3)"* && -n "$position_ms" ]]; then
    if [[ "$position_ms" -lt 5000 ]]; then
      seen_fresh_start=1
    fi
    if (( poll_count % 4 == 0 )); then
      printf '%s | PLAYING position=%s ms\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$position_ms"
    fi
    if [[ "$seen_fresh_start" -eq 1 && "$position_ms" -ge "$target_ms" ]]; then
      adb shell log -t LUMENATE_FORENSICS \
        "DISCONNECT_REQUEST_AT_MEDIA_POSITION_${position_ms}MS"
      printf '%s | disabling Bluetooth at media position %s ms\n' \
        "$(date '+%Y-%m-%d %H:%M:%S')" "$position_ms"
      adb shell cmd bluetooth_manager disable
      adb shell log -t LUMENATE_FORENSICS \
        "BLUETOOTH_OFF_AFTER_MEDIA_POSITION_${position_ms}MS"
      sleep 1
      adapter_state="$(adb shell dumpsys bluetooth_manager | grep -m 1 '^  State:' || true)"
      connection_state="$(adb shell dumpsys bluetooth_manager | grep -m 1 'server_address:.*mtu:' || true)"
      printf '%s | adapter after disable | %s | %s\n' \
        "$(date '+%Y-%m-%d %H:%M:%S')" "$adapter_state" "$connection_state"
      disconnect_epoch="$(date +%s)"
      while [[ "$(( $(date +%s) - disconnect_epoch ))" -lt "$post_disconnect_seconds" ]]; do
        state_line="$(adb shell dumpsys media_session | grep -m 1 'state=PlaybackState' || true)"
        printf '%s | post-disconnect | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$state_line"
        sleep 1
      done
      exit 0
    fi
  fi

  poll_count="$((poll_count + 1))"
  sleep 0.25
done

adb shell log -t LUMENATE_FORENSICS "DISCONNECT_HOLD_WATCHER_TIMEOUT"
echo "timed out before a fresh playback crossed ${target_ms} ms" >&2
exit 1
