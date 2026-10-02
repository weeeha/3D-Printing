export type ViewMode = "geometry" | "surface" | "realistic";

export const VIEW_MODES: { id: ViewMode; label: string }[] = [
  { id: "geometry", label: "Geometry" },
  { id: "surface", label: "Surface" },
  { id: "realistic", label: "Realistic" },
];
