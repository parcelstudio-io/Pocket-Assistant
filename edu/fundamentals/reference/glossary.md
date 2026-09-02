# Glossary

Terms are grouped by idea rather than alphabetically so related concepts stay
together. Datasheet definitions always take priority for a particular part.

## Physical quantities and units

| Term | Meaning |
| --- | --- |
| **Charge (`Q` or `q`)** | Electrical property measured in coulombs (`C`). About `6.24 × 10^18` elementary charges have magnitude 1 C. |
| **Current (`I`)** | Rate of charge flow. `1 A = 1 C/s`. Conventional current direction is the direction positive charge would move. |
| **Voltage (`V`)** | Difference in electric potential energy per charge between two nodes. `1 V = 1 J/C`. It always needs a reference. |
| **Resistance (`R`)** | Ratio of voltage to current for an ohmic condition, measured in ohms (`Ω`). Real resistance can vary with temperature and operating point. |
| **Conductance (`G`)** | Ease of conduction: `G = 1/R`, measured in siemens (`S`). |
| **Power (`P`)** | Rate of energy transfer, measured in watts (`W = J/s`). |
| **Energy (`E`)** | Capacity to do work or produce heat, measured in joules (`J`) or watt-hours (`Wh`). `1 Wh = 3600 J`. |
| **Capacity (`Ah`)** | Charge capacity: current multiplied by time. It is not energy until voltage is included. |
| **Frequency (`f`)** | Cycles per second, measured in hertz (`Hz`). |
| **Period (`T`)** | Time for one cycle: `T = 1/f`. |
| **Temperature** | Thermal state, often in degrees Celsius. It is not the same as heat or power. |
| **Heat** | Energy transferred because of a temperature difference. Electrical loss often becomes heat. |
| **Peak** | Largest instantaneous magnitude in a stated interval. |
| **Average** | Time-average value. State the time window and operating pattern. |
| **RMS** | Root-mean-square value; for a resistor it gives the DC-equivalent heating value. |

## Prefixes

| Prefix | Symbol | Factor | Example |
| --- | --- | --- | --- |
| giga | `G` | `10^9` | `2.4 GHz` radio |
| mega | `M` | `10^6` | `1 MΩ` |
| kilo | `k` | `10^3` | `4.7 kΩ` |
| milli | `m` | `10^-3` | `250 mA = 0.250 A` |
| micro | `µ` or `u` | `10^-6` | `10 µF` |
| nano | `n` | `10^-9` | `100 nF` |
| pico | `p` | `10^-12` | `50 pF` |

Capitalization matters: `mA` is milliampere; `MA` is megaampere.

## Circuit structure

| Term | Meaning |
| --- | --- |
| **Circuit** | A set of connected components with one or more complete paths for current. |
| **Node / net** | Conductors intended to share one electrical potential. “Net” is common in schematic/PCB tools. |
| **Branch** | One path between two nodes. |
| **Loop** | A closed path through a circuit. |
| **Source** | Element delivering energy or a signal under stated conditions. |
| **Load** | Element receiving electrical power or signal energy. A device can act differently at different times. |
| **Return path** | The path current takes back to its source. It is as important as the outgoing path. |
| **Ground (`GND`)** | The circuit's chosen voltage reference and often a return network. It is not automatically Earth or zero voltage everywhere. |
| **Earth / protective earth (`PE`)** | A safety connection to Earth used by mains equipment. It is not synonymous with low-voltage circuit ground. |
| **Chassis / frame** | Mechanical conductive structure. Whether it connects to circuit ground is a deliberate design decision. |
| **Open circuit** | Broken/incomplete path; ideal current through the gap is zero. Voltage may still exist across it. |
| **Short circuit** | Unintended very-low-resistance connection between nodes. Current is limited by the real source and path impedance. |
| **Floating** | Lacking a defined DC reference to the circuit node in question. It can still couple capacitively or through RF fields. |
| **Series** | Components share the same branch current. |
| **Parallel** | Components connect across the same two nodes and therefore share voltage. |

## Components and power

| Term | Meaning |
| --- | --- |
| **Resistor** | Component intended to provide resistance, bias, limit current, divide voltage, or dissipate power. |
| **Capacitor (`C`)** | Stores separated charge/electric-field energy and opposes instantaneous voltage change. Measured in farads (`F`). |
| **Inductor (`L`)** | Stores magnetic-field energy and opposes instantaneous current change. Measured in henries (`H`). |
| **Diode** | Semiconductor that strongly favors current in one direction under its rated conditions. |
| **MOSFET** | Voltage-controlled transistor commonly used as a switch. Gate voltage is relative to source, not simply “relative to ground.” |
| **`RDS(on)`** | MOSFET drain-source resistance while on, specified at particular gate drive and temperature. |
| **LDO** | Linear regulator that lowers voltage and dissipates approximately `(Vin − Vout)I` as loss. |
| **Buck converter** | Switching converter that reduces voltage. |
| **Boost converter** | Switching converter that increases voltage. |
| **Buck-boost converter** | Switching converter that can regulate with input above or below output. |
| **Efficiency (`η`)** | Useful output power divided by input power. It varies with voltage, load, temperature, and implementation. |
| **Quiescent current** | Current used internally by a device, usually under specifically stated no-load or disabled conditions. |
| **Inrush current** | Short initial current while capacitors charge or systems start. |
| **Load transient** | Rapid change in demanded current and the rail's response to it. |
| **Decoupling capacitor** | Local capacitor that supplies/absorbs fast current near a device and helps keep rail impedance low. |
| **Bulk capacitor** | Larger energy reservoir supporting slower load changes; the distinction from decoupling is functional, not absolute. |
| **ESR / ESL** | A capacitor's equivalent series resistance / inductance; real capacitors are not ideal. |
| **UVLO** | Undervoltage lockout: prevents or stops operation below a threshold, often with hysteresis. |
| **Hysteresis** | Different turn-on and turn-off thresholds, preventing rapid chatter near one voltage. |
| **Fuse** | One-time overcurrent protection element. Operation depends on current and time. |
| **PPTC / resettable fuse** | Polymer positive-temperature-coefficient protection device whose resistance rises after sufficient current heating; not an instant precision current limit. |
| **Protected cell** | Cell combined with an electronic protection circuit against certain abnormal limits. Protection cutoff is not a normal state-of-charge controller. |
| **Voltage sag** | Reduction in terminal voltage under load due to internal/path impedance and electrochemical behavior. |

