#!/usr/bin/env python3
"""Generate independent prototype CAD, editable solids, drawings and measured checks.

Outputs are design artifacts, not evidence of a printed or flown aircraft.
Use CadQuery 2.6.1; all lengths in mm. +Y is nose, +X is aircraft right.
"""
from pathlib import Path
import json
import math

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import trimesh

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "cad/parameters.json").read_text())
OUT = ROOT / "cad/generated"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = ROOT / "verification"
RESULTS.mkdir(exist_ok=True)


def capsule(a, b, width, height):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    core = cq.Workplane("XY").box(length, width, height, centered=(True,True,False))
    core = core.rotate((0,0,0),(0,0,1), math.degrees(math.atan2(dy,dx))).translate((*mid,0))
    for x,y in (a,b):
        core = core.union(cq.Workplane("XY").center(x,y).circle(width/2).extrude(height))
    return core


def cylinder(x,y,r,z,h):
    return cq.Workplane("XY").workplane(offset=z).center(x,y).circle(r).extrude(h)


def build_frame():
    s = cq.Workplane("XY").box(P["deck_length"],P["deck_width"],P["deck_thickness"], centered=(True,True,False))
    s = s.edges("|Z").fillet(1.5)
    window = cq.Workplane("XY").box(P["deck_window_length"],P["deck_window_width"],4).translate((0,0,1))
    s = s.cut(window)
    # Slots accept an approximately 1-mm-wide soft thread/elastic. No hard zip tie over pouch.
    for y in (-9.5,9.5):
        s = s.cut(cq.Workplane("XY").center(0,y).rect(6,1.5).extrude(3))
    for x,y in CENTRES:
        root = (math.copysign(11,x),math.copysign(9,y))
        s = s.union(capsule(root,(x,y),P["arm_width"],P["arm_height"]))
        s = s.union(cylinder(x,y,P["motor_mount_outer_diameter"]/2,0,P["motor_mount_height"]))
        # Bore leaves a shallow seat, then a through-hole for the motor leads.
        s = s.cut(cylinder(x,y,P["motor_bore"]/2,P["motor_seat_height"],P["motor_mount_height"]+1))
        s = s.cut(cylinder(x,y,P["motor_wire_hole_diameter"]/2,-1,P["motor_mount_height"]+2))
    # Four supports leave underside components and the centre opening accessible.
    px,py=P["support_pad_centres_abs_xy"]
    for x in (-px,px):
        for y in (-py,py):
            s = s.union(cylinder(x,y,P["support_pad_radius"],P["deck_thickness"],P["support_pad_height"]))
    return s.clean()


def build_coupon():
    # Five bores, left to right 6.0/6.1/6.2/6.3/6.4. Orientation mark at 6.0 end.
    s = cq.Workplane("XY").box(50,10,1, centered=(True,True,False))
    for i,d in enumerate((6.0,6.1,6.2,6.3,6.4)):
        x = -20+i*10
        s = s.union(cylinder(x,0,4.25,0,6))
        s = s.cut(cylinder(x,0,d/2,-1,8))
    s = s.cut(cq.Workplane("XY").center(-24.5,-4.5).rect(1,1).extrude(2))
    return s.clean()


def build_battery_bridge():
    bx,by=P["battery_bridge_xy"]
    plate_t=P["battery_bridge_plate_thickness"]
    plate_z=P["battery_bottom_z"]-plate_t
    s=cq.Workplane("XY").box(bx,by,plate_t,centered=(True,True,False)).translate((0,0,plate_z))
    wall_h=plate_z-P["deck_thickness"]
    for x in (-P["battery_bridge_wall_x"],P["battery_bridge_wall_x"]):
        wall=cq.Workplane("XY").box(P["battery_bridge_wall_thickness"],P["battery_bridge_wall_length"],wall_h,centered=(True,True,False)).translate((x,0,P["deck_thickness"]))
        s=s.union(wall)
    return s.clean()


def envelope(name,dimensions,z):
    x,y,h = dimensions
    s = cq.Workplane("XY").box(x,y,h,centered=(True,True,False)).translate((0,0,z))
    cq.exporters.export(s,str(OUT/f"{name}.step"))
    return s


