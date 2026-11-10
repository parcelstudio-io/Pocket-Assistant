# One-shot health report, for USB or the Wi-Fi web REPL (2026-11-09).
#   import diag            (stop the clock with Ctrl-C first; Ctrl-D restarts it)
# Prints one DIAG line per check, then DIAG END. Touches no outputs: screen, amp and lamp stay as they are.
import time, gc, board, busio, digitalio, microcontroller, supervisor

def line(k, v):
    print("DIAG %-9s %s" % (k, v))

line("uptime", "%.0f s since boot, reset reason %s" % (time.monotonic(), str(microcontroller.cpu.reset_reason).split(".")[-1]))
line("cpu", "%.1f C, free RAM %d kB" % (microcontroller.cpu.temperature, gc.mem_free() // 1024))
try:
    import wifi
    r = wifi.radio
    if r.connected:
        line("wifi", "%s  %s  RSSI %s dBm  ch %s" % (r.ap_info.ssid, r.ipv4_address, r.ap_info.rssi, r.ap_info.channel))
    else:
        line("wifi", "not connected")
except Exception as e:
    line("wifi", "error %s" % e)

def pin(name, io):
    p = digitalio.DigitalInOut(io)
    p.switch_to_input(pull=digitalio.Pull.UP)
    v = p.value
    p.deinit()
    return v
for name, io in (("snooze", board.IO18), ("arm", board.IO21)):
    try:
        line(name, "pressed/on (low)" if not pin(name, io) else "released/off (high)")
    except ValueError:
        line(name, "pin in use")
try:
    a = digitalio.DigitalInOut(board.IO39); a.switch_to_input()
    line("alert", "gauge alert LOW (active)" if not a.value else "gauge alert high (quiet)")
    a.deinit()
except ValueError:
    line("alert", "pin in use")

try:
    i2c = busio.I2C(board.IO9, board.IO8)
except ValueError:
    i2c = None
    line("i2c", "bus in use: run after Ctrl-C and a soft reboot")
if i2c:
    while not i2c.try_lock():
        pass
    found = i2c.scan()
    names = {0x18: "accel", 0x36: "gauge", 0x38: "humidity", 0x49: "encoder", 0x60: "proximity", 0x68: "clock"}
    line("i2c", " ".join("%s=%s" % (n, "ok" if a in found else "MISSING") for a, n in sorted(names.items())))
    def reg(r):
        b = bytearray(2)
        i2c.writeto_then_readfrom(0x36, bytes([r]), b)
        return (b[0] << 8) | b[1]
    try:
        v = reg(0x02) * 78.125e-6
        soc = reg(0x04) / 256
        cr = reg(0x16); cr = cr - 65536 if cr > 32767 else cr
        state = "charging" if cr * 0.208 > 1 else ("discharging" if cr * 0.208 < -1 else "steady")
        line("battery", "%.3f V  %.0f%%  %+.1f %%/h  %s" % (v, soc, cr * 0.208, state))
    except OSError:
        line("battery", "gauge no answer")
    i2c.unlock()
    try:
        import adafruit_ds3231, adafruit_ahtx0, adafruit_vcnl4040, adafruit_lis3dh
        t = adafruit_ds3231.DS3231(i2c).datetime
        line("clock", "%04d-%02d-%02d %02d:%02d:%02d UTC" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))
        h = adafruit_ahtx0.AHTx0(i2c)
        line("climate", "%.1f C  %.0f %%RH" % (h.temperature, h.relative_humidity))
        line("prox", "%d counts" % adafruit_vcnl4040.VCNL4040(i2c).proximity)
        x, y, z = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18).acceleration
        line("tilt", "x %.1f  y %.1f  z %.1f m/s2" % (x, y, z))
    except Exception as e:
        line("sensors", "error %s" % e)
    i2c.deinit()
print("DIAG END")
