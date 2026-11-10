# DIY projects — how every new build starts

These are prototypes, not production products. Design comes first.

## 1. New folder per product

Every product gets its own directory here: `DIY/<product_name>/` (snake_case, like
`cyber_clock_v2`, `pocket_ai_sphere`). All drawings, wiring sheets, docs and edu pages for it live
inside that folder.

## 2. Design language — the top priority

Design and colour come first on every build, ahead of cost and convenience (builder's rule 2026-11-07).

- Sleek, sophisticated, minimalist. Futuristic and simple — never busy or complicated-looking.
- Must sit with the existing family: brass builds (Pocket AIs, Pocket AI Sphere, Cyber Dawn) and
  stainless-steel builds (drone onward).
- Few lines: at most 2–3 rods beyond the outline. Wires hidden or routed as deliberate lines.
- Colour tone: **white, ivory or black as much as possible** (builder's words, 2026-11-07, the latest
  of three that day; they replace the brass/ivory/light-grey line). The frame is its own metal, brass or
  stainless. Any other colour (blue, green or red boards, coloured wires, tape, labels, cell wraps) is
  hidden inside the build or under a white, ivory or black cover. The green 2.42" OLED board is the
  example to avoid. Light is white or warm white only.
- When two options work equally well, pick the cleaner-looking one.

## 3. Step one: the final build diagram (stop for approval)

Show the finished product first, the way Cyber Dawn was done:

- **Form drawing** — how it looks, with dimensions.
- **Wiring sheet** — high fidelity, every component wired pin to pin, ~95% certain it works as
  drawn. Check pinouts, voltages and logic levels against datasheets / product pages.
- **Real parts only** — every component is a product that exists and is sold now, linked on its
  name. Skip parts already owned (`pocket_ai_assistant/docs/INVENTORY.md`).
- No overlapping wires; hops at crossings; component names, not part numbers, in prose.

Then stop and ask for approval.

## 4. Step two: educational pages (after approval only)

Explain the science, engineering and physics behind *why* the build and each component were
designed that way. No edu pages or firmware before the diagram is approved.
