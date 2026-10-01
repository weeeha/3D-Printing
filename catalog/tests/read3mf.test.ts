import { describe, it, expect } from "vitest";
import { strToU8, zipSync } from "fflate";
import { read3mf } from "@/lib/read3mf";

const NS = `xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"`;

// A unit tetrahedron: 4 vertices, 4 triangles. Attributes deliberately out of order on one vertex.
const TETRA_MESH = `<mesh><vertices>
  <vertex x="0" y="0" z="0"/><vertex x="1" y="0" z="0"/><vertex z="0" x="0" y="1"/><vertex x="0" y="0" z="1"/>
</vertices><triangles>
  <triangle v1="0" v2="2" v3="1"/><triangle v1="0" v2="1" v3="3"/><triangle v1="0" v2="3" v3="2"/><triangle v1="1" v2="2" v3="3"/>
</triangles></mesh>`;

const zip = (files: Record<string, string>) =>
  zipSync(Object.fromEntries(Object.entries(files).map(([k, v]) => [k, strToU8(v)])));

/** Apply a column-major 4x4 to a point. */
const apply = (m: number[], [x, y, z]: number[]) => [
  m[0] * x + m[4] * y + m[8] * z + m[12],
  m[1] * x + m[5] * y + m[9] * z + m[13],
  m[2] * x + m[6] * y + m[10] * z + m[14],
];

describe("read3mf", () => {
  it("reads a bare mesh with no transform", () => {
    const parts = read3mf(zip({
      "3D/3dmodel.model": `<model unit="millimeter" ${NS}><resources><object id="1" type="model">${TETRA_MESH}</object></resources><build><item objectid="1"/></build></model>`,
    }));
    expect(parts).toHaveLength(1);
    expect(Array.from(parts[0].positions)).toEqual([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]);
    expect(Array.from(parts[0].indices)).toEqual([0, 2, 1, 0, 1, 3, 0, 3, 2, 1, 2, 3]);
    expect(parts[0].matrix).toEqual([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  });

  it("follows components into other model files, as Bambu Studio projects do", () => {
    const parts = read3mf(zip({
      "3D/3dmodel.model": `<model unit="millimeter" ${NS}><resources>
        <object id="5" type="model"><components>
          <component p:path="/3D/Objects/object_1.model" objectid="1" transform="1 0 0 0 1 0 0 0 1 10 0 0"/>
          <component p:path="/3D/Objects/object_1.model" objectid="2" transform="1 0 0 0 1 0 0 0 1 0 20 0"/>
        </components></object>
      </resources><build><item objectid="5" transform="1 0 0 0 1 0 0 0 1 100 100 0"/></build></model>`,
      "3D/Objects/object_1.model": `<model unit="millimeter" ${NS}><resources>
        <object id="1" type="model">${TETRA_MESH}</object>
        <object id="2" type="model">${TETRA_MESH}</object>
      </resources></model>`,
    }));
    expect(parts).toHaveLength(2);
    // Component translation composes with the build item's: origin lands at (110,100,0) and (100,120,0).
    expect(apply(parts[0].matrix, [0, 0, 0])).toEqual([110, 100, 0]);
    expect(apply(parts[1].matrix, [0, 0, 0])).toEqual([100, 120, 0]);
  });

  it("applies rotation from a 3MF row-major transform", () => {
    // 90° about Z: x axis maps to y.
    const parts = read3mf(zip({
      "3D/3dmodel.model": `<model ${NS}><resources><object id="1">${TETRA_MESH}</object></resources>
        <build><item objectid="1" transform="0 1 0 -1 0 0 0 0 1 0 0 0"/></build></model>`,
    }));
    expect(apply(parts[0].matrix, [1, 0, 0]).map((v) => Math.round(v))).toEqual([0, 1, 0]);
  });

  it("says what is wrong with a file that has no model", () => {
    expect(() => read3mf(zip({ "Metadata/other.txt": "x" }))).toThrow("No 3D/3dmodel.model");
  });
});
