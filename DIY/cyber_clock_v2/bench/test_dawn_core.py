#!/usr/bin/env python3
# Host tests for the alarm logic (2026-11-09):  python3 bench/test_dawn_core.py
import os, sys, random, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "circuitpython"))
import dawn_core as c

NY = ZoneInfo("America/New_York")
UTC = datetime.timezone.utc
fails = 0

def check(name, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))

def u(y, mo, d, h=0, mi=0, s=0):
    return int(datetime.datetime(y, mo, d, h, mi, s, tzinfo=UTC).timestamp())

# calendar and time zone against the system's tz database, 20 000 random instants 2024-2040
random.seed(1)
bad = 0
for _ in range(20000):
    t = random.randint(u(2024, 1, 1), u(2040, 12, 31))
    ref = datetime.datetime.fromtimestamp(t, NY)
    lt = c.Local(t)
    if (lt.year, lt.month, lt.day, lt.hour, lt.minute, lt.second, lt.wday) != \
       (ref.year, ref.month, ref.day, ref.hour, ref.minute, ref.second, ref.weekday()):
        bad += 1
check("local time matches tz database", bad == 0, "%d mismatches" % bad)

# every DST edge 2025-2035, a second either side
bad = 0
for y in range(2025, 2036):
    for m in (3, 11):
        for d in range(1, 15):
            for h in range(0, 24):
                t = u(y, m, d, h)
                for dt in (-1, 0, 1):
                    ref = datetime.datetime.fromtimestamp(t + dt, NY)
                    if c.utc_offset(t + dt) != int(ref.utcoffset().total_seconds()):
                        bad += 1
check("offset right at every DST edge", bad == 0, "%d mismatches" % bad)

# local_to_utc round trip
bad = 0
for _ in range(5000):
    t = random.randint(u(2025, 1, 1), u(2035, 1, 1))
    lt = c.Local(t)
    if c.local_to_utc(lt.year, lt.month, lt.day, lt.hour, lt.minute, lt.second) not in (t, t - 3600, t + 3600):
        bad += 1
    elif datetime.datetime.fromtimestamp(t, NY).fold == 0 and c.local_to_utc(lt.year, lt.month, lt.day, lt.hour, lt.minute, lt.second) != t:
        bad += 1
check("local_to_utc inverts Local", bad == 0, "%d bad" % bad)

def at(y, mo, d, h, mi, s=0):
    return int(datetime.datetime(y, mo, d, h, mi, s, tzinfo=NY).timestamp())

# due alarms. 2026-11-09 is a Monday.
a = [c.Alarm(7, 0, 0, True), c.Alarm(9, 0, 2, True), c.Alarm(6, 0, 1, False)]
key = c.due_alarm(a, at(2026, 11, 9, 7, 0, 5), 0)
check("rings at 07:00", key is not None)
check("not again after it fired", c.due_alarm(a, at(2026, 11, 9, 7, 0, 30), key) is None)
check("catch-up 7 min late", c.due_alarm(a, at(2026, 11, 9, 7, 7), 0) is not None)
check("no catch-up 12 min late", c.due_alarm(a, at(2026, 11, 9, 7, 12), 0) is None)
check("weekend alarm silent on Monday", c.due_alarm(a, at(2026, 11, 9, 9, 0), 0) is None)
check("weekend alarm rings Saturday", c.due_alarm(a, at(2026, 11, 14, 9, 0), 0) is not None)
check("off alarm silent", c.due_alarm(a, at(2026, 11, 10, 6, 0), 0) is None)
check("weekday mode", c.Alarm(6, 0, 1).due_day(4) and not c.Alarm(6, 0, 1).due_day(5))
check("no alarm at 07:01:00 when none set", c.due_alarm(a, at(2026, 11, 9, 8, 0), 0) is None)

# next alarm
n, when = c.next_alarm(a, at(2026, 11, 9, 22, 0))
check("next is tomorrow 07:00", n is a[0] and when == at(2026, 11, 10, 7, 0))
n, when = c.next_alarm([c.Alarm(9, 0, 2, True)], at(2026, 11, 9, 22, 0))
check("next weekend alarm is Saturday", when == at(2026, 11, 14, 9, 0))
check("nothing on: none", c.next_alarm([c.Alarm()], at(2026, 11, 9, 1, 0)) == (None, None))
n, when = c.next_alarm([c.Alarm(7, 0, 0, True)], at(2027, 3, 13, 23, 0))
check("next across spring DST", when == at(2027, 3, 14, 7, 0))

# settings
s = c.Settings()
s.volume, s.snooze_min, s.snooze_until, s.last_fired = 8, 12, at(2026, 11, 9, 7, 9), 29400000
s.alarms[1] = c.Alarm(5, 45, 1, True)
r = c.Settings.unpack(bytes(s.pack()))
check("settings round trip", (r.volume, r.snooze_min, r.snooze_until, r.last_fired, r.alarms[1].text(), r.alarms[1].mode, r.alarms[1].on)
      == (8, 12, s.snooze_until, 29400000, "05:45", 1, True))
check("blank memory gives defaults", c.Settings.unpack(b"\xff" * 25).volume == 6)
check("pack leaves byte 0 alone", s.pack()[0] == 0)
check("wrap", c.wrap(24, 0, 23) == 0 and c.wrap(-1, 0, 59) == 59)

print("SUMMARY", "all pass" if not fails else "%d FAIL" % fails)
sys.exit(1 if fails else 0)
