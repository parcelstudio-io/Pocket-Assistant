# Speech bench test. Run from the REPL: import say_test
# Plays say.wav (16 kHz, 16-bit mono) with the amp held off until I2S is running.
import time, board, digitalio, audiobusio, audiocore

sd = digitalio.DigitalInOut(board.IO17)
sd.switch_to_output(value=False)
i2s = audiobusio.I2SOut(board.IO14, board.IO15, board.IO16)   # BCLK, LRC, DIN
with open("say.wav", "rb") as f:
    wav = audiocore.WaveFile(f)
    i2s.play(wav)
    time.sleep(0.05)
    sd.value = True
    while i2s.playing:
        time.sleep(0.05)
sd.value = False
i2s.deinit(); sd.deinit()
print("done, said it")