def validate_export(shape,name):
    stl = OUT/f"{name}.stl"
    cq.exporters.export(shape,str(stl),tolerance=0.02,angularTolerance=0.08)
    cq.exporters.export(shape,str(OUT/f"{name}.step"))
    mesh = trimesh.load_mesh(stl)
    volume = shape.val().Volume()
    result = {
        "solid_valid":bool(shape.val().isValid()),
        "solid_count":len(shape.solids().vals()),
        "mesh_watertight":bool(mesh.is_watertight),
        "mesh_winding_consistent":bool(mesh.is_winding_consistent),
        "mesh_components":len(mesh.split()),
        "solid_volume_mm3":volume,
        "mesh_volume_mm3":float(mesh.volume),
        "stl_volume_error_percent":abs(float(mesh.volume)-volume)/volume*100,
        "bounds_mm":mesh.bounds.tolist(),
        "extents_mm":mesh.extents.tolist(),
        "solid_PLA_mass_estimate_g":volume/1000*P["material_density_g_cm3"]
    }
    assert result["solid_valid"] and result["solid_count"] == 1
    assert result["mesh_watertight"] and result["mesh_winding_consistent"] and result["mesh_components"] == 1
    assert result["stl_volume_error_percent"] < 1
    return result


def corner_clearance(dims):
    halfx,halfy = dims[0]/2,dims[1]/2
    distance = math.hypot(max(A-halfx,0),max(A-halfy,0))
    return distance-P["prop_diameter"]/2


A = P["wheelbase_diagonal"]/(2*math.sqrt(2))
CENTRES = [(A,A),(A,-A),(-A,-A),(-A,A)]
frame = build_frame()
coupon = build_coupon()
bridge=build_battery_bridge()
# Print the battery bridge upside down with its broad plate on the print bed.
bridge_print=bridge.rotate((0,0,0),(1,0,0),180).translate((0,0,P["battery_bottom_z"]))
frame_report = validate_export(frame,"xs_wifi_75_frame")
coupon_report = validate_export(coupon,"motor_fit_coupon")
bridge_report=validate_export(bridge_print,"battery_bridge_print")
cq.exporters.export(bridge,str(OUT/"battery_bridge_assembly.step"))
electronics = envelope("electronics_keepout_NOT_A_PART",P["electronics_envelope"],P["electronics_bottom_z"])
battery = envelope("battery_keepout_NOT_A_PART",P["battery_envelope"],P["battery_bottom_z"])
assembly = cq.Assembly()
assembly.add(frame,name="frame",color=cq.Color(0.12,0.55,0.6))
assembly.add(bridge,name="battery_bridge",color=cq.Color(0.2,0.6,0.65))
assembly.add(electronics,name="provisional_electronics",color=cq.Color(0.1,0.6,0.2,0.6))
assembly.add(battery,name="provisional_battery",color=cq.Color(0.4,0.4,0.4,0.5))
rotor_intersections=[]
motor_intersections=[]
assert abs(P["electronics_bottom_z"]-P["deck_thickness"]-P["support_pad_height"]-P["insulating_spacer_thickness"]) < 1e-6
for i,(x,y) in enumerate(CENTRES):
    motor=cylinder(x,y,P["motor_diameter"]/2,P["motor_seat_height"],P["motor_length"])
    disk=cylinder(x,y,P["prop_diameter"]/2,P["prop_bottom_z_assumption"],P["prop_thickness_envelope"])
    assembly.add(motor,name=f"motor_{i+1}",color=cq.Color(0.7,0.7,0.75))
    assembly.add(disk,name=f"prop_sweep_{i+1}",color=cq.Color(0.9,0.25,0.12,0.25))
    interference=motor.intersect(frame)
    motor_volume=sum(s.Volume() for s in interference.solids().vals())
    motor_intersections.append({"motor":i+1,"frame_intersection_mm3":motor_volume})
    assert motor_volume < 1e-6
    for name,part in (("frame",frame),("electronics",electronics),("battery",battery),("battery_bridge",bridge)):
        intersection = disk.intersect(part)
        vol = sum(s.Volume() for s in intersection.solids().vals())
        rotor_intersections.append({"motor":i+1,"part":name,"intersection_mm3":vol})
        assert vol < 1e-6, (i,name,vol)
assembly.save(str(OUT/"clearance_assembly.step"))

