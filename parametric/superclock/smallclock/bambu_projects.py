"""
Bambu Studio presets and project files for the final smallclock parts (P1S, 0.4 mm nozzle).

    python3 bambu_projects.py

Reads the print-ready STLs in print/smallclock/ and writes print/smallclock/bambu/:
  <part>.3mf           Bambu project with printer, filament and process set: open and slice
  <part>.gcode.3mf     the same, already sliced (fit tests only): open and send to the printer
  presets/*.json       the processes as user presets, for Bambu Studio > File > Import > Import Configs

Everything inherits from Bambu's own system presets (read from the installed app), so only the
smallclock changes are spelled out below. Rerun after the CAD changes.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

APP = "/Applications/BambuStudio.app"
PROFILES = os.path.join(APP, "Contents/Resources/profiles/BBL")
HERE = os.path.dirname(os.path.abspath(__file__))
PRINT_DIR = os.path.normpath(os.path.join(HERE, "../../../print/smallclock"))
OUT = os.path.join(PRINT_DIR, "bambu")

MACHINE = "Bambu Lab P1S 0.4 nozzle"
MACHINE_MODEL = "Bambu Lab P1S"                     # its default plate (Textured PEI) and model id
BASE_PROCESS = "0.20mm Standard @BBL X1C"          # Bambu's 0.20 mm process for the P1S 0.4
PLA = "Bambu PLA Basic @BBL P1S 0.4 nozzle"         # fit tests: dimensions only, PLA is fine
PETG = "Bambu PETG HF @BBL P1S 0.4 nozzle"          # finals: a Pi 4 behind a screen runs warm

# The smallclock settings on top of the base process (see the README's print settings table)
BODY = {"wall_loops": "3", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid",
        "enable_support": "1", "support_type": "tree(auto)", "support_on_build_plate_only": "1"}
PROCESSES = {
    # front ring on the bed; an inner brim keeps the visible flush edge clean
    "smallclock flush dome": {**BODY, "brim_type": "inner_only", "brim_width": "4"},
    # stands on the 1.2 mm rabbet wall, which the bezel skirt later hides
    "smallclock pebble body": {**BODY, "brim_type": "outer_only", "brim_width": "5"},
    "smallclock bezel": {"wall_loops": "3", "enable_support": "0", "brim_type": "no_brim"},
}

# part -> (STL in print/smallclock, process, filament, also slice it)
PARTS = {
    "smallclock_dome_flush_fit_test": ("smallclock_dome_flush_balanced_fit_test.stl", "smallclock flush dome", PLA, True),
    "smallclock_dome_flush_body": ("smallclock_dome_flush_balanced_body.stl", "smallclock flush dome", PETG, False),
    "smallclock_pebble_fit_test": ("smallclock_pebble_fit_test.stl", "smallclock pebble body", PLA, True),
    "smallclock_pebble_body": ("smallclock_pebble_body.stl", "smallclock pebble body", PETG, False),
    "smallclock_pebble_bezel": ("smallclock_pebble_bezel.stl", "smallclock bezel", PETG, False),
}


def index(kind):
    """System preset name -> file, for one preset kind (machine, process, filament)."""
    names = {}
    folder = os.path.join(PROFILES, kind)
    for f in os.listdir(folder):
        if f.endswith(".json"):
            with open(os.path.join(folder, f)) as fh:
                name = json.load(fh).get("name")      # a few files are G-code templates, not presets
            if name:
                names[name] = os.path.join(folder, f)
    return names


def resolve(kind, name, _index={}):
    """A system preset with its whole inherits chain flattened, as the CLI wants it."""
    if kind not in _index:
        _index[kind] = index(kind)
    with open(_index[kind][name]) as fh:
        preset = json.load(fh)
    flat = resolve(kind, preset["inherits"]) if preset.get("inherits") else {}
    flat.update({k: v for k, v in preset.items() if k != "inherits"})
    return flat


def write_json(path, data):
    with open(path, "w") as fh:
        json.dump(data, fh, indent=4)


def user_preset(name, overrides):
    """An importable Bambu Studio user preset: the base process plus our changes."""
    return {"type": "process", "name": name, "inherits": BASE_PROCESS, "from": "User",
            "instantiation": "true", "print_settings_id": name, **overrides}


def stamp_model_id(path, model_id):
    """The CLI leaves printer_model_id blank in a sliced file; the GUI writes the model's id
    (C12 for the P1S), and the printer checks it before it prints. The G-code is untouched."""
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item)
            if item.filename == "Metadata/slice_info.config":
                data = data.replace(b'key="printer_model_id" value=""',
                                    f'key="printer_model_id" value="{model_id}"'.encode())
            dst.writestr(item, data)
    os.replace(tmp, path)


def build(part, stl, process, filament, slice_it, tmp):
    model = resolve("machine", MACHINE_MODEL)
    # The CLI does not apply the printer's default plate the way the GUI does (it fell back to the Cool Plate)
    machine = {**resolve("machine", MACHINE), "from": "system", "curr_bed_type": model["default_bed_type"]}
    proc = {**resolve("process", BASE_PROCESS), **PROCESSES[process],
            "name": process, "inherits": BASE_PROCESS, "from": "User", "print_settings_id": process}
    fil = {**resolve("filament", filament), "from": "system"}
    paths = [os.path.join(tmp, f"{part}_{k}.json") for k in ("machine", "process", "filament")]
    for path, data in zip(paths, (machine, proc, fil)):
        write_json(path, data)
    outputs = [(f"{part}.3mf", [])] + ([(f"{part}.gcode.3mf", ["--slice", "0"])] if slice_it else [])
    for out_name, extra in outputs:
        cmd = [os.path.join(APP, "Contents/MacOS/BambuStudio"), "--orient", "0", "--arrange", "1",
               "--load-settings", f"{paths[0]};{paths[1]}", "--load-filaments", paths[2],
               *extra, "--export-3mf", out_name, "--outputdir", OUT, os.path.join(PRINT_DIR, stl)]
        run = subprocess.run(cmd, capture_output=True, text=True)
        target = os.path.join(OUT, out_name)
        if run.returncode != 0 or not os.path.exists(target):
            sys.exit(f"{out_name}: BambuStudio failed ({run.returncode})\n{(run.stdout + run.stderr)[-2000:]}")
        if extra:
            stamp_model_id(target, model["model_id"])
        print(f"{out_name:44s} {process} / {filament}" + summary(target))


def summary(path):
    """Print time and filament from a sliced file's G-code header, if it has one."""
    with zipfile.ZipFile(path) as z:
        gcode = [n for n in z.namelist() if n.endswith(".gcode")]
        if not gcode:
            return ""
        head = z.read(gcode[0])[:20000].decode(errors="ignore")
    time = re.search(r"total estimated time: ([^;\n]+)", head)
    grams = re.search(r"total filament weight \[g\] : ([\d.]+)", head)
    return f"  ->  {time.group(1).strip() if time else '?'}, {grams.group(1) if grams else '?'} g"


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "presets"), exist_ok=True)
    for name, overrides in PROCESSES.items():
        write_json(os.path.join(OUT, "presets", f"{name}.json"), user_preset(name, overrides))
    with tempfile.TemporaryDirectory() as tmp:
        for part, (stl, process, filament, slice_it) in PARTS.items():
            build(part, stl, process, filament, slice_it, tmp)
    for leftover in ("plate_1.gcode", "result.json"):       # the CLI's own side files
        if os.path.exists(os.path.join(OUT, leftover)):
            os.remove(os.path.join(OUT, leftover))
