# All-parts bench check, self-serve. Run from the REPL: import all_check
# The glass shows the clock and waits. Press snooze (or any knob button, or turn the knob) to
# start a run; the glass then asks for each action in turn: press snooze, turn the knob, press
# each knob button, hand over the light sensor, tilt the board. Clock and climate are read,
# the summary shows for 10 s, and the glass goes back to waiting. Runs for 60 min, then
# returns to the REPL. Every event also prints on the console.
# Snooze (new 2026-11-08): one leg GPIO18, the other G, internal pull-up, pressed = low.
# OLED SPI clock 12 / data 11, DC 6, CS 10, RST 7. Amp BCLK 14, LRC 15, DIN 16, SD 17. Chain SCL 9 / SDA 8.
import time, math, array, board, busio, digitalio, displayio, terminalio, audiobusio, audiocore
from fourwire import FourWire
from adafruit_display_text import label
import adafruit_displayio_ssd1306

TZ = -5
WINDOW = 3600
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# ---- display ------------------------------------------------------------------------------
displayio.release_displays()
spi = busio.SPI(board.IO12, board.IO11)
bus = FourWire(spi, command=board.IO6, chip_select=board.IO10, reset=board.IO7, baudrate=1000000)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)
group = displayio.Group()
display.root_group = group
head = label.Label(terminalio.FONT, text="CYBER DAWN   check", x=0, y=5)
line = label.Label(terminalio.FONT, text="", x=0, y=21)
big = label.Label(terminalio.FONT, text="", x=0, y=40, scale=2)
foot = label.Label(terminalio.FONT, text="", x=0, y=59)
for item in (head, line, big, foot):
    group.append(item)

def put(lbl, text):
    if lbl.text != text:
        lbl.text = text

print("DISPLAY ON")

# ---- speaker: short beeps, SD gated so there is no pop ------------------------------------
sd = digitalio.DigitalInOut(board.IO17)
sd.switch_to_output(value=False)
i2s = audiobusio.I2SOut(board.IO14, board.IO15, board.IO16)

def sample(freq, level=7000):
    n = 16000 // freq
    return audiocore.RawSample(array.array("h", [int(math.sin(2 * math.pi * i / n) * level) for i in range(n)]), sample_rate=16000)

BEEP, CHIRP = sample(880), sample(1320)

def tone(s, sec):
    i2s.play(s, loop=True)
    time.sleep(0.03)
    sd.value = True
    time.sleep(sec)
    sd.value = False
    time.sleep(0.02)
    i2s.stop()

def beep():
    tone(BEEP, 0.12)

def chirp():
    tone(BEEP, 0.1)
    tone(CHIRP, 0.15)

# ---- snooze -------------------------------------------------------------------------------
snooze = digitalio.DigitalInOut(board.IO18)
snooze.switch_to_input(pull=digitalio.Pull.UP)
print("SNOOZE at rest reads", "HIGH: open, the pull-up holds it (good)" if snooze.value else "LOW: held down, or the GPIO18 leg is shorted to G")

def pressed():
    """Debounced: low on two reads 15 ms apart."""
    if snooze.value:
        return False
    time.sleep(0.015)
    return not snooze.value

# ---- the chain ----------------------------------------------------------------------------
i2c = rtc = prox = acc = aht = ss = knob = None
try:
    i2c = busio.I2C(board.IO9, board.IO8)
except RuntimeError as e:
    print("CHAIN bus failed: %s" % e)

def attach(name, make):
    try:
        d = make()
        print("CHAIN %-9s ok" % name)
        return d
    except Exception as e:
        print("CHAIN %-9s MISSING (%s)" % (name, e))
        return None

if i2c:
    import adafruit_ds3231, adafruit_vcnl4040, adafruit_lis3dh, adafruit_ahtx0
    from adafruit_seesaw import seesaw, rotaryio
    rtc = attach("clock", lambda: adafruit_ds3231.DS3231(i2c))
    prox = attach("proximity", lambda: adafruit_vcnl4040.VCNL4040(i2c))
    acc = attach("accel", lambda: adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18))
    aht = attach("humidity", lambda: adafruit_ahtx0.AHTx0(i2c))
    ss = attach("encoder", lambda: seesaw.Seesaw(i2c, addr=0x49))

NAMES = {1: "SELECT", 2: "UP", 3: "LEFT", 4: "DOWN", 5: "RIGHT"}
MASK = sum(1 << p for p in NAMES)
if ss:
    for p in NAMES:
        ss.pin_mode(p, ss.INPUT_PULLUP)
    knob = rotaryio.IncrementalEncoder(ss)

def buttons_down():
    b = ss.digital_read_bulk(MASK)
    return [n for p, n in NAMES.items() if not (b >> p) & 1]

def local_text():
    lt = time.localtime(time.mktime(rtc.datetime) + TZ * 3600)
    return ("%s %d %s %d" % (DAYS[lt.tm_wday], lt.tm_mday, MONTHS[lt.tm_mon - 1], lt.tm_year),
            "%02d:%02d:%02d" % (lt.tm_hour, lt.tm_min, lt.tm_sec))

# ---- one guided run -----------------------------------------------------------------------
def step(word, instruction, seconds, check, status=lambda: ""):
    """Show the instruction; poll check() ~50x/s until it returns a note or time runs out."""
    put(line, instruction); put(big, word); put(foot, "")
    print("STEP %s: %s (%d s)" % (word, instruction, seconds))
    end = time.monotonic() + seconds
    while True:
        note = check()
        if note:
            return note
        left = end - time.monotonic()
        if left <= 0:
            return None
        put(foot, "%s%2ds" % (status(), left))
        time.sleep(0.02)

