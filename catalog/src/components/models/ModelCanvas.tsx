"use client";

import { Canvas } from "@react-three/fiber";
import { Bounds, OrbitControls } from "@react-three/drei";
import { Component, Suspense, useEffect, useState, type ReactNode } from "react";
import { Model, type Measure, type PrintFormat } from "./Model";
import { Plate, type PlateColours } from "./Plate";
import type { ViewMode } from "@/lib/view-modes";

export type CanvasProps = {
  url: string;
  format: PrintFormat;
  mode: ViewMode;
  wireframe: boolean;
  colour: string | null;
  /** Plate position under the model, scene X and Z, mm. */
  plateOffset: [number, number];
  onMeasure: (m: Measure) => void;
  onError: (message: string) => void;
};

type Tokens = PlateColours & { background: string };

/** Scene colours follow the page tokens, so the viewer matches light and dark. */
function useTokens(): Tokens | null {
  const [tokens, setTokens] = useState<Tokens | null>(null);
  useEffect(() => {
    const read = () => {
      const cs = getComputedStyle(document.documentElement);
      const v = (name: string) => cs.getPropertyValue(name).trim();
      setTokens({ background: v("--viewport"), bed: v("--bed"), line: v("--bed-line"), noGo: v("--muted") });
    };
    read();
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", read);
    const mo = new MutationObserver(read);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => { mq.removeEventListener("change", read); mo.disconnect(); };
  }, []);
  return tokens;
}

/** A file that will not parse or download reports its reason instead of blanking the canvas. */
class LoadBoundary extends Component<{ onError: (m: string) => void; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: unknown) {
    this.props.onError(error instanceof Error ? error.message : String(error));
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

export default function ModelCanvas(props: CanvasProps) {
  const tokens = useTokens();
  if (!tokens) return null;
  const realistic = props.mode === "realistic";

  return (
    <Canvas shadows camera={{ position: [180, 150, 230], fov: 40, near: 1, far: 5000 }} gl={{ antialias: true }}>
      <color attach="background" args={[tokens.background]} />
      <hemisphereLight args={["#ffffff", "#3a3d3a", props.mode === "geometry" ? 1.3 : 1.05]} />
      <directionalLight
        position={[160, 320, 140]}
        intensity={realistic ? 1.8 : 1.2}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-220}
        shadow-camera-right={220}
        shadow-camera-top={220}
        shadow-camera-bottom={-220}
        shadow-camera-near={1}
        shadow-camera-far={900}
      />
      <Plate offset={props.plateOffset} colours={tokens} />
      <LoadBoundary key={props.url} onError={props.onError}>
        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.25}>
            <Model
              url={props.url}
              format={props.format}
              mode={props.mode}
              wireframe={props.wireframe}
              colour={props.colour}
              onMeasure={props.onMeasure}
            />
          </Bounds>
        </Suspense>
      </LoadBoundary>
      <OrbitControls makeDefault enableDamping />
    </Canvas>
  );
}