# Worst-case placement/radius allowance is subtracted, not mistaken for real printed accuracy.
allowance = math.sqrt(2)*(P["motor_axis_position_tolerance"]+P["component_xy_placement_tolerance"])+P["prop_radius_tolerance"]
clearances = {
    "adjacent_motor_spacing_mm":2*A,
    "diagonal_motor_spacing_mm":P["wheelbase_diagonal"],
    "adjacent_prop_tip_gap_mm":2*A-P["prop_diameter"],
    "electronics_to_prop_nominal_mm":corner_clearance(P["electronics_envelope"]),
    "battery_to_prop_nominal_mm":corner_clearance(P["battery_envelope"]),
    "electronics_to_prop_tolerance_adjusted_mm":corner_clearance(P["electronics_envelope"])-allowance,
    "battery_to_prop_tolerance_adjusted_mm":corner_clearance(P["battery_envelope"])-allowance,
    "battery_bridge_to_prop_tolerance_adjusted_mm":corner_clearance(P["battery_bridge_xy"])-allowance,
    "overall_prop_envelope_xy_mm":2*A+P["prop_diameter"],
    "motor_centres_xy_mm":CENTRES,
    "required_clearance_mm":P["required_horizontal_prop_clearance"],
    "tolerance_allowance_mm":allowance
}
assert clearances["battery_to_prop_tolerance_adjusted_mm"] >= P["required_horizontal_prop_clearance"]
assert clearances["electronics_to_prop_tolerance_adjusted_mm"] >= P["required_horizontal_prop_clearance"]
assert clearances["battery_bridge_to_prop_tolerance_adjusted_mm"] >= P["required_horizontal_prop_clearance"]
structure_mass=frame_report["solid_PLA_mass_estimate_g"]+bridge_report["solid_PLA_mass_estimate_g"]
assert structure_mass <= P["frame_mass_budget_g"]
bridge_electronics_volume=sum(s.Volume() for s in bridge.intersect(electronics).solids().vals())
assert bridge_electronics_volume < 1e-6
plate_gap=P["battery_bottom_z"]-P["battery_bridge_plate_thickness"]-P["electronics_bottom_z"]-P["electronics_envelope"][2]
assert plate_gap >= 1-1e-6
assert P["battery_bridge_wall_x"]+P["battery_bridge_wall_thickness"]/2 <= P["deck_length"]/2
px,py=P["support_pad_centres_abs_xy"]
pad_r=P["support_pad_radius"]
pcb_x,pcb_y=P["bare_pcb_xy"]
assert px+pad_r <= pcb_x/2 and py+pad_r <= pcb_y/2
header_holes=[(x,y*2.54) for x in (-7.62,7.62) for y in range(-3,4)]
min_pad_header_distance=min(math.hypot(x-hx,y-hy) for x in(-px,px) for y in(-py,py) for hx,hy in header_holes)
assert min_pad_header_distance > pad_r+0.55

report = {
    "status":"PASS: virtual geometry only; physical fit/strength/flight NOT TESTED",
    "design":P,
    "frame":frame_report,"coupon":coupon_report,"battery_bridge":bridge_report,"clearances":clearances,
    "total_printed_structure_mass_estimate_g":structure_mass,
    "battery_bridge_to_electronics_vertical_gap_mm":plate_gap,
    "battery_bridge_to_electronics_intersection_mm3":bridge_electronics_volume,
    "rotor_boolean_collision_tests":rotor_intersections,
    "motor_boolean_collision_tests":motor_intersections,
    "pcb_support_checks": {
        "bare_pcb_xy_mm":P["bare_pcb_xy"],
        "pad_footprints_inside_bare_pcb":True,
        "minimum_distance_to_header_hole_centre_mm":min_pad_header_distance,
        "pad_radius_plus_header_hole_radius_mm":pad_r+0.55,
        "spacer_mm":P["insulating_spacer_thickness"],
        "populated_underside_component_clearance":"NOT VERIFIED; inspect before assembly"
    },
    "unverified":["Purchased kit battery dimensions","PCB populated stack and wire bend envelope","Printed bore tolerances","Prop axial height and flex","Arm strength and resonance","Motor thrust/current","Flight tuning","Camera mount"]
}
(RESULTS/"cad-report.json").write_text(json.dumps(report,indent=2)+"\n")

# Draw engineering views at equal aspect; dimensions are labelled in mm.
fig,(ax,side)=plt.subplots(1,2,figsize=(13,7),gridspec_kw={"width_ratios":[1.4,1]})
deck_x,deck_y=P["deck_length"],P["deck_width"]
ex,ey,ez=P["electronics_envelope"]
bx,by,bz=P["battery_envelope"]
prop_r=P["prop_diameter"]/2
for i,(x,y) in enumerate(CENTRES):
    ax.plot([math.copysign(11,x),x],[math.copysign(9,y),y],color="#248c97",lw=5)
    ax.add_patch(Circle((x,y),P["motor_mount_outer_diameter"]/2,fc="#248c97",ec="black"))
    ax.add_patch(Circle((x,y),P["motor_bore"]/2,fc="white",ec="black"))
    ax.add_patch(Circle((x,y),prop_r,fc="#fdd7c4",ec="#c5572a",alpha=.3))
    ax.text(x,y-8,f"M{i+1}",ha="center",size=9)
