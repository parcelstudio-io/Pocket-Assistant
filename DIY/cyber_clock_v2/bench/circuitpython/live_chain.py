import serial, time, sys
s = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5)
s.write(b'\x03\x03'); time.sleep(0.8); s.write(b'\x04'); time.sleep(2.5); s.write(b'\x03\x03'); time.sleep(1); s.read(16384)
code = """import time, board, busio, adafruit_ds3231, adafruit_vcnl4040, adafruit_lis3dh, adafruit_ahtx0
from adafruit_seesaw import seesaw, rotaryio
i2c = busio.I2C(board.IO9, board.IO8)
rtc = adafruit_ds3231.DS3231(i2c)
rtc.lost_power = False
print('clock lost-power flag cleared, now', rtc.lost_power)
prox = adafruit_vcnl4040.VCNL4040(i2c); acc = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18)
ss = seesaw.Seesaw(i2c, addr=0x49)
names = {1:'select', 2:'up', 3:'left', 4:'down', 5:'right'}
mask = sum(1 << p for p in names)
for p in names: ss.pin_mode(p, ss.INPUT_PULLUP)
knob = rotaryio.IncrementalEncoder(ss)
seen = set(); last_pos = knob.position; maxprox = 0; minlux = 1e9; maxlux = 0; tilt = set()
t0 = time.monotonic(); nxt = 0
while time.monotonic() - t0 < 90:
    b = ss.digital_read_bulk(mask)
    for p, n in names.items():
        if not (b >> p) & 1 and n not in seen:
            seen.add(n); print('BUTTON', n)
    pos = knob.position
    if pos != last_pos: print('KNOB', pos); last_pos = pos
    pr = prox.proximity; lx = prox.lux
    maxprox = max(maxprox, pr); minlux = min(minlux, lx); maxlux = max(maxlux, lx)
    x, y, z = acc.acceleration
    for ax, v in (('x', x), ('y', y), ('z', z)):
        if abs(v) > 8: tilt.add(ax + ('+' if v > 0 else '-'))
    if time.monotonic() - t0 > nxt:
        print('t=%2ds prox %d lux %d acc %.1f %.1f %.1f' % (nxt, pr, lx, x, y, z)); nxt += 10
    time.sleep(0.03)
print('SUMMARY buttons', sorted(seen), 'knob end', knob.position, 'max prox', maxprox, 'lux %d..%d' % (minlux, maxlux), 'tilt axes', sorted(tilt))
print('LIVE END')
"""
s.write(b'\x05'); time.sleep(0.2); s.write(code.replace('\n','\r').encode()); time.sleep(0.3); s.read(16384); s.write(b'\x04')
end = time.time() + 110; out = b''
while time.time() < end:
    chunk = s.read(1024); out += chunk
    if chunk: sys.stdout.write(chunk.decode(errors='replace')); sys.stdout.flush()
    if b'LIVE END' in out or b'Traceback' in out: break
