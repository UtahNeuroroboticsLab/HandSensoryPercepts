#!/usr/bin/env python3
"""
Analyze hand sensory percept SVG files from the HandSensoryPercepts web app.

For each electrode combination SVG, extracts:
  1. Whether the combination elicited any sensation (any region non-white)
  2. A dict of all 91 regions with their fill colors and anatomical labels

Region labeling follows the convention:
  T1-T8   = Thumb
  I1-I12  = Index finger
  M1-M12  = Middle finger
  R1-R12  = Ring finger
  K1-K12  = Pinky (K to avoid collision with Palm P)
  P1-P16  = Palm
  W1-W11  = Wrist

NOTE: The region-to-label mapping must be defined per hand side (left/right).
      A default mapping is provided based on typical region ordering from the
      flood-fill algorithm. You should verify/adjust it by visual inspection
      of one REF SVG per hand side.

Usage:
    python analyze_percepts.py <patient_dir> [--output results.json]

Example:
    python analyze_percepts.py ./PatientData/p6 --output p6_results.json
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Region extraction
# ---------------------------------------------------------------------------

REGION_PATTERN = re.compile(
    r'data-region="(region-\d+)"[^/]*?fill="(#[0-9a-fA-F]+)"'
)

WHITE_COLORS = {"#ffffff", "#fff", "#FFFFFF", "#FFF"}


def extract_regions(svg_path: str) -> dict:
    """
    Parse an SVG file and return a dict mapping region IDs to fill colors.

    Returns:
        {"region-001": "#ffffff", "region-002": "#ffe600", ...}
    """
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    regions = {}
    for match in REGION_PATTERN.finditer(content):
        region_id = match.group(1)
        fill_color = match.group(2).lower()
        regions[region_id] = fill_color

    return regions


def has_sensation(regions: dict) -> bool:
    """Return True if any region has a non-white fill."""
    return any(color not in WHITE_COLORS for color in regions.values())


def non_white_regions(regions: dict) -> dict:
    """Return only the regions with non-white fills."""
    return {
        rid: color for rid, color in regions.items()
        if color not in WHITE_COLORS
    }


# ---------------------------------------------------------------------------
# Filename parsing (when no manifest.csv is available)
# ---------------------------------------------------------------------------

FILENAME_PATTERN = re.compile(
    r"(\d+)_hand_(\d+)_of_(\d+)_(left|right)_"
    r"(?:REF_(\d+)|anode-(Ch\d+)_cathode-(Ch\d+))"
    r"\.svg$"
)


def parse_filename(filename: str) -> dict:
    """
    Extract metadata from an SVG filename.

    Returns dict with keys:
        patient_id, hand_number, total_hands, hand_side,
        item_type ("reference" | "stimulus"),
        ref_number (if reference), anode, cathode (if stimulus),
        title (human-readable label)
    """
    m = FILENAME_PATTERN.match(filename)
    if not m:
        return {"filename": filename, "parse_error": True}

    info = {
        "patient_id": m.group(1),
        "hand_number": int(m.group(2)),
        "total_hands": int(m.group(3)),
        "hand_side": m.group(4),
    }

    if m.group(5):  # REF
        info["item_type"] = "reference"
        info["ref_number"] = int(m.group(5))
        info["title"] = f"REF_{m.group(5).zfill(2)}"
    else:
        info["item_type"] = "stimulus"
        info["anode"] = m.group(6)
        info["cathode"] = m.group(7)
        info["title"] = f"{m.group(6)}-->{m.group(7)}"

    return info


# ---------------------------------------------------------------------------
# Manifest parsing
# ---------------------------------------------------------------------------

def load_manifest(manifest_path: str) -> list:
    """Load manifest.csv and return list of dicts."""
    rows = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Region label mapping
# ---------------------------------------------------------------------------

# This is a TEMPLATE mapping for a right hand with 91 regions.
# Region numbering depends on the flood-fill order, which runs roughly
# top-to-bottom, left-to-right in the SVG coordinate space.
#
# You MUST verify this mapping by opening a REF SVG and comparing
# region numbers to anatomical positions. To help with this, the script
# can dump a numbered region report (see --dump-regions flag).
#
# For now, we output region IDs as-is (region-001 through region-091)
# and provide a stub mapping that you fill in after visual verification.

def get_default_label_map() -> dict:
    """
    Return a dict mapping region-XXX to anatomical labels.

    This returns a placeholder identity mapping. Replace with the real
    mapping after visual verification of one reference SVG.
    """
    # Placeholder: just use region numbers
    return {f"region-{i:03d}": f"region-{i:03d}" for i in range(1, 92)}


def load_label_map(path: str) -> dict:
    """
    Load a region label map from a JSON file.

    Expected format: {"region-001": "T1", "region-002": "T2", ...}
    """
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_patient(patient_dir: str, label_map: dict = None) -> dict:
    """
    Analyze all SVG files in a patient directory.

    Returns:
        {
            "patient_dir": "...",
            "hand_side": "right",
            "total_svgs": 100,
            "combinations": [
                {
                    "filename": "...",
                    "title": "Ch00-->Ch01",
                    "item_type": "stimulus",
                    "anode": "Ch00",
                    "cathode": "Ch01",
                    "sensation_detected": true,
                    "num_active_regions": 5,
                    "regions": {
                        "T1": {"color": "#ffffff", "active": false},
                        "T2": {"color": "#ffe600", "active": true},
                        ...
                    }
                },
                ...
            ],
            "summary": {
                "total_stimulus_combinations": 90,
                "combinations_with_sensation": 45,
                "combinations_without_sensation": 45,
                "reference_hands": 10,
                "references_with_marks": 2
            }
        }
    """
    patient_dir = Path(patient_dir)
    if label_map is None:
        label_map = get_default_label_map()

    # Check for manifest
    manifest_path = patient_dir / "manifest.csv"
    manifest_lookup = {}
    if manifest_path.exists():
        rows = load_manifest(str(manifest_path))
        for row in rows:
            if row.get("filename"):
                manifest_lookup[row["filename"]] = row

    # Find all SVG files
    svg_files = sorted(patient_dir.glob("*.svg"))
    if not svg_files:
        print(f"No SVG files found in {patient_dir}", file=sys.stderr)
        return None

    results = {
        "patient_dir": str(patient_dir),
        "hand_side": None,
        "total_svgs": len(svg_files),
        "combinations": [],
    }

    stim_count = 0
    stim_with_sensation = 0
    ref_count = 0
    ref_with_marks = 0

    for svg_path in svg_files:
        fname = svg_path.name

        # Get metadata from manifest or filename
        if fname in manifest_lookup:
            meta = manifest_lookup[fname]
            info = {
                "filename": fname,
                "title": meta.get("item_title", ""),
                "item_type": meta.get("item_type", "unknown"),
                "hand_side": meta.get("hand_side", ""),
                "anode": meta.get("anode", ""),
                "cathode": meta.get("cathode", ""),
            }
        else:
            info = parse_filename(fname)
            info["filename"] = fname

        if results["hand_side"] is None and info.get("hand_side"):
            results["hand_side"] = info["hand_side"]

        # Extract region colors
        raw_regions = extract_regions(str(svg_path))
        sensation = has_sensation(raw_regions)
        active_count = len(non_white_regions(raw_regions))

        # Build labeled region dict
        labeled_regions = {}
        for region_id, color in sorted(raw_regions.items()):
            label = label_map.get(region_id, region_id)
            labeled_regions[label] = {
                "color": color,
                "active": color not in WHITE_COLORS,
            }

        entry = {
            "filename": fname,
            "title": info.get("title", ""),
            "item_type": info.get("item_type", "unknown"),
            "sensation_detected": sensation,
            "num_active_regions": active_count,
            "regions": labeled_regions,
        }

        if info.get("item_type") == "stimulus":
            entry["anode"] = info.get("anode", "")
            entry["cathode"] = info.get("cathode", "")
            stim_count += 1
            if sensation:
                stim_with_sensation += 1
        elif info.get("item_type") == "reference":
            ref_count += 1
            if sensation:
                ref_with_marks += 1

        results["combinations"].append(entry)

    results["summary"] = {
        "total_stimulus_combinations": stim_count,
        "combinations_with_sensation": stim_with_sensation,
        "combinations_without_sensation": stim_count - stim_with_sensation,
        "reference_hands": ref_count,
        "references_with_marks": ref_with_marks,
    }

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze hand sensory percept SVG files"
    )
    parser.add_argument(
        "patient_dir",
        help="Path to a patient directory containing SVG files"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output JSON file path (default: print to stdout)"
    )
    parser.add_argument(
        "--label-map",
        default=None,
        help="Path to a JSON file mapping region IDs to anatomical labels"
    )
    parser.add_argument(
        "--dump-regions",
        action="store_true",
        help="Print region IDs and their fill counts across all SVGs (for building label maps)"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the summary, not per-combination details"
    )

    args = parser.parse_args()

    # Dump mode: show region stats to help build label maps
    if args.dump_regions:
        patient_dir = Path(args.patient_dir)
        svg_files = sorted(patient_dir.glob("*.svg"))

        # Count how often each region is non-white
        from collections import Counter
        region_activity = Counter()

        for svg_path in svg_files:
            raw = extract_regions(str(svg_path))
            for rid, color in raw.items():
                if color not in WHITE_COLORS:
                    region_activity[rid] += 1

        print(f"Region activity across {len(svg_files)} SVGs:")
        print(f"{'Region':<15} {'Times Active':<15} {'Pct':>6}")
        print("-" * 38)
        for rid in sorted(region_activity.keys()):
            count = region_activity[rid]
            pct = 100.0 * count / len(svg_files)
            print(f"{rid:<15} {count:<15} {pct:5.1f}%")

        inactive = set(f"region-{i:03d}" for i in range(1, 92)) - set(region_activity.keys())
        if inactive:
            print(f"\nNever-active regions ({len(inactive)}):")
            print(", ".join(sorted(inactive)))

        return

    # Normal analysis mode
    label_map = None
    if args.label_map:
        label_map = load_label_map(args.label_map)

    results = analyze_patient(args.patient_dir, label_map)
    if results is None:
        sys.exit(1)

    if args.summary_only:
        output = {
            "patient_dir": results["patient_dir"],
            "hand_side": results["hand_side"],
            "total_svgs": results["total_svgs"],
            "summary": results["summary"],
            "sensation_by_combination": [
                {
                    "title": c["title"],
                    "item_type": c["item_type"],
                    "sensation_detected": c["sensation_detected"],
                    "num_active_regions": c["num_active_regions"],
                }
                for c in results["combinations"]
            ],
        }
    else:
        output = results

    json_str = json.dumps(output, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(json_str)
        print(f"Results written to {args.output}", file=sys.stderr)
        print(f"Summary: {results['summary']}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
