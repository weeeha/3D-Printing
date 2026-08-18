#!/usr/bin/env python3
"""Assemble the spec-sheet preview page from the generated SVGs + build stats.

    python3 make_page.py

Inlines the SVGs (the Artifact CSP blocks external requests, so nothing may be
referenced by URL) and namespaces nothing -- the colour script emits no filter ids.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
stats = json.load(open(os.path.join(HERE, "cstats.json")))

SHEETS = [
    ("csign_airgap", "Air-gap notice", "CAUTION",
     "Do not connect this machine to the internet",
     "Crossed-out Wi-Fi roundel. The joke that started the whole thing."),
    ("csign_clankers", "Occupancy notice", "CAUTION",
     "No clankers allowed — maximum occupancy 0",
     "Crossed-out robot head. Bipedal, wheeled and disembodied units alike."),
    ("csign_bilingual", "Bilingual prohibition", "AVIS / NOTICE",
     "La lecture du présent avis est interdite / Reading this notice is prohibited",
     "Québec order: AVIS leads because the Charte de la langue française requires "
     "French to be predominant. Note “100 $” with the sign after the number, and the "
     "space before the colon. No safety-alert triangle — ANSI reserves it for CAUTION "
     "and above."),
]


def svg_for(name):
    raw = open(os.path.join(HERE, name + ".svg")).read()
    return re.sub(r'\swidth="100%"', '', raw, count=1)


def chips(cols):
    order = [("W", "white"), ("K", "black"), ("Y", "yellow"), ("B", "blue")]
    sw = {"W": "#F2F0EA", "K": "#141414", "Y": "#F2C200", "B": "#12529B"}
    out = []
    for k, label in order:
        if k in cols:
            out.append('<li><span class="dot" style="background:%s"></span>%s</li>'
                       % (sw[k], label))
    return "".join(out)


def sheet(name, title, signal, sub, note):
    s = stats[name]
    rows = [
        ("plate", "256 &times; 200 &times; 4 mm"),
        ("signal word", signal),
        ("filaments", "%d" % len(s["colours"])),
        ("3mf objects", "%d" % s["objects"]),
        ("art faces", "{:,}".format(s["faces"])),
        ("triangles", "{:,}".format(s["tris"])),
        ("watertight", "all parts" if s["solid"] else "FAILED"),
    ]
    cells = "".join('<div class="spec"><dt>%s</dt><dd>%s</dd></div>' % r for r in rows)
    return """
<section class="sheet" aria-labelledby="h-{name}">
  <div class="sheet-head">
    <div>
      <p class="eyebrow">{name}.3mf</p>
      <h2 id="h-{name}">{title}</h2>
      <p class="sub">{sub}</p>
    </div>
    <p class="verdict" data-ok="{ok}">{verdict}</p>
  </div>
  <figure class="mount">
    <div class="dimline" aria-hidden="true"><span>256 mm</span></div>
    <div class="plate">{svg}</div>
    <figcaption>{note}</figcaption>
  </figure>
  <ul class="chips">{ch}</ul>
  <dl class="specs">{cells}</dl>
