# Cyber Dawn — user manual

Written 2026-11-09, the night the build was fully assembled. The sunrise lamp is left out (builder's
call, 2026-11-09): the OLED's rising horizon is the whole dawn. The alarm program is
`bench/circuitpython/cyberdawn.py`, with its logic in `dawn_core.py` (host tests:
`python3 bench/test_dawn_core.py`).

## The controls

| Control | Where | What it is |
|---|---|---|
| Snooze button | lid, rear left | the big 16 mm [snooze button](https://www.adafruit.com/product/1505), hit without looking |
| Knob | lid, rear right | the [rotary encoder](https://www.adafruit.com/product/6310): a turning ring, a centre press and four direction keys |
| Hand-wave hole | lid, front left | the [proximity and light sensor](https://www.adafruit.com/product/4161) looks up through it |
| Arm switch | left wall, high | the [arm switch](https://www.amazon.com/dp/B09R434VJQ): all alarms on or off |
| Charger USB-C | rear panel | the [charger board](https://www.adafruit.com/product/6106)'s port: power and charging |
| Controller USB | right wall | the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894)'s ports: for flashing only |

On the knob: **turning** and the **UP / DOWN** keys do the same thing. **Centre** and **RIGHT** both
mean "yes, next". **LEFT** means back.

## The face

```
Mon 9 Nov    AL 07:00      date, and the next alarm (or "snz 7m", or "alarms off")
   07:42                   the time
21C 34%         +86%       room temperature and humidity, battery (+ = charging)
```

- The face dims in a dark room and lights fully for 10 s when you **pass a hand over the lid** or
  press the snooze button.
- The whole picture shifts by a pixel each minute, to spread wear on the OLED.
- Local time is New York. Daylight saving changes on its own.

## Everyday use

| To do this | Do this |
|---|---|
| Set an alarm | Turn the knob to open the menu and pick ALARM 1, 2 or 3. Press. Turn to set the hour, press. Turn for minutes, press. Turn to pick every day, weekdays or weekends, press. Turn to switch it ON or off, press to save. |
| Arm or disarm | Slide the arm switch. The face shows "alarms off" when disarmed. Disarming also silences a ringing or snoozed alarm. |
| Wake up | Five minutes before the alarm, a thin horizon line rises up the face as it brightens. At the alarm, a soft two-note chime starts quietly and grows to your volume over a minute. |
| Snooze | Hit the big button. The chime stops and comes back after the snooze time, 9 minutes unless you change it. The face shows the minutes left. |
| Turn the alarm off | Hold the knob's centre and turn it a couple of clicks. A single press can't do it, so it can't be switched off half asleep. |
| Cancel a snooze early | The same: hold the centre and turn, on the normal face. |
| Change the volume | Menu, VOLUME, press, turn. You hear each level as you choose it. Press to save. |
| Change the snooze time | Menu, SNOOZE, press, turn from 1 to 30 minutes, press. |
| Set the clock | Menu, SET TIME, press, set the hour and minute, press. Seconds start at zero. |
| Focus timer | Tip the clock onto its side for 2 seconds. A soft chime confirms, and the face counts down 25 minutes. Three chimes at the end. Tip it again to stop early. |

Menus close on their own after 20 seconds without a touch, without saving. LEFT also backs out.

## What it does for you

- **Alarms survive resets.** Settings, a ringing alarm and a snooze are all kept in the controller's
  memory. A reset or power dip in the middle of a snooze still rings on time.
- **An alarm missed by a reset still rings,** as long as the clock is back within 10 minutes.
- **Ringing stops by itself after 20 minutes,** to save the cell.
- **On the cell, Wi-Fi turns off while the alarm rings.** A Wi-Fi burst on top of the chime is the
  surge that can trip the cell. It comes back on after snooze or off.
- **A crash resets the clock** within 5 seconds, and a power dip at start-up resets it up to five
  times in a row.

## Power

- **Normal use: USB-C into the charger's port on the rear panel.** The clock runs from it and charges
  the cell at the same time. Orange LED on the charger = charging; off = full.
- **Start it with USB-C in.** On the cell alone, the start-up surge (screen and Wi-Fi together) dips
  the power. Once it is running, pulling USB-C is fine: the cell takes over.
- **Never use the controller's own USB for power.** It is for flashing. The cell would end up carrying
  the clock, and the charger can't charge from that side.
- **To flash:** pull the 5 V wire at the controller first, then plug in its USB.
- **To switch off:** pull USB-C, then unplug the cell's plug at the fuel gauge. There is no power
  switch; the arm switch is not one.
- The spoken line plays only at power-up.

## Battery

- One Nitecore 16340, 950 mAh. Full is 4.2 V. Recharge below about 3.6 V.
- The gauge's percentage is wrong for the first cycle or two (it showed 109 % and 4 % on 2026-11-09).
  It learns the cell as it drains and recharges.

## Health check over Wi-Fi

From this computer, with no cable:

```bash
python3 ~/Desktop/Projects/DIY/cyber_clock_v2/bench/wifi_repl.py
```

It pauses the clock, reports Wi-Fi, snooze, arm, gauge alert, all six chain parts, battery, time,
room climate, proximity and tilt, then restarts the clock. Alarm settings are kept. In a browser:
`http://circuitpython.local/code/`. The console password is in `bench/wifi.local.toml`. Wi-Fi roughly
doubles the drain on the cell; to turn it off, put `#` in front of the SSID line in `settings.toml`.

## When something goes wrong

| What you see | Cause | Fix |
|---|---|---|
| Face says "alarms off" with the switch on | The switch is wired the other way round | Flip `ARM_WHEN_LOW` at the top of `cyberdawn.py` |
| Screen blank, Wi-Fi up, health check refused | Safe mode after a power dip | `safemode.py` resets it up to five times in a row. After that, press the controller's RST. |
| Everything dead, charger's green LED off | The cell's protection tripped | Plug USB-C into the charger for two seconds. The cell wakes. |
| Cell reads 0.3–0.4 V in its holder | Same trip | Same fix |
| The board dies the moment a cell goes in, even with USB-C in | A plug wired backwards | Meter every battery plug before use: + must read positive on the board's + mark. A reversed gauge-to-charger cable caused all the trips of 2026-11-08/09. |
| A new cell reads 0 V | Tripped or faulty out of the box | Try the charger. If it stays at 0 V, claim it from the seller. |
