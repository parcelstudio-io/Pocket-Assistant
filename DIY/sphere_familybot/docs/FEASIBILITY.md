# Sphere FamilyBot: feasibility and architecture

**Assessed 2026-11-03. Paper only: nothing bought, printed, soldered or flashed.** This is the study that comes before step one of the house rule (the final build diagram), so there is no dimensioned form drawing, wiring sheet, edu page or firmware here. It asks one question: can a fat, cute sphere robot like the [Enabot EBO Max](https://store.enabot.com/products/ebo-max-familybot), driven from a phone, be built on this bench, and what would each of its eight advertised use cases cost in hardware, software and honesty.

Web version (US Letter, black and grey): [Sphere FamilyBot Feasibility](https://claude.ai/artifact/MWhd6VxxzZM6K5AWWRuXgb). The page is `pages/sphere-familybot-feasibility.html`, written by `pages/gen/feasibility_page.py` from this file; edit this file and rerun the script.

<!-- fig:look -->

## The verdict in one table

| Use case on the EBO page | Verdict | What a prototype here delivers | What it does not |
| --- | --- | --- | --- |
| Two-way video | Achievable | Live 1080p30 video to the phone's browser, phone microphone to the robot's speaker, robot microphone back, all over WebRTC; the 5 inch round screen that is the face shows the caller at 1080 × 1080 | EBO's two separate eye screens; ours is one face |
| 4K camera | Partly | 4608 × 2592 stills and time-lapse from the camera module, which is more pixels than 4K; 1080p30 live video and clips | 4K video: the Raspberry Pi 5 has no hardware video encoder, and neither does the Jetson Orin Nano |
| V-SLAM navigation | Hard | Mapping and go-to-point with a 2D lidar puck and slam_toolbox + Nav2, which is the robust way; visual SLAM as a stage 3 experiment with a second camera module | EBO-grade visual SLAM on a camera alone; GPU visual SLAM needs a Jetson plus a stereo camera, about $650 more |
| AI patrol & care | Achievable | Scheduled patrols between waypoints, person and pet detection at tens of frames a second on the AI HAT, clips and push alerts, follow-a-person, return to the dock at 20 percent | Night vision (no infrared illuminator in this design), a full-house map in 15 minutes |
| Elderly care | Partly, and never as a safety device | Pose-based fall detection with a voice check-in and an alert, spoken reminders, inactivity alerts, a two-way call | Reliable fall detection from a camera 160 mm above the floor; it misses falls behind furniture and in other rooms and raises false alarms on floor exercise |
| Kids & pet companionship | Achievable | Pet detection and following, photos, a voice, two big eyes on the round screen, a drive-it-yourself mode | EBO's cloud personality, its accessories, its laser toy (left out on purpose for eye safety) |
| Real-world coding | Achievable, the easiest of the eight | A Blockly block editor in the web app that writes Python against a small robot API, run on the robot with speed and bump limits; the same API as text Python for older kids | Nothing of substance; this is the one feature a hobby build can match outright |
| Embodied AI | Achievable with the desktop in the loop | Wake word on the robot, speech to text and the language model on the desktop (the same server Pip uses), tool calls that drive, look, snap and speak, memory in a file; an MCP server so Claude can drive it too | On-robot language models: possible only with the AI HAT+ 2 and models under about 6 billion parameters, several seconds per answer |

The short version: the drive, the video, the voice and the coding are a solid stage 1 for about $550 in new parts. Patrol and mapping are a real stage 2 for about $220 more. True 4K video and camera-only V-SLAM are the two claims a Raspberry Pi build should not make.

## What the EBO Max actually is

**$599.99, 129 × 127 × 117 mm, 750 ± 10 g.** Those are the store page's own figures, read 2026-11-03, along with: a 2500 mAh battery, 3 to 4 hours to charge, "Standby / Video Recording: 4–6 hours, Continuous Movement: up to 3 hours", an 8 MP sensor recording 4K (3840 × 2160) through a 131° lens, a brushed gear motor, 20 to 60 cm/s, obstacles up to 12 mm, slopes up to 15°, 53 dB when moving, 2.4 and 5 GHz Wi-Fi, 64 GB built in plus a 32 GB card, H.265 video, a 4-microphone array with 360° sound localisation "best within 5 m", face profiles for 10 people (the store page says 20) and one voice ID, and a body of PC + ABS.

It is not a ball with wheels. Enabot's product photos show a white sphere with a black visor and two round eye screens sitting on a black base, and the one hands-on review that describes the drive says it "moves on rubber tracks rather than wheels" and credits a "clever tumbler design" that lets it "self-balance and recover if bumped by pets or children" ([Irish Examiner](https://www.irishexaminer.com/business/technology/arid-41887744.html), 2026-07-29). The same review notes that "because the camera sits at floor level, it simply cannot capture anything high up in the room", that the dock wants two metres of clear space, and that voice commands "need absolute silence". The rolling-ball look the brief has in mind belongs to the earlier EBO Air and SE, whose side caps are the wheels; the taller EBO X is a two-wheeled self-balancer with a pop-up camera.

**Navigation and docking** are listed as "V-SLAM + Route Memory + Infrared Docking", with route, marked-point and full-house patrols, fall detection, tap-to-go on the map and obstacle avoidance. **The app** adds two-way video, voice calls, AI reminders, time-lapse, "skeleton mode" shots, a wake word ("EBO EBO" within 3 to 5 m), drag-and-drop coding blocks for kids (the language is not named), scheduled camera-off, encrypted peer-to-peer streaming with local storage, and "MCP support coming soon" so an AI agent can drive it. Enabot does not publish the processor, the motor count or the drive geometry; everything above is from its store page, its landing page and the review.

## Three ways to roll a sphere

The camera is the whole problem. Video through a rolling shell is useless, so in every real product the camera lives in a part that does not roll, and the sphere is a silhouette rather than a mechanism. Three geometries deliver that silhouette.

**A. A sphere on a hidden base (EBO Max).** The sphere rests on a short cart, tracked in EBO's case, and a low centre of mass makes EBO's rock back upright when nudged. It is the most stable of the three. Tracks are the hard part on a bench; two wheels and two ball casters under the same fat ball give the same stance from a parts drawer, at the price of a flat under the belly, which the EBO hides the same way.

**B. Wheels as the sphere's cheeks (EBO Air and SE).** Two large wheels are the sphere's side caps; the body hangs between them on the axle with its mass low, like a pendulum. One axle, two motors, no caster, and the body rights itself after a bump for the same reason the tumbler does. The price is a nod: the body swings when the wheels accelerate, which is why EBO's small ball wobbles on video.

**C. An internal cart in a sealed shell (Sphero).** Elegant and wrong for this job: the camera would look through plastic that rolls, scratches and fogs.

**A is the pick, with wheels, at the builder's word (2026-11-03).** A screen on the front wants a body that does not nod, and a fat, cute ball wants a face low on its front, which is exactly the EBO Max's stance. So the body sits still on hidden wheels: two Ø70 mm wheels on an 84 mm track in wells in the ball's lower sides, a ball caster 55 mm ahead of and behind the axle in pockets under the belly, and no base at all, at the builder's second word. The numbers are dull in the right way: the centre of mass is about 75 mm up, so the robot tips sideways only past 29°, fore and aft only past 36°, and across the diagonal between a wheel and a caster, its weakest line, past 24°; a 15° slope needs a third of the motors' torque, and braking at 1 m/s² moves nothing. Four wheels were weighed for stability and turned down: two free wheels on a fixed axle fight every turn, four driven wheels skid-steer and scrub carpet, and either moves the weakest line from 33 mm to about 42 mm from the centre, a toddler's push either way. What actually saves a pushed-over ball is its shape: past the tip angle it leaves its wheels and rocks on its round shell, and because the centre of mass sits 25 mm below the sphere's centre it rolls back upright on its own, the EBO Max's tumbler trick for free; the IMU reports the tumble and the motors stop until it settles. The pendulum of B, with its 10° nod, stays in this section as the alternative if a base ever feels like a cheat; the self-righting of EBO's tumbler is not needed on four points of contact, and if the robot is knocked over it says so through the IMU and stops.

## Compute: a Raspberry Pi 5, not a Jetson

| | [Raspberry Pi 5, 8 GB](https://www.microcenter.com/product/673711/raspberry-pi-5-8gb) | [Jetson Orin Nano Super developer kit](https://www.microcenter.com/product/691058/nvidia-jetson-orin-nano-super-developer-kit) |
| --- | --- | --- |
| Price on 2026-11-03 | $174.99 at Micro Center Brooklyn (10 in stock, in-store only); $200 at Adafruit | $349.99 at Micro Center Brooklyn (25+ in stock, in-store only); $399 list since July 2026, up from $249 |
| CPU, memory | 4 × Cortex-A76 at 2.4 GHz, 8 GB LPDDR4X | 6 × Cortex-A78AE, 8 GB LPDDR5 at 102 GB/s |
| AI | none on board; AI HAT+ adds 13 or 26 TOPS (INT8), AI HAT+ 2 adds 40 TOPS (INT4) with 8 GB of its own | 67 TOPS (INT8) on the 1024-core GPU |
| Video encode | "Raspberry Pi 5 uses software video encoders"; 1080p30 H.264 costs 30 to 40 percent of the CPU | "1080p30 supported by 1-2 CPU cores": no hardware encoder either (the Orin NX has one) |
| Video decode | 4Kp60 HEVC in hardware | 1 × 4K60 H.265 in hardware |
| Cameras | 2 × 4-lane MIPI, Camera Module 3 supported out of the box with autofocus and HDR | up to 4 CSI cameras; the official camera module needs a third-party driver |
| Power | 5 V 5 A USB-C; 3 to 8 W in practice | 7 to 25 W; needs 9 to 19 V DC and a bigger battery |
| Size | 85 × 56 mm board | 103 × 90 × 35 mm kit with its heatsink and fan |
| ROS 2 | Jazzy on Ubuntu 24.04, well trodden | JetPack with Isaac ROS, including GPU visual SLAM |
| Wi-Fi | dual-band 802.11ac on board | M.2 card in the kit |

**The Pi wins on size, power, camera support and $175**, and the Jetson's one decisive advantage, GPU visual SLAM, also needs a stereo camera that NVIDIA's own setup page pins to a RealSense, a few hundred dollars more. Neither board encodes 4K video in hardware, so the Jetson would not rescue the 4K claim. The AI HAT adds the perception the Pi lacks for a tenth of the Jetson's price difference. If stage 3 ever wants cuVSLAM, the ROS 2 stack moves to a Jetson with the drive and the body unchanged; NVIDIA has also announced a Jetson Orin Nano 2 with "nearly twice the inference performance", with no price or date yet.

## The architecture

<!-- fig:arch -->

**Brain.** The [Raspberry Pi 5](https://www.microcenter.com/product/673711/raspberry-pi-5-8gb) with its [active cooler](https://www.adafruit.com/product/5815) runs Ubuntu 24.04 and ROS 2 Jazzy, the web app, the video server, the behaviour code and the kids' Python sandbox. The 8 GB model is the floor: ROS 2, a SLAM node, a video encoder and a browser-facing server share it. The [AI HAT+](https://www.microcenter.com/product/687348/raspberry-pi-ai-hat-26-tops) (26 TOPS, $109.99, 3 in stock in Brooklyn) rides on the PCIe port from stage 2; the [AI HAT+ 2](https://www.microcenter.com/product/705302/raspberry-pi-ai-hat-2) ($188.99) is the stage 3 alternative with 8 GB of its own memory for small language and vision-language models.

**Eye.** The [Camera Module 3 Wide](https://www.adafruit.com/product/5658) ($38.50; the standard lens is $33.99 at Micro Center, the Wide was not in Brooklyn stock today): 4608 × 2592 pixels, 102° × 67° field (EBO quotes 131°), phase-detect autofocus, HDR, 4 g. It sits in a notch at the top of the screen's bezel, lens about 160 mm off the floor and aimed 10° up, fixed, because the body does not nod, and reaches the Pi over a [300 mm Pi 5 camera cable](https://www.microcenter.com/product/671933/raspberry-pi-5-camera-cable-300mm) ($2.99). The screen is HDMI, so the Pi's second MIPI connector stays free for a stereo twin at stage 3.

**Reflexes.** An owned [ESP32-S3 dev kit](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) (4 spare) is the motion controller on a USB cable to the Pi: it reads the two encoders and the IMU at 200 Hz, closes the wheel speed loops, holds the heading, enforces the speed ramp and the bump stop, and halts the motors if the Pi stops talking for 300 ms. The Pi sends twist commands and receives odometry over the same serial link; micro-ROS or a 20-line text protocol, builder's choice.

**Muscle.** Two [micro metal gearmotors, 150:1, with encoders](https://www.pololu.com/product/5166) ($29.95 each at Pololu): 210 rpm and 2.4 kg·cm stall at 6 V, 12 counts per motor turn, so 1800 counts per wheel turn, 0.12 mm each. Run from the cell bus at 3.3 to 4.2 V on [Ø70 mm black wheels](https://www.pololu.com/product/1425) ($7.45 the pair, silicone tyres, press-fit on the motor shafts) they top out near 0.5 m/s, close to EBO's 0.6, and crawl at 0.1 m/s. A 1.2 kg robot on a 15° slope needs 0.55 kg·cm per wheel, a quarter of Pololu's 2 kg·cm continuous guidance. The owned [dual H-bridge driver](https://www.amazon.com/dp/B075S368Y2) (4 spare) switches them; its 1.5 A per channel covers the 1.0 A these motors draw at stall on the cell bus. A pair of [motor brackets](https://www.pololu.com/product/989) ($2.95) mounts them inside the ball's lower sides, and two [ball casters](https://www.pololu.com/product/955) ($4.49 each, 3/4 inch steel balls) in pockets under the belly, 55 mm ahead of and behind the axle, carry the front and the back.

**Stance.** An owned [motion sensor](https://www.amazon.com/dp/B07MMZ37PT) (the 6-axis module, 8 spare once the pack lands, due 11-19 to 12-15) gives heading hold, a tip alarm and bump detection; the [fused-orientation IMU](https://www.adafruit.com/product/4754) ($29.50) is the stage 3 upgrade if drift shows. There is no servo: nothing on the body moves but the wheels.

**Power.** The [UPS HAT (E)](https://www.waveshare.com/ups-hat-e.htm) ($32.99 from Waveshare; [its wiki](https://www.waveshare.com/wiki/UPS_HAT_(E)) has the setup) holds four 21700 cells in parallel, feeds the Pi 5 V at up to 6 A through pogo pins on the underside, charges from any USB-C source from 5 to 20 V at up to 40 W, and reports voltage, current and charge over I²C. Four [Molicel 21700 cells](https://imrbatteries.com/products/molicel-p42a-21700-4200mah-45a-battery) ($5.99 each at IMR Batteries, in stock; 4200 mAh, 67 g) make a 60 Wh pack at 268 g that sits just over the axle, as low as the motors allow, and keeps the robot on its feet. The motors take the cell bus straight from the HAT's battery pads so their spikes never touch the Pi's 5 V rail. One EEPROM line (`PSU_MAX_CURRENT=5000`) tells the Pi it may draw 5 A.

**Voice.** All owned: an [I²S microphone](https://www.amazon.com/dp/B092HWW4RS) (13 spare) and an [I²S amplifier](https://www.amazon.com/dp/B0CDWXZZCH) (7 spare) on the Pi's I²S pins under the standard voice-HAT overlay, driving the spare [3 W speaker](https://www.adafruit.com/product/1669) from Cyber Dawn's pair (the 20 mm [enclosed speakers](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) are too quiet for a room). Echo cancellation runs in software on the Pi; expect push-to-talk quality at first and full duplex only with tuning.

**Face.** The [5 inch round touch screen](https://www.waveshare.com/5inch-1080x1080-lcd.htm) ($129.99 at Waveshare; 1080 × 1080 IPS, toughened glass bonded to the panel, 10-point touch over USB, HDMI to one of the Pi 5's micro-HDMI ports, about 3 W from a USB port, driver-free on Raspberry Pi OS; [its wiki](https://www.waveshare.com/wiki/5inch_1080x1080_LCD) has the setup): a kiosk browser page draws two big eyes that blink, look and squint, shows the caller's face during a call, and a clock and the battery when idle; a tap on the face is "come here", a long press is "stop". It is 127 mm of glass set flush in the white shell with nothing round it but a 4 mm bezel and the camera's notch, and it is the part that makes it a face. The [4 inch DSI round screen](https://www.waveshare.com/4inch-dsi-lcd-c.htm) ($89.99) is the smaller alternative that brings the ball back to 184 mm (variation A).

**Radio and phone.** The Pi's own dual-band Wi-Fi; the body is printed plastic, so nothing shields it, and there is no metal on it. Tailscale on the robot, the phone and the desktop gives every device a stable name and an end-to-end encrypted path from anywhere with no port forwarding; its certificate tool gives the robot a valid HTTPS name, which the phone's browser demands before it will hand over the microphone.

**Software on the Pi.** go2rtc serves the camera as WebRTC to the browser and carries the phone's microphone back out of the speaker (its `exec` source runs `rpicam-vid`, its `backchannel` option pipes audio to a player); a small FastAPI server handles driving, telemetry, settings, the Blockly runner and the MCP endpoint over WebSocket and HTTP; ROS 2 Jazzy with slam_toolbox and Nav2 owns the map and the patrols from stage 2; the Hailo runtime runs YOLO detection and pose on the AI HAT; openWakeWord listens for the wake word on the CPU; everything else lives on the desktop that already runs Pip's server.

## Phone control: a web app, not a native app

**The phone opens a page, nothing is installed.** A progressive web app served by the robot works on iPhone and Android alike, carries WebRTC in every modern browser, runs the Blockly editor, and can be added to the home screen with push notifications (iOS allows web push for installed web apps since 16.4). A native app would buy background calls and a nicer icon at the cost of two codebases and an App Store account; for a prototype that is a bad trade.

**Driving** is a WebSocket at 20 Hz carrying a joystick vector; the motion controller stops the wheels if commands pause for 300 ms. On the home network the command path is a few tens of milliseconds. **Video** is a WebRTC track: `rpicam-vid` with its `--low-latency` option encodes 1080p30 H.264 in software (Raspberry Pi says it "will still easily achieve 1080p30"), go2rtc hands it to the browser, and glass-to-glass delay of a few hundred milliseconds is the realistic target; it must be measured, because software encoding adds latency that the old hardware path did not. **Talk** is the browser's microphone track going the other way into the speaker. Away from home the same page works over Tailscale, and the only difference is the phone network's delay.

**Native WebRTC on the desktop** is also an option: the builder's workstation can receive the robot's stream and run the heavy models, which is how stage 3's embodied AI works.

## The eight use cases, one by one

### Two-way video

EBO: 4K camera, two-way video and audio, the caller shown in the robot's eyes. Ours: the camera module through go2rtc at 1080p30 (or 720p60 for driving), the phone's microphone into the 3 W speaker, the robot's microphone back to the phone. The caller's face goes on the 5 inch round screen, a crop of the phone's camera track over the same WebRTC session, at up to 1080 × 1080 and whatever frame rate the Pi's kiosk browser draws, 15 to 30 a second. **Verdict: achievable in stage 1.** The thing to test first is echo: a 3 W speaker 80 mm from a microphone needs the software echo canceller tuned, or push-to-talk.

### 4K camera

The sensor is 4K-class: 4608 × 2592 stills, time-lapse and HDR photos are the camera module's native output, and they exceed EBO's 3840 × 2160. Video is not: the Pi 5 encodes H.264 in software at 1080p30 for 30 to 40 percent of its CPU, and 4K would need the whole processor and more. A USB camera with its own 4K encoder was checked as a way round this: the [Waveshare 8 MP USB camera](https://www.waveshare.com/product/ai/cameras/imx415-8mp-usb-camera-a.htm) outputs 4K at 30 frames a second, but as MJPEG at over 100 Mb/s, and decoding that on the Pi for the AI models would eat the CPU the encoder was meant to spare; nothing with confirmed 4K H.264 output was found today. EBO records H.265 in its own chip. **Verdict: partly. Say "12-megapixel photos and 1080p video" and nobody is misled.**

### V-SLAM navigation

| Option | Needs | On the Pi 5 | Verdict |
| --- | --- | --- | --- |
| 2D lidar SLAM: [D500 lidar kit](https://www.waveshare.com/d500-lidar-kit.htm) ($95.99; 0.03 to 12 m, 10 Hz, 45 g, 1.45 W) with slam_toolbox and Nav2 | one UART, ROS 2 Jazzy | runs comfortably; this is the standard hobby-robot stack | **achievable, the stage 2 plan** |
| RTAB-Map with a depth or stereo camera | a stereo pair (a second Camera Module 3 on the free connector, software-synced) or an [OAK-D Lite](https://shop.luxonis.com/products/oak-d-lite-1) ($269) | heavy; a vendor tutorial says the Pi 5 "cannot smoothly run" it in Docker; expect map updates at 1 to 3 Hz at 640 × 480 | hard; stage 3 experiment |
| ORB-SLAM3, monocular-inertial with the main camera and the IMU | calibration, a C++ build, patience | sparse map and pose only, no occupancy grid for Nav2; scale from the IMU | hard; localisation research, not navigation |
| Isaac ROS cuVSLAM on a Jetson | the Jetson ($349.99), a RealSense stereo camera, JetPack 7.2, 30 Hz synced stereo | not on a Pi | out of reach at this budget |

A lidar puck under the cap, scanning through a 10 mm slot round the head about 172 mm off the floor, sees chair and table legs and the edges of most furniture, which is what a floor robot needs, and slam_toolbox maps a flat in a walk. EBO uses V-SLAM because a lidar would not fit a 129 mm ball; ours has room, and the Ø39 × 34 mm puck hides under the lift-off cap and scans through the slot, so nothing shows but a dark line round the head; it is stage 2, and without it the slot is a line. Docking uses an AprilTag printed on the dock that the camera homes on from a metre away, and the Nav2 goal gets it to that metre. **Verdict: navigation achievable with a lidar; camera-only V-SLAM hard; the EBO phrase "V-SLAM" should not appear on ours.**

### AI patrol & care

The AI HAT runs YOLOv8 detection and pose at tens of frames a second on the robot (Hailo's own figures for the 26 TOPS chip are 491 fps for the small detector and 393 fps for the small pose model on a desktop host; the Pi's PCIe lane and the camera pipeline will cut that to tens). Patrol is a Nav2 waypoint list on a schedule: visit the marked spots, turn in place, run detection, log what was seen with a thumbnail, record a 10 s clip on a person or pet, push a notification, return to the dock below 20 percent. Follow-a-person is the pose model plus a simple controller that keeps the box centred. **Verdict: achievable in stage 2.** What EBO has and this does not: night vision (no infrared LEDs and no NoIR sensor; adding both is a stage 3 line), sound localisation (two microphones give left or right, EBO's four give a bearing), and a "15 minutes to map the downstairs" polish that takes real tuning.

### Elderly care

**Fall detection** is a pose model and a rule: a person's hip keypoints drop below knee height and stay there for 20 s with no motion, the robot drives closer, asks "are you all right?", listens for 15 s, then pushes an alert and opens a two-way call. That works in a demo and fails in the ways every camera system does: the lens is about 120 mm off the floor, so a sofa, a table or a doorframe hides the person; the robot is in one room and the fall is in another; a person doing floor exercise or playing with a grandchild trips it. **Reminders** are a schedule and the text-to-speech voice, with the robot going to the person first; that is easy and useful. **Inactivity alerts** come from the detection log: no person seen in the usual rooms for N hours. **Calls** are the two-way video above. **Verdict: partly, as a companion that notices and asks, never as a medical alert.** A pendant button still wins at the one job that matters.

**Privacy.** Everything stays in the flat: detection, voice and video run on the robot and the desktop, nothing goes to a cloud, and the only remote path is the family's own Tailscale network with access lists per person. The robot keeps a scheduled camera-off like EBO's, a visible lens-on light, a "park" posture that faces the dock wall, a log of who connected when, and recordings that expire after a set number of days. The person being watched must agree to all of it, in words, before the robot enters their home; an elder who did not ask for a camera is being surveilled, not cared for.

### Kids & pet companionship

Pet detection and following, photos and clips, a voice that chirps and talks, drive-it-yourself from the phone and the coding mode below cover what EBO sells here, minus its accessories and its laser toy, which is left out on purpose. The eyes on the round screen are the charm; Crumb already has a face, and this one is bigger. **Verdict: achievable in stages 1 and 2.**

### Real-world coding

Blockly, Google's open-source block editor, lives in the web app and generates Python. A `familybot` module with a dozen calls (`drive`, `turn`, `look`, `say`, `photo`, `wait_for_face`, `wait_for_pet`, `led`) runs the program in a subprocess on the robot with the speed capped and the bump stop active, and the live video sits next to the editor so the child watches the code move. Older kids get the same module as plain Python. The same calls are the tools of the MCP server, so what a child does with blocks, Claude can do with words. **Verdict: achievable, and the cheapest feature of the eight.**

### Embodied AI

The loop is perceive, plan, act, remember. **Perceive:** detections and pose from the AI HAT, the wake word from openWakeWord on the CPU, speech turned to text by faster-whisper on the desktop, a snapshot described by a vision model in Ollama when the plan needs eyes. **Plan:** the language model on the desktop (Pip's server already runs gpt-oss:20b on the RTX 5000 Ada with tool calling) chooses among the robot's tools: go to a named place, find a person, take a photo, say something, set a reminder. **Act:** the tools are the FastAPI endpoints. **Remember:** a notes file per person with faces, rooms and preferences. Expect one to three seconds from the end of a sentence to the start of a spoken answer, which is the lag the EBO review complains of too. On-robot inference is a stage 3 experiment with the AI HAT+ 2: models up to about 6 billion parameters, several seconds per answer, no desktop needed. **Verdict: achievable with the desktop in the loop; the MCP server is a weekend and makes the robot a tool any agent can use.**

## Parts, cost and budgets

Amazon could not be read in this session (its pages refuse automated readers), so the links go to Micro Center Brooklyn, Adafruit, Pololu, Waveshare and IMR Batteries, all read 2026-11-03. Micro Center prices are in-store; Pololu, Waveshare, IMR and Zoro add shipping. Everything owned is left off per the house rule and listed separately below.

### Stage 1: the sphere that drives, streams and talks

| Part | Price | Source, stock on 2026-11-03 |
| --- | --- | --- |
| [Raspberry Pi 5, 8 GB](https://www.microcenter.com/product/673711/raspberry-pi-5-8gb) | $174.99 | Micro Center Brooklyn, 10 in stock, in-store only ([Adafruit](https://www.adafruit.com/product/5813) $200) |
| [Active cooler](https://www.adafruit.com/product/5815) | $13.50 | Adafruit, in stock (Micro Center lists it at $9.99; check Brooklyn) |
| [Camera Module 3 Wide](https://www.adafruit.com/product/5658) | $38.50 | Adafruit, 87 in stock (Brooklyn had the [standard lens](https://www.microcenter.com/product/662016/raspberry-pi-camera-3) at $33.99, 6 in stock) |
| [Pi 5 camera cable, 300 mm](https://www.microcenter.com/product/671933/raspberry-pi-5-camera-cable-300mm) | $2.99 | Micro Center Brooklyn, 5 in stock |
| [UPS HAT (E)](https://www.waveshare.com/ups-hat-e.htm) | $32.99 | Waveshare direct; cells not included |
| 4 × [Molicel 21700 cell](https://imrbatteries.com/products/molicel-p42a-21700-4200mah-45a-battery) | $23.96 | IMR Batteries, in stock (the 5000 mAh Samsung cell was sold out) |
| 2 × [micro metal gearmotor with encoder, 150:1](https://www.pololu.com/product/5166) | $59.90 | Pololu, backorders allowed; also on DigiKey's marketplace |
| [wheel pair, Ø70 mm, black](https://www.pololu.com/product/1425) | $7.45 | Pololu, in stock |
| 2 × [ball caster, 3/4 inch steel ball](https://www.pololu.com/product/955) | $8.98 | Pololu, active |
| [motor bracket pair](https://www.pololu.com/product/989) | $2.95 | Pololu |
| [5 inch round touch screen, HDMI](https://www.waveshare.com/5inch-1080x1080-lcd.htm) | $129.99 | Waveshare direct; the face; driver-free on Raspberry Pi OS; check the box for a micro-HDMI lead for the Pi 5, else a $5 adapter |
| [27 W USB-C power supply](https://www.adafruit.com/product/5814) | $14.04 | Adafruit, in stock; charges through the HAT and later lives in the dock |
| [microSD card, 64 GB](https://www.raspberrypi.com/products/sd-cards/) | about $12 | Micro Center or Adafruit |
| printed body: bottom half, head, cap, dock cradle, in white PETG | about $25 | about 500 g of filament, or a print service |
| **Stage 1 total** | **about $550** | before shipping and tax |

### Stage 2 and 3 additions

| Part | Price | For |
| --- | --- | --- |
| [AI HAT+, 26 TOPS](https://www.microcenter.com/product/687348/raspberry-pi-ai-hat-26-tops) | $109.99 | stage 2 perception; Micro Center Brooklyn, 3 in stock |
| [D500 lidar kit](https://www.waveshare.com/d500-lidar-kit.htm) | $95.99 | stage 2 mapping and patrol; Waveshare (listed at $69.99 at OpenELAB, unverified) |
| [AI HAT+ 2](https://www.microcenter.com/product/705302/raspberry-pi-ai-hat-2) | $188.99 | stage 3 on-robot language and vision models; takes the PCIe port instead of the 26 TOPS HAT, so choose one at stage 2 |
| [fused-orientation IMU](https://www.adafruit.com/product/4754) | $29.50 | stage 3 if the owned sensor drifts |
| second [Camera Module 3](https://www.microcenter.com/product/662016/raspberry-pi-camera-3) | $33.99 | stage 3 stereo for the visual SLAM experiment |
| dock: two spring contacts, two magnets, a printed cradle, an AprilTag | about $15 | stage 2 auto-recharge |
| **Stage 2 total** | **about $770** | with the 26 TOPS HAT and the lidar; the EBO Max is $599.99, $569.99 at one reseller today |

### Owned parts that serve

The [ESP32-S3 dev kit](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) (4 spare) as the motion controller; the [dual H-bridge driver](https://www.amazon.com/dp/B075S368Y2) (4 spare); one [motion sensor](https://www.amazon.com/dp/B07MMZ37PT) from the pack due 11-19 to 12-15 (8 spare); an [I²S microphone](https://www.amazon.com/dp/B092HWW4RS) (13 spare) and an [I²S amplifier](https://www.amazon.com/dp/B0CDWXZZCH) (7 spare); the spare [3 W speaker](https://www.adafruit.com/product/1669) from Cyber Dawn's pair; a [toggle switch](https://www.amazon.com/dp/B0CZ6XZ2P9) (17 spare); [1.5 mm stainless coupons](https://www.amazon.com/dp/B082ZNMD46) (about 4 spare) for the caster plates and the motor mounts; wire, Kapton, heat-shrink and the M3 screw kit from bench stock. The 13 Nitecore 16340 cells and the 12 IMREN 18350 cells cannot serve: a Pi 5 draws up to 5 A at 5 V and the 16340's 2 A protection would trip, and the 18350s are 35 mm long in a 70 mm holder.

### Size, mass and runtime

**A Ø200 mm sphere with the lidar inside, about 1.25 kg.** The 5 inch screen sets the size: 127 mm of glass in a Ø136 mm module wants a ball of 200 mm to sit flush in and still read as a face rather than a porthole; the UPS HAT with its four cells (88 × 56 × 30 mm) sits over the axle, and the Pi, the cooler and the AI HAT (85 × 56 × 45 mm) stand behind the screen. That is 1.55 times the EBO Max in width and 1.7 times its mass: a round moon, as asked.

| Item | Mass, est. |
| --- | --- |
| UPS HAT (E) with four 21700 cells | 395 g |
| Raspberry Pi 5, cooler, AI HAT+ | 110 g |
| 5 inch round screen with its board | 130 g |
| printed body, 2 mm wall: bottom half, head and cap | 370 g |
| motors, encoders, brackets, wheels, casters | 100 g |
| lidar | 45 g |
| speaker, amplifier, microphone, motion controller, driver, IMU | 50 g |
| wiring, HDMI and USB leads, fasteners | 50 g |
| **Total** | **about 1,250 g** |

**Runtime: about 5 hours watching, 3.5 hours patrolling, from a 60 Wh pack.** The Pi with the camera streaming 1080p30 is about 5 W, the round screen about 3 W, the AI HAT about 2.5 W while it infers, the motors about 2 W on average while cruising, the lidar 1.45 W, the voice and the motion controller about 1 W, and the converters lose a tenth: 11.5 W standing watch, 16 W on patrol. The EBO Max quotes 4 to 6 hours and 3 hours from 2500 mAh. Charging from the 27 W supply through the HAT takes about 3 hours; a 40 W PD supply about 2. All of these are listing figures and estimates, to be replaced by a power meter at the bench.

## Design direction: the family look

<!-- fig:form -->

**A white moon with one big round face.** The body is a Ø200 mm sphere in white PETG, printed as a bottom half, a head and a lift-off cap, with nothing on it but the 5 inch round touch screen set flush low on the front, two big eyes on it, and the camera in a notch at the top of the screen's bezel, lens about 160 mm off the floor. It sits on its own wheels: two Ø70 mm black wheels in wells in its lower sides with about 9 mm of tyre showing, two ball casters in pockets under the belly, which rides 6 mm off the floor, and no base, at the builder's word. The lidar, if stage 2 comes, hides under the cap and scans through a 10 mm slot round the head at 172 mm up, so it shows as a dark line and not a hat; the speaker fires through a grille of holes on the right side, and the toggle and the USB-C port hide under the tail. No stainless ring: the family's one line is left off this one at the builder's word, and the slot is the only line it has. Nothing nods: the screen and the camera stay level because the body does not swing. The EBO Max is the same stance, white and round, with tracks where ours has wheels and a visor where ours has one plain face.

### Moon from six angles

<!-- fig:views -->

Turned round, it stays a ball. From the front the screen is a full circle with the camera's notch at twelve o'clock; from the side the glass vanishes into the shell and only the speaker grille and the slot remain; from behind it is a white ball with one dark line round its head; from above, a cap. There is nothing on it that a hand would catch on, which is what a floor robot among children and pets wants.

### Three cute variations

<!-- fig:variants -->

The builder asked for three cute looks to choose from and picked C. **A, Pebble** was the first draft: a 184 mm ball with the 4 inch screen in a black visor, the camera window above the eyes and one stainless ring. **B, Buddy** takes the EBO Max's own cues: the lower third of the ball is black, so it reads as a base without adding one and swallows the wheels; the eyes are two round windows in the visor (one 4 inch screen behind a two-hole mask, or two small round screens, which cannot show the caller); the camera sits in a bump on the visor's brow; no ring. **C, Moon**, the pick and the design drawn above, is the quietest: a 200 mm sphere with the 5 inch round screen set flush and nothing else on it, the camera a notch in the screen's bezel, no plate, no ring. C answers the bigger-screen question and costs about $40 and 40 g more than A; the insides are the same in all three, and so are the hidden wheels and the lidar slot.

The form drawing with dimensions, the wiring sheet pin to pin, and the parts check against datasheets are step one of the house rule and come next, once the builder approves C as drawn.

## Staged plan

1. **Stage 1, the sphere that drives (about $550).** Buy the Pi, cooler, camera, cable, screen, UPS HAT, cells, motors, brackets, wheels, casters, supply and card. Draw the form and wiring sheets, stop for approval. Print the body's bottom half, its head and its cap, build the motion controller on the owned dev kit, bring up Ubuntu, go2rtc, the eyes page and the web app. Done looks like: drive it round the flat from the phone with live video and talk, eyes on the screen, two hours on a charge.
2. **Stage 2, the sphere that patrols (about $220 more).** Add the AI HAT and the lidar; bring up ROS 2 Jazzy, slam_toolbox and Nav2; build the dock with its tag; add detection, clips, notifications, schedules and follow-me. Done looks like: map the flat, tap a room on the phone, watch it go there, patrol on a schedule, dock itself.
3. **Stage 3, the sphere that thinks and teaches.** Blockly and the Python API; the MCP server; the wake word, voice and the desktop language model with tool calls; reminders and the fall-detection demo with its check-in; optionally the AI HAT+ 2 for on-robot models, the fused IMU, and a USB stereo twin for a visual SLAM experiment.

## Open questions for the builder

- **The look.** Moon is the pick (Figure 5) and is drawn; Pebble and Buddy stay in the figure in case the ball should shrink to 184 mm. A ball on hidden wheels with no base (geometry A, at your word); the rolling cheeks (B) stay in the text as the alternative if a base ever feels like a cheat.
- **Size.** 200 mm is what the 5 inch screen dictates; the 4 inch screen brings it back to 184 mm (Pebble). Is 1.55 × the EBO Max acceptable on the floor of a flat?
- **The AI HAT.** The 26 TOPS HAT at $109.99 for perception, or the AI HAT+ 2 at $188.99 straight away for on-robot language models? They share the one PCIe port.
- **Lidar or not.** The puck under the cap is what makes navigation work, at the price of a dark slot round the head; without it the robot drives by hand and follows faces only, and the slot is a line.
- **The face.** The 5 inch screen is the pick; EBO-style twin eye windows (Buddy) are the cheaper, smaller alternative that cannot show the caller.
- **Printing.** White PETG shells 200 mm across: a Bambu Lab A1 (256 mm bed, $259.99 at Micro Center Brooklyn on 2026-11-03) prints the bottom half, the head and the cap whole, an A1 mini (180 mm bed, $199.99) needs each cut in two, or a print service by upload at about 6 to 7 cents a gram. No project record names a printer: which is on the shelf?
- **Who is it for.** The elder-care features change the design (a bigger speaker, louder, a camera-off switch on the body); the kids' features do not. Which comes first?
- **Name.** Working name "FamilyBot" is Enabot's word; the family has Pip and Crumb.

## Sources read on 2026-11-03

Enabot: the [store page](https://store.enabot.com/products/ebo-max-familybot) (specifications, comparison, FAQ) and the [landing page](https://www.enabot.com/home-robot/ebo-max). Review: [Irish Examiner](https://www.irishexaminer.com/business/technology/arid-41887744.html), 2026-07-29. Raspberry Pi: the [Pi 5 page](https://www.raspberrypi.com/products/raspberry-pi-5/), the [processors page](https://www.raspberrypi.com/documentation/computers/processors.html), the [camera software documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html), the [Camera Module 3 page](https://www.raspberrypi.com/products/camera-module-3/), the [AI HAT+ page](https://www.raspberrypi.com/products/ai-hat/), the [AI HAT+ 2 page](https://www.raspberrypi.com/products/ai-hat-plus-2/) and the [AI HAT documentation](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html). NVIDIA: the [Jetson Orin page](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/), the [developer kit page](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/), the [Isaac ROS cuVSLAM package](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_visual_slam/index.html), its [RealSense setup page](https://nvidia-isaac-ros.github.io/getting_started/sensors/realsense_setup.html) and the [performance summary](https://nvidia-isaac-ros.github.io/performance/index.html); the July 2026 price rise from [CNX Software](https://www.cnx-software.com/2026/07/22/nvidia-increases-the-price-of-jetson-modules-and-devkits-by-up-to-101/). Software: the [go2rtc exec](https://github.com/AlexxIT/go2rtc/blob/master/internal/exec/README.md) and [WebRTC](https://github.com/AlexxIT/go2rtc/blob/master/internal/webrtc/README.md) notes, the Hailo model zoo tables for [detection](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_object_detection.rst) and [pose](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_pose_estimation.rst), [Blockly](https://developers.google.com/blockly), [Nav2](https://docs.nav2.org), [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox), [RTAB-Map](http://introlab.github.io/rtabmap/), [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3), [openWakeWord](https://github.com/dscripka/openWakeWord), [Tailscale](https://tailscale.com). Shops: Micro Center Brooklyn search pages, Adafruit, Pololu, Waveshare and its wiki, IMR Batteries, Luxonis, Zoro. The owned-parts counts are from `DIY/PARTS_BY_PROJECT.md` (read 2026-11-03).