ax.add_patch(Rectangle((-deck_x/2,-deck_y/2),deck_x,deck_y,fc="#248c97",alpha=.3,ec="black"))
ax.add_patch(Rectangle((-ex/2,-ey/2),ex,ey,fill=False,ec="green",ls="--",label=f"Electronics envelope {ex:g} x {ey:g}"))
ax.add_patch(Rectangle((-bx/2,-by/2),bx,by,fill=False,ec="gray",lw=2,label=f"Provisional battery {bx:g} x {by:g}"))
ax.annotate("Nose +Y",xy=(0,43),xytext=(0,33),arrowprops={"arrowstyle":"->"},ha="center")
ax.annotate("",xy=(-A,-44),xytext=(A,-44),arrowprops={"arrowstyle":"<->"})
ax.text(0,-43,f"Adjacent centres {2*A:.3f}",ha="center",va="bottom",size=9)
ax.text(0,-50,f"Diagonal {P['wheelbase_diagonal']:.3f} | prop sweep width {2*A+2*prop_r:.3f}",ha="center",size=9)
ax.set(xlim=(-48,48),ylim=(-53,47),aspect="equal",title="XS-WIFI-75 Rev A — top view")
ax.set_xlabel("X / mm (aircraft right)"); ax.set_ylabel("Y / mm")
ax.legend(loc="upper left",fontsize=7)
side.add_patch(Rectangle((-deck_x/2,0),deck_x,P["deck_thickness"],fc="#248c97"))
side.add_patch(Rectangle((-ex/2,P["electronics_bottom_z"]),ex,ez,fc="green",alpha=.3,ec="green"))
tx,ty=P["battery_bridge_xy"]
plate_t=P["battery_bridge_plate_thickness"]
plate_z=P["battery_bottom_z"]-plate_t
side.add_patch(Rectangle((-tx/2,plate_z),tx,plate_t,fc="#248c97"))
for x in (-P["battery_bridge_wall_x"],P["battery_bridge_wall_x"]):
    wall_t=P["battery_bridge_wall_thickness"]
    side.add_patch(Rectangle((x-wall_t/2,P["deck_thickness"]),wall_t,plate_z-P["deck_thickness"],fc="#248c97"))
side.add_patch(Rectangle((-bx/2,P["battery_bottom_z"]),bx,bz,fc="gray",alpha=.4,ec="gray"))
for x in (-A,A):
    od=P["motor_mount_outer_diameter"]
    md=P["motor_diameter"]
    side.add_patch(Rectangle((x-od/2,0),od,P["motor_mount_height"],fc="#248c97",alpha=.7))
    side.add_patch(Rectangle((x-md/2,P["motor_seat_height"]),md,P["motor_length"],fc="silver",ec="black"))
    prop_mid_z=P["prop_bottom_z_assumption"]+P["prop_thickness_envelope"]/2
    side.plot([x-prop_r,x+prop_r],[prop_mid_z,prop_mid_z],color="#c5572a",lw=3)
side.axhline(P["prop_bottom_z_assumption"],color="#c5572a",ls="--",alpha=.4)
side.text(0,27,"Side projection: rotor circles are offset in Y.\nOverlapping X projections are not collisions.",ha="center",size=8)
side.text(0,-8,f"Rotor Z / battery / stack are assumptions.\nMeasure parts before printing final frame.\n{P['motor_seat_height']:g} seat + {P['motor_length']:g} motor = {P['motor_seat_height']+P['motor_length']:g} body top.",ha="center",size=8)
side.set(xlim=(-42,42),ylim=(-13,34),aspect="equal",title="Side envelope — no camera")
side.set_xlabel("X / mm"); side.set_ylabel("Z / mm")
fig.suptitle("PROTOTYPE — dimensional model verified, not physically fitted or flight tested",fontsize=12)
fig.tight_layout()
fig.savefig(OUT/"dimensioned-layout.svg")
fig.savefig(OUT/"dimensioned-layout.pdf")
fig.savefig(OUT/"dimensioned-layout.png",dpi=160)
plt.close(fig)
print(json.dumps({"status":report["status"],"frame_mass_g":frame_report["solid_PLA_mass_estimate_g"],"battery_bridge_mass_g":bridge_report["solid_PLA_mass_estimate_g"],"total_printed_structure_mass_g":structure_mass,"clearances":clearances},indent=2))
