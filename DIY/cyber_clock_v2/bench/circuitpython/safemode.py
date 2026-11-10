# Power-dip recovery (2026-11-09). CircuitPython runs this file instead of code.py when it lands in safe
# mode. A power dip at start-up on the cell (screen + Wi-Fi surge) was leaving the clock stuck there.
# On a brownout: wait for the rail to settle, then reset. After 5 dips in a row, stay in safe mode so a
# failing cell cannot loop forever. code.py sets the counter back to 0 on every good start.
import time, microcontroller, supervisor

COUNT = 0              # byte of microcontroller.nvm that holds the dip counter
LIMIT = 5

if supervisor.runtime.safe_mode_reason == supervisor.SafeModeReason.BROWNOUT:
    n = microcontroller.nvm[COUNT]
    n = 0 if n == 255 else n          # fresh flash reads 0xFF
    if n < LIMIT:
        microcontroller.nvm[COUNT] = n + 1
        time.sleep(3)
        microcontroller.reset()
