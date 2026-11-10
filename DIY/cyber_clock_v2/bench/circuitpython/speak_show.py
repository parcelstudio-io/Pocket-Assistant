# Display + speaker check. Run from the REPL: import speak_show
# OLED: title, live local time from the real-time clock, date. Speaker: say_check.wav through
# the amp, SD held low until I2S is running (no pop). Afterwards the clock runs for 10 min.
# OLED 4-wire SPI: clock GPIO12, data GPIO11, DC GPIO6, CS GPIO10, reset GPIO7.
# Amp: BCLK GPIO14, LRC GPIO15, DIN GPIO16, SD GPIO17. Chain: SCL GPIO9, SDA GPIO8.
import time, board, busio, digitalio, displayio, terminalio, audiobusio, audiocore
import adafruit_displayio_ssd1306, adafruit_ds3231
from fourwire import FourWire
from adafruit_display_text import label

WAV = "say_check.wav"
TZ = -5          # the clock chip keeps UTC; New York is UTC-5 in November
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

displayio.release_displays()
spi = busio.SPI(board.IO12, board.IO11)                       # clock, data
bus = FourWire(spi, command=board.IO6, chip_select=board.IO10, reset=board.IO7, baudrate=1000000)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)
group = displayio.Group()
display.root_group = group
title = label.Label(terminalio.FONT, text="CYBER DAWN", x=34, y=8)
clock = label.Label(terminalio.FONT, text="", x=16, y=32, scale=2)
foot = label.Label(terminalio.FONT, text="", x=0, y=57)
for item in (title, clock, foot):
    group.append(item)

rtc = adafruit_ds3231.DS3231(busio.I2C(board.IO9, board.IO8))   # SCL, SDA

def local():
    return time.localtime(time.mktime(rtc.datetime) + TZ * 3600)

def show(note=None):
    t = local()
    clock.text = "%02d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
    foot.text = note if note else "%s %d %s %d" % (DAYS[t.tm_wday], t.tm_mday, MONTHS[t.tm_mon - 1], t.tm_year)
    return t

t = show("speaker check")
print("DISPLAY ON  %02d:%02d:%02d local" % (t.tm_hour, t.tm_min, t.tm_sec))

# Is the amp's SD wire there? Drive high, let go, read: the 10 k pull-down on SD pulls it low.
sd = digitalio.DigitalInOut(board.IO17)
sd.switch_to_output(value=True); time.sleep(0.002)
sd.switch_to_input(pull=None); time.sleep(0.005)
print("SD released from high reads", "LOW: amp SD wired (pull-down seen)" if not sd.value else "HIGH: SD open or no pull-down")
sd.switch_to_output(value=False)             # amp off before I2S comes up: no pop

i2s = audiobusio.I2SOut(board.IO14, board.IO15, board.IO16)   # BCLK, LRC, DIN
with open(WAV, "rb") as f:
    wav = audiocore.WaveFile(f)
    print("WAV %d Hz %d-bit %d ch" % (wav.sample_rate, wav.bits_per_sample, wav.channel_count))
    i2s.play(wav)
    time.sleep(0.05)
    sd.value = True
    t0 = time.monotonic()
    while i2s.playing:
        show("speaking...")
        time.sleep(0.1)
    sd.value = False
print("SPOKE %s in %.1f s" % (WAV, time.monotonic() - t0))
i2s.deinit(); sd.deinit()

end = time.monotonic() + 600
mark = 0
while time.monotonic() < end:
    t = show()
    if time.monotonic() - t0 > mark:
        print("CLOCK %02d:%02d:%02d %s" % (t.tm_hour, t.tm_min, t.tm_sec, foot.text)); mark += 60
    time.sleep(0.2)
print("CLOCK END")
