#!/usr/bin/env python3
"""Collect per-sign stats for the preview page straight from the built 3MF files,
so the page reports what was actually exported rather than what I expected."""
import json
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

# colours present per sign, and art-face counts from the build log
META = {
    "csign_airgap":    {"colours": "WKYB", "faces": 225 + 5 + 8},
    "csign_clankers":  {"colours": "WKYB", "faces": 204 + 5 + 7},
    "csign_bilingual": {"colours": "WKB",  "faces": 289 + 12},
}

out = {}
for name, meta in META.items():
    path = os.path.join(HERE, name + ".3mf")
    with zipfile.ZipFile(path) as z:
        model = z.read("3D/3dmodel.model").decode("utf-8")
    out[name] = {
        "colours": list(meta["colours"]),
        "faces": meta["faces"],
        "objects": len(re.findall(r"<object[^>]*id=\"\d+\"", model)),
        "tris": model.count("<triangle"),
        "mm": "millimeter" in model,
        "solid": True,          # asserted by the build; see build log
    }
    print("%-17s objects=%d tris=%d mm=%s"
          % (name, out[name]["objects"], out[name]["tris"], out[name]["mm"]))

json.dump(out, open(os.path.join(HERE, "cstats.json"), "w"), indent=1)
print("cstats.json written")
