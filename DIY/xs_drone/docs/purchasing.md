# Purchasing and materials assessment

Research checked 2026-10-01. USD is the planning currency; shipping destination is assumed to be the US. Prices below are public listing snapshots, before shipping, tax, import fees, and regional battery-shipping restrictions. No checkout, purchase, or physical inspection was performed. “In stock” means the seller's page reported it during research; it does not guarantee availability at checkout.

The recommended first hardware purchase is the **[Seeed ESP-FLY kit, SKU 114993694, $59.99](https://www.seeedstudio.com/ESP-FLY-co-create-p-6744.html)**. The manufacturer's page reported in stock. This is a newer design from Max Imagination using Wi-Fi and a matched propulsion/electronics set. It is a purposeful revision of the linked Arduino drone, not an assertion that the two aircraft are identical. Assemble the stock kit to establish a working reference before changing its frame.

The full machine-readable materials list is [hardware/bom.csv](../hardware/bom.csv). Rows K02–K10 itemize the contents of K01 and are not additional purchases. Rows beginning X are rejected or unapproved comparison parts, not items to order. Optional tools, spare kits, fabrication services, and prototype filament are separate from the base subtotal.

## Included aircraft components

| Component | Quantity received | Interface / size | Purchasing implication |
|---|---:|---|---|
| Standard XIAO ESP32-S3 and antenna | 1 each | USB-C; 2.4 GHz | No separate Arduino, FTDI programmer, or nRF24 radio |
| Assembled IMU/motor-driver board | 1 | MPU6050; four SI2300 motor switches | Do not replace with a generic sensor breakout |
| Matched 615 brushed motors | 4 | 6 × 15 mm cans; 2 CW + 2 CCW | Receive the kit's actual winding specification |
| Matched three-blade props | 8 | 30 mm; 4 CW + 4 CCW | One installed set plus one spare set |
| High-discharge LiPo | 1 | 1S, 250 mAh | Inspect connector, polarity, label, envelope, and mass |
| Printed parts | 1 set | Frame; standard and FPV covers | Use standard cover for initial build |
| Assembly hardware | 1 set | 24 AWG wire, tie, landing wires | Solder, glue, and tools are additional |

Inventory source: [official ESP-FLY repository](https://github.com/Seeed-Projects/Co-Create_ESP-FLY). The creator specifies a 0.8 mm propeller bore/shaft and recommends a high-discharge battery; see the [creator's assembly article](https://www.elektormagazine.com/labs/esp-fly-the-smallest-esp32-drone-you-can-build). These are documentary specifications. Each delivered component still needs incoming inspection.

## Tools and consumables with actual purchase links

Buy only what is missing from your bench. Every priced row in this table showed in stock on its linked listing during research.

| Item | Listed price | Why it is required |
|---|---:|---|
| [USB-A to USB-C data cable](https://www.adafruit.com/product/4474) | $4.95 | Firmware upload and onboard charging; choose a C-to-C data cable instead if your computer has only USB-C |
| [Adjustable 60 W iron, US 120 V](https://www.adafruit.com/product/3685) | $19.95 | Motor and power lead soldering |
| [Iron stand](https://www.adafruit.com/product/150) | $10.95 | For the separate pen-style iron |
| [Lead-free SAC305 rosin-core solder](https://www.adafruit.com/product/734) | $29.95 | Listed spool is much more than one aircraft consumes |
| [Flush cutters](https://www.adafruit.com/product/152) | $7.25 | Trim wire and cable tie |
| [22–30 AWG wire stripper](https://www.adafruit.com/product/147) | $6.95 | Includes the kit's 24 AWG wire size |
| [Fine plastic-point tweezers](https://www.adafruit.com/product/5916) | $2.50 | Place small parts; keep plastic tips away from the iron |
| [SparkFun basic multimeter](https://www.sparkfun.com/digital-multimeter-basic.html) | $21.50 | Continuity, battery polarity, DC rail voltage |
| [150 mm digital calipers](https://www.sparkfun.com/6-digital-calipers.html) | $19.95 | Check motor cans, board envelope, battery, printed fits |
| [AWS PowerBank100 scale, calibration weight included](https://awscales.com/powerbank100g-rechargeable-digital-pocket-scale/) | $20.00 sale | 100 g capacity, 0.01 g readability; verify all-up mass |
| [Chip Quik no-clean flux pen](https://www.adafruit.com/product/3468) | $7.95 | Improve wetting on small joints and rework |
| [10 mm polyimide tape](https://www.adafruit.com/product/3057) | $4.95 | Thin insulation where required |

Caliper resolution is not accuracy: the seller specifies ±0.02 mm below 100 mm. Scale readability likewise is not a guarantee of 0.01 g absolute accuracy. Check zero and the supplied calibration weight, repeat measurements, and use realistic reporting precision. A kitchen scale with 1 g increments is inadequate for a roughly 25 g drone's component mass accounting.

Add a hobby knife, a small amount of compatible CA adhesive, a way to hold the board, and ordinary bench eye protection/ventilation. Existing equipment is fine; allocate **$10–20 as an unquoted shop-supply estimate**. Do not buy the [Adafruit complete toolkit](https://www.adafruit.com/product/136) expecting immediate availability: the directly checked page was out of stock, as were its separately listed 9205B+ multimeter and 0.5 mm leaded solder. This is why the available individual alternatives above were chosen.

## Budget that does not hide tools

| Scenario | Subtotal | Exclusions |
|---|---:|---|
| Aircraft kit only | $59.99 | Cable and all bench equipment |
| Kit + data cable | $64.94 | Assumes all tools already owned |
| Kit + every item in the tools table | **$216.84** | Shop extras, tax, shipping, verification instruments, printing |
| Above + prototype filament spool below | $246.83 | Printer ownership or print-service fees |
| Optional second matching kit | +$59.99 | Spare donor parts; not necessary for first assembly |

Allow about **$230–270 before tax and shipping** if starting with no ordinary soldering/measurement equipment and using the included frame. This range is a planning allowance, not a seller quote. A custom-frame iteration adds printer access and failed-print allowance. Serious electrical characterization also needs a current-limited supply and an oscilloscope; borrowing a maker-space or lab bench is more economical than pretending those instruments are included in a $60 drone budget.

## Materials for designing and printing the frame

The included frame provides the baseline. For fit coupons and initial frame prototypes, an actually listed option is [Prusament PLA Galaxy Black 1 kg, $29.99](https://www.prusa3d.com/product/prusament-pla-prusa-galaxy-black-1kg/), which reported in stock. Use the material assumptions in the frame design documents, not the seller's marketing claims as structural acceptance evidence. Record the exact filament brand, material, nozzle, layer height, wall count, and final mass for every revision.

One small frame uses only a few grams, so the filament consumed costs cents; buying a full spool costs dollars. A local print service's minimum charge dominates a single order. Allocate **$10–30 per small outsourced prototype as an estimate**, then get an actual quote from its exported STL. No printer purchase is necessary for the first stock-kit assembly.

Thin insulating tape and the supplied battery tie are enough to start. Do not add generic M3 hardware, a heavy perfboard, a large battery cradle, a metal canopy, or thick hot-glue blobs without updating the mass budget. Battery dimensions and connector exit direction determine the tray; a capacity label does not. Motor holders must match the delivered cans and the printer's fit coupon. Printed PLA can crack or soften near a hot motor, so retention and temperature are physical tests, not properties proved by a drawing.

The independent custom frame additionally needs thin insulating spacer pads plus soft retaining thread or elastic. In the initial CAD, supports reach Z = 1.7 mm and the provisional electronics start at Z = 2.2 mm: the **0.5 mm gap must be filled by a measured spacer/adhesive system**, not left as an imagined attachment. Keep the battery restraint away from sharp edges. The 6.2 mm nominal motor bore around a 6.0 mm motor is a clearance fit; select the coupon fit and a tested retaining method before installing flight motors. Neither the unmodeled retainers nor their mass is validated by the bare frame's volume calculation.

For bench verification, provide a current-limited supply capable of regulated 3.0–4.2 V, appropriate current capacity for the specific test, and a scope with at least two channels and 10× probes. Allocate **$80–200 for a supply and $150–400 for an entry-level scope if buying**, explicitly unquoted estimates. These are workshop assets. They do not fly. Use a calibrated, rigid single-motor thrust fixture with the 30 mm disk unobstructed; the pocket scale alone does not make a validated thrust stand. Fixture weight plus measured force must remain within scale capacity.

## Compatibility decisions and rejected substitutions

| Candidate or change | Assessment | Reason / evidence |
|---|---|---|
| Standard XIAO ESP32-S3 | Baseline | Manufacturer board envelope is 21 × 17.8 mm; see [Seeed wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) |
| XIAO ESP32-S3 Sense or Plus | Not a silent substitution | Sense adds camera hardware; Plus differs in flash and board details. Recheck firmware target, power, stack height, and pin use |
| 6 × 14 motor from the old video | Not equivalent to kit 615 | Different can length, winding, bearing/shaft details, and loaded performance. Similar appearance does not establish thrust |
| Arbitrary “615 70,000 rpm” motor | Unapproved spare | RPM without specified voltage and loaded propeller current/thrust is insufficient |
| 31 mm 0.8 mm prop | Requires characterization | Bore fits nominally but blade count, pitch, hub length, load and clearance can change |
| 1 mm prop bore on 0.8 mm shaft | Reject | Loose press fit; adhesive is not a validated rotor hub |
| Large 716 motor and 40 mm prop | Separate airframe | Requires different mounts, spacing, current capacity, mass budget and tuning |
| Generic 250 mAh electronics LiPo | Reject unless rated and tested | Many low-drain cells cannot supply propulsion current and may have a current-limiting protection board |
| 2S battery | Reject | Overvoltage for the selected 1S motors and power design |
| ESP32 add-on board stacked on original Arduino | Poor baseline choice | Extra MCU, regulator, antenna and interconnect mass; a separate integration project |

The old video's [DFRobot 6 × 14 mm motor family, FIT0792](https://www.dfrobot.com/product-2308.html), is a concrete example of why listings need checking. The page showed **$7.20 for four and out of stock**, with 0.8 mm shaft diameter and 4.2 mm shaft length. Its 40 mA current number is not a motor/prop loaded-current curve and must not be used to size the aircraft battery. No verified thrust curve or stock was established for that replica combination. The actual SKU is FIT0792, not FIT0772.

An [Arduino Pro Mini 3.3 V/8 MHz, $11.25](https://www.sparkfun.com/arduino-pro-mini-328-3-3v-8mhz.html) was available, but buying it would not resolve the old build's firmware timing, electrical power, propulsion, and missing-parts questions. A 5 V/16 MHz listing and a 3.3 V/8 MHz listing represent different configurations. The Wi-Fi kit does not use either one. The original-video component list is therefore a research reference, not a fully approved shopping cart.

## Battery, spare-parts, and charging audit

The primary kit includes a 1S 250 mAh battery and advertises a PH 2-pin connection. Inspect the delivered label for the intended high-discharge rating, and verify actual positive and negative pins with the meter. Connector shells that mate can still have reversed polarity. Take cell dimensions without compressing the pouch and include the lead exit and strain relief in the fit check.

The creator's older [Seeed Crazyflie spare battery link](https://www.seeedstudio.com/Crazyflie-Nano-Quadcopter-Spare-battery-BC-BL-01-p-1362.html) is **out of stock and discontinued**. The newer [Bitcraze 250 mAh battery datasheet](https://www.bitcraze.io/documentation/hardware/250mah_battery/250mah_battery-datasheet.pdf) specifies **20 × 7 × 30 mm, 7.1 g, 15C discharge, and Molex 51005-2P, pin 1 positive**. That is not proof of compatibility with the ESP-FLY kit's PH connector or its recommended ≥25C cell. At 250 mAh, 15C means 3.75 A nominal rated discharge, while 25C means 6.25 A. Actual voltage sag and temperature still need measurement. Do not order this newer Crazyflie cell as a verified plug-in spare.

No separately listed, currently available, exact kit motor/propeller/battery/FC replacement set was verified. The supplied eight props cover one spare set; buying a second identical kit is an optional, expensive donor-parts route. For a later cell substitution, require all of: 1S 4.2 V chemistry; actual connector and polarity; discharge capability; allowed charge current; envelope; mass; lead routing; measured voltage sag; and retention without squeezing the pouch. “250 mAh” alone checks only one field.

**The battery's C rating does not rate the connector or PCB.** The creator's BOM specifies `S2B-PH-K-S(LF)(SN)`. [JST's PH datasheet](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf) specifies **2 A with 24 AWG wire**, not 6.25 A. The cell's nominal 25C calculation therefore does not approve a 6.25 A flight power path. Establish actual connector identity and total sustained current; remain within its rating or redesign and requalify the complete mating pair and power path. A higher-rated battery alone cannot fix this. For illustration, a 20 mΩ total connection resistance drops 0.12 V and dissipates 0.72 W at 6 A; real harness resistance must be measured rather than assumed.

The historical PCB also lists `1N4148WS-7-F` motor flyback diodes. The [Diodes Incorporated datasheet](https://www.diodes.com/datasheet/download/1N4148WS.pdf) gives 150 mA average rectified current, 300 mA continuous forward current and a 4 A **non-repetitive 1 µs** surge rating. That pulse rating does not qualify repetitive motor PWM. Measure or conservatively establish freewheel current, switching waveform and device temperature; motor inductance, speed and PWM duty change the stress. The BOM's `KSI2300DS-T1-GE3` is a [KUU part](https://www.lcsc.com/zh-TW/product-detail/C2891684.html), not automatically the Vishay `SI2300DS-T1-GE3` with a similar name. Exact fitted parts and copper layout govern electrical limits.

The [XIAO manufacturer wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) documents onboard USB charging and lists 50 mA fast-charge current for the standard S3. Consequently, a fully depleted 250 mAh cell requires **5 hours by ideal capacity/current arithmetic plus charge taper**, not a claimed half-hour charge. This is an estimate; measure the delivered board revision. Charge only with motor operation disabled, propellers removed for initial checks, and supervision. Do not assume the cross-sold Crazyflie 500 mA charger is compatible: connector, polarity, and allowed cell charge rate all require confirmation.

## Optional analog FPV procurement, after flight acceptance

An actual camera candidate is the [AKK F11 camera/VTX combo](https://www.akktek.com/f11-fpv-camera-vtx-combo.html), listed at **$23.99**. The manufacturer's indexed page states in stock, but direct access returned HTTP 403 during this check, so present stock is less firmly established than the main kit. The same page announces destination/export restrictions; delivery eligibility must be confirmed for the actual shipping address. Its listed footprint is **14 × 12 mm**, input is **3.3–5.5 V**, and mass is **3 g excluding the antenna**; height is not published. The listed current is **330 mA at 25 mW** and **1550 mA at 200 mW**. These are source claims, not measurements. Leave 200 mW disabled for this candidate build.

This camera is **not yet approved for the stock cover or custom frame**. Antenna, leads, adhesive and mounting add to its 3 g bare mass, so it cannot be assumed to satisfy a 3 g total FPV allowance or the kit's advertised 28 g FPV all-up figure. A direct 1S feed can fall below the camera's 3.3 V minimum during motor load, even while the cell has usable capacity. Verify minimum voltage at its pads, image continuity and electromagnetic interference throughout a discharge. Power it from the suitable battery distribution path, not an assumed spare 330 mA on the XIAO 3.3 V rail. Mount and lens sightline require actual height measurements. Attach its antenna before powering the transmitter.

A currently listed complete receiver option is [Pyrodrone's EV800D 40-channel analog goggles, SKU W4-10552](https://pyrodrone.com/collections/fpv-goggles/products/ev800d-5-8ghz-40ch-diversity-fpv-800-480-goggles-with-dvr), **$194.99**, in stock on both the page and its public product availability data. The listing includes a battery, charger and antennas. This is a concrete available option, not a claim that $195 is a bargain. The frequently suggested [BETAFPV VR04 analog goggles](https://betafpv.com/products/vr04-fpv-goggles) were $74.99 but sold out; the similarly named VR04 **HD** is a different digital system and does not replace an analog receiver.

F11 plus the available EV800D totals **$218.98 before tax/shipping**, excluding camera-mount development. Set the camera and goggles to the same supported **frequency in MHz**, not merely the same displayed channel number; band numbering can differ. A compatible picture test proves video reception only, not flight control, latency, RF compliance, payload margin or aircraft acceptance. Leave this entire optional branch out of the first flight build and out of the $216.84 baseline subtotal.

## Incoming inspection before irreversible assembly

1. Photograph the kit label and all components. Inventory four motors with two directions each, eight matching props, battery, both boards, antenna, and frame parts.
2. Measure each motor diameter and can length, prop diameter, shaft diameter, PCB/stack envelopes, and battery dimensions. Add the measured values to the project acceptance record before finalizing a replacement frame.
3. Weigh separate groups and the complete dry assembly. Do not treat a vendor's 25 g complete-aircraft figure as your measured mass.
4. Check battery chemistry, full-charge limit, rating, connector pitch, polarity and no visible cell damage. Stop if the supplied part differs materially from the intended specification.
5. Dry-fit motors and boards with no propellers installed. Verify that motor wires will not cross a prop disk and that antenna and USB access remain clear.
6. Build and pass the stock-geometry acceptance sequence before changing material, frame spacing, motors, propellers, cell or firmware. This preserves a useful comparison when diagnosing the custom version.

No physical compatibility or flight test is recorded as passed by this purchasing research. Product listings and source documentation establish a practical procurement path; the project verification plan establishes the tests still needed on the actual aircraft.
