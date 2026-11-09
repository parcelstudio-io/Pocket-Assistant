# Following: can the drone follow a person, locally, in real time?

Drafted 2026-11-09 at the builder's question; nothing has flown. Web version with the drawings: [XS Drone Following](https://claude.ai/artifact/LYYQRGev8wnFg92FFNJxxc), source [pages/following.html](pages/following.html);
the aircraft is the one on [custom-build.md](custom-build.md) and its [build page](https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up).

Short answer: yes, indoors, with the aircraft as the reflexes and the computer on the desk as the brain. No Raspberry Pi
flies. The drone stays the 33 g car-like ladder, forward ranger included: leaving it off was weighed and declined on
2026-11-09.

## Three questions

**A Raspberry Pi 5 on the drone?** No. The board alone is 46 g and wants 5 V at up to 5 A, so the aircraft to carry it starts near 300 g with bigger cells and 3-inch props: a different project. Even a Pi Zero 2 W (10 g) drags in a 5 V supply and a camera, about 25 g, and the drone grows into the 716-motor class. None of it is needed: the Wi-Fi link already exists for control, and a video stream rides the same link to the computer on the desk, which has more compute than any flying Pi.

**The LiDAR?** The drone has no scanning LiDAR and never did: the payload plan rejected the 47 g LD19 that Crumb uses and the 110 g RPLIDAR. What it has are two laser rangers the size of a fingernail, 0.5 g each. The down-looking one gives one distance and is what height hold runs on; it is not optional for indoor flying. The forward one gives an 8 × 8 grid of distances over 60° to 3.5 m: a stop-before-the-wall reflex, not a map. Leaving it off saves 0.5 g and the biggest single firmware item (porting ST's driver, the boot re-addressing dance). It changes nothing in size.

**Smaller drone, local processing?** The drone stays exactly this size; following adds nothing to it. Every added gram of thinking goes on the desk. Processing is local in the strict sense: the PC joins the drone's own Wi-Fi network, as the phone app does today, and no frame or command touches the internet.

## Where the thinking happens

The split is the Crazyflie's, which ESP-Drone inherits: a fast loop on the aircraft keeps it level and at height;
a slow loop on a computer tells it where to go. The PC joins the drone's own Wi-Fi network, as the phone app does;
nothing touches the internet.

| Job | Where | How |
| --- | --- | --- |
| Attitude, 500 Hz | drone | the motion sensor through ESP-Drone's existing loop |
| Height hold | drone | down-looking ranger into the Kalman estimator, as planned |
| Forward stop | drone | the forward 8 × 8 ranger clamps forward speed under 60 cm |
| Video | drone → PC | QVGA JPEG over UDP, the camera task in the firmware plan |
| See the person | PC | a small detector; the RTX 5000 Ada does it in milliseconds |
| Decide where to go | PC | box centre and height into yaw rate, forward speed, height |
| Fly there | PC → drone | velocity setpoints over the existing UDP link, 15 to 20 a second |

| Stage | Time |
| --- | --- |
| Capture and JPEG on the drone | 40 to 70 ms |
| Wi-Fi, drone to PC | 10 to 30 ms |
| Detector | 5 to 10 ms on the GPU; 30 to 60 ms on a laptop CPU |
| Follow controller | under 1 ms |
| Wi-Fi, PC to drone | 5 to 15 ms |
| Commander to motors | 2 to 10 ms |
| Whole loop | 60 to 140 ms with the GPU; 100 to 200 ms on a CPU |

A person walking at 1 m/s moves 15 cm in 150 ms. Only the follow commands cross the air; a dropped frame costs a
little lag, never control (the commander levels after 300 ms of silence and cuts thrust after 500 ms).

## What it can do

- **Rotate toward you.** Yes. Yaw in place from the four motors, up to about 90° a second, driven by how far your box sits off the centre of the picture.
- **Keep its distance.** Yes. Your height in the picture is the range: at 2.5 m a standing adult fills about two thirds of the frame. The controller holds 2.5 m, moving at up to 0.8 m/s.
- **Hold height.** Yes, from the down-looking ranger: 1.2 m, about head height when you are seated. Not sensed by the camera at all.
- **Follow around a corner.** Yes. It turns with you, and when it cuts the corner the forward ranger sees the wall the camera is not looking at and clamps forward speed to zero under 60 cm. That reflex runs on the drone, with or without the brain.
- **Hold still when it loses you.** Not on its own. With no optical-flow sensor it has no horizontal position hold, so it hovers level but drifts. The rule: no person for 1 s, hover; 5 s, land. The controller's own 500 ms link timeout sits under that.
- **Run for how long.** About 3 min a pack, four packs, so 12 min of following per charge round. The limit of this class, not of the brain.

Follow law: box centre off the frame centre → yaw rate (limit 90°/s); box height → range → forward speed (hold 2.5 m,
limit 0.8 m/s); height setpoint 1.2 m on the down-looking ranger; no person for 1 s → hover, 5 s → land. Camera about
66° wide (the stock lens; read the module, OV2640 or OV3660, off the board when it arrives).

## The forward ranger stays

Leaving it off was weighed: 0.5 g lighter, a symmetric nose with the flashlight centred, two firmware items instead of
four. The builder kept it on 2026-11-09, and following is the reason: the camera looks at the person, not at the wall
the drone is about to cut past, and the ranger's stop-before-the-wall reflex covers that blind spot. The nose stays as
approved: flashlight left, ranger right.

|  | With the forward ranger (the build) | Camera-only nose (declined 2026-11-09) |
| --- | --- | --- |
| Flying mass, est. | 33.7 g | 33.2 g |
| Thrust to weight on the vendor's 68 gf | 2.02 | 2.05 |
| Footprint, height | 71 × 91 mm, 26 mm | the same |
| Nose | flashlight left, ranger right | flashlight on the centre line |
| Stops before a wall | yes, under 60 cm | no; the brain only sees what the camera sees |
| Firmware to write | camera task, ST multizone driver, boot re-addressing, lamp | camera task, lamp |
| I²C devices | three, one re-addressed at boot | two, both at their factory addresses |
| Pins | all ten used | D7 free |
| Decision 2026-11-09 | kept | declined |

What the decision costs: ST's multizone driver and the boot re-addressing stay on the firmware list, as the payload
plan already had them.

## Not promised

- **Position hold.** No optical-flow sensor fits (the PMW3901 needs four SPI pins; the XIAO has none free). Expect slow
  drift and a slow orbit; the loop corrects aim and range, not sideslip.
- **Frame rate.** 10 to 15 fps at 320 × 240 is the plan; the Wi-Fi budget is measured before the rate goes up.
- **Light.** The detector needs a lit room.
- **Mapping.** None; that is Crumb's and the FamilyBot's job with a real LiDAR on a ground robot.
