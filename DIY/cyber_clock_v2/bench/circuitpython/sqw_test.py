# SQW → GPIO4 bench test. Run from the REPL: import sqw_test
# 1) pull-up present, 2) 1 Hz square wave reaches GPIO4, 3) Alarm 1 pulls GPIO4 low and releases it.
# Restores the clock's control register and Alarm 1 when done.
import time, board, busio, digitalio
from adafruit_bus_device.i2c_device import I2CDevice

CTRL, STAT, A1 = 0x0E, 0x0F, 0x07
i2c = busio.I2C(board.IO9, board.IO8)
rtc = I2CDevice(i2c, 0x68)

def rd(reg, n=1):
    buf = bytearray(n)
    with rtc:
        rtc.write_then_readinto(bytes([reg]), buf)
    return buf

def wr(reg, *vals):
    with rtc:
        rtc.write(bytes([reg]) + bytes(vals))

def bcd(b):
    return (b >> 4) * 10 + (b & 0x0F)

pin = digitalio.DigitalInOut(board.IO4)
pin.direction = digitalio.Direction.INPUT
ctrl0 = rd(CTRL)[0]
a1_0 = bytes(rd(A1, 4))
print("control 0x%02x  status 0x%02x" % (ctrl0, rd(STAT)[0]))

# 1) Pull-up. Internal pull-down (~45 kΩ) against the external 10 kΩ: high only if the resistor is there.
wr(CTRL, ctrl0 | 0x04)            # INTCN=1: line idle (released)
wr(STAT, rd(STAT)[0] & ~0x03)     # clear A1F/A2F so nothing holds it low
pin.pull = digitalio.Pull.DOWN
time.sleep(0.05)
external = pin.value
print("1) idle, internal pull-down:", "HIGH  -> external pull-up present" if external else "LOW  -> NO pull-up (or wrong pad)")
# Without the 10 kΩ, borrow the internal ~45 kΩ pull-up so 2) and 3) still prove the wire itself.
pin.pull = None if external else digitalio.Pull.UP
if not external:
    print("   running 2) and 3) on the internal pull-up")

# 2) 1 Hz square wave: INTCN=0, RS2:RS1=00. Count falling edges for 3 s.
wr(CTRL, ctrl0 & ~0x1C)
falls, last, end = 0, pin.value, time.monotonic() + 3
while time.monotonic() < end:
    v = pin.value
    if last and not v:
        falls += 1
    last = v
print("2) 1 Hz square wave: %d falling edges in 3 s (expect 3)" % falls)

# 3) Alarm 1: match seconds only, 5 s ahead. INTCN=1, A1IE=1.
wr(STAT, rd(STAT)[0] & ~0x03)
now = bcd(rd(0x00)[0] & 0x7F)
target = (now + 5) % 60
wr(A1, ((target // 10) << 4) | (target % 10), 0x80, 0x80, 0x80)   # A1M2-4 set: seconds match
wr(CTRL, (ctrl0 & ~0x1C) | 0x05)
print("3) alarm set for :%02d (now :%02d), GPIO4 =" % (target, now), int(pin.value))
t0, fired = time.monotonic(), None
while time.monotonic() - t0 < 8:
    if not pin.value:
        fired = time.monotonic() - t0
        break
if fired is None:
    print("   alarm did NOT pull GPIO4 low")
else:
    print("   GPIO4 went LOW after %.2f s, A1F=%d" % (fired, rd(STAT)[0] & 1))
    wr(STAT, rd(STAT)[0] & ~0x01)
    time.sleep(0.01)
    print("   flag cleared, GPIO4 =", int(pin.value), "(expect 1)")

wr(A1, a1_0[0], a1_0[1], a1_0[2], a1_0[3])
wr(CTRL, ctrl0)
wr(STAT, rd(STAT)[0] & ~0x03)
pin.deinit(); i2c.deinit()
print("done, control restored to 0x%02x" % ctrl0)
