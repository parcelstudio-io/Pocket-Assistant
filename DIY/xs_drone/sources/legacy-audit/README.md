# Original Arduino firmware audit fixtures

These two files are an incomplete evidence snapshot used to reproduce the original receiver's full-throttle radio-loss defect. They are not a buildable firmware project and must not be flashed to a drone. Use the recommended ESP-FLY workflow in [the firmware instructions](../../firmware/README.md).

The source was retrieved from the creator's public [MultiWii RF24 folder](https://drive.google.com/drive/folders/1RpVh6NTzbtIL2lJVP0EqVGJy4QKX_Syh), within the [MultiWii NRF24 Brushed Drone V5 Code folder](https://drive.google.com/drive/folders/1Wa6SFih_hcIrxEzUuxwNU-PlUgMRvL15), on 1 October 2026. Individual records are [NRF24_RX.cpp](https://drive.google.com/file/d/1UU3dsAgjY_X1gx3jyX_8TkapLi_5Tzje/view) and [config.h](https://drive.google.com/file/d/1gjLKzkfWdR2RV0Ux_f0AUZh1YKsQZNNV/view).

The upstream project credits Alexandre Dubus and the MultiWii contributors; the sketch credits iforced2D and ELECTRONOOBS, with an ELECTRONOOBS modification dated 11 April 2020. The accompanying upstream `MultiWii.cpp` identifies MultiWii version 2.3 from November 2013 and grants redistribution/modification under GNU GPL version 3 or later. These source excerpts retain their original authorship; the full GPL text is supplied as [COPYING](COPYING). The public Drive snapshot is the source of this audit, rather than a claim that any named contributor authored the defect.

The saved fixtures normalize CRLF line endings to LF and remove surplus trailing blank lines. Program statements and configuration content were not repaired. Downloaded and local byte hashes are recorded separately:

| File | Downloaded SHA256 | Saved fixture SHA256 |
|---|---|---|
| NRF24_RX.cpp | `e60ce122795fd2d709c9a46cf87366ad296d76254d53ff0ac65c9b0a92f3280f` | `6cfd245942125ba3329faee32dc00c6f89b9ddd0a126926aa127a86dfd72d8d8` |
| config.h | `c7c81ce3909f1f708425d31608584bc845bef759d1ea9424da95e61c28b4431f` | `e6ee0d1873d903acf6093da50186b49ccc9f15000e8aa54a60723a1adb4cef44` |

To repeat the receiver defect test after preparing the ESP-FLY source:

```bash
python3 tests/firmware_audit.py \
  --esp-source firmware/.work/esp-fly \
  --original-source sources/legacy-audit
```

Four assertions reproduce startup/reset mapping to 2000, a valid low-throttle packet mapping to 1000, retention at the exact 1000 ms boundary, and the incorrect change to 2000 after that boundary. Passing those assertions confirms the bug exists. See [the complete audit](../../docs/firmware-audit.md) for its implications while armed.
