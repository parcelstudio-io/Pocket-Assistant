# Solar and battery feasibility

> **Superseded 2026-10-31 (Rev B).** Solar is removed from the Cyber Dawn design: the clock charges
> over USB-C through the [charger board](https://www.adafruit.com/product/6106)'s own port and runs on
> one Nitecore 16340 cell between unplugs. The 5 W [solar panel](https://www.adafruit.com/product/5367),
> the [DC jack adapter](https://www.adafruit.com/product/4287) and the
> [DC jack to screw terminals](https://www.adafruit.com/product/368) are kept as owned stock for another
> project; nothing solar is wired and the charger's solar input stays empty. The decisions are in
> [COMPACT_DESIGN.md](COMPACT_DESIGN.md). The analysis below is left intact as the record of why.

## Decision

Solar is feasible as a **detachable charging assist** and can approach energy neutrality in a good outdoor/window installation with eco firmware. It is not credible to promise continuous operation from a small panel mounted on a bedside clock under ordinary indoor illumination.

Recommended prototype:

- 5 W, nominal 6 V [solar panel](https://www.adafruit.com/product/5367) on a detachable cable
- Protected 1-cell 6600 mAh LiPo
- [Solar charger board](https://www.adafruit.com/product/6106) with 5 V boost for the controller-board prototype
- [Fuel gauge](https://www.adafruit.com/product/5580)
- USB-C retained as the dependable primary and recovery source

Keep the clock and battery shaded indoors. Put only the panel in the sun-facing location.

## Transparent energy model

These are design estimates, not measurements. The first functional prototype must log its own energy for at least seven representative days.

| Mode | Average power assumption | Energy/day | What is enabled |
|---|---:|---:|---|
| Eco | 0.23 W | 5.5 Wh | OLED presence-blanked overnight, no seconds, BLE off, brief Wi-Fi sync, optional sensors mostly asleep |
| Balanced | 0.40 W | 9.6 Wh | OLED visible at adaptive contrast, periodic Wi-Fi, climate/presence sensing |
| Always connected | 0.55 W | 13.2 Wh | OLED continuously visible, frequent network activity, limited sleep |
| Ten-minute alarm event | — | add roughly 0.1–0.3 Wh | Practical speaker level with radio work suppressed |

The display is a meaningful base load. The [2.42-inch OLED listing](https://www.adafruit.com/product/2719) gives an average of about 50 mA at 3.3 V:

```text
OLED average power ≈ 3.3 V × 0.050 A = 0.165 W
OLED if continuously on ≈ 0.165 W × 24 h = 3.96 Wh/day
```

Actual OLED consumption depends heavily on how many pixels are illuminated. The black-background UI, no always-on seconds, lower night contrast, presence blanking, and scheduled display sleep improve both energy use and OLED life.

## Battery reserve

```text
6600 mAh × 3.7 V = 24.42 Wh nominal
delivered estimate = 24.42 Wh × 0.80 usable depth × 0.85 conversion = 16.61 Wh
```

| Mode | Estimated runtime from 6600 mAh |
|---|---:|
| Eco, 5.5 Wh/day | about 72 hours |
| Balanced, 9.6 Wh/day | about 42 hours |
| Always connected, 13.2 Wh/day | about 30 hours |

This is a reserve, not a week-long UPS. A 4400 mAh cell would deliver roughly 11 Wh by the same assumptions: around two eco days or about one balanced day.

The real-time clock's coin cell preserves time but cannot operate the controller or speaker. Firmware must reserve main-battery energy for the next alarm, yet it must also shut down safely before cell protection disconnects. No battery design can guarantee an audible alarm after its main cell is exhausted.

## Panel yield

For early sizing, use:

```text
daily harvested energy ≈ panel watts × peak-sun-hours × 0.60
```

The 0.60 factor is a conservative allowance for panel temperature, angle, charger/conversion loss, wiring, and imperfect tracking. It does not account for severe shade.

| Panel / sun case | Estimated harvested energy | Interpretation |
|---|---:|---|
| 2 W × 4 h × 0.60 | 4.8 Wh/day | Below even the eco budget; experiment/trickle only |
| 5 W × 2 h × 0.60 | 6.0 Wh/day | Barely covers eco mode; no recharge margin |
| 5 W × 4 h × 0.60 | 12.0 Wh/day | Can cover balanced mode on a good day, with little weather margin |
| 10 W × 4 h × 0.60 | 24.0 Wh/day | Better seasonal/shade margin; larger than the clock and limited by charger current |

Voltaic's own [5 W solar-system guidance](https://voltaicsystems.com/5-watt-5-volt-35wh-solar-system/) gives a broad 7–17 Wh/day range depending on location and season, which is consistent with treating 12 Wh/day as a fair-weather midpoint rather than a guarantee.

Indoor room light is orders of magnitude less useful than outdoor sun, and window glass, orientation, overhangs, trees, and winter sun angle matter. A panel bonded to the clock also forces the bedside object into the wrong location and exposes the battery to heat. The “solar sail” solves both problems: put the panel where light is available and keep the clock where it is useful.

## Charger assessment

### Prototype choice: the charger board with 5 V boost

The Adafruit [solar charger board](https://www.adafruit.com/product/6106) with 5 V boost accepts USB/DC/solar input, manages a 1-cell LiPo, prioritizes the system load, and provides up to a nominal 5 V / 1 A output. This makes it convenient for a prototype on the controller board.

Important caveats:

- Its charge safety timer is fixed at six hours on this breakout. A large pack under weak solar may time out before reaching full charge and require another charge cycle.
- Cold-starting with a weak panel and a sudden load above roughly 200 mA can be troublesome. Keep OLED, radio, and amplifier disabled until the rail stabilizes, then sequence them.
- A 3 W amp can create short peak currents near the boost output's practical limit. Add bulk capacitance, cap volume in battery mode, and scope the rail during simultaneous Wi-Fi transmit and audio.
- Connect the LiPo only to this charger. Do not also attach it to a Feather or other onboard battery charger.
- During USB debugging of the controller board, prevent external 5 V and USB 5 V from back-feeding. Use an explicit power mux/ideal-diode design or disconnect one source.

### Fallback for large-pack testing

If the six-hour timer or weak-sun behavior prevents reliable charging, use the [large-pack solar charger](https://www.adafruit.com/product/4755) followed by a separately enabled SparkFun [boost board](https://www.sparkfun.com/lipower-boost-converter.html). It costs more and uses more board area but separates the solar charger and load-regulator decisions.

### Production direction

A custom board should use a buck-based digital rail, power the amplifier from the battery/system rail, include battery-temperature sensing, measure input voltage/current as well as state of charge, and implement proper USB/source isolation. A linear solar charger should be paired with a roughly 6–7 V panel; excess voltage from a nominal “12 V” panel becomes heat rather than useful output.

## Firmware power policy

| State of charge | Policy |
|---:|---|
| Above 30% | Normal adaptive OLED, scheduled network activity, configured sensors |
| 20–30% | Lower contrast, remove seconds/animation, lengthen sync intervals |
| 10–20% | Display off except interaction/pre-alarm, BLE/Wi-Fi and optional air sensor off |
| Reserve threshold | Real-time clock wake and alarm/audio only; short low-battery indication after dismissal |
| Safe cell cutoff | Orderly shutdown; the real-time clock retains time on its coin cell |

Audio volume can be capped at low state of charge, but the device should not silently disable the alarm. The next-alarm screen must explicitly warn when estimated reserve cannot reach the event.

## Solar validation experiment

Before claiming solar operation:

1. Instrument panel voltage/current, charger status, 5 V load current, battery voltage, and estimated state of charge.
2. Log at one-minute intervals without relying on cloud connectivity.
3. Measure USB-only baseline in eco, balanced, and always-connected modes for 24 hours each.
4. Test the exact panel location for at least seven representative days.
5. Include clear sun, window glass, partial shade, dawn/dusk cycling, and a cloudy day.
6. Start once with a low battery and cold panel to expose startup oscillation.
7. Trigger a full-volume alarm during Wi-Fi transmission and watch both rails for reset/glitch margin.
8. Measure charger and battery temperature; stop testing if the cell approaches its vendor limits.

### Pass criteria

- Balanced-mode average is at or below 0.40 W, or the energy model is revised honestly.
- The alarm completes without reset at the chosen maximum volume in every source condition.
- The battery remains within its specified charge temperature range.
- A 5 W panel produces at least 1.25× measured daily load in the intended good-weather installation; otherwise move to 10 W or describe solar as supplemental only.
- USB-C can recover a deeply depleted unit predictably.

