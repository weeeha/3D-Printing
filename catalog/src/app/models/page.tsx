import type { Metadata } from "next";
import { ModelsPage as ModelsView } from "@/components/models/ModelsPage";

export const metadata: Metadata = {
  title: "Models",
  description: "Every print-ready file, sliced for the P1S: print time, filament, cost and bed fit.",
};

export default function ModelsPage() {
  return <ModelsView />;
}
