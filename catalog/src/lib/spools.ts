import type { Finish } from "./colours.mjs";

export type Source = "bambu" | "amazon";
export type Material = "PLA" | "PETG" | "PVA" | "Support";

export type Spool = {
  id: string;
  source: Source;
  brand: string;
  material: Material;
  productLine: string;
  colourName: string;
  colourCode: string;
  hex: string;
  hex2?: string;
  finish: Finish;
  weightKg: number;
  isRefill: boolean;
  orderId: string;
  orderDate: string;
  /** null for every Amazon spool: the order history showed no prices. */
  pricePaidCad: number | null;
};