</section>""".format(name=name, title=title, sub=sub, note=note, svg=svg_for(name),
                    cells=cells, ch=chips(s["colours"]),
                    ok="1" if s["solid"] else "0",
                    verdict="print-ready" if s["solid"] else "check geometry")


CSS = """
:root{
  --ground:#D3D6D2; --card:#F7F6F2; --ink:#15171B; --ink-soft:#555A61;
  --rule:#B7BAB5; --steel:#2C5677; --stamp:#9A3A22; --mount:#C2C5C1;
  --display:"Helvetica Neue",Helvetica,Arial,sans-serif;
  --body:"Iowan Old Style",Georgia,"Times New Roman",serif;
  --data:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root{ --ground:#111316; --card:#1C1F23; --ink:#E8E7E2; --ink-soft:#969BA3;
         --rule:#2F333A; --steel:#84AECF; --stamp:#D9694A; --mount:#0B0D0F; }
}
:root[data-theme="dark"]{ --ground:#111316; --card:#1C1F23; --ink:#E8E7E2;
  --ink-soft:#969BA3; --rule:#2F333A; --steel:#84AECF; --stamp:#D9694A; --mount:#0B0D0F; }
:root[data-theme="light"]{ --ground:#D3D6D2; --card:#F7F6F2; --ink:#15171B;
  --ink-soft:#555A61; --rule:#B7BAB5; --steel:#2C5677; --stamp:#9A3A22; --mount:#C2C5C1; }

*{box-sizing:border-box}
body{ background:var(--ground); color:var(--ink); font-family:var(--body);
  line-height:1.6; margin:0; padding:clamp(1rem,4vw,3.5rem) }
.wrap{ max-width:1080px; margin:0 auto; display:flex; flex-direction:column;
  gap:clamp(1.75rem,4vw,3rem) }

header.top{ background:var(--card); border:1px solid var(--rule);
  padding:clamp(1.25rem,3vw,2.25rem); display:flex; flex-direction:column; gap:.75rem }
.kicker{ font-family:var(--data); font-size:.7rem; letter-spacing:.18em;
  text-transform:uppercase; color:var(--steel); margin:0 }
h1{ font-family:var(--display); font-weight:700; letter-spacing:-.02em;
  font-size:clamp(1.9rem,5vw,3rem); line-height:1.03; margin:0;
  text-wrap:balance; text-transform:uppercase }
.lede{ margin:0; max-width:64ch; color:var(--ink-soft); font-size:1.03rem }
.stamp{ align-self:flex-start; margin-top:.4rem; transform:rotate(-2.5deg);
  border:2px solid var(--stamp); color:var(--stamp); font-family:var(--data);
  font-size:.66rem; letter-spacing:.16em; text-transform:uppercase;
  padding:.45rem .8rem; box-shadow:inset 0 0 0 1px var(--stamp) }

.sheet{ background:var(--card); border:1px solid var(--rule);
  padding:clamp(1.1rem,3vw,2rem); display:flex; flex-direction:column; gap:1.2rem }
.sheet-head{ display:flex; flex-wrap:wrap; gap:1rem; align-items:flex-start;
  justify-content:space-between; border-bottom:1px solid var(--rule);
  padding-bottom:1rem }
.eyebrow{ font-family:var(--data); font-size:.72rem; letter-spacing:.1em;
  color:var(--steel); margin:0 0 .3rem }
.sheet h2{ font-family:var(--display); text-transform:uppercase;
  letter-spacing:-.01em; font-size:clamp(1.15rem,2.6vw,1.6rem); margin:0; line-height:1.1 }
.sub{ margin:.25rem 0 0; color:var(--ink-soft); font-size:.95rem }
.verdict{ font-family:var(--data); font-size:.68rem; letter-spacing:.14em;
  text-transform:uppercase; margin:0; padding:.34rem .6rem; white-space:nowrap;
  border:1px solid currentColor; color:var(--steel) }
.verdict[data-ok="0"]{ color:var(--stamp) }

.mount{ margin:0; background:var(--mount); padding:clamp(.9rem,3vw,2rem);
  display:flex; flex-direction:column; gap:.7rem }
.dimline{ display:flex; align-items:center; gap:.5rem; color:var(--ink-soft);
  font-family:var(--data); font-size:.65rem; letter-spacing:.08em }
.dimline::before,.dimline::after{ content:""; height:1px; flex:1;
  background:currentColor; opacity:.5 }
.plate{ line-height:0 }
.plate svg{ display:block; width:100%; height:auto }
figcaption{ color:var(--ink-soft); font-size:.85rem; max-width:62ch; line-height:1.5 }

.chips{ list-style:none; display:flex; flex-wrap:wrap; gap:.9rem; margin:0; padding:0;
  font-family:var(--data); font-size:.68rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-soft) }
.chips li{ display:flex; align-items:center; gap:.4rem }
.dot{ width:.85rem; height:.85rem; border:1px solid var(--rule); display:inline-block }

.specs{ display:grid; grid-template-columns:repeat(auto-fit,minmax(132px,1fr));
  gap:1px; background:var(--rule); border:1px solid var(--rule); margin:0 }
.spec{ background:var(--card); padding:.65rem .8rem }
.spec dt{ font-family:var(--data); font-size:.62rem; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-soft) }
.spec dd{ font-family:var(--data); font-size:.88rem; margin:.25rem 0 0;
  font-variant-numeric:tabular-nums }

.notes{ background:var(--card); border:1px solid var(--rule);
  padding:clamp(1.1rem,3vw,2rem); display:flex; flex-direction:column; gap:.9rem }
.notes h2{ font-family:var(--display); text-transform:uppercase; margin:0;
  font-size:1.25rem; letter-spacing:-.01em }
.notes h3{ font-family:var(--data); font-size:.7rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--steel); margin:.6rem 0 -.4rem }
.notes p,.notes li{ max-width:66ch; color:var(--ink-soft) }
.notes ol,.notes ul{ margin:0; padding-left:1.2rem; display:flex;
  flex-direction:column; gap:.4rem }
.notes strong{ color:var(--ink) }
.warn{ border-left:3px solid var(--stamp); padding-left:.9rem }
pre{ overflow-x:auto; background:var(--mount); padding:.8rem; margin:0;
  font-family:var(--data); font-size:.76rem; line-height:1.5 }
code{ font-family:var(--data); font-size:.88em }
footer{ color:var(--ink-soft); font-family:var(--data); font-size:.68rem;
  letter-spacing:.08em; text-transform:uppercase }
a{ color:var(--steel) }
a:focus-visible{ outline:2px solid var(--steel); outline-offset:2px }
@media (prefers-reduced-motion:reduce){ *{animation:none!important;
  transition:none!important} }
