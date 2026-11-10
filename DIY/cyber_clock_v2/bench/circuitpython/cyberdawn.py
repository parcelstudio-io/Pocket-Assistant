# Cyber Dawn alarm clock (2026-11-09). code.py imports this. Logic lives in dawn_core.py.
#
# Controls (docs/USER_MANUAL.md):
#   knob turn / centre press  open the menu, pick, edit, save. UP/DOWN keys = turn, RIGHT = press,
#                             LEFT = back.
#   snooze button             ringing: snooze. Otherwise: lights the face.
#   hold centre + turn        ringing: dismiss. While snoozed: cancel the snooze.
#   arm switch                alarms armed or not; disarming also stops a ringing or snoozed alarm.
#   hand over the lid         lights the face for 10 s.
#   tilt onto its side, 2 s   start or stop a 25 min focus timer.
#
# Pins: OLED SPI clock 12 / data 11, DC 6, CS 10, RST 7. Amp BCLK 14, LRC 15, DIN 16, SD 17 (10 k
# pull-down). Chain SCL 9 / SDA 8. Snooze 18, arm 21 (pull-ups, active low). Lamp 40 not fitted.
import time, math, array, os, board, busio, digitalio, displayio, terminalio, audiobusio, audiocore
import vectorio, microcontroller, supervisor
from fourwire import FourWire
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import dawn_core as core

ARM_WHEN_LOW = True       # arm switch closed to ground = armed. Flip if the switch reads backwards.
PRE_ALARM = 5 * 60        # the horizon starts rising 5 min before an alarm
RAMP = 60                 # the chime grows from level 1 to the set volume over 60 s
BRIGHT_FOR = 10           # seconds the face stays bright after a wave or a button
MENU_IDLE = 20            # seconds of no input before a menu or edit closes without saving
FOCUS_MIN = 25

def log(*a):
    print("DAWN", *a)

# ---- display ---------------------------------------------------------------------------------
displayio.release_displays()
spi = busio.SPI(board.IO12, board.IO11)
bus = FourWire(spi, command=board.IO6, chip_select=board.IO10, reset=board.IO7, baudrate=1000000)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)
root = displayio.Group()
display.root_group = root
top = label.Label(terminalio.FONT, text="", x=0, y=5)
big = label.Label(terminalio.FONT, text="", x=2, y=29, scale=3)
foot = label.Label(terminalio.FONT, text="", x=0, y=58)
white = displayio.Palette(1)
white[0] = 0xFFFFFF
horizon = vectorio.Rectangle(pixel_shader=white, width=128, height=1, x=0, y=64)
for item in (top, big, foot, horizon):
    root.append(item)

def put(lbl, text):
    if lbl.text != text:
        lbl.text = text

def set_bright(level):
    try:
        if abs(display.brightness - level) > 0.005:
            display.brightness = level
    except Exception:
        pass

put(big, "--:--")

# ---- chain -----------------------------------------------------------------------------------
i2c = busio.I2C(board.IO9, board.IO8)

def attach(name, make):
    try:
        d = make()
        log("chain", name, "ok")
        return d
    except Exception as e:
        log("chain", name, "MISSING", e)
        return None

import adafruit_ds3231
rtc = attach("clock", lambda: adafruit_ds3231.DS3231(i2c))
try:
    import adafruit_vcnl4040
    prox = attach("proximity", lambda: adafruit_vcnl4040.VCNL4040(i2c))
except ImportError:
    prox = None
try:
    import adafruit_lis3dh
    acc = attach("accel", lambda: adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18))
except ImportError:
    acc = None
try:
    import adafruit_ahtx0
    aht = attach("humidity", lambda: adafruit_ahtx0.AHTx0(i2c))
except ImportError:
    aht = None
try:
    from adafruit_seesaw import seesaw, rotaryio
    ss = attach("encoder", lambda: seesaw.Seesaw(i2c, addr=0x49))
except ImportError:
    ss = None

