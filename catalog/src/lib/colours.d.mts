export type Finish =
  | "basic" | "matte" | "silk" | "sparkle" | "translucent"
  | "dual" | "rainbow" | "glow" | "marble";

export type Swatch = { hex: string; finish: Finish; hex2?: string };

export declare const COLOURS: Record<string, Swatch>;
export declare function lookupColour(key: string): Swatch | undefined;
