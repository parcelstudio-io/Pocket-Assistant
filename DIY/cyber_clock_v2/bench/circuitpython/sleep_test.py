# Load test (2026-11-09): deep sleep for 5 min so the cell carries almost nothing, then wake and boot
# the clock. Run over Wi-Fi: supervisor.set_next_code_file("sleep_test.py"); supervisor.reload()
import alarm, time, wifi
print("SLEEP 300 s from", time.monotonic())
time.sleep(1)
wifi.radio.enabled = False      # an open Wi-Fi console keeps the board in pretend sleep
alarm.exit_and_deep_sleep_until_alarms(alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 300))
