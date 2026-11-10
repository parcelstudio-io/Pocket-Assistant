# Charge watch. Run from the REPL: import gauge_watch
# Every 10 s: look for the fuel gauge (0x36); once found, show cell volts, % and charge rate on
# the OLED and print them. Runs 60 min. Charger status comes from the gauge's rate sign.
import time, board, busio, displayio, terminalio
import adafruit_displayio_ssd1306
from fourwire import FourWire
from adafruit_display_text import label
displayio.release_displays()
spi = busio.SPI(board.IO12, board.IO11)
bus = FourWire(spi, command=board.IO6, chip_select=board.IO10, reset=board.IO7, baudrate=1000000)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)
g = displayio.Group(); display.root_group = g
rows = [label.Label(terminalio.FONT, text="", x=0, y=6 + 16 * i) for i in range(4)]
for r in rows: g.append(r)
rows[0].text = "CYBER DAWN  battery"
i2c = busio.I2C(board.IO9, board.IO8)
def reg(r):
    b = bytearray(2)
    while not i2c.try_lock(): pass
    try:
        i2c.writeto_then_readfrom(0x36, bytes([r]), b)
    finally:
        i2c.unlock()
    return (b[0] << 8) | b[1]
t0 = time.monotonic()
while time.monotonic() - t0 < 3600:
    m = int((time.monotonic() - t0) // 60)
    try:
        v = reg(0x02) * 78.125e-6; soc = reg(0x04) / 256
        cr = reg(0x16); cr = cr - 65536 if cr > 32767 else cr; rate = cr * 0.208
        state = "charging" if rate > 0.5 else ("draining" if rate < -0.5 else "steady")
        rows[1].text = "cell %.3f V  %3.0f%%" % (v, soc)
        rows[2].text = "rate %+.1f %%/h" % rate
        rows[3].text = "%s  t=%dm" % (state, m)
        print("GAUGE t=%dm V=%.3f SOC=%.1f%% rate=%+.1f%%/h %s" % (m, v, soc, rate, state))
    except OSError:
        rows[1].text = "gauge: no answer"
        rows[2].text = "reseat its QT cable"
        rows[3].text = "t=%dm" % m
        print("NOGAUGE t=%dm" % m)
    time.sleep(10)
print("WATCH END")
