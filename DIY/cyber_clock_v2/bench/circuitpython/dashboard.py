# Bench dashboard. Run from the REPL: import dashboard
# OLED: clock on top, then light / proximity / humidity, then knob position and the last button.
import time, board, busio, displayio, terminalio
import adafruit_displayio_ssd1306, adafruit_ds3231, adafruit_vcnl4040, adafruit_lis3dh, adafruit_ahtx0
from fourwire import FourWire
from adafruit_display_text import label
from adafruit_seesaw import seesaw, rotaryio

displayio.release_displays()
spi = busio.SPI(board.IO12, board.IO11)
bus = FourWire(spi, command=board.IO6, chip_select=board.IO10, reset=board.IO7, baudrate=1000000)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)
group = displayio.Group(); display.root_group = group
rows = []
for i in range(4):
    row = label.Label(terminalio.FONT, text="", x=0, y=6 + 16 * i)
    rows.append(row); group.append(row)

i2c = busio.I2C(board.IO9, board.IO8)
rtc = adafruit_ds3231.DS3231(i2c)
prox = adafruit_vcnl4040.VCNL4040(i2c)
acc = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18)
aht = adafruit_ahtx0.AHTx0(i2c)
ss = seesaw.Seesaw(i2c, addr=0x49)
names = {1: "SELECT", 2: "UP", 3: "LEFT", 4: "DOWN", 5: "RIGHT"}
mask = sum(1 << p for p in names)
for p in names:
    ss.pin_mode(p, ss.INPUT_PULLUP)
knob = rotaryio.IncrementalEncoder(ss)
last_btn = "-"; seen = set(); t0 = time.monotonic(); slow = 0
while time.monotonic() - t0 < 300:
    b = ss.digital_read_bulk(mask)
    for p, n in names.items():
        if not (b >> p) & 1:
            if n != last_btn:
                print("BUTTON", n)
            last_btn = n; seen.add(n)
    t = rtc.datetime
    rows[0].text = "%02d:%02d:%02d  %4.1fC" % ((t.tm_hour - 5) % 24, t.tm_min, t.tm_sec, aht.temperature)
    rows[1].text = "lux %4d  prox %3d" % (prox.lux, prox.proximity)
    x, y, z = acc.acceleration
    rows[2].text = "tilt %+3.0f %+3.0f %+3.0f" % (x, y, z)
    rows[3].text = "knob %4d  %s" % (knob.position, last_btn)
    if time.monotonic() - t0 > slow:
        print("t=%3ds" % slow, rows[0].text, "|", rows[1].text, "|", rows[3].text); slow += 30
    time.sleep(0.05)
print("SUMMARY buttons seen", sorted(seen), "knob", knob.position)
print("DASH END")
