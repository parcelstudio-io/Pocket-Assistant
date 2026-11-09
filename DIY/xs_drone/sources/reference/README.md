# Creator reference files

These four files were downloaded from Max Imagination's public ESP-FLY project folder, linked by [the creator's project article](https://www.elektormagazine.com/labs/esp-fly-the-smallest-esp32-drone-you-can-build). They retain the creator's attribution. Acquisition links, versions and SHA-256 hashes are recorded in [evidence.json](../evidence.json).

The schematic image was visually inspected; its GPIO assignments were compared with the supplied ESP-FLY firmware. The brushed wiring diagram shows the modular construction alternative. The retail kit instead includes an assembled board containing the IMU and motor drivers; do not buy a second IMU because it appears in that diagram.

The Gerber archive is historical revision `331d8f50`, exported 2025-02-07. The BOM filename indicates a later 2025-03-29 revision, and the schematic is labelled up to date without an unambiguous matching Gerber revision. These files are not proof of the current retail kit's exact PCB revision. A buyer must resolve revisions before ordering replacement PCBs.

The electronics are publicly accessible, but this research did not find a complete explicit hardware redistribution license. Retaining files locally for this requested design review does not grant a right to republish them under this project's own license. No paid frame STL was acquired or reproduced.

Run `python3 tests/verify_gerber.py` from the project root to validate downloaded hashes and independently extract the historical PCB envelope/header drilling. Those tests do not perform PCB design-rule checks, electrical simulation or hardware testing.
