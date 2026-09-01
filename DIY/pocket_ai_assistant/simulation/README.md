# Partial Wokwi fixture

This fixture represents only the corrected ESP32-C3 display/action-button contract:

- SSD1306 on GPIO21 SDA / GPIO20 SCL;
- OLED deliberately set to `0x3d` to exercise the alternate-address probe; and
- active-low GPIO10 action button (`A` key in Wokwi).

It uses Wokwi's ESP32-C3 DevKitM model, not the mechanically different SuperMini. Wokwi does not prove the battery/holder/PTC/switch/regulator path, real INMP441 acoustics, MAX98357A bridge output, speaker enclosure, Wi-Fi performance inside brass, solder quality, or temperature. Those require lesson 6's physical tests.

In `diagram.json`, the DevKitM model names GPIO20/21 `RX`/`TX`; these are connected to SCL/SDA respectively. The corrected firmware still addresses the GPIO numbers.

Validate the diagram without credentials:

```bash
wokwi-cli lint --warnings-as-errors simulation/diagram.json
```

To run the corrected source artifact after rebuilding it, export `WOKWI_CLI_TOKEN` in the same shell and point Wokwi CLI at the merged binary plus `firmware/.work/xiaozhi-esp32/build/xiaozhi.elf`. Do not store the token in this repository. The present Codex process has Wokwi CLI 0.26.1 but does not inherit that variable, so only linting was performed here.
