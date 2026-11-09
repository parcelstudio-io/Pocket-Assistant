# Assembly and execution plan

Baseline: ESP-FLY kit, standard XIAO ESP32-S3, supplied frame, 1S battery, phone Wi-Fi control. First flights have no camera. The original video and its faults remain documented, but its Arduino wiring and firmware must not be mixed into this build. The custom XS-WIFI-75 frame is a second qualification stage.

Use [purchasing.md](purchasing.md) to order, [wiring.md](wiring.md) for connections, [firmware/README.md](../firmware/README.md) for software, and [acceptance-tests.md](acceptance-tests.md) to decide whether to proceed. Proposed labor is 2–4 hours for receiving/dry fit, 2–4 for careful assembly, 3–6 for electrical/software qualification, and several short flight sessions. Custom-frame printing, changes and retuning may add 1–3 days. These are planning allowances for an experienced maker, not a promised beginner completion time.

## 1. Receive and establish the real hardware specification

Buy the kit and only missing tools. Do not buy all alternative rows in the CSV. Preserve packing/part labels and photograph both PCB faces and all wires before soldering. Inspect solder quality, loose components, motor dents, shaft runout, cell condition and antenna connector.

Measure the motor cans and shafts, prop hub/bore and diameter, board outline, populated stack, antenna, battery envelope and connector. Check the battery positive/negative with a meter; never infer it solely from red/black lead color or the shape of a mating connector. Record the actual JST/Molex/other series and manufacturer limits. Determine whether the retail PCB matches the source schematic revision. This prevents a pin-correct source design from being applied to a revised kit blindly.

Use the supplied frame for a dry assembly with **no props**. The motors should stay axial and stationary without excessive force. The PCB must not rest on its small components. The battery must be retained without squeezing its pouch; USB and battery disconnect must remain accessible. Mark nose, M1–M4 and motor wire pairs. Test a motor's direction at low power only after current-limited power is available.

## 2. Establish a safe software baseline before applying motor power

Prepare the pinned firmware and apply the local hardening patch using the supplied build procedure. Set a unique Wi-Fi password. The stock source contains a startup motor test; the local patch defaults that test off. Inspect the resulting build report, rather than assuming an upstream prebuilt binary contains these changes. Compilation does not prove flight suitability.

Connect the XIAO over a data-capable USB cable with the flight battery disconnected. If needed, hold BOOT while connecting USB to enter download mode, then release. Identify the actual serial port by observing device enumeration. Follow the flash instructions for the built image and its correct addresses. Do not use an arbitrary ESP32, ESP32-C3, ESP-FC or Betaflight image.

At this bare-XIAO stage, check only the target identity, upload and basic boot capability. The MPU6050 is on the separate driver board, so its absence is expected until step 3 joins the boards. After that connection, capture the full boot log and stop on failed IMU initialization, repeated resets, unexplained motor output, or malformed sensor data. Distinguish expected missing optional sensors from failure of the required MPU6050. Check the selected pins against the delivered PCB and [wiring.md](wiring.md).

## 3. Join the controller and motor board

With USB and battery disconnected, align XIAO and driver-board orientation using the board labels and reference wiring image. Headers are electrical connections, not spacers that can be arbitrarily flipped. Dry-check all 14 pins before soldering. Tack two opposing corners, check alignment and clearance, then finish the remaining joints. Inspect under magnification for bridges and incomplete wetting.

Join the designated battery rails to the XIAO BAT pads with the supplied short red/black wires. Do not connect VBAT to the XIAO 3V3 pin or assume the 5V pin supplies power on battery. The motor board and XIAO require a common ground. Follow the source diagram for the built-in battery-divider connection; adding another divider in parallel changes calibration.

Perform continuity/polarity checks with no power. A capacitor charging from the meter can initially look like low resistance, so do not declare a short from a brief continuity beep alone. Conversely, a diode reading through a FET is not proof that all wiring is correct. Record rails and investigate any stable near-short before powering.

## 4. Fit motors, wires and antenna

Install each matched CW/CCW motor in its intended location. Viewed from above with the nose forward, the baseline assignment is:

| Position | Motor | GPIO | Direction viewed from above |
|---|---|---:|---|
| Front right | M1 | 7 | CCW |
| Rear right | M2 | 4 | CW |
| Rear left | M3 | 3 | CCW |
| Front left | M4 | 1 | CW |

This mapping is checked against the creator wiring and supplied firmware; verify actual rotation before installing props. Wire colors are an identification aid, not a substitute for that test. Brushed motors can rotate in reverse when polarity is reversed, but brush timing/wear may make the wrong directional motor unsuitable.

Route leads below the rotor plane along the arms with enough slack for strain relief, but no loose loop near a shaft. Solder one pair at a time to its named motor pads. Keep solder joints short and support the lead mechanically. Protect the battery pouch from tools and molten solder. Use the smallest amount of compatible retention adhesive needed; keep it out of bearings, shafts and motor end caps. Do not permanently glue shut an untested electronics compartment.

Install the original matched 2.4 GHz antenna. Seat its tiny coax connector straight and strain relieve the cable. Do not follow antenna-trimming advice as a routine step. Keep the radiator away from the cell and motor wiring, with physical clearance from every rotor. Fit landing wires or supplied feet so the motor ends and cell cannot strike the bench. Their geometry and mass belong in the final checks.