"""

HTML = """<title>ANSI Notice Signs &mdash; 256 &times; 200 mm</title>
<style>{css}</style>
<div class="wrap">
  <header class="top">
    <p class="kicker">Bambu Lab &middot; one AMS unit &middot; four filaments</p>
    <h1>Absurd ANSI notice signs</h1>
    <p class="lede">Three deadpan safety plaques built to the ANSI&nbsp;Z535 and
    ISO&nbsp;7010 grammar &mdash; coloured signal-word header, safety-alert triangle,
    prohibition roundels &mdash; sized to a single build plate with the artwork as a
    flush colour inlay rather than raised type.</p>
    <p class="stamp">Print-ready &middot; watertight &middot; colours disjoint</p>
  </header>

  {sheets}

  <section class="notes" aria-labelledby="h-notes">
    <h2 id="h-notes">Print notes</h2>

    <h3>Why white is free</h3>
    <p>The plate is white and art exists <em>only</em> where a 0.6&nbsp;mm pocket is cut,
    so a white symbol is the <strong>absence</strong> of coloured art with the plate
    showing through at full height. White costs no filament slot &mdash; which is what
    keeps these inside one 4-slot AMS.</p>

    <h3>Colours are separated by subtraction</h3>
    <p>Two colours must never overlap or both parts claim the same pocket. So the yellow
    band is not a rectangle with black drawn on top &mdash; it is:</p>
    <pre>yellow band = band_rect &minus; (triangle &cup; exclamation &cup; letters)</pre>
    <p>Exactly like offset printing plates. The build fails any colour pair overlapping
    by more than 0.02&nbsp;mm&sup2;.</p>

    <h3>Why 256 &times; 200 and not 256 &times; 256</h3>
    <p>The advertised 256&sup3; volume is not usable for a flat footprint. A
    filament-cutter exclusion zone caps real full-width prints at roughly
    <strong>256 &times; 228 mm</strong>, so a full square plate gets rejected by the
    slicer.</p>

    <h3>Slicer setup</h3>
    <ol>
      <li>Import the <code>.3mf</code> &mdash; four objects (<code>plate_white</code>,
      <code>art_black</code>, <code>art_yellow</code>, <code>art_blue</code>), already
      positioned in millimetres. The bilingual sign has no yellow, so it carries three.</li>
      <li>Select all and assemble into one object so they slice as a part group.</li>
      <li>Assign a filament per part by name.</li>
      <li>Layer height <strong>0.2 mm</strong>. The 0.6 mm inlay is exactly three layers,
      so the colour change lands on a layer boundary &mdash; keep the inlay an integer
      multiple of whatever layer height you pick.</li>
    </ol>
    <p>The parts share coincident surfaces with zero clearance. That is correct for
    multi-material parts; don't add a gap.</p>

    <h3>Warping</h3>
    <p class="warn">A 256 &times; 200 mm flat plate is close to the worst case for FDM
    &mdash; maximum leverage for corner lift as the first layers cool. PLA or PETG rather
    than ABS/ASA, brim on, textured PEI, door open for PLA.</p>

    <h3>Standards details worth keeping</h3>
    <ul>
      <li>The <strong>safety-alert triangle</strong> belongs only to DANGER / WARNING /
      CAUTION. NOTICE never carries one, so the bilingual sign has none.</li>
      <li>All three signs are prohibitions, so every pictogram is an ISO
      <strong>prohibition roundel</strong> &mdash; ring, 45&deg; bar, symbol &mdash; not a
      blue mandatory-action disc.</li>
      <li>Pictograms are generated from primitives, not traced artwork, so they scale
      with the layout.</li>
    </ul>

    <h3>Editing</h3>
    <p>Copy lives in display lists at the bottom of
    <code>build_signs_color.py</code>. The 2D dry run takes seconds because glyph widths
    are measured once at a reference size and scaled arithmetically, never re-measured:</p>
    <pre>SIGNS_SVG=1 freecadcmd build_signs_color.py</pre>
    <p>A <strong>4.5 mm cap-height floor</strong> is enforced for a 0.4 mm nozzle; below
    about 1.2 extrusion widths thin strokes print patchy. Overflow is reported, never
    silently shrunk &mdash; including a bounding-box test of all fused art against the
    plate, which catches overflow in directions per-line checks cannot see.</p>

    <h3>On the parody</h3>
    <p>Fictional issuing bodies and no real municipal crest or wordmark, so these read as
    jokes rather than as counterfeit government or regulatory notices.</p>
  </section>

  <footer>Generated from FreeCAD 1.1.1 &middot; previews traced from the extruded
  geometry</footer>
</div>
"""

out = HTML.format(css=CSS, sheets="\n".join(sheet(*s) for s in SHEETS))
dst = os.path.join(HERE, "signs_preview.html")
open(dst, "w").write(out)
print("wrote %s (%.0f KB)" % (dst, os.path.getsize(dst) / 1024.0))
