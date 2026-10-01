import { strFromU8, unzipSync } from "fflate";

/**
 * A 3MF reader for print files. three's bundled 3MFLoader cannot open Bambu
 * Studio projects: they keep each part in 3D/Objects/object_N.model and point
 * at it from the root model with a `p:path` component, which it does not
 * follow. This reader follows components across files and composes their
 * transforms. It parses with regular expressions, so it runs (and is tested)
 * without a DOM.
 */
export type MeshPart = {
  positions: Float32Array;
  indices: Uint32Array;
  /** Column-major 4x4, ready for THREE.Matrix4.fromArray. */
  matrix: number[];
};

const ROOT = "/3D/3dmodel.model";
const IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];

type ObjectEntry = { body: string };
type Mesh = { positions: Float32Array; indices: Uint32Array };

export function read3mf(bytes: Uint8Array): MeshPart[] {
  const files = unzipSync(bytes, { filter: (f) => f.name.endsWith(".model") });
  const docs: Record<string, string> = {};
  for (const [name, data] of Object.entries(files)) docs[`/${name.replace(/^\//, "")}`] = strFromU8(data);
  return parse3mfDocs(docs);
}

/** Same as read3mf, from model files already unzipped. Keys are paths like "/3D/3dmodel.model". */
export function parse3mfDocs(docs: Record<string, string>): MeshPart[] {
  if (!docs[ROOT]) throw new Error("No 3D/3dmodel.model in this file, so it is not a 3MF model.");

  const objects = new Map<string, Map<string, ObjectEntry>>();
  const objectsIn = (path: string) => {
    let found = objects.get(path);
    if (!found) {
      found = new Map();
      for (const m of (docs[path] ?? "").matchAll(/<object\b([^>]*)>([\s\S]*?)<\/object>/g)) {
        const id = attr(m[1], "id");
        if (id) found.set(id, { body: m[2] });
      }
      objects.set(path, found);
    }
    return found;
  };

  const meshes = new Map<string, Mesh>();
  const parts: MeshPart[] = [];

  function visit(path: string, id: string, matrix: number[], depth: number) {
    if (depth > 16) throw new Error("3MF components nest too deep.");
    const obj = objectsIn(path).get(id);
    if (!obj) return;
    const meshXml = obj.body.match(/<mesh\b[^>]*>([\s\S]*?)<\/mesh>/)?.[1];
    if (meshXml) {
      const key = `${path}#${id}`;
      let mesh = meshes.get(key);
      if (!mesh) meshes.set(key, (mesh = parseMesh(meshXml)));
      parts.push({ ...mesh, matrix });
    }
    for (const c of obj.body.matchAll(/<component\b([^>]*?)\/?>/g)) {
      const childId = attr(c[1], "objectid");
      if (!childId) continue;
      visit(attr(c[1], "p:path") ?? path, childId, multiply(matrix, toMatrix(attr(c[1], "transform"))), depth + 1);
    }
  }

  for (const item of docs[ROOT].matchAll(/<item\b([^>]*?)\/?>/g)) {
    const id = attr(item[1], "objectid");
    if (id) visit(ROOT, id, toMatrix(attr(item[1], "transform")), 0);
  }
  return parts;
}

function parseMesh(xml: string): Mesh {
  const vertexTags = xml.match(/<vertex\b[^>]*>/g) ?? [];
  const positions = new Float32Array(vertexTags.length * 3);
  vertexTags.forEach((tag, i) => {
    positions[i * 3] = Number(attr(tag, "x"));
    positions[i * 3 + 1] = Number(attr(tag, "y"));
    positions[i * 3 + 2] = Number(attr(tag, "z"));
  });
  const triangleTags = xml.match(/<triangle\b[^>]*>/g) ?? [];
  const indices = new Uint32Array(triangleTags.length * 3);
  triangleTags.forEach((tag, i) => {
    indices[i * 3] = Number(attr(tag, "v1"));
    indices[i * 3 + 1] = Number(attr(tag, "v2"));
    indices[i * 3 + 2] = Number(attr(tag, "v3"));
  });
  return { positions, indices };
}

function attr(tag: string, name: string): string | undefined {
  return tag.match(new RegExp(`(?:^|\\s)${name}="([^"]*)"`))?.[1];
}

/** 3MF's "m00 m01 m02 m10 m11 m12 m20 m21 m22 m30 m31 m32" (row vectors) as column-major 4x4. */
function toMatrix(transform: string | undefined): number[] {
  if (!transform) return IDENTITY;
  const e = transform.trim().split(/\s+/).map(Number);
  if (e.length !== 12 || e.some(Number.isNaN)) return IDENTITY;
  return [e[0], e[1], e[2], 0, e[3], e[4], e[5], 0, e[6], e[7], e[8], 0, e[9], e[10], e[11], 1];
}

/** a · b for column-major 4x4: apply b first, then a. */
function multiply(a: number[], b: number[]): number[] {
  const out = new Array<number>(16);
  for (let col = 0; col < 4; col++) {
    for (let row = 0; row < 4; row++) {
      let sum = 0;
      for (let k = 0; k < 4; k++) sum += a[k * 4 + row] * b[col * 4 + k];
      out[col * 4 + row] = sum;
    }
  }
  return out;
}