## 5. Power and controller tests, without props

Start from a regulated, current-limited 1S-equivalent supply with its output off while connecting. Set polarity and voltage first; choose the current limit for the test being run. A low limit suitable for board-only bring-up will cause motor-step brownouts and must not be mistaken for an aircraft fault. The supply must not charge a connected LiPo; use it as a battery replacement for these tests. Use USB separately unless the board's power-path behavior has been checked.

Check 3.3 V, VBAT and idle current before enabling motor drive. Test each motor individually at low command, verifying assignment, direction and complete stop. With the frame held stationary and props absent, confirm the IMU axes: nose down, right side down and clockwise yaw must appear correctly in telemetry. Test corrective motor responses on a guarded fixture as described in the acceptance plan; do not depend on motor sound alone.

Connect the phone to the drone's local Wi-Fi network, keep it on the network even without internet, and open the selected app. Verify neutral axes, zero throttle, command direction, range, stop control and voltage display. The phone controls attitude commands and throttle; the flight loop runs onboard. Avoid tilt-to-control and aggressive rates until the basic mapping is qualified.

Run every stale-link test, including app backgrounding, screen lock, forced app stop, Wi-Fi off, reconnect and a stalled sender. Confirm actual motor outputs stop within the specified bound and cannot resume from a nonzero-throttle reconnection. A disconnected app indicator alone is insufficient evidence. Save logs and observations in the measurement sheet.

## 6. Propulsion and electrical qualification on a fixture

Only after all prop-free checks pass, test the supplied motor/prop/battery combination on a rigid guarded thrust stand. Install the correct handed prop with its designed face upward. Support the motor correctly while pressing the hub; force through the shaft can damage the end cap. Do not drill a prop hub or bond a loose prop onto an undersized shaft.

Measure thrust and current for each motor at consistent voltages. Next characterize the complete propulsion system with the real connector and battery to capture sag and shared losses. Record loaded voltage at both ends of the connector, the 3.3 V rail, component temperatures and reset events. Capture repetitive flyback/drain waveforms when evaluating diode stress. Do not perform loaded-prop runs from a loose bench supply wire that can enter the propellers.

Compare measured current and temperature with the actual connector, diode, FET, board and cell ratings. The PH connection and small historical flyback diodes are open design gates, not already approved parts at any current. If a rating fails, document and redesign that component/power path before proceeding. A higher-C battery does not solve an underrated connector.

Stop before the pack is over-discharged or any component exceeds its applicable rating. The inspected stock firmware does not implement a completed battery shutdown function; treat the low-battery indication as an advisory requiring pilot action. Do not rely on a presumed automatic cutoff to protect the cell.

## 7. Controlled first flight

Use a clear, enclosed test area with a soft landing surface, no bystanders or pets, minimal air movement and a spotter if practical. Start line-of-sight. Confirm the stop action, level startup calibration, correct props, secure cell and fully accessible disconnect. Establish the actual center of gravity near the crossing of the motor diagonals; adjust battery position without entering the clearance envelope.

Make a brief low hover, land and inspect. Do not continue if the drone flips, oscillates strongly, drifts uncontrollably, resets, loses orientation, or requires near-maximum throttle merely to hover. Fix motor/prop/sensor ordering before changing PID values. Self-level mode provides attitude leveling, not position or altitude hold; gentle drift is different from an incorrect axis response.

Progress from several seconds to 30 seconds and then one minute. Inspect screws/adhesive/retainers, motors, driver components and connector after each early flight. Determine a conservative landing timer from recorded consumed capacity and loaded voltage, leaving reserve. Only extend flight after repeatable logs and consistent behavior. Do not test intentional link loss in free flight; prove the motor-stop behavior on the fixture.

## 8. Custom frame and FPV are separate changes

After the kit baseline works, print the motor coupon, measure the real components, update the CAD and print XS-WIFI-75. Follow [frame-design.md](frame-design.md), repeat current/thrust/clearance/CG checks, and retune only when the configuration is correct. Do not change motors, props, battery and frame simultaneously; that obscures causes when a problem appears.

Add analog FPV last. Measure the camera with its antenna, lead and mount. Confirm its supply range through the entire battery discharge, its installed envelope and cooling, and the resulting flying mass. The custom frame currently has no camera mount. Qualify a new mount before fitting it. Match receiver/transmitter frequency explicitly and verify control still works with video powered. Wi-Fi phone control does not deliver this analog video to the phone.

Before outdoor use, check the rules for the actual location. Under the assumed US recreational use, this small mass does not remove the TRUST or airspace requirements; FPV use requires a co-located visual observer under the FAA recreational guidance. See [FAA recreational rules](https://www.faa.gov/uas/recreational_flyers) and [AC 91-57D](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_91-57D.pdf). A “25 mW” analog transmitter label alone is not proof of lawful unlicensed operation; verify its FCC authorization or applicable amateur-radio conditions and permitted frequency. [FCC model-aircraft video-transmitter guidance](https://docs.fcc.gov/public/attachments/DA-18-581A1_Rcd.pdf).

No automatic purchases, PCB orders or flight were performed. This package provides the build sequence and acceptance evidence needed for the physical work.