def run(snooze_hold):
    results = []

    def result(name, ok, note=""):
        results.append((name, ok))
        print("RESULT %-9s %s  %s" % (name, "PASS" if ok else "FAIL", note))

    if snooze_hold is not None:
        result("snooze", True, "pressed to start, held %.2f s" % snooze_hold)
    else:
        state = {"was_high": snooze.value}
        def snooze_check():
            if pressed():
                if state["was_high"]:
                    put(big, "SNOOZE!"); beep()
                    t0 = time.monotonic()
                    while pressed():
                        time.sleep(0.02)
                    return "pressed, held %.2f s" % (time.monotonic() - t0)
            else:
                state["was_high"] = True
            return None
        note = step("SNOOZE", "Press snooze", 45, snooze_check)
        result("snooze", bool(note), note or "no press seen: check the GPIO18 leg and the G leg")

    if knob:
        start = knob.position
        def knob_check():
            d = knob.position - start
            put(big, "KNOB %+d" % d)
            return "%+d steps" % d if abs(d) >= 4 else None
        note = step("KNOB", "Turn the knob", 30, knob_check)
        result("knob", bool(note), note or "no turn seen")
    else:
        result("knob", False, "encoder missing from the chain")

    if ss:
        seen = set()
        def buttons_check():
            for n in buttons_down():
                if n not in seen:
                    print("BUTTON", n); seen.add(n); put(big, n); beep()
            return "all five" if len(seen) == 5 else None
        def buttons_status():
            todo = [n[0] for p, n in sorted(NAMES.items()) if n not in seen]
            return "todo " + " ".join(todo) + "  " if todo else ""
        note = step("BUTTONS", "Press each button", 45, buttons_check, buttons_status)
        missing = [n for p, n in sorted(NAMES.items()) if n not in seen]
        result("buttons", not missing, "all five seen" if not missing else "seen %s; missing %s" % (sorted(seen), missing))
    else:
        result("buttons", False, "encoder missing from the chain")

    if prox:
        base = sorted(prox.proximity for _ in range(5))[2]
        lux0 = prox.lux
        def wave_check():
            p = prox.proximity
            put(big, "prox %d" % p)
            return "prox %d -> %d, lux %.0f -> %.0f" % (base, p, lux0, prox.lux) if p > base + 60 else None
        note = step("WAVE", "Hand over the sensor", 30, wave_check)
        result("proximity", bool(note), note or "no rise above %d seen" % base)
    else:
        result("proximity", False, "missing from the chain")

    if acc:
        ax, ay, az = acc.acceleration
        def angle(v):
            x, y, z = v
            n = math.sqrt(x * x + y * y + z * z) * math.sqrt(ax * ax + ay * ay + az * az)
            c = max(-1.0, min(1.0, (x * ax + y * ay + z * az) / n)) if n else 1.0
            return math.degrees(math.acos(c))
        def tilt_check():
            v = acc.acceleration
            a = angle(v)
            put(big, "tilt %d" % a)
            return "turned %.0f deg, g=(%.1f,%.1f,%.1f)" % ((a,) + tuple(v)) if a > 45 else None
        note = step("TILT", "Tilt the board", 30, tilt_check)
        result("tilt", bool(note), note or "no tilt over 45 deg seen")
    else:
        result("tilt", False, "accelerometer missing from the chain")

    if rtc:
        t = rtc.datetime
        print("CLOCK %04d-%02d-%02d %02d:%02d:%02d UTC  lost_power=%s" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, rtc.lost_power))
        result("clock", t.tm_year >= 2026 and not rtc.lost_power, "%02d:%02d:%02d UTC" % (t.tm_hour, t.tm_min, t.tm_sec))
    else:
        result("clock", False, "missing from the chain")
    if aht:
        result("climate", True, "%.1f C  %.0f %%" % (aht.temperature, aht.relative_humidity))
    else:
        result("climate", False, "missing from the chain")
    result("display", True, "text on the glass (builder confirms)")
    result("speaker", True, "beeps (builder confirms)")

    passed = sum(1 for _, ok in results if ok)
    fails = [n for n, ok in results if not ok]
    print("SUMMARY %d/%d pass%s" % (passed, len(results), "" if not fails else "; FAIL " + " ".join(fails)))
    put(line, "done"); put(big, "%d/%d pass" % (passed, len(results)))
    put(foot, ("fail: " + " ".join(fails))[:21] if fails else "all parts answered")
    chirp()
    return passed, len(results), fails

# ---- wait for the builder, run, repeat ----------------------------------------------------
chirp()
t_end = time.monotonic() + WINDOW
runs = 0
last = ""
while time.monotonic() < t_end:
    put(line, "Press snooze to start"); put(foot, last or "or any knob button")
    print("WAITING run %d" % (runs + 1))
    trigger = None
    k0 = knob.position if knob else 0
    while trigger is None and time.monotonic() < t_end:
        if pressed():
            t0 = time.monotonic()
            while pressed():
                time.sleep(0.02)
            trigger = ("snooze", time.monotonic() - t0)
        elif ss and buttons_down():
            trigger = ("button", None)
            while buttons_down():
                time.sleep(0.02)
        elif knob and abs(knob.position - k0) >= 2:
            trigger = ("knob", None)
        else:
            if rtc:
                put(big, local_text()[1])
            time.sleep(0.05)
    if trigger is None:
        break
    runs += 1
    print("RUN %d START by %s" % (runs, trigger[0]))
    beep()
    passed, total, fails = run(trigger[1] if trigger[0] == "snooze" else None)
    last = ("last: %d/%d pass" % (passed, total)) if not fails else ("fail: " + " ".join(fails))[:21]
    hold = time.monotonic() + 10
    while time.monotonic() < hold:
        time.sleep(0.05)
print("IDLE END after %d run(s)" % runs)
