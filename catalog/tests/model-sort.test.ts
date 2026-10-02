import { describe, it, expect } from "vitest";
import { MODELS } from "@/lib/models";
import { groupByFolder, sortModels } from "@/lib/model-sort";

const ids = (ms: { id: string }[]) => ms.map((m) => m.id);

describe("groupByFolder", () => {
  it("puts folders with sliced files first, then by name, refusals last", () => {
    expect(groupByFolder(MODELS.models).map(([folder]) => folder)).toEqual(["smallclock", "toolkit", "signs"]);
  });
});

describe("sortModels", () => {
  it("sorts by print time, shortest first, with unsliced files last", () => {
    const sorted = sortModels(MODELS.models, "time", "asc");
    expect(ids(sorted).slice(0, 3)).toEqual(["smallclock-cradle", "smallclock-shell", "smallclock-lid"]);
    expect(sorted.slice(-6).every((m) => m.slice.status === "failed")).toBe(true);
  });

  it("keeps unsliced files last when sorting descending", () => {
    const sorted = sortModels(MODELS.models, "cost", "desc");
    expect(sorted[0].id).toBe("kit-9cubes-parts");
    expect(sorted.slice(-6).every((m) => m.slice.status === "failed")).toBe(true);
  });

  it("sorts names case-insensitively", () => {
    expect(sortModels(MODELS.models, "name", "asc")[0].id).toBe("csign-airgap");
    expect(sortModels(MODELS.models, "name", "desc")[0].id).toBe("test-plate-tile-conflict");
  });

  it("does not reorder the input", () => {
    const before = ids(MODELS.models);
    sortModels(MODELS.models, "grams", "desc");
    expect(ids(MODELS.models)).toEqual(before);
  });
});
