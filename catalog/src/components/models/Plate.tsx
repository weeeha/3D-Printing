"use client";

import { useMemo } from "react";
import * as THREE from "three";
import { BED, NO_GO } from "@/lib/models";

export type PlateColours = { bed: string; line: string; noGo: string };

const GRID_STEP = 32;

/**
 * The P1S build plate in scene units (mm). Bed X maps to scene X and bed Y to
 * scene -Z, so the front edge (Y=0) faces the default camera. `offset` moves
 * the plate under the model so parts sit where the slicer placed them.
 */
export function Plate({ offset, colours }: { offset: [number, number]; colours: PlateColours }) {
  const grid = useMemo(() => {
    const half = BED / 2;
    const pts: number[] = [];
    for (let v = 0; v <= BED; v += GRID_STEP) {
      pts.push(v - half, 0, -half, v - half, 0, half, -half, 0, v - half, half, 0, v - half);
    }
    return new THREE.BufferGeometry().setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
  }, []);
  const [x0, y0, x1, y1] = NO_GO;

  return (
    <group position={[offset[0], 0, offset[1]]}>
      <mesh rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[BED, BED]} />
        <meshStandardMaterial color={colours.bed} roughness={0.95} />
      </mesh>
      <lineSegments geometry={grid} position-y={0.05}>
        <lineBasicMaterial color={colours.line} />
      </lineSegments>
      <mesh rotation-x={-Math.PI / 2} position={[(x0 + x1) / 2 - BED / 2, 0.1, BED / 2 - (y0 + y1) / 2]}>
        <planeGeometry args={[x1 - x0, y1 - y0]} />
        <meshBasicMaterial color={colours.noGo} transparent opacity={0.2} />
      </mesh>
    </group>
  );
}