SELECT, UP, LEFT, DOWN, RIGHT = 1, 2, 3, 4, 5
KEYMASK = sum(1 << p for p in (SELECT, UP, LEFT, DOWN, RIGHT))
knob = None
if ss:
    for p in (SELECT, UP, LEFT, DOWN, RIGHT):
        ss.pin_mode(p, ss.INPUT_PULLUP)
    knob = rotaryio.IncrementalEncoder(ss)

def gauge():
    """(volts, percent, rate %/h) from the fuel gauge, or None."""
    def reg(r):
        b = bytearray(2)
        while not i2c.try_lock():
            pass
        try:
            i2c.writeto_then_readfrom(0x36, bytes([r]), b)
        finally:
            i2c.unlock()
        return (b[0] << 8) | b[1]
    try:
        c = reg(0x16)
        c = c - 65536 if c > 32767 else c
        return reg(0x02) * 78.125e-6, reg(0x04) / 256, c * 0.208
    except OSError:
        return None

# ---- buttons ---------------------------------------------------------------------------------
snooze_pin = digitalio.DigitalInOut(board.IO18)
snooze_pin.switch_to_input(pull=digitalio.Pull.UP)
arm_pin = digitalio.DigitalInOut(board.IO21)
arm_pin.switch_to_input(pull=digitalio.Pull.UP)

def armed():
    return (not arm_pin.value) if ARM_WHEN_LOW else arm_pin.value

class Inputs:
    """Edges since the last poll: turns, key presses, snooze press, and centre held."""
    def __init__(self):
        self.pos = knob.position if knob else 0
        self.keys_prev = 0
        self.snooze_prev = False
        self.snooze_t = 0

    def poll(self):
        turn, pressed = 0, set()
        if knob:
            try:
                p = knob.position
                turn, self.pos = p - self.pos, p
                bits = ss.digital_read_bulk(KEYMASK)
                down = 0
                for k in (SELECT, UP, LEFT, DOWN, RIGHT):
                    if not (bits >> k) & 1:
                        down |= 1 << k
                for k in (SELECT, UP, LEFT, DOWN, RIGHT):
                    if down & (1 << k) and not self.keys_prev & (1 << k):
                        pressed.add(k)
                self.keys_prev = down
            except (OSError, RuntimeError):
                pass
        now = time.monotonic()
        s = not snooze_pin.value
        snooze = s and not self.snooze_prev and now - self.snooze_t > 0.25
        if snooze:
            self.snooze_t = now
        self.snooze_prev = s
        return turn, pressed, snooze

    def held(self, k):
        return bool(self.keys_prev & (1 << k))

inputs = Inputs()

# ---- sound -----------------------------------------------------------------------------------
sd = digitalio.DigitalInOut(board.IO17)
sd.switch_to_output(value=False)          # amp off until I2S runs: no pop
i2s = audiobusio.I2SOut(board.IO14, board.IO15, board.IO16)
RATE = 16000

def make_chime():
    """Two soft decaying notes, A5 then E6, as floats -1..1."""
    out = array.array("f")
    for f, n in ((880, 5600), (1319, 7200)):
        k = 2 * math.pi * f / RATE
        for i in range(n):
            out.append(math.sin(k * i) * math.exp(-i / 2400) * min(1.0, i / 80))
    return out

CHIME = make_chime()
_levels = {}

def chime_at(level):
    """RawSample of the chime at level 1-10, cached."""
    level = max(1, min(10, int(level)))
    if level not in _levels:
        amp = 2800 * level
        _levels[level] = audiocore.RawSample(array.array("h", [int(v * amp) for v in CHIME]), sample_rate=RATE)
    return _levels[level]

def play(level):
    i2s.stop()
    i2s.play(chime_at(level))
    time.sleep(0.02)
    sd.value = True

def quiet():
    i2s.stop()
    sd.value = False

# ---- settings and time -----------------------------------------------------------------------
cfg = core.Settings.unpack(bytes(microcontroller.nvm[0:core.NVM_SIZE]))

