# 5 — White, silver, and black finish

The coherent palette is **satin-white main tube and guards (about 45%)**,
**bare/satin-silver braces and hardware (about 35%)**, and **black face,
controls, mesh, and boards (about 20%)**. White OLED pixels tie the face back
to the structure. The finish must follow electrical/mechanical work, not hide
defects.

## Per-component treatment after dry-fit

| Part | Preferred native color | Safe treatment | Never coat/cover |
| --- | --- | --- | --- |
| 1.5 mm brass main tube | White | Fabricate and solder completely; clean/degrease; scuff; metal etch primer; thin satin-white coats. Test the complete system on scrap | Adhesive seats unless qualified for paint; clearance-critical surfaces |
| 1.0 mm nickel-silver braces | Silver | Leave bare and polish gently; if brass fallback is used, prime/paint satin silver after all soldering | Solder joints before fabrication is complete |
| OLED | White pixels, black PCB | Thin white PETG/ABS bezel; black removable edge tape/sleeve behind bezel | Glass, flex cable, components, connector, active pixels |
| ESP32-C3 | Black PCB | Leave native; hide wiring behind black nonconductive guard | Ceramic antenna and its keepout, USB, BOOT/RESET, LEDs needed for debug, pads |
| INMP441 | Black PCB | Black edge sleeve or guard; place behind a small black acoustic opening | Microphone port on either board face |
| MAX98357A/regulator/charger | Black if available | Removable black guard or loose sleeve with ventilation and labeled test access | ICs that dissipate heat, adjustment/configuration pads, USB, charger LEDs |
| Speaker | Silver/black native | Black acoustic cloth and a thin white/silver perimeter retainer | Diaphragm, sound port, moving surround |
| Protected 16340 + holder | Hidden | White fish-paper/polycarbonate holder guard and a black removable cell door | Cell wrapper, terminals, protection end, polarity marks, labels needed for inspection |
| Wires | Black secondary; white for regulated rail if labeled | Route in straight bundles; add tiny printed heat-shrink labels at ends | Do not rely on color alone for polarity |
| Switch/button | Black | Leave black actuator visible in a silver/white opening | Contacts, moving gap |

## Best finish sequence

1. Build and solder only the empty brass structure.
2. Dry-fit exact-size dummy modules, correct collisions, and deburr.
3. Clean all flux according to its data sheet; degrease without contaminating future joints.
4. Try the complete primer/paint/clear system on scrap brass. Bend and scratch-test after full cure.
5. Mask all planned glue/insulation seats and apply multiple thin coats outdoors/in a suitable spray area.
6. Let the coating fully cure—not merely feel dry.
7. Install nonconductive guards, then electronics; insert the removable protected cell last.

Bare nickel-silver rod gives the cleanest small silver accent. If it is unavailable, satin-silver paint on the empty brass fallback is predictable. Hand-tinning a large visible member is hard to make uniform and adds heat/flux; nickel/chrome electroplating is a specialist alternative completed before electronics.

## RF and heat cautions

Avoid conductive paint, metallic foil, metal-filled putty, or a closed metal cover near the ESP32 antenna. Ordinary satin-silver paint may contain metallic pigment; keep it out of the antenna keepout and validate Wi-Fi range with the finished frame. Do not wrap the regulator/amplifier tightly in heat-shrink. Use a removable black guard with air space instead.
