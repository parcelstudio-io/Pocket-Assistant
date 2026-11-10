# Lab record template

Copy this file for one experiment. Complete the planning fields before power
is applied. Do not erase a surprising or failed result; add a dated correction
or a new run.

## Identity

```text
test title:
test ID:
date/time and timezone:
operator:
location/ambient conditions:
schematic or wiring revision:
firmware commit/build ID:
test-article ID and exact module markings:
```

Attach clear photographs of both sides of every unidentified marketplace
module and of the complete test wiring.

## Question and prediction

```text
one question this test answers:

hypothesis/prediction:

competing explanation(s):

measurement that separates them:
```

## Diagram and evidence inputs

Draw the complete source and return path, rail names, component values, switch
positions, connectors in physical pin order, and probe points.

| Input or claim | Value/statement | Unit/condition | Evidence label | Source |
| --- | --- | --- | --- | --- |
| Example: supply setting | 3.30 | V | SETPOINT | instrument front panel |
|  |  |  | DATASHEET / TYPICAL / ASSUMED / CALCULATED / MEASURED |  |

## Safety envelope

```text
power source:
set voltage:
initial current limit:
maximum permitted current limit:
energy-producing loads present:
cell status (normally ABSENT for foundations labs):
instrument ground/reference review:
PPE and ventilation:
```

Stop and remove power for any of the following:

- unexpected current-limit operation;
- voltage outside the pre-set safe range;
- unexpected heat, smell, smoke, swelling, arcing, or noise;
- unstable or strained wiring;
- a probe/reference connection that is not understood; or
- any observation outside this test's authorized envelope.

Additional test-specific stop conditions:

```text

```

## Instruments

| Instrument | Make/model or ID | Mode/range/settings | Calibration or sanity check |
| --- | --- | --- | --- |
| Bench supply |  | CV setpoint; CC limit | polarity verified at cable end |
| DMM |  | jack and mode | probes shorted/open as applicable |
| Oscilloscope |  | probe ratio, coupling, bandwidth, sample rate, trigger | ground reviewed |
| Logic analyzer |  | threshold, sample rate, decoder settings | ground reviewed |

## Acceptance rule

Write this before the test. Use requirements and applicable datasheet limits,
not a result-dependent rule.

```text
PASS if:

FAIL if:

INCONCLUSIVE if:
```

## Procedure

1. Disconnect all sources and discharge stored energy.
2. Inspect and perform the planned unpowered checks.
3. Verify source polarity and current limit at the cable end.
4. Connect according to the drawing.
5. Record the exact ordered actions below.

```text
6.
7.
8.
```

## Results

| Run | Controlled condition | Measured result with unit | Instrument/probe points | Observation |
| ---: | --- | --- | --- | --- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

Files and photographs:

```text

```

## Interpretation

```text
result: PASS / FAIL / INCONCLUSIVE

what the evidence supports:

what it does not support:

uncertainty and instrument limits:

unexpected observations:

next discriminating test:
```

## Change log and review

| Date/time | Change or review comment | Author |
| --- | --- | --- |
|  |  |  |

Do not relabel a calculation or simulator output as a physical measurement.
Do not generalize one sample, one room temperature, or one successful attempt
to every unit or operating condition.
