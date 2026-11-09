# Frame design and fabrication

## First build: supplied frame

Use the frame included in the ESP-FLY kit for the first qualified flight. Inspect every motor socket, the board seat, cable routing, top cover and propeller clearance before assembly. The vendor's “50 mm class” and overall dimensions are product descriptions, not sufficient data to manufacture its internal geometry. The creator's exact replacement STL is separately sold on [Cults](https://cults3d.com/en/3d-model/gadget/esp-fly-an-esp32-micro-drone-body-frame-3d-design-stl-files). This folder does not reproduce that paid design.

## Custom option: XS-WIFI-75 Rev A

This folder includes an independent, camera-free open frame generated from [parameters.json](../cad/parameters.json). It is intended to carry the ESP-FLY electronics and 615 motors after the real components are measured. It is not a physically verified replacement for the retail frame.

| Feature | Design value | Status |
|---|---:|---|
| Diagonal between opposite motor axes | 75.000 mm | CAD-defined |
| Adjacent motor-axis spacing | 53.033 mm | Calculated |
| Overall propeller swept width/length | 83.033 mm | Calculated for 30 mm props |
| Motor bodies | 6 × 15 mm nominal | Published size; measure purchased parts |
| Propellers | 30 mm diameter, 0.8 mm bore | Kit nominal; confirm shaft fit |
| Motor socket bore / outside diameter | 6.20 / 8.00 mm | Print coupon to select actual bore |
| Socket height / lower supporting ledge | 6.00 / 0.60 mm | CAD-defined |
| Motor-wire exit | 4.80 mm through opening | Verify motor end-cap and lead exit fit |
| Centre deck | 34 × 24 × 1.2 mm | CAD-defined |
| Arms | 2.8 mm wide × 1.8 mm high | Prototype dimensions; no structural qualification |
| Electronics envelope | 26 × 22 × 12 mm | Planar margin around 21 × 17.8 mm XIAO; height provisional |
| Battery envelope | 30 × 20 × 8 mm | Provisional allowance; **not the kit battery's measured dimensions** |
| Battery bridge plate | 32 × 22 × 0.8 mm, top at Z = 16 mm | Printable separate part; supports battery without loading the PCB |
| Bridge sidewalls | 1.2 mm thick × 18 mm long, centred X = ±15 mm | Rest on deck; inspect/qualify attachment and bending |
| Rotor lower Z | 17.2 mm | Provisional; measure prop hub and shaft insertion |
| Camera and antenna mounts | Not modelled | Keep antenna below sweep, qualify separately; no camera fit claim |

The historical controller Gerber outline is 21.000 × 17.750 mm, verified from the actual outline file. The board's header holes are not mounting-screw holes. This frame uses small support pads and thin insulating attachment material; it does not drill the controller or invent a bolt pattern. Source and revision details are in [wifi-options.md](wifi-options.md).

## Files you can use

- [Frame STEP](../cad/generated/xs_wifi_75_frame.step): editable solid for Fusion, FreeCAD or similar CAD.
- [Frame STL](../cad/generated/xs_wifi_75_frame.stl): print prototype after dimensions are checked.
- [Motor-fit coupon STL](../cad/generated/motor_fit_coupon.stl): test before a full frame.
- [Battery bridge STL](../cad/generated/battery_bridge_print.stl): already oriented upside down for support-free printing; [assembly-position STEP](../cad/generated/battery_bridge_assembly.step) uses the drone coordinate system.
- [Assembly STEP](../cad/generated/clearance_assembly.step): frame plus differently named motor, prop-sweep and provisional component solids.
- [Dimensioned PDF](../cad/generated/dimensioned-layout.pdf) and [SVG](../cad/generated/dimensioned-layout.svg): drawing and envelope overview.
- [Generator](../cad/generate.py): modify dimensions and regenerate; [geometry report](../verification/cad-report.json) records checks.

The `*_keepout_NOT_A_PART.step` solids are reserved space, not printable electronics or batteries. The assembly's propeller cylinders represent the entire rotating swept volume; they are not propeller designs. Buy the specified molded propellers.

## How to reproduce or modify it

```sh
uv venv --python 3.11 .venv/cad
uv pip install --python .venv/cad/bin/python -r cad/requirements.txt
.venv/cad/bin/python cad/generate.py
```

Run from this project directory. Generated CAD and drawings are deterministic from the parameters except for export metadata. The generator stops if the solid is invalid, disconnected, the STL is not watertight, or the declared component envelope fails the specified rotor margin. It does not solve stress, vibration, cooling, aerodynamics or control-loop stability.

To adapt the design: measure the largest body including solder and connectors; update the keepout dimensions; preserve board orientation; choose prop diameter; then increase wheelbase until all clearances pass with placement allowance. Recheck mass, thrust and arm stiffness. Do not simply scale the entire STL: that scales motor bores, wall thicknesses and lead exits as well.

## Print and fit protocol

1. Measure all four motor cans in two directions, shaft diameter, motor length and lead exit. Measure the cell without compressing its pouch. Measure the populated PCB stack, USB plug access, battery connector projection and wire bend radius. Record values before editing the CAD.
2. Print the fit coupon flat. The five bores from its marked end are 6.0, 6.1, 6.2, 6.3 and 6.4 mm. The small corner notch marks the 6.0 mm end. Test with an unpowered motor; select a bore that supports it without pressing on the end cap, binding the rotor or deforming the can. Never force a 6 mm can into an undersized print.
3. Proposed starting profile: PLA, 0.20–0.40 mm nozzle, 0.12–0.16 mm layers, at least two continuous wall lines where geometry permits, full-density thin arms and sockets, flat deck on the bed, supports off. Use the filament/printer's proven temperatures and slow small-feature settings. These are starting settings, not validated print parameters. Check the slicer's line preview for continuous socket walls and arms.
4. Remove any elephant-foot ridge from the lower openings. Deburr by hand and repeat motor fit checks. Verify the ledge supports the intended can surface and leaves wires free. If it bears on a fragile plastic motor end cap or presses the leads, change the seat design before using it.
5. Weigh both printed parts. The generated ideal solid-PLA estimate is 1.94 g for the frame and 1.45 g for the bridge, totaling 3.39 g, excluding glue, tape, battery restraint and dimensional over-extrusion. Budget at most 4 g for the complete installed frame/retention assembly; investigate any excess before adding payload. Print the bridge from its pre-oriented STL with its broad plate on the bed and walls upward; no support should be required. Remove any sharp plate edges that could abrade the cell.
6. Seat the controller on its four pads using a measured 0.5 mm insulating spacer/adhesive system. Pad tops are at Z = 1.7 mm; the reserved electronics start at Z = 2.2 mm. Pad centres are (±5.5, ±8.5) mm with 1.4 mm radius, inside a 17.75 mm-wide, 21 mm-long bare PCB and clear of the nominal header drill holes. This does **not** verify clearance to populated underside parts or solder. Inspect those areas and move the pads if needed, preserving IMU orientation and recalculating. Secure the board firmly; avoid thick soft foam that allows it to oscillate relative to the frame. Provide USB access and avoid force on its connector.
7. Fit the battery bridge over the electronics, with its two walls resting on the deck at X = ±15 mm. The plate's underside is Z = 15.2 mm, leaving 1.0 mm above the provisional electronics envelope. The walls are outside that envelope. Verify actual components, USB and leads clear it, then secure its feet with a measured light attachment; do not let the battery load the bare PCB, USB connector or SMD components. Retain the battery on the bridge with a light, broad elastic loop and thin insulating pad. The deck has thread/elastic routing slots; hard narrow ties can damage a cell. Pad thickness adds to the actual battery height and must remain within the reserved envelope or trigger a CAD update. Confirm the bridge and restraint remain inside their validated envelopes with the stated placement allowance. Keep a quick battery-disconnect path.
8. Route motor wires along the arms below the propeller plane, strain relieve near each motor and board pad, and inspect from all angles. Locate the unmodified antenna where it cannot enter a propeller or lie against the cell. No antenna bracket or landing gear is assumed in the CAD; add measured lightweight retention/feet and repeat mass/clearance checks.
9. Install props only for the later acceptance stage. Slowly rotate each by hand and measure both horizontal and vertical clearance, including elastic, antenna and leads. Require at least 2 mm static clearance to unrelated objects and inspect again with gentle frame deflection. More clearance may be needed if measured flex warrants it.

The frame is open and has no propeller guards. Do not call its outer motor sockets guards. Guarded frames require a separate mass, clearance and thrust assessment; no untested guard is implicitly included here.

## Strength and tuning qualification

With motors off and battery removed, check every joint for cracks, motor retention and arm stiffness. Apply a known small load at each motor seat and measure deflection; compare all four. A simple beam estimate can help identify an obviously thin arm, but printed layers, fillets, stress concentrations and motor vibration dominate many real failures. The CAD validity result is not an FEA result.

Start powered evaluation on a restrained test fixture with guards around the fixture. Record vibration and motor temperatures. Do not reuse a loose or cracked socket. Complete the entire flight progression again after transferring from the stock frame; longer arms alter inertia and resonance. No PID values for this custom frame are claimed to be validated.
