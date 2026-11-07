# Amplifier bench test. Run from the REPL: import tone_test
# 1) SD wire + amp power: the breakout's 1 MΩ SD-to-VIN resistor pulls a released GPIO17 high.
# 2) Tone: SD held low, I2S up, 440 Hz generated in code, SD high for 2 s, SD low again.
import time, array, math, board, digitalio, audiobusio, audiocore

sd = digitalio.DigitalInOut(board.IO17)

def released(level):   # drive, let go, read 5 ms later; a floating pin keeps its charge
    n = 0
    for i in range(20):
        sd.switch_to_output(value=level); time.sleep(0.002)
        sd.switch_to_input(pull=None); time.sleep(0.005)
        n += sd.value
    return n

up, down = released(False), released(True)
print("1) SD after release: from low high %d/20, from high high %d/20" % (up, down))
if down == 0:
    print("   pulled LOW: 10 kΩ pull-down fitted on SD (wins over the board's 1 MΩ)")
elif up == 20:
    print("   pulled HIGH: SD wired and amp powered, but NO 10 kΩ pull-down")
else:
    print("   floating: SD wire open, and no pull-down")
sd.switch_to_output(value=False)            # amp off before I2S comes up: no pop

rate, freq = 16000, 440
n = rate // freq
wave = array.array("h", [int(math.sin(2 * math.pi * i / n) * 8000) for i in range(n)])
tone = audiocore.RawSample(wave, sample_rate=rate)
i2s = audiobusio.I2SOut(board.IO14, board.IO15, board.IO16)   # BCLK, LRC, DIN
i2s.play(tone, loop=True)
time.sleep(0.1)
sd.value = True
print("2) tone on for 2 s")
time.sleep(2)
sd.value = False
time.sleep(0.05)
i2s.stop(); i2s.deinit(); sd.deinit()
print("done, amp off")
