# Cyber Dawn (2026-11-09): the alarm clock. See docs/USER_MANUAL.md and cyberdawn.py.
# Earlier start-up show: speak_show.py. Chain monitor: chain_monitor.py (import it at the REPL).
import time
import microcontroller
microcontroller.nvm[0] = 0   # good start: clear safemode.py's power-dip counter
time.sleep(1.5)              # let the 5 V rail settle before the screen and amp load it
import cyberdawn
