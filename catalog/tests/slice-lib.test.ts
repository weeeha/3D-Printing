import { describe, it, expect } from "vitest";
import {
  flattenProfile, parseInfo, boundsOf, bedOffset, placeItems, parseSliceInfo, parsePlate,
  parseSettings, productLine, failureReason, slug,
} from "../scripts/slice-lib.mjs";

// Real Bambu Studio 02.07.01.62 --info output for print/signs/sign_airgap.3mf. It centres every
// object on itself, so its min/max say nothing about where the file actually puts the parts.
const INFO_TWO_OBJECTS = `[sign_airgap.3mf]
size_x = 256.000000
size_y = 200.000000
size_z = 4.000000
min_x = -128.000000
min_y = -100.000000
min_z = -2.000000
max_x = 128.000000
max_y = 100.000000
max_z = 2.000000
number_of_facets = 39878
manifold = yes
number_of_parts =  1
volume = 199960.781250
size_x = 244.000000
size_y = 188.000000
size_z = 0.600000
min_x = -122.000000
min_y = -94.000000
min_z = -0.300000
max_x = 122.000000
max_y = 94.000000
max_z = 0.300000
number_of_facets = 38606
manifold = yes
number_of_parts =  254
volume = 4460.942383
`;

const SLICE_INFO = `<?xml version="1.0" encoding="UTF-8"?>
<config>
  <plate>
    <metadata key="index" value="1"/>
    <metadata key="prediction" value="23397"/>
    <metadata key="weight" value="171.97"/>
    <metadata key="support_used" value="false"/>
    <filament id="1" tray_info_idx="GFA01" type="PLA" color="#FFFFFF" used_m="41.63" used_g="132.16" group_id="0" nozzle_diameter="0.40" volume_type="Standard" used_for_object="true" used_for_support="false"/>
    <filament id="2" tray_info_idx="GFA00" type="PLA" color="#EC008C" used_m="13.14" used_g="39.81" group_id="0" nozzle_diameter="0.40" volume_type="Standard" used_for_object="true" used_for_support="false"/>
  </plate>
</config>`;

describe("flattenProfile", () => {
  const profiles: Record<string, Record<string, unknown>> = {
    "filament/fdm_filament_common": { name: "fdm_filament_common", filament_density: ["0"], filament_cost: ["0"], cooling: "on" },
    "filament/fdm_filament_pla": { name: "fdm_filament_pla", inherits: "fdm_filament_common", filament_density: ["1.24"] },
    "filament/Bambu PLA Basic @BBL X1C": { name: "Bambu PLA Basic @BBL X1C", inherits: "fdm_filament_pla", filament_cost: ["24.99"] },
  };
  const read = (kind: string, name: string) => {
    const p = profiles[`${kind}/${name}`];
    if (!p) throw new Error(`missing ${kind}/${name}`);
    return p;
  };

  it("merges the chain parent first and lets the child win", () => {
    const flat = flattenProfile("filament", "Bambu PLA Basic @BBL X1C", read);
    expect(flat).toMatchObject({
      name: "Bambu PLA Basic @BBL X1C",
      filament_density: ["1.24"],
      filament_cost: ["24.99"],
      cooling: "on",
    });
    expect(flat).not.toHaveProperty("inherits");
  });
});

describe("parseInfo", () => {
  it("counts objects and sums triangles and volume", () => {
    expect(parseInfo(INFO_TWO_OBJECTS)).toEqual({ objects: 2, triangles: 78484, volumeCm3: 204.42 });
  });
});

describe("boundsOf and bedOffset", () => {
  // A unit cube's two opposite corners; each part's matrix is column-major with translation at 12-14.
  const corners = new Float32Array([0, 0, 0, 1, 1, 1]);
  const at = (x: number, y: number, z: number) => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x, y, z, 1];
  const sign = [{ positions: corners, matrix: at(0, 0, 0) }, { positions: corners, matrix: at(255, 199, 3) }];

  it("measures where the file actually puts the parts", () => {
    expect(boundsOf(sign)).toEqual({ min: [0, 0, 0], max: [256, 200, 4], size: [256, 200, 4] });
  });

  it("puts a file modelled at 0..256 on the bed, stepped back from the no-go corner", () => {
    // Centred, this 200 mm-deep sign would sit at Y 28..228 and touch the 18 x 28 mm corner.
    expect(bedOffset(boundsOf(sign))).toEqual([0, 33, 0]);
  });

  it("leaves a centred part alone when it is clear of the corner", () => {
    expect(bedOffset({ min: [0, 0, 0], max: [100, 75, 23] })).toEqual([78, 90.5, 0]);
  });

  it("centres an origin-centred model and drops it to Z=0", () => {
    const offset = bedOffset({ min: [-60.3, -60.3, -20.95], max: [60.3, 60.3, 20.95] });
    expect(offset[0]).toBeCloseTo(128);
    expect(offset[1]).toBeCloseTo(128);
    expect(offset[2]).toBeCloseTo(20.95);
  });
});

