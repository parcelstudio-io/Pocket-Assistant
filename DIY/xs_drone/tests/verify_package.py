#!/usr/bin/env python3
"""Check package consistency, local references, actual saved CAD checks and BOM arithmetic.

Does not claim hardware validation. Run the separate CAD generator and firmware
host/target tools to regenerate their evidence after changes.
"""
import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parent.parent
checks=[]


def require(value,description):
    if not value:
        raise AssertionError(description)
    checks.append(description)


def main():
    missing=[]
    count=0
    for path in ROOT.rglob("*.md"):
        if any(p in (".venv",".work","work",".cache") for p in path.relative_to(ROOT).parts):
            continue
        content=path.read_text()
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)",content):
            target=target.strip().strip("<>")
            parts=urlsplit(target)
            if parts.scheme or target.startswith("#"):
                continue
            dest=unquote(parts.path)
            if not dest:
                continue
            count+=1
            resolved=(path.parent/dest).resolve()
            if resolved==ROOT/"verification/package-report.json":
                continue  # This successful run creates its own linked result below.
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {dest}")
    require(not missing,"All local Markdown file links resolve: "+str(missing))

    with (ROOT/"hardware/bom.csv").open(newline="") as stream:
        rows=list(csv.DictReader(stream))
    require(len({r["id"] for r in rows})==len(rows),"Unique BOM identifiers")
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows),"BOM column counts consistent")
    prices={r["id"]:Decimal(r["purchase_price_usd"] or "0") for r in rows}
    total=prices["K01"]+sum((prices[f"T{i:02}"] for i in range(1,13)),Decimal(0))
    require(total==Decimal("216.84"),"Kit plus 12 basic tools totals USD216.84")
    require(prices["K01"]+prices["T01"]==Decimal("64.94"),"Kit plus cable totals USD64.94")
    require(all(Decimal(r["purchase_price_usd"] or "0")==0 and r["purchase_quantity"]=="0" for r in rows if r["id"] in [f"K{i:02}" for i in range(2,11)]),"Included kit parts are not double-counted")

    params=json.loads((ROOT/"cad/parameters.json").read_text())
    cad=json.loads((ROOT/"verification/cad-report.json").read_text())
    require(cad["design"]==params,"CAD report corresponds to current parameter values")
    frame=cad["frame"]
    require(frame["solid_valid"] and frame["solid_count"]==1,"Frame is one valid CAD solid")
    require(frame["mesh_watertight"] and frame["mesh_winding_consistent"] and frame["mesh_components"]==1,"Exported frame is one watertight consistently wound mesh")
    require(frame["stl_volume_error_percent"]<1,"STL and exact CAD volumes agree within 1 percent")
    require(len(cad["rotor_boolean_collision_tests"])==16 and all(t["intersection_mm3"]<1e-6 for t in cad["rotor_boolean_collision_tests"]),"All 16 saved rotor/part solid intersections are zero")
    require(all(t["frame_intersection_mm3"]<1e-6 for t in cad["motor_boolean_collision_tests"]),"All four motor cans clear frame material")
    c=cad["clearances"]
    require(math.isclose(c["adjacent_motor_spacing_mm"],params["wheelbase_diagonal"]/math.sqrt(2)),"Wheelbase/adjacent spacing relation checked independently")
    require(c["battery_to_prop_tolerance_adjusted_mm"]>=params["required_horizontal_prop_clearance"],"Declared battery tolerance envelope clears rotors")
    require(c["electronics_to_prop_tolerance_adjusted_mm"]>=params["required_horizontal_prop_clearance"],"Declared electronics tolerance envelope clears rotors")
    require(c["battery_bridge_to_prop_tolerance_adjusted_mm"]>=params["required_horizontal_prop_clearance"],"Battery bridge tolerance envelope clears rotors")
    require(cad["battery_bridge_to_electronics_intersection_mm3"]<1e-6 and cad["battery_bridge_to_electronics_vertical_gap_mm"]>=1-1e-6,"Battery bridge clears reserved electronics and supports cell independently")
    require(cad["total_printed_structure_mass_estimate_g"]<=params["frame_mass_budget_g"],"Combined ideal frame and bridge mass below structural budget")
    require(cad["pcb_support_checks"]["pad_footprints_inside_bare_pcb"],"Pads lie beneath the bare PCB footprint")
    require(not params["battery_dimensions_verified"] and not params["stack_height_verified"],"Unmeasured physical fit remains labelled unverified")
    with (ROOT/"verification/measurement-log.csv").open(newline="") as stream:
        measurements=list(csv.DictReader(stream))
    require(all(r["result"]=="NOT_RUN" for r in measurements),"No physical measurement falsely recorded as performed")
    fw=json.loads((ROOT/"firmware/build-report.json").read_text())
    patch=ROOT/"firmware"/fw["patch"]
    require(hashlib.sha256(patch.read_bytes()).hexdigest()==fw["patch_sha256"],"Firmware patch matches the successfully compiled build report")
    require(fw["sdk"]["target"]=="esp32s3" and fw["sdk"]["version"]=="v5.0.7","Firmware report is for selected MCU and pinned SDK")
    require(fw["tests"]["control_assertions_passed"]>=84 and fw["tests"]["udp_length_assertions_passed"]==128,"Firmware report includes finite/range control and UDP tests")

    generated={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/"cad/generated").iterdir()) if p.is_file()}
    report={"status":"PASS: document, BOM and saved digital-model consistency only","check_count":len(checks),"checks":checks,"local_markdown_links_checked":count,"bom_rows":len(rows),"kit_and_basic_tools_usd":str(total),"cad_artifact_sha256":generated,"physical_tests":"NOT RUN"}
    (ROOT/"verification/package-report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="cad_artifact_sha256"},indent=2))


if __name__=="__main__":
    main()