def save():
    b = cfg.pack()
    if bytes(microcontroller.nvm[1:core.NVM_SIZE]) != bytes(b[1:]):
        microcontroller.nvm[1:core.NVM_SIZE] = b[1:]
        log("saved")

def now_utc():
    t = rtc.datetime
    return core.epoch(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

def minute_key(utc):
    return (utc + core.utc_offset(utc)) // 60

def set_rtc_local(hour, minute):
    lt = core.Local(now_utc())
    u = core.local_to_utc(lt.year, lt.month, lt.day, hour, minute, 0)
    y, mo, d = core.civil_from_days(u // 86400)
    s = u % 86400
    rtc.datetime = time.struct_time((y, mo, d, s // 3600, s % 3600 // 60, 0, core.weekday(u // 86400), -1, -1))
    log("clock set to %02d:%02d local" % (hour, minute))

# ---- Wi-Fi off while ringing on the cell (ARCHITECTURE: no radio bursts on top of the chime) --
wifi_was_off = False

def radio(on):
    global wifi_was_off
    try:
        import wifi
        if not on and wifi.radio.enabled:
            wifi.radio.enabled = False
            wifi_was_off = True
            log("wifi off for the alarm")
        elif on and wifi_was_off:
            wifi.radio.enabled = True
            ssid = os.getenv("CIRCUITPY_WIFI_SSID")
            if ssid:
                wifi.radio.connect(ssid, os.getenv("CIRCUITPY_WIFI_PASSWORD"))
            wifi_was_off = False
            log("wifi back on")
    except Exception as e:
        log("wifi", e)

# ---- the clock -------------------------------------------------------------------------------
class Clock:
    def __init__(self):
        self.mode = "face"           # face, menu, edit, ring
        self.bright_until = time.monotonic() + BRIGHT_FOR
        self.last_input = time.monotonic()
        self.menu_i = 0
        self.edit = None             # (item, fields list, field index, working values)
        self.ring_t0 = 0
        self.ring_next = 0
        self.turn_while_held = 0
        self.focus_end = 0
        self.tilt_since = 0
        self.tilt_armed = True
        self.rest = acc.acceleration if acc else None
        self.prox_base = None
        self.climate = ""
        self.battery = ""
        self.slow_t = 0
        self.shift_t = 0
        self.shift_i = 0
        self.lux = 50

    # ---- sensors, every few seconds ----
    def slow(self, mono):
        if mono < self.slow_t:
            return
        self.slow_t = mono + 15
        if aht:
            try:
                self.climate = "%dC %d%%" % (round(aht.temperature), round(aht.relative_humidity))
            except Exception:
                pass
        g = gauge()
        if g:
            v, pct, rate = g
            self.battery = "%s%d%%" % ("+" if rate > 1 else "", max(0, min(100, round(pct))))
        if mono > self.shift_t:                       # pixel shift each minute spreads OLED wear
            self.shift_t = mono + 60
            self.shift_i = (self.shift_i + 1) % 4
            root.x, root.y = ((0, 0), (1, 0), (1, 1), (0, 1))[self.shift_i]

    def wave(self, mono):
        if not prox:
            return False
        try:
            p = prox.proximity
            if mono % 5 < 0.06:
                self.lux = prox.lux
        except Exception:
            return False
        if self.prox_base is None:
            self.prox_base = p
        hand = p > self.prox_base + 60
        if not hand:
            self.prox_base = self.prox_base * 0.95 + p * 0.05
        return hand

    def tilted(self, mono):
        """True once when the clock has been on its side for 2 s."""
        if not acc or not self.rest:
            return False
        try:
            x, y, z = acc.acceleration
        except Exception:
            return False
        ax, ay, az = self.rest
        n = math.sqrt((x * x + y * y + z * z) * (ax * ax + ay * ay + az * az))
        ang = math.degrees(math.acos(max(-1.0, min(1.0, (x * ax + y * ay + z * az) / n)))) if n else 0
        if ang < 20:
            self.tilt_armed, self.tilt_since = True, 0
            return False
        if ang > 40 and self.tilt_armed:
            if not self.tilt_since:
                self.tilt_since = mono
            elif mono - self.tilt_since > 2:
                self.tilt_armed = False
                return True
        return False

    # ---- ringing ----
    def start_ring(self, utc, why):
        log("RING", why)
        self.mode = "ring"
        self.ring_t0 = time.monotonic()
        self.ring_next = 0
        self.turn_while_held = 0
        if cfg.snooze_until == 0 or cfg.snooze_until > utc:
            cfg.snooze_until = utc                  # a reset while ringing resumes the ring
        save()
        g = gauge()
        if g is None or g[2] <= 0:                  # on the cell: keep the radio quiet
            radio(False)

    def stop_ring(self, snooze, utc):
        quiet()
        self.mode = "face"
        self.bright_until = time.monotonic() + BRIGHT_FOR
        cfg.snooze_until = utc + cfg.snooze_min * 60 if snooze else 0
        save()
        log("SNOOZE %d min" % cfg.snooze_min if snooze else "DISMISS")
        radio(True)

    def ring(self, turn, pressed, snooze, utc, mono):
        if snooze:
            return self.stop_ring(True, utc)
        if inputs.held(SELECT):
            self.turn_while_held += abs(turn)
            if self.turn_while_held >= 2:
                return self.stop_ring(False, utc)
        else:
            self.turn_while_held = 0
        if mono - self.ring_t0 > core.RING_LIMIT:
            log("ring limit reached")
            return self.stop_ring(False, utc)
        if mono >= self.ring_next:
            level = 1 + (cfg.volume - 1) * min(1.0, (mono - self.ring_t0) / RAMP)
            play(level)
            self.ring_next = mono + 1.6
        lt = core.Local(utc)
        put(top, "  WAKE UP      %s" % lt.date_text()[:3])
        put(big, "%02d:%02d" % (lt.hour, lt.minute))
        put(foot, "snooze  |  hold+turn: off" if int(mono) % 4 < 2 else "")
        horizon.y = 0 if int(mono * 2) % 2 else 63
        set_bright(1.0)

    # ---- face ----
    def face(self, turn, pressed, snooze, utc, mono, waved):
        if turn or pressed & {SELECT, RIGHT, UP, DOWN}:
            if cfg.snooze_until and inputs.held(SELECT):
                self.turn_while_held += abs(turn)
                if self.turn_while_held >= 2:
                    cfg.snooze_until = 0
                    save()
                    log("snooze cancelled")
                    self.turn_while_held = 0
                return
            self.mode, self.menu_i = "menu", 0
            return
        if not inputs.held(SELECT):
            self.turn_while_held = 0
        if snooze or waved:
            self.bright_until = mono + BRIGHT_FOR
        lt = core.Local(utc)
        if self.focus_end:
            left = int(self.focus_end - mono)
            if left <= 0:
                self.focus_end = 0
                log("focus done")
                for _ in range(3):
                    play(3)
                    time.sleep(0.9)
                quiet()
            else:
                put(big, "%02d:%02d" % (left // 60, left % 60))
                put(top, "FOCUS        %02d:%02d" % (lt.hour, lt.minute))
        if not self.focus_end:
            put(big, "%02d:%02d" % (lt.hour, lt.minute))
            a, when = core.next_alarm(cfg.alarms, utc)
            if not armed():
                mark = "alarms off"
            elif cfg.snooze_until:
                mark = "snz %dm" % max(1, (cfg.snooze_until - utc + 59) // 60)
            elif a:
                mark = "AL " + a.text()
            else:
                mark = ""
            put(top, "%-11s%10s" % (lt.date_text(), mark))
        put(foot, "%-10s%11s" % (self.climate, self.battery))
        # the horizon rises through the 5 min before an alarm
        a, when = core.next_alarm(cfg.alarms, utc) if armed() else (None, None)
        if when and when - utc <= PRE_ALARM:
            frac = 1 - (when - utc) / PRE_ALARM
            horizon.y = int(63 - 30 * frac)
            set_bright(0.05 + 0.95 * frac)
        else:
            horizon.y = 64
            dark = self.lux < 3
            set_bright(1.0 if mono < self.bright_until else (0.01 if dark else 0.4))

    # ---- menu ----
    def menu_items(self):
        items = []
        for i, a in enumerate(cfg.alarms):
            items.append(("alarm", i, "ALARM %d" % (i + 1), a.text(), "%s  %s" % (core.MODES[a.mode], "ON" if a.on else "off")))
        items.append(("volume", 0, "VOLUME", "%d" % cfg.volume, "turn, press to set"))
        items.append(("snooze", 0, "SNOOZE", "%d min" % cfg.snooze_min, "turn, press to set"))
        lt = core.Local(now_utc())
        items.append(("time", 0, "SET TIME", "%02d:%02d" % (lt.hour, lt.minute), "press to change"))
        items.append(("back", 0, "BACK", "", "press to leave"))
        return items

    def menu(self, turn, pressed, snooze):
        items = self.menu_items()
        step = turn + (1 if UP in pressed else 0) - (1 if DOWN in pressed else 0)
        self.menu_i = core.wrap(self.menu_i + step, 0, len(items) - 1)
        kind, idx, name, value, hint = items[self.menu_i]
        put(top, "%-14s%7s" % (name, "%d/%d" % (self.menu_i + 1, len(items))))
        put(big, value)
        put(foot, hint)
        set_bright(1.0)
        if LEFT in pressed or snooze or (kind == "back" and pressed & {SELECT, RIGHT}):
            self.mode = "face"
            return
        if pressed & {SELECT, RIGHT}:
            if kind == "alarm":
                a = cfg.alarms[idx]
                self.edit = [kind, idx, ["hour", "minute", "days", "on"], 0, [a.hour, a.minute, a.mode, 1 if a.on else 0]]
            elif kind == "volume":
                self.edit = [kind, idx, ["volume"], 0, [cfg.volume]]
            elif kind == "snooze":
                self.edit = [kind, idx, ["minutes"], 0, [cfg.snooze_min]]
            elif kind == "time":
                lt = core.Local(now_utc())
                self.edit = [kind, idx, ["hour", "minute"], 0, [lt.hour, lt.minute]]
            self.mode = "edit"

    def edit_step(self, turn, pressed, snooze, utc):
        kind, idx, fields, fi, vals = self.edit
        step = turn + (1 if UP in pressed else 0) - (1 if DOWN in pressed else 0)
        f = fields[fi]
        if step:
            if f == "hour":
                vals[fi] = core.wrap(vals[fi] + step, 0, 23)
            elif f == "minute":
                vals[fi] = core.wrap(vals[fi] + step, 0, 59)
            elif f == "days":
                vals[fi] = core.wrap(vals[fi] + step, 0, len(core.MODES) - 1)
            elif f == "on":
                vals[fi] = 1 - vals[fi] if step % 2 else vals[fi]
            elif f == "volume":
                vals[fi] = max(1, min(10, vals[fi] + step))
                play(vals[fi])                      # hear the level while choosing it
            elif f == "minutes":
                vals[fi] = max(1, min(30, vals[fi] + step))
        if LEFT in pressed or snooze:
            if fi == 0:
                self.mode = "menu"                  # leave without saving
                quiet()
                return
            self.edit[3] = fi - 1
            return
        if pressed & {SELECT, RIGHT}:
            if fi + 1 < len(fields):
                self.edit[3] = fi + 1
                return
            self.commit(kind, idx, vals, utc)
            self.mode = "menu"
            quiet()
            return
        # show it, the field being changed in brackets
        if kind in ("alarm", "time"):
            h = "[%02d]" % vals[0] if f == "hour" else "%02d" % vals[0]
            m = "[%02d]" % vals[1] if f == "minute" else "%02d" % vals[1]
            put(big, h + ":" + m)
            if kind == "alarm":
                d = core.MODES[vals[2]]
                o = "ON" if vals[3] else "off"
                put(foot, ("[%s]" % d if f == "days" else d) + "  " + ("[%s]" % o if f == "on" else o))
            else:
                put(foot, "press to set the clock")
            put(top, "%-21s" % ("ALARM %d" % (idx + 1) if kind == "alarm" else "SET TIME"))
        else:
            put(big, "%d%s" % (vals[0], " min" if kind == "snooze" else ""))
            put(foot, "press to save")
            put(top, kind.upper())

    def commit(self, kind, idx, vals, utc):
        if kind == "alarm":
            a = cfg.alarms[idx]
            a.hour, a.minute, a.mode, a.on = vals[0], vals[1], vals[2], vals[3] == 1
            cfg.last_fired = max(cfg.last_fired, minute_key(utc))   # never ring at once for a past time
            log("alarm %d %s %s %s" % (idx + 1, a.text(), core.MODES[a.mode], "on" if a.on else "off"))
        elif kind == "volume":
            cfg.volume = vals[0]
        elif kind == "snooze":
            cfg.snooze_min = vals[0]
        elif kind == "time":
            set_rtc_local(vals[0], vals[1])
            cfg.last_fired = max(cfg.last_fired, minute_key(now_utc()))
        save()

    # ---- one pass of the loop ----
    def step(self):
        mono = time.monotonic()
        utc = now_utc()
        turn, pressed, snooze = inputs.poll()
        waved = self.wave(mono)
        if turn or pressed or snooze or waved:
            self.last_input = mono
        self.slow(mono)

        # disarm silences everything
        if not armed():
            if self.mode == "ring":
                self.stop_ring(False, utc)
            elif cfg.snooze_until:
                cfg.snooze_until = 0
                save()
        elif self.mode != "ring":
            if cfg.snooze_until and utc >= cfg.snooze_until:
                self.start_ring(utc, "snooze over")
            else:
                key = core.due_alarm(cfg.alarms, utc, cfg.last_fired)
                if key:
                    cfg.last_fired = key
                    self.start_ring(utc, "alarm")

        if self.mode == "ring":
            self.ring(turn, pressed, snooze, utc, mono)
            return
        if self.mode in ("menu", "edit") and mono - self.last_input > MENU_IDLE:
            self.mode = "face"
            quiet()
        if self.mode == "menu":
            self.menu(turn, pressed, snooze)
        elif self.mode == "edit":
            self.edit_step(turn, pressed, snooze, utc)
        else:
            if self.tilted(mono):
                self.focus_end = 0 if self.focus_end else mono + FOCUS_MIN * 60
                log("focus", "on" if self.focus_end else "off")
                play(2)
            self.face(turn, pressed, snooze, utc, mono, waved)

def greet():
    """The spoken line, only on a real power-up and only if no alarm is waiting."""
    try:
        if supervisor.runtime.run_reason != supervisor.RunReason.STARTUP or cfg.snooze_until:
            return
        with open("say_check.wav", "rb") as f:
            w = audiocore.WaveFile(f)
            i2s.play(w)
            time.sleep(0.05)
            sd.value = True
            while i2s.playing:
                time.sleep(0.05)
        quiet()
    except OSError:
        pass

def main():
    if not rtc:
        put(top, "CLOCK CHIP MISSING")
        put(big, "--:--")
        while True:
            time.sleep(1)
    clock = Clock()
    clock.step()
    greet()
    log("running; armed=%s next=%s" % (armed(), core.next_alarm(cfg.alarms, now_utc())[0] and core.next_alarm(cfg.alarms, now_utc())[0].text()))
    while True:
        try:
            clock.step()
        except (OSError, RuntimeError) as e:          # a glitch on the chain: log it, keep the alarm alive
            log("glitch", e)
            time.sleep(0.2)
        time.sleep(0.04)

try:
    main()
except KeyboardInterrupt:
    quiet()
    raise
except Exception as e:
    import traceback
    traceback.print_exception(e)
    quiet()
    log("crash, resetting in 5 s")
    time.sleep(5)
    microcontroller.reset()
