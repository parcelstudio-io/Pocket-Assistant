import time, board, busio
import adafruit_ds3231, adafruit_vcnl4040, adafruit_lis3dh, adafruit_ahtx0
from adafruit_seesaw import seesaw, rotaryio

while True:   # wait for the chain: its boards carry the bus pull-ups
    try:
        i2c = busio.I2C(board.IO9, board.IO8)   # SCL, SDA: the controller board's chain pins
        break
    except RuntimeError:
        print("no pull-ups on GPIO8/GPIO9: check the QT-to-header cable (red 3V3, black GND, blue 8, yellow 9)")
        time.sleep(2)
rtc = adafruit_ds3231.DS3231(i2c)
prox = adafruit_vcnl4040.VCNL4040(i2c)
acc = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18)
aht = adafruit_ahtx0.AHTx0(i2c)

ss = seesaw.Seesaw(i2c, addr=0x49)
assert (ss.get_version() >> 16) & 0xFFFF == 5740, "not an ANO encoder"
names = ["select", "up", "left", "down", "right"]
pins = (1, 2, 3, 4, 5)
mask = sum(1 << p for p in pins)
for pin in pins:
    ss.pin_mode(pin, ss.INPUT_PULLUP)
knob = rotaryio.IncrementalEncoder(ss)
print("buttons at rest:", hex(ss.digital_read_bulk(mask)), "(0x3e = all five released)")

while True:
    # Look at the buttons ~30 times over the second and keep any press, so a tap counts.
    seen, end = set(), time.monotonic() + 1
    while time.monotonic() < end:
        low = ~ss.digital_read_bulk(mask) & mask
        seen.update(n for n, p in zip(names, pins) if low & (1 << p))
        time.sleep(0.03)
    t = rtc.datetime
    x, y, z = acc.acceleration
    pressed = [n for n in names if n in seen]
    print(f"{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}  "
          f"knob={knob.position:4d} {pressed}  "
          f"prox={prox.proximity:4d} lux={prox.lux:5.0f}  "
          f"g=({x:5.1f},{y:5.1f},{z:5.1f})  "
          f"{aht.temperature:4.1f}C {aht.relative_humidity:3.0f}%")
