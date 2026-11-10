"""Small libopus wrapper and 16 kHz to 24 kHz PCM conversion.

Xiaozhi v1 sends one bare Opus packet per 60 ms WebSocket binary message.
Realtime accepts and returns signed little-endian 24 kHz mono PCM.
"""

from array import array
import ctypes
import ctypes.util
import sys


INPUT_RATE = 16_000
OUTPUT_RATE = 24_000
FRAME_MS = 60
INPUT_SAMPLES = INPUT_RATE * FRAME_MS // 1000
OUTPUT_SAMPLES = OUTPUT_RATE * FRAME_MS // 1000
OUTPUT_FRAME_BYTES = OUTPUT_SAMPLES * 2
MAX_OPUS_PACKET = 4096


class OpusError(RuntimeError):
    pass


def _library():
    path = ctypes.util.find_library("opus")
    if not path:
        raise OpusError("libopus is missing; install the system libopus package")
    lib = ctypes.CDLL(path)
    lib.opus_decoder_create.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    lib.opus_decoder_create.restype = ctypes.c_void_p
    lib.opus_decoder_destroy.argtypes = [ctypes.c_void_p]
    lib.opus_decode.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32,
                                ctypes.POINTER(ctypes.c_int16), ctypes.c_int, ctypes.c_int]
    lib.opus_decode.restype = ctypes.c_int
    lib.opus_encoder_create.argtypes = [ctypes.c_int32, ctypes.c_int, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_int)]
    lib.opus_encoder_create.restype = ctypes.c_void_p
    lib.opus_encoder_destroy.argtypes = [ctypes.c_void_p]
    lib.opus_encode.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int16), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32]
    lib.opus_encode.restype = ctypes.c_int
    return lib


class OpusDecoder:
    def __init__(self):
        self.lib = _library()
        error = ctypes.c_int()
        self.handle = self.lib.opus_decoder_create(INPUT_RATE, 1, ctypes.byref(error))
        if not self.handle or error.value != 0:
            raise OpusError(f"opus_decoder_create failed: {error.value}")

    def decode(self, packet: bytes) -> bytes:
        if not packet or len(packet) > MAX_OPUS_PACKET:
            raise OpusError("invalid Opus packet length")
        encoded = (ctypes.c_ubyte * len(packet)).from_buffer_copy(packet)
        output = (ctypes.c_int16 * (INPUT_RATE * 120 // 1000))()
        count = self.lib.opus_decode(self.handle, encoded, len(packet), output, len(output), 0)
        if count < 0:
            raise OpusError(f"opus_decode failed: {count}")
        return ctypes.string_at(output, count * 2)

    def close(self):
        if self.handle:
            self.lib.opus_decoder_destroy(self.handle)
            self.handle = None


class OpusEncoder:
    def __init__(self):
        self.lib = _library()
        error = ctypes.c_int()
        # OPUS_APPLICATION_VOIP = 2048.
        self.handle = self.lib.opus_encoder_create(OUTPUT_RATE, 1, 2048, ctypes.byref(error))
        if not self.handle or error.value != 0:
            raise OpusError(f"opus_encoder_create failed: {error.value}")

    def encode(self, pcm: bytes) -> bytes:
        if len(pcm) != OUTPUT_FRAME_BYTES:
            raise ValueError(f"expected {OUTPUT_FRAME_BYTES} PCM bytes")
        samples = (ctypes.c_int16 * OUTPUT_SAMPLES).from_buffer_copy(pcm)
        output = (ctypes.c_ubyte * MAX_OPUS_PACKET)()
        count = self.lib.opus_encode(self.handle, samples, OUTPUT_SAMPLES, output, len(output))
        if count < 0:
            raise OpusError(f"opus_encode failed: {count}")
        return bytes(output[:count])

    def close(self):
        if self.handle:
            self.lib.opus_encoder_destroy(self.handle)
            self.handle = None


def upsample_16_to_24(pcm: bytes) -> bytes:
    """Convert signed little-endian mono PCM with linear interpolation.

    Each 60 ms A1 frame has exactly 960 samples, so the 3:2 ratio is exact
    without a carry buffer. The final interpolated point holds the last input
    sample until the next frame.
    """
    if len(pcm) % 2:
        raise ValueError("PCM16 data must have an even byte count")
    samples = array("h")
    samples.frombytes(pcm)
    if sys.byteorder != "little":
        samples.byteswap()
    if not samples:
        return b""
    output = array("h")
    for pos in range(len(samples) * 3 // 2):
        index, remainder = divmod(pos * 2, 3)
        first = samples[index]
        second = samples[min(index + 1, len(samples) - 1)]
        output.append((first * (3 - remainder) + second * remainder) // 3)
    if sys.byteorder != "little":
        output.byteswap()
    return output.tobytes()
