"use client";

import { useLoader } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import { STLLoader, toCreasedNormals } from "three-stdlib";
import * as THREE from "three";
import { ThreeMfLoader } from "./ThreeMfLoader";
import type { ViewMode } from "@/lib/view-modes";

// Adapted from 3d-models-playground's components/scene/Model.tsx, narrowed to print formats.

export type PrintFormat = "3mf" | "stl";
/** Print size in mm as X × Y × Z (Z up), and mesh volume. */
export type Measure = { size: [number, number, number]; volumeCm3: number };

type Props = {
  url: string;
  format: PrintFormat;
  mode: ViewMode;
  wireframe: boolean;
  /** Filament colour for Realistic; null shows neutral plastic. */
  colour: string | null;
  onMeasure?: (m: Measure) => void;
};

const CREASE_ANGLE = THREE.MathUtils.degToRad(30);
const EDGE_ANGLE = 30;

// One shared material per study mode; only one model is on screen at a time.
const geometryMaterial = new THREE.MeshStandardMaterial({ color: "#b9bcc1", roughness: 1, metalness: 0, flatShading: true });
const surfaceMaterial = new THREE.MeshStandardMaterial({ color: "#cfc9c0", roughness: 0.85, metalness: 0 });
const edgeMaterial = new THREE.LineBasicMaterial({ color: "#1c1c1c" });

type MeshState = { flat: THREE.BufferGeometry; smooth: THREE.BufferGeometry; edges: THREE.LineSegments };

/**
 * Per-mesh variants, built once per loaded object: flat = one normal per
 * triangle, smooth = creased at 30°, plus hard edges for Geometry. Cached on
 * the object, so StrictMode's second useMemo call adds nothing.
 */
function prepare(object: THREE.Object3D) {
  const cached = object.userData.viewStates as Map<THREE.Mesh, MeshState> | undefined;
  if (cached) return cached;
  const states = new Map<THREE.Mesh, MeshState>();
  object.traverse((child) => {
    const mesh = child as THREE.Mesh;
    if (!mesh.isMesh) return;
    mesh.castShadow = true;
    const flat = mesh.geometry.index ? mesh.geometry.toNonIndexed() : mesh.geometry.clone();
    flat.computeVertexNormals();
    const smooth = toCreasedNormals(flat.clone(), CREASE_ANGLE);
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(flat, EDGE_ANGLE), edgeMaterial);
    edges.raycast = () => {};
    mesh.add(edges);
    states.set(mesh, { flat, smooth, edges });
  });
  object.userData.viewStates = states;
  return states;
}

function applyMode(states: Map<THREE.Mesh, MeshState>, mode: ViewMode, wireframe: boolean, realistic: THREE.Material) {
  const material = mode === "geometry" ? geometryMaterial : mode === "surface" ? surfaceMaterial : realistic;
  (material as THREE.MeshStandardMaterial).wireframe = wireframe;
  for (const [mesh, s] of states) {
    mesh.material = material;
    mesh.geometry = mode === "geometry" ? s.flat : s.smooth;
    // Only Realistic has soft shadows on itself; in study modes self-shadowing just adds acne.
    mesh.receiveShadow = mode === "realistic";
    s.edges.visible = mode === "geometry" && !wireframe;
  }
}

/** Print formats are Z-up: stand the model up, centre it on X/Z and set it on the plate (Y=0). */
function grounding(object: THREE.Object3D) {
  const box = new THREE.Box3().setFromObject(object);
  box.applyMatrix4(new THREE.Matrix4().makeRotationX(-Math.PI / 2));
  const center = box.getCenter(new THREE.Vector3());
  return { position: new THREE.Vector3(-center.x, -box.min.y, -center.z), size: box.getSize(new THREE.Vector3()) };
}

/** Mesh volume from signed tetrahedra, cm³. */
function volumeOf(object: THREE.Object3D) {
  let v = 0;
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  object.updateMatrixWorld(true);
  object.traverse((child) => {
    const mesh = child as THREE.Mesh;
    if (!mesh.isMesh) return;
    const pos = mesh.geometry.attributes.position;
    const idx = mesh.geometry.index;
    const n = idx ? idx.count : pos.count;
    for (let i = 0; i < n; i += 3) {
      a.fromBufferAttribute(pos, idx ? idx.getX(i) : i).applyMatrix4(mesh.matrixWorld);
      b.fromBufferAttribute(pos, idx ? idx.getX(i + 1) : i + 1).applyMatrix4(mesh.matrixWorld);
      c.fromBufferAttribute(pos, idx ? idx.getX(i + 2) : i + 2).applyMatrix4(mesh.matrixWorld);
      v += a.dot(b.cross(c)) / 6;
    }
  });
  return Math.abs(v) / 1000;
}

function LoadedModel({ object, mode, wireframe, colour, onMeasure }: Omit<Props, "url" | "format"> & { object: THREE.Object3D }) {
  const volumeCm3 = useMemo(() => volumeOf(object), [object]);
  const states = useMemo(() => prepare(object), [object]);
  const realistic = useMemo(
    () => new THREE.MeshPhysicalMaterial({ color: colour ?? "#e4e3df", roughness: 0.42, metalness: 0, clearcoat: 0.2, clearcoatRoughness: 0.5 }),
    [colour],
  );
  useEffect(() => () => realistic.dispose(), [realistic]);
  useEffect(() => applyMode(states, mode, wireframe, realistic), [states, mode, wireframe, realistic]);
  const grounded = useMemo(() => grounding(object), [object]);
  useEffect(() => {
    const s = grounded.size;
    onMeasure?.({ size: [s.x, s.z, s.y], volumeCm3 });
  }, [grounded, volumeCm3, onMeasure]);

  return (
    <group position={grounded.position}>
      <group rotation={[-Math.PI / 2, 0, 0]}>
        <primitive object={object} />
      </group>
    </group>
  );
}

function ThreeMfSource({ url, ...rest }: Omit<Props, "format">) {
  const group = useLoader(ThreeMfLoader, url);
  const object = useMemo(() => group.clone(true), [group]);
  return <LoadedModel object={object} {...rest} />;
}

function StlSource({ url, ...rest }: Omit<Props, "format">) {
  const geometry = useLoader(STLLoader, url);
  const object = useMemo(() => new THREE.Mesh(geometry), [geometry]);
  return <LoadedModel object={object} {...rest} />;
}

export function Model({ format, ...rest }: Props) {
  return format === "stl" ? <StlSource {...rest} /> : <ThreeMfSource {...rest} />;
}