## Digital logic and buses

| Term | Meaning |
| --- | --- |
| **Logic low/high** | Voltage ranges a receiver interprets as 0 or 1. Exact thresholds are datasheet conditions, not always 0 V and rail voltage. |
| **GPIO** | General-purpose input/output pin. It is a signal pin with limited drive, not a general power rail. |
| **Push-pull** | Output actively drives both high and low. |
| **Open-drain** | Output actively pulls low or releases the line; an external pull-up creates high. Multiple devices can share a line safely if all follow the protocol. |
| **Tri-state / high impedance** | Output driver releases the line and draws little current. The voltage then needs another defined path. |
| **Pull-up / pull-down** | Resistor that gives an otherwise released input or bus a default logic level. |
| **Contention** | Two outputs drive incompatible levels, creating excess current and invalid logic. |
| **Boot strap** | Pin sampled during reset to select a startup configuration. Later use must preserve the required reset-time level. |
| **Edge** | Transition between logic levels. Edge speed, not only bit rate, affects signal integrity. |
| **Rise/fall time** | Time a signal takes to move between defined low/high percentages or thresholds. |
| **I2C** | Addressed, two-wire, open-drain control bus using SDA and SCL. |
| **SDA / SCL** | I2C serial data / serial clock. Both require a valid released-high path. |
| **Controller / target** | Preferred I2C terms for the device initiating transfers and the addressed responding device. |
| **ACK / NACK** | Receiver pulls the acknowledge bit low / leaves it high after a byte. |
| **I2S** | Clocked serial stream for PCM digital audio. Despite the similar name, it is not I2C. |
| **BCLK / SCK** | I2S bit clock. `SCK` is not the I2C `SCL`. |
| **WS / LRCLK** | I2S word-select or left/right clock, normally one period per audio frame. |
| **Slot** | Time allocation for one channel's sample in an I2S frame. Slot width may exceed sample width. |
| **Sample rate** | Number of audio frames/samples per second per channel. |
| **Nyquist frequency** | Half the sample rate; real anti-alias filtering requires usable bandwidth below it. |

## Audio and radio

| Term | Meaning |
| --- | --- |
| **Amplitude** | Magnitude of a varying signal. State peak, peak-to-peak, or RMS. |
| **Impedance (`Z`)** | Frequency-dependent opposition to AC, incorporating resistance and reactance. Measured in ohms. |
| **Class-D amplifier** | Efficient switching audio amplifier whose output waveform is filtered by the load/acoustics and circuit. |
| **BTL** | Bridge-tied load: the load is driven differentially between two amplifier outputs. Neither output is ground. |
| **Clipping** | Output cannot follow the requested waveform and flattens/distorts at a limit. |
| **SPL** | Sound-pressure level in dB relative to 20 µPa in air, under stated measurement conditions. |
| **Decibel (`dB`)** | Logarithmic ratio, not an absolute unit without a reference such as dBm or dB SPL. |
| **RF** | Radio-frequency electrical and electromagnetic behavior. |
| **Wavelength (`λ`)** | Distance a wave travels in one period: `λ = v/f`; about 12.5 cm in free space at 2.4 GHz. |
| **Near field** | Region near an antenna where field behavior and coupling are strongly geometry-dependent. |
| **RSSI** | Receiver's estimate of received signal strength; useful comparatively under controlled conditions, not a complete link-quality metric. |
| **dBm** | Power level in decibels relative to 1 mW. |
| **EMI / EMC** | Electromagnetic interference / ability of equipment to operate compatibly in its electromagnetic environment. |

## Engineering evidence and construction

| Term | Meaning |
| --- | --- |
| **Nominal** | Named or target value, not a guarantee of the exact received value. |
| **Minimum / maximum** | Guaranteed bound only under the datasheet's stated conditions. |
| **Typical** | Representative behavior, generally not guaranteed for every unit. |
| **Tolerance** | Permitted deviation from nominal. |
| **Margin** | Separation between predicted/measured worst condition and required limit. |
| **Derating** | Operating below a headline rating to account for temperature, life, variation, or reliability. |
| **Schematic** | Logical electrical diagram showing components and nets, usually not physical placement. |
| **Symbol** | Schematic representation of a component. |
| **Footprint** | PCB pad/hole pattern and physical metadata for a component package. |
| **BOM** | Bill of materials: controlled list of parts, quantities, identities, and status. |
| **ERC / DRC** | Electrical-rules check / physical design-rules check. Both depend on correct inputs and rules. |
| **Wetting** | Molten solder spreading and bonding to a clean solderable surface. |
| **Flux** | Chemistry that removes/inhibits oxide during soldering; type and residue handling matter. |
| **Strain relief** | Mechanical support that keeps cable force away from solder joints and conductors. |
| **Qualification** | Evidence that a design/article meets defined requirements across defined conditions. |
| **Acceptance** | Decision that a particular article meets pre-established pass/fail criteria. |
| **Verification** | Evidence that specified requirements were met—“built the thing right.” |
| **Validation** | Evidence that the result serves the intended use—“built the right thing.” |