describe("placeItems", () => {
  it("moves every build item by the same offset and keeps its objectid", () => {
    const xml = `<build>
<item objectid="1" />
<item objectid="2" transform="1 0 0 0 1 0 0 0 1 5 6 7" />
</build>`;
    const out = placeItems(xml, [10, 20, 30]);
    expect(out).toContain(`<item objectid="1" transform="1 0 0 0 1 0 0 0 1 10 20 30" />`);
    expect(out).toContain(`<item objectid="2" transform="1 0 0 0 1 0 0 0 1 15 26 37" />`);
  });

  it("keeps an item's rotation while adding the offset", () => {
    const xml = `<item objectid="3" transform="0 1 0 -1 0 0 0 0 1 1 2 3"/>`;
    expect(placeItems(xml, [10, 0, 0])).toContain(`transform="0 1 0 -1 0 0 0 0 1 11 2 3"`);
  });
});

describe("parseSliceInfo", () => {
  it("reads time and grams per filament slot", () => {
    expect(parseSliceInfo(SLICE_INFO)).toEqual({
      seconds: 23397,
      filaments: [
        { slot: 1, type: "PLA", hex: "#FFFFFF", grams: 132.16 },
        { slot: 2, type: "PLA", hex: "#EC008C", grams: 39.81 },
      ],
    });
  });
});

describe("parsePlate", () => {
  it("rounds footprints and marks the prime tower", () => {
    const plate = parsePlate(JSON.stringify({
      bbox_objects: [
        { name: "Object_1", bbox: [71.53795, 71.53795, 96.46205, 96.46205] },
        { name: "wipe_tower", bbox: [160.1, 210.2, 192.74894, 244.26242] },
      ],
    }));
    expect(plate).toEqual([
      { name: "Object_1", box: [71.5, 71.5, 96.5, 96.5], tower: false },
      { name: "wipe_tower", box: [160.1, 210.2, 192.7, 244.3], tower: true },
    ]);
  });
});

describe("parseSettings", () => {
  it("pulls the settings the panel shows", () => {
    const s = parseSettings(JSON.stringify({
      printer_settings_id: "Bambu Lab P1S 0.4 nozzle",
      print_settings_id: "0.20mm Standard @BBL X1C",
      filament_settings_id: ["Bambu PLA Matte @BBL P1S 0.4 nozzle", "Bambu PLA Basic @BBL P1S 0.4 nozzle"],
      layer_height: "0.2",
      sparse_infill_density: "15%",
      wall_loops: "2",
      enable_support: "0",
      nozzle_diameter: ["0.4"],
    }));
    expect(s).toEqual({
      settings: {
        printer: "Bambu Lab P1S 0.4 nozzle", process: "0.20mm Standard @BBL X1C",
        layer: 0.2, infill: "15%", walls: 2, supports: false, nozzle: 0.4,
      },
      filamentPresets: ["Bambu PLA Matte @BBL P1S 0.4 nozzle", "Bambu PLA Basic @BBL P1S 0.4 nozzle"],
    });
  });
});

describe("productLine", () => {
  it("names the Bambu product line of a filament preset", () => {
    expect(productLine("Bambu PLA Matte @BBL P1S 0.4 nozzle")).toBe("PLA Matte");
    expect(productLine("Bambu PETG HF @BBL X1C")).toBe("PETG HF");
    expect(productLine("Generic PLA")).toBe("PLA Basic");
    expect(productLine(undefined)).toBe("PLA Basic");
  });
});

describe("failureReason", () => {
  it("explains a G-code conflict between overlapping parts", () => {
    const r = failureReason(" G-code conflicts detected after slicing. Please make sure the 3mf file can be successfully sliced");
    expect(r.short).toBe("G-code conflict");
    expect(r.reason).toMatch(/separate objects that overlap/);
  });
  it("explains an object conflict with the bed", () => {
    expect(failureReason("Object conflicts were detected. Please verify the slicing").short).toBe("object conflict");
  });
  it("falls back to the slicer's own message", () => {
    expect(failureReason("Nothing to be sliced")).toEqual({
      short: "slicer error",
      reason: "Bambu Studio could not slice this file: Nothing to be sliced",
    });
  });
});

describe("slug", () => {
  it("makes a hash-safe id", () => {
    expect(slug("TEST-PLATE_tile+conflict")).toBe("test-plate-tile-conflict");
    expect(slug("smallclock_shell")).toBe("smallclock-shell");
  });
});
