"""Cyber Dawn bench check: is each chain board the right chip, and is it live?

Run from the REPL:  import parts_check
For each board: an identity test (a register only that chip answers that way), then
readings and a plausibility test. The two thermometers (clock chip and humidity
sensor) are compared with each other. Chain on GPIO9 (SCL) and GPIO8 (SDA).
"""
import time, math, board, busio
import adafruit_ds3231, adafruit_vcnl4040, adafruit_lis3dh, adafruit_ahtx0
from adafruit_seesaw import seesaw, rotaryio

i2c = busio.I2C(board.IO9, board.IO8)
passed = []


def report(name, ok, detail):
    passed.append(ok)
    print(("PASS " if ok else "FAIL ") + name + ": " + detail)


def reg(addr, r, n=1):
    while not i2c.try_lock():
        pass
    try:
        buf = bytearray(n)
        i2c.writeto_then_readfrom(addr, bytes([r]), buf)
        return buf
    finally:
        i2c.unlock()


while not i2c.try_lock():
    pass
found = sorted(i2c.scan())
i2c.unlock()
print("on the bus:", [hex(a) for a in found])

# Real-time clock, 0x68: the time must advance, and the chip has its own thermometer.
rtc = adafruit_ds3231.DS3231(i2c)
a = rtc.datetime
time.sleep(2.2)
b = rtc.datetime
step = (b.tm_hour * 3600 + b.tm_min * 60 + b.tm_sec) - (a.tm_hour * 3600 + a.tm_min * 60 + a.tm_sec)
raw = reg(0x68, 0x11, 2)
rtc_temp = (raw[0] - 256 if raw[0] > 127 else raw[0]) + (raw[1] >> 6) * 0.25
report("real-time clock 0x68", 2 <= step <= 3 and b.tm_year >= 2026 and not rtc.lost_power,
       f"{b.tm_year}-{b.tm_mon:02}-{b.tm_mday:02} {b.tm_hour:02}:{b.tm_min:02}:{b.tm_sec:02}, "
       f"+{step} s in 2.2 s, lost-power flag {rtc.lost_power}, own thermometer {rtc_temp:.2f} C")

# Rotary encoder, 0x49: the seesaw firmware reports its product number.
ss = seesaw.Seesaw(i2c, addr=0x49)
product = (ss.get_version() >> 16) & 0xFFFF
mask = sum(1 << p for p in (1, 2, 3, 4, 5))
for p in (1, 2, 3, 4, 5):
    ss.pin_mode(p, ss.INPUT_PULLUP)
knob = rotaryio.IncrementalEncoder(ss)
rest = ss.digital_read_bulk(mask)
report("rotary encoder 0x49", product == 5740,
       f"firmware product {product} (5740 = this encoder), wheel at {knob.position}, "
       f"buttons {hex(rest)} ({'all released' if rest == mask else 'some held'})")

# Proximity and light sensor, 0x60: device ID register 0x0C reads 0x0186.
dev = reg(0x60, 0x0C, 2)
dev_id = dev[0] | dev[1] << 8
prox = adafruit_vcnl4040.VCNL4040(i2c)
time.sleep(0.3)
p, lux, white = prox.proximity, prox.lux, prox.white
report("proximity and light sensor 0x60", dev_id == 0x0186 and 0 <= lux < 100000,
       f"ID {hex(dev_id)} (0x186 = VCNL4040), proximity {p}, light {lux:.0f} lux, white {white}")

# Accelerometer, 0x18: WHO_AM_I register 0x0F reads 0x33; at rest it must feel 1 g.
who = reg(0x18, 0x0F)[0]
acc = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18)
time.sleep(0.1)
mags = []
for _ in range(20):
    x, y, z = acc.acceleration
    mags.append(math.sqrt(x * x + y * y + z * z))
    time.sleep(0.025)
mean = sum(mags) / len(mags)
spread = max(mags) - min(mags)
report("accelerometer 0x18", who == 0x33 and 8.8 <= mean <= 10.8 and spread > 0,
       f"WHO_AM_I {hex(who)} (0x33 = LIS3DH), gravity {mean:.2f} m/s2 "
       f"(x {x:.1f}, y {y:.1f}, z {z:.1f}), live jitter {spread:.2f}")

# Temperature and humidity sensor, 0x38: calibrated status bit, plausible room values,
# and its temperature must agree with the clock chip's thermometer.
aht = adafruit_ahtx0.AHTx0(i2c)
status = aht.status
t_aht, rh = aht.temperature, aht.relative_humidity
report("temperature and humidity sensor 0x38",
       bool(status & 0x08) and 5 < t_aht < 45 and 5 < rh < 95 and abs(t_aht - rtc_temp) < 4,
       f"calibrated {bool(status & 0x08)}, {t_aht:.1f} C, {rh:.0f} % RH; "
       f"clock chip says {rtc_temp:.2f} C ({t_aht - rtc_temp:+.1f} C apart)")

print(f"{sum(passed)} of {len(passed)} boards read correctly"
      + ("" if found == [0x18, 0x38, 0x49, 0x60, 0x68] else "; bus list is not the expected five"))
i2c.deinit()
