# Bill of materials and US purchase links

Prices and stock notes were checked **2026-09-23**, before tax and shipping. Distributor inventory moves quickly; verify stock and price in the cart. The machine-readable version is in [`bom/bom.csv`](../bom/bom.csv), whose order-code column holds the vendor part numbers; the parts actually bought, with dates, are in [`ORDER_SHEET.md`](ORDER_SHEET.md) and [`INVENTORY.md`](INVENTORY.md). Each part below is named by what it is and linked to the exact product bought.

**Rev B 2026-10-31: solar removed, compact body, 16340 cell.** Every part below is owned; the purchase tables are kept as the September reasoning and each row now carries its status. The battery is one Nitecore 16340 cell in the owned [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) on an owned JST-PH pigtail, through the [fuel gauge](https://www.adafruit.com/product/5580) into the [charger board](https://www.adafruit.com/product/6106)'s BAT port, charger jumper at 500 mA. The 5 W [solar panel](https://www.adafruit.com/product/5367), the [DC jack adapter](https://www.adafruit.com/product/4287), the [DC jack to screw terminals](https://www.adafruit.com/product/368), the [panel-mount USB-C extension](https://www.adafruit.com/product/6069), the 6600 mAh [battery](https://www.adafruit.com/product/353) and the 1200 mAh [battery](https://www.amazon.com/dp/B09G2S88Q3) are owned and not used in Rev B. The body is 82 × 52 × 68 mm ([`COMPACT_DESIGN.md`](COMPACT_DESIGN.md)); the only things left to buy or print are the acrylic face and the PETG shell.

## Purchase strategy

Do not buy everything at once.

1. **Bench order:** prove the display, the clock's alarm interrupt, local audio, and physical controls over USB.
2. **Battery order:** add one protected pack, one power-path charger, and the fuel gauge only after the peak-load test exists. *Done 2026-10-26; Rev B (2026-10-31) swaps the pack for one owned 16340 cell.*
3. **Solar order:** measure 24-hour energy first, then size the panel. The 5 W recommendation is a hypothesis to validate, not a guarantee. *Bought 2026-10-26, then removed from the design 2026-10-31; the parts are held for another project.*
4. **Mechanical order:** cut the final acrylic and brass only after RF, speaker, and thermal mockups. *Rev B: the 82 × 52 mm acrylic face is cut after the bench fit check in [`COMPACT_DESIGN.md`](COMPACT_DESIGN.md).*

## Core USB-powered prototype

| Qty | Part | US source | Checked price | Why this one |
|---:|---|---|---:|---|
| 1 | [Controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) | DigiKey | ≈$15.00 | 8 MB flash, 8 MB PSRAM, native USB, Wi-Fi/BLE, I2S |
| 1 | 2.42-inch 128×64 [OLED display](https://www.adafruit.com/product/2719) | Adafruit | $39.95 | Readable bedside size; framed module; use 4-wire SPI |
| 1 | [Real-time clock](https://www.adafruit.com/product/5188), STEMMA QT | Adafruit | $13.95 | Temperature-compensated time and hardware alarm interrupt |
| 1 | [Coin cell](https://www.amazon.com/dp/B0D8T4C5PK) | Amazon, 10-pack as bought; a [Panasonic single](https://www.digikey.com/en/products/detail/panasonic-energy/CR1220/269740) from DigiKey also works | ≈$1.13 (single) | Independent clock backup; non-rechargeable |
| 1 | I2S 3 W mono [amplifier](https://www.adafruit.com/product/3006) | Adafruit | $5.95 | Digital audio, no MCLK, shutdown control. The build uses the owned HiLetgo [amplifier](https://www.amazon.com/dp/B0CDWXZZCH) instead, same chip and pinout |
| 1 | 4 Ω / 3 W enclosed [mono speaker](https://www.adafruit.com/product/3351) | Adafruit | $3.95 | Enclosure is easier to tune than a bare micro-speaker. Out of stock on 2026-10-19, so the stereo [speaker](https://www.adafruit.com/product/1669) pair was bought instead |
| 1 | [Rotary encoder](https://www.adafruit.com/product/6310) with I2C adapter | Adafruit | $13.95 | Distinctive wheel plus five directional switches; interrupt output |
| 1 | 16 mm momentary [snooze button](https://www.adafruit.com/product/1505) | Adafruit | $0.95 | The big button on the lid (Rev B); the brass snooze rail is retired |
| 1 | Mini slide [arm switch](https://www.adafruit.com/product/805) | Adafruit | $0.95 | Alarm arm/disarm input; do not use as hard power. The build uses an owned Chanzon [slide switch](https://www.amazon.com/dp/B09R434VJQ) |
| 1 | Adafruit [proximity and light sensor](https://www.adafruit.com/product/4161) | Adafruit | $5.95 | Hand-wave display wake plus automatic contrast |
| 1 | [Accelerometer](https://www.adafruit.com/product/2809) | Adafruit | $4.95 | Low-power orientation/tap sensing for flip-to-focus |
| 1 | [Temperature and humidity sensor](https://www.adafruit.com/product/4566) | Adafruit | $4.50 | Low-cost room sensing; place away from heat sources |
| 1 | Half-size [solder-in proto board](https://www.adafruit.com/product/1609) | Adafruit | $4.50 | More robust than a solderless breadboard for alarm testing. Dropped 2026-10-19: the owned breadboards carry Phase 1 |
| 4 | 100 mm [QT cable](https://www.adafruit.com/product/4210) | Adafruit | $0.95 ea. | Clock and sensor bus |
| 1 lot | Passives, MOSFET, headers, insulated wire, heat-shrink | [DigiKey prototyping supplies](https://www.digikey.com/en/products/filter/prototyping-fabrication-products/636) | ≈$12 allowance | Decoupling, pull-ups, optional buzzer switch, safe wiring |

Approximate core-electronics subtotal: **$131.48**. Shipping, tax, tools, and enclosure stock are excluded. All of it is owned (Adafruit 2026-10-19, DigiKey 2026-10-28, Amazon 2026-10-26); see `ORDER_SHEET.md`.

## Battery-ready additions (Rev B: one 16340 cell)

| Qty | Part | US source | Checked price | Notes |
|---:|---|---|---:|---|
| 1 | USB/DC/solar [charger board](https://www.adafruit.com/product/6106) with 5 V boost | Adafruit | $8.95 | **Owned**, in Rev B. 5 V / 1 A output and power path; its own USB-C port is the charging port, through the rear panel; solar input left empty; jumper cut to 500 mA (ships closed at 1 A) |
| 1 | [Fuel gauge](https://www.adafruit.com/product/5580) | Adafruit | $5.95 | **Owned**, in Rev B. On the battery lead between the holder and the charger's BAT port |
| 1 | Nitecore 16340 cell, 3.6 V 950 mAh, protected | owned ×6 from the Pocket AI build | not recorded | **Owned**, in Rev B: the battery. 2 A discharge limit, 4.20 V termination; about 3.4 Wh, roughly 10 h with the face lit |
| 1 | [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | Amazon, 10-pack 2026-10-27 | not recorded | **Owned**, in Rev B. 43 × 18 × 14 mm; meter the leads for polarity before the cell goes in |
| 1 | JST-PH 2.0 mm pigtail pair | Amazon, 20-pair set 2026-09-02 (listing not re-linked) | not recorded | **Owned**, in Rev B. Holder leads to the fuel gauge's plug; meter polarity, not wire colour |
| 1 | Protected 3.7 V [6600 mAh battery](https://www.adafruit.com/product/353) | Adafruit | $24.50 | **Owned, not used in Rev B.** 24.4 Wh nominal; too large for the compact body and never suited the charger's 6 h timer on USB |
| 1 | Protected 3.7 V 1200 mAh [battery](https://www.amazon.com/dp/B09G2S88Q3) | Amazon | not recorded | **Owned, not used in Rev B.** Was the Phase 4 bench pack |
| 1 | [Panel-mount USB-C extension](https://www.adafruit.com/product/6069) | Adafruit | $4.50 | **Owned, not used in Rev B.** The charger board's own port reaches the rear panel |

Battery-ready electronics total: approximately **$175.38** including the core order, as first costed with the 6600 mAh pack; the Rev B cell, holder and pigtail were already owned.

The charger board's six-hour safety timer and weak-source startup behavior were a concern with the large pack (superseded: 950 mAh at 500 mA terminates in about 3 h). A production design should use one integrated PMIC topology, battery-temperature sensing, and an explicit power mux/backfeed solution.

## Solar additions (owned, not used in Rev B)

Solar was removed from the design on 2026-10-31. The parts below were bought 2026-10-26 and are held for another project; nothing is wired to the charger board's solar input.

| Qty | Part | US source | Checked price | Notes |
|---:|---|---|---:|---|
| 1 | 5 W / nominal 6 V ETFE [solar panel](https://www.adafruit.com/product/5367) | Adafruit (bought 2026-10-26); the same panel from [Voltaic direct](https://voltaicsystems.com/5-watt-panel-etfe/) at $35.00 | $34.95 | **Owned, not used in Rev B.** 148 × 223 × 4 mm; around 6.12 V / 940 mA at rated peak |
| 1 | Voltaic barrel-to-bare-wire [panel lead](https://voltaicsystems.com/W045/) | Voltaic Systems | $3.50 | Not bought. Bought instead: the [DC jack adapter](https://www.adafruit.com/product/4287) plus [DC jack to screw terminals](https://www.adafruit.com/product/368), both **owned, not used in Rev B**; see `ORDER_SHEET.md` |

Electronics plus the 5 W solar package: approximately **$213.88**, before mechanical materials, tools, tax, or shipping (history; the solar package is held stock in Rev B).

The 2 W [solar panel](https://www.adafruit.com/product/5366) is useful for charging experiments but is too marginal for a dependable always-on clock. The [10 W Voltaic panel](https://voltaicsystems.com/10-watt-panel-etfe/) provides better seasonal margin if measurements show more than about 10 Wh/day.

## Mechanical materials

Exact cost depends on local fabrication, so these are not included in the electronic subtotal.

| Material | Suggested US source | Specification / note |
|---|---|---|
| Bare copper sculpture wire | [WesBell 20 AWG solid bare copper](https://wesbellwireandcable.com/products/electrical-wire/bare-copper-cable/solid-bare-copper-20/) | 20 AWG is about 0.8 mm; decoration/structure only |
| Round [brass tube set](https://www.amazon.com/dp/B0F2FKLC2N) | Amazon, M METERXITY; [K&S round brass tubing](https://ksmetals.com/collections/round-brass-tubing) is the hobby-shop alternative | **Owned** (bought 2026-10-26: the 2–7 mm OD × 0.5 mm wall set, one tube per size; see `INVENTORY.md`). Rev B uses about 300 mm of the 3 mm tube for two U cradles under the body; the exoskeleton and snooze rail are retired |
| Smoked/dark-gray acrylic | [SendCutSend acrylic](https://sendcutsend.com/materials/acrylic/) | **To buy.** 3 mm, one piece 82 × 52 mm, the whole face (Rev B); cut after the bench fit check in [`COMPACT_DESIGN.md`](COMPACT_DESIGN.md) |
| Black PETG/ASA | [Printed Solid PETG](https://www.printedsolid.com/collections/1-75mm-petg?page=2) | **To print.** The 82 × 52 × 68 mm body, lid and rear panel with 2 mm walls; use existing filament if available |
| [M3 heat-set inserts](https://www.mcmaster.com/94459A130/) | McMaster-Carr | Serviceable housing joints |
| [M3 low-profile screws](https://www.mcmaster.com/92855A309/) | McMaster-Carr | Match length to CAD stack-up |
| Closed-cell foam / gasket | [McMaster-Carr foam tape](https://www.mcmaster.com/products/foam-tape/) | Speaker seal, rattle control, acrylic isolation |

Budget roughly **$40–60** for small-quantity frame, acrylic, printed parts, fasteners, and consumables. A complete solar prototype was costed at **$255–275** before tools and freight; in Rev B the remaining spend is the acrylic face and any filament.

## Alternatives and upgrades

| Need | Alternative | Price/status at check | Tradeoff |
|---|---|---:|---|
| Conventional Bluetooth music streaming | Adafruit [Wi-Fi and Bluetooth Feather board](https://www.adafruit.com/product/5400) | $19.95, in stock | Classic BT/A2DP, but separate firmware/power branch; alarm must preempt streaming |
| Lower-cost input | Plain [rotary encoder](https://www.adafruit.com/product/377) with push | $4.50, in stock | Saves about $9.45 and I2C complexity; less distinctive interaction |
| Wide OLED | Newhaven 3.12-inch 256×64 [wide OLED display](https://www.mouser.com/ProductDetail/Newhaven-Display/NHD-3.12-25664UMB3) | ≈$40.06 | Excellent panoramic UI; higher current and more difficult integration |
| True CO2 | Sensirion [CO2 sensor](https://www.adafruit.com/product/5190) breakout | $49.95, in stock | Direct photoacoustic CO2 rather than an estimated eCO2; cost and energy increase |
| Larger acoustic driver | PUI [40 mm speaker](https://www.digikey.com/en/products/detail/pui-audio-inc/AS04004MR-F-WP-R/17051383), 4 Ω / 3 W | ≈$10.41 | Better product-grade driver; needs a designed chamber |
| Robust large-pack solar path | [Large-pack solar charger](https://www.adafruit.com/product/4755) + SparkFun [boost board](https://www.sparkfun.com/lipower-boost-converter.html) | $14.95 + $17.50 | More parts/cost, but avoids relying on the charger board's fixed safety timeout |

## Tools not included

Soldering iron and lead-free or leaded electronics solder as locally appropriate, flux, fume extraction, multimeter, current/power logger, USB power meter, oscilloscope for peak-load diagnosis, wire cutters/strippers, calipers, bending jig, eye protection, and access to a 3D printer or fabrication service.
