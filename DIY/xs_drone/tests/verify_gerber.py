#!/usr/bin/env python3
"""Check creator evidence integrity and actual Gerber geometry; stdlib only.

This intentionally supports the pinned export's linear absolute-millimeter
outline, not arbitrary Gerber dialects. Unexpected syntax fails explicitly.
No archive member is extracted to the filesystem.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, label, tolerance=1e-6):
    require(abs(actual - expected) <= tolerance,
            f"{label}: actual {actual}, expected {expected}")


def inspect_outline(text):
    require("%MOMM*%" in text, "Expected millimeter Gerber units")
    require("%FSLAX46Y46*%" in text, "Expected absolute 4.6 Gerber format")
    require(not re.search(r"(?:^|\n)G0?[23](?:\*|X|Y)", text),
            "Arcs are outside this pinned linear-export checker")
    positions = []
    edges = []
    current = None
    for line in text.splitlines():
        if not line.startswith("X"):
            continue
        match = re.fullmatch(r"X(-?\d+)Y(-?\d+)D0([12])\*", line)
        require(match is not None, f"Unsupported coordinate record: {line}")
        point = (int(match[1]) / 1_000_000, int(match[2]) / 1_000_000)
        positions.append(point)
        if match[3] == "1":
            require(current is not None, "Draw before first move")
            require(point != current, "Degenerate outline segment")
            edges.append((current, point))
        current = point
    require(len(positions) >= 4, "Too few profile coordinates")
    adjacency = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)
    require(all(len(neighbors) == 2 for neighbors in adjacency.values()),
            "Profile has open or branching vertices")
    visited, pending = set(), [next(iter(adjacency))]
    while pending:
        point = pending.pop()
        if point not in visited:
            visited.add(point)
            pending.extend(adjacency[point])
    require(len(visited) == len(adjacency), "Profile contains separate loops")
    xs, ys = zip(*positions)
    return {
        "bounds_mm": dict(x_min=min(xs), x_max=max(xs), y_min=min(ys), y_max=max(ys)),
        "size_mm": [max(xs) - min(xs), max(ys) - min(ys)],
        "linear_segments": len(edges),
        "closed_single_loop": True,
    }


def inspect_drill(text, diameter):
    require("METRIC" in text and "G90" in text, "Expected absolute metric drills")
    tools = {}
    active = None
    holes = []
    for line in text.splitlines():
        tool_def = re.fullmatch(r"T(\d+)C([0-9.]+)", line)
        tool_sel = re.fullmatch(r"T(\d+)", line)
        point = re.fullmatch(r"X(-?[0-9.]+)Y(-?[0-9.]+)", line)
        if tool_def:
            tools[int(tool_def[1])] = float(tool_def[2])
        elif tool_sel:
            active = int(tool_sel[1])
            require(active in tools, f"Undefined drill tool {active}")
        elif point and abs(tools.get(active, -1) - diameter) < 1e-9:
            holes.append((float(point[1]), float(point[2])))
    rows = sorted(set(x for x, _ in holes))
    require(len(rows) == 2, "Expected two header rows")
    row_ys = [sorted(y for x, y in holes if x == row) for row in rows]
    require(row_ys[0] == row_ys[1], "Header rows do not align")
    require(len(row_ys[0]) == 7, "Expected seven holes per header row")
    pitches = [b - a for a, b in zip(row_ys[0], row_ys[0][1:])]
    return {
        "diameter_mm": diameter,
        "hole_count": len(holes),
        "row_separation_mm": rows[1] - rows[0],
        "pitches_mm": pitches,
        "holes_xy_mm": holes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Write derived JSON report")
    args = parser.parse_args()
    evidence = json.loads((ROOT / "sources/evidence.json").read_text())
    checked_hashes = []
    for entry in evidence["files"]:
        data = (ROOT / entry["path"]).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        require(digest == entry["sha256"], f"Hash mismatch: {entry['path']}")
        checked_hashes.append({"path": entry["path"], "sha256": digest, "match": True})
    expected = evidence["gerber_observations"]
    with zipfile.ZipFile(ROOT / expected["archive"]) as archive:
        outline = inspect_outline(archive.read(expected["outline_member"]).decode("ascii"))
        drilling = inspect_drill(archive.read(expected["drill_member"]).decode("ascii"),
                                 expected["header_drill_diameter_mm"])
    for key, value in expected["outline_bounds_mm"].items():
        close(outline["bounds_mm"][key], value, key)
    for actual, target in zip(outline["size_mm"], expected["outline_size_mm"]):
        close(actual, target, "Outline dimension")
    require(drilling["hole_count"] == expected["header_hole_count"], "Header hole count")
    close(drilling["row_separation_mm"], expected["header_row_separation_mm"], "Row separation")
    for pitch in drilling["pitches_mm"]:
        close(pitch, expected["header_pitch_mm"], "Header pitch")
    report = {
        "status": "PASS: source-file integrity and historical bare-PCB geometry only",
        "hash_checks": checked_hashes,
        "outline": outline,
        "header_drilling": drilling,
        "physical_fit_verified": False,
        "current_retail_pcb_revision_verified": False,
        "electrical_operation_verified": False,
    }
    result = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(result)
    print(result, end="")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
