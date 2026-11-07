# OLED bench demo. Run from the REPL: import oled_clock
# Title plus a live clock from the real-time clock chip (UTC-5 on the glass).
# Display: 2.42" module in 4-wire SPI (BS1 = BS2 = 0, i.e. R3 + R5 bridged, R2 + R4 empty).
import time, board, busio, displayio, terminalio
import adafruit_displayio_ssd1306, adafruit_ds3231
from fourwire import FourWire
from adafruit_display_text import label

displayio.release_displays()
spi = busio.SPI(board.IO12, board.IO11)                       # clock, data
bus = FourWire(spi, command=board.IO6, chip_select=board.IO10, reset=board.IO7, baudrate=1000000)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)

group = displayio.Group()
display.root_group = group
group.append(label.Label(terminalio.FONT, text="CYBER DAWN", x=34, y=12))
clock = label.Label(terminalio.FONT, text="", x=16, y=40, scale=2)
group.append(clock)

rtc = adafruit_ds3231.DS3231(busio.I2C(board.IO9, board.IO8))
while True:
    t = rtc.datetime
    clock.text = "%02d:%02d:%02d" % ((t.tm_hour - 5) % 24, t.tm_min, t.tm_sec)
    time.sleep(0.2)
