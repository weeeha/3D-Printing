import type { Metadata } from "next";
import { ModelsWorkbench } from "@/components/models/ModelsWorkbench";

export const metadata: Metadata = {
  title: "Models",
  description: "Every print-ready file, sliced for the P1S: print time, filament, cost and bed fit.",
};

export default function ModelsPage() {
  return <ModelsWorkbench />;
}
