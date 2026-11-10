# Cyber Dawn alarm logic (2026-11-09). Pure integer maths, no hardware, so the same file runs on the
# board (CircuitPython) and on the host for tests (bench/test_dawn_core.py).
# Time: the real-time clock keeps UTC. Local time is New York: UTC-5, UTC-4 in US daylight saving
# (second Sunday of March 02:00 local to first Sunday of November 02:00 local).

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
STD_OFFSET = -5 * 3600
MODES = ("every day", "weekdays", "weekends")
N_ALARMS = 3
CATCH_UP = 10 * 60          # an alarm missed by a reset or power dip still rings if under 10 min late
RING_LIMIT = 20 * 60        # ringing gives up after 20 min (battery), and counts as dismissed


# ---- calendar --------------------------------------------------------------------------------
def days_from_civil(y, m, d):
    """Days since 1970-01-01 (Howard Hinnant's algorithm)."""
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def civil_from_days(z):
    z += 719468
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    return y + (m <= 2), m, d


def epoch(y, mo, d, h=0, mi=0, s=0):
    return days_from_civil(y, mo, d) * 86400 + h * 3600 + mi * 60 + s


def weekday(days):
    """0 = Monday. 1970-01-01 was a Thursday."""
    return (days + 3) % 7


def nth_sunday(y, m, n):
    first = days_from_civil(y, m, 1)
    return first + (6 - weekday(first)) % 7 + 7 * (n - 1)


def utc_offset(utc):
    """Seconds to add to UTC for New York local time at this instant."""
    y = civil_from_days(utc // 86400)[0]
    start = nth_sunday(y, 3, 2) * 86400 + 2 * 3600 - STD_OFFSET        # 02:00 EST = 07:00 UTC
    end = nth_sunday(y, 11, 1) * 86400 + 2 * 3600 - (STD_OFFSET + 3600)  # 02:00 EDT = 06:00 UTC
    return STD_OFFSET + (3600 if start <= utc < end else 0)


class Local:
    """Broken-down local time."""
    def __init__(self, utc):
        self.utc = utc
        t = utc + utc_offset(utc)
        self.days = t // 86400
        self.year, self.month, self.day = civil_from_days(self.days)
        sec = t % 86400
        self.hour, self.minute, self.second = sec // 3600, sec % 3600 // 60, sec % 60
        self.wday = weekday(self.days)

    def date_text(self):
        return "%s %d %s" % (DAYS[self.wday], self.day, MONTHS[self.month - 1])


def local_to_utc(y, mo, d, h, mi, s=0):
    """Inverse of Local for a wall-clock time. The repeated hour in autumn gives the first of the two;
    the missing hour in spring maps forward an hour."""
    wall = epoch(y, mo, d, h, mi, s)
    dst = wall - (STD_OFFSET + 3600)
    if utc_offset(dst) == STD_OFFSET + 3600:
        return dst
    return wall - STD_OFFSET          # standard time, or (inside the spring gap) an hour forward


# ---- alarms ----------------------------------------------------------------------------------
class Alarm:
    def __init__(self, hour=7, minute=0, mode=0, on=False):
        self.hour, self.minute, self.mode, self.on = hour, minute, mode, on

    def due_day(self, wday):
        if self.mode == 1:
            return wday < 5
        if self.mode == 2:
            return wday >= 5
        return True

    def text(self):
        return "%02d:%02d" % (self.hour, self.minute)


def due_alarm(alarms, utc, last_fired):
    """The minute key (local minutes since 1970) of an alarm that should ring now, or None.
    Looks back CATCH_UP seconds so a reset across the alarm minute does not lose it."""
    for back in range(0, CATCH_UP + 1, 60):
        t = Local(utc - back)
        key = (t.utc + utc_offset(t.utc)) // 60
        if key <= last_fired:
            return None
        for a in alarms:
            if a.on and a.hour == t.hour and a.minute == t.minute and a.due_day(t.wday):
                return key
    return None


def next_alarm(alarms, utc):
    """(alarm, utc) of the next enabled alarm within 8 days, or (None, None)."""
    best = None
    now = Local(utc)
    for dd in range(0, 8):
        y, mo, d = civil_from_days(now.days + dd)
        wd = weekday(now.days + dd)
        for a in alarms:
            if not (a.on and a.due_day(wd)):
                continue
            when = local_to_utc(y, mo, d, a.hour, a.minute)
            if when > utc and (best is None or when < best[1]):
                best = (a, when)
        if best:
            return best
    return None, None


# ---- settings, stored in microcontroller.nvm -------------------------------------------------
# byte 0: safemode.py's power-dip counter (not ours)
# 1: magic 0xCD   2: volume 1-10   3: snooze minutes   4: reserved
# 5..16: three alarms x (hour, minute, mode, on)
# 17..20: snooze-until, UTC seconds, 0 = none (also "ringing" across a reset)
# 21..24: last-fired local minute key
MAGIC = 0xCD
NVM_SIZE = 25


class Settings:
    def __init__(self):
        self.volume = 6
        self.snooze_min = 9
        self.alarms = [Alarm(7, 0, 0, False), Alarm(8, 30, 2, False), Alarm(6, 30, 1, False)]
        self.snooze_until = 0
        self.last_fired = 0

    def pack(self):
        b = bytearray(NVM_SIZE)
        b[1], b[2], b[3] = MAGIC, self.volume, self.snooze_min
        for i, a in enumerate(self.alarms):
            b[5 + 4 * i:9 + 4 * i] = bytes((a.hour, a.minute, a.mode, 1 if a.on else 0))
        b[17:21] = self.snooze_until.to_bytes(4, "big")
        b[21:25] = self.last_fired.to_bytes(4, "big")
        return b

    @classmethod
    def unpack(cls, b):
        s = cls()
        if len(b) < NVM_SIZE or b[1] != MAGIC:
            return s                                   # blank or foreign memory: defaults
        s.volume = min(10, max(1, b[2]))
        s.snooze_min = min(30, max(1, b[3]))
        for i in range(N_ALARMS):
            h, m, mode, on = b[5 + 4 * i:9 + 4 * i]
            if h < 24 and m < 60 and mode < len(MODES):
                s.alarms[i] = Alarm(h, m, mode, on == 1)
        s.snooze_until = int.from_bytes(b[17:21], "big")
        s.last_fired = int.from_bytes(b[21:25], "big")
        return s


def wrap(v, lo, hi):
    """Step a value round a closed range, for knob editing."""
    span = hi - lo + 1
    return lo + (v - lo) % span
