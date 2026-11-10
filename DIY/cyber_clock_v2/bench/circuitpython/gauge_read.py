# Fuel gauge raw read (MAX17048 at 0x36) + bus scan. Run from the REPL: import gauge_read
import time, board, busio
i2c = busio.I2C(board.IO9, board.IO8)
while not i2c.try_lock():
    pass
print("SCAN", [hex(a) for a in i2c.scan()])
def reg(r):
    b = bytearray(2)
    i2c.writeto_then_readfrom(0x36, bytes([r]), b)
    return (b[0] << 8) | b[1]
try:
    print("VERSION 0x%04x" % reg(0x08))
    for i in range(8):
        v = reg(0x02) * 78.125e-6
        soc = reg(0x04) / 256
        cr = reg(0x16); cr = cr - 65536 if cr > 32767 else cr
        print("GAUGE t=%2ds  V=%.3f  SOC=%.1f%%  rate=%+.1f%%/h" % (i * 5, v, soc, cr * 0.208))
        time.sleep(5)
except OSError as e:
    print("GAUGE no answer at 0x36:", e)
i2c.unlock(); i2c.deinit()
print("GAUGE END")
