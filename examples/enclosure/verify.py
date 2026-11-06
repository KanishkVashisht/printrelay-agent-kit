#!/usr/bin/env python3
"""Independently inspect this example's ASCII STL files; Python standard library only.

This bounded fixture check measures geometry. It does not certify printability,
fit, wall thickness, self-intersection freedom, strength, or application safety.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
VERTEX = re.compile(rf"vertex\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})$")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(data):
    """Parse only the generated single-solid ASCII STL grammar, without repair."""
    lines = [line.strip() for line in data.decode("ascii").splitlines() if line.strip()]
    if not lines or not re.fullmatch(r"solid(?: .*)?", lines[0]) or not re.fullmatch(r"endsolid(?: .*)?", lines[-1]):
        raise ValueError("Expected one ASCII STL solid.")
    triangles = []
    interior = lines[1:-1]
    if not interior or len(interior) % 7:
        raise ValueError("Incomplete STL facets.")
    for offset in range(0, len(interior), 7):
        facet = interior[offset:offset+7]
        if not facet[0].startswith("facet normal ") or facet[1] != "outer loop" or facet[5:] != ["endloop", "endfacet"]:
            raise ValueError("Invalid STL facet grammar.")
        normal = [float(value) for value in facet[0].split()[2:]]
        if len(normal) != 3 or not all(math.isfinite(v) for v in normal):
            raise ValueError("Invalid stored normal.")
        points = []
        for line in facet[2:5]:
            match = VERTEX.fullmatch(line)
            if not match:
                raise ValueError("Invalid vertex line.")
            point = tuple(map(float, match.groups()))
            if not all(math.isfinite(v) for v in point):
                raise ValueError("Non-finite coordinate.")
            points.append(point)
        triangles.append(tuple(points))
    vertices = sorted({point for triangle in triangles for point in triangle})
    edge_uses, seen = defaultdict(list), set()
    signed_volume = 0.0
    for index, triangle in enumerate(triangles):
        identity = tuple(sorted(triangle))
        if identity in seen:
            raise ValueError("Duplicate triangle.")
        seen.add(identity)
        a, b, c = triangle
        u, v = [b[i]-a[i] for i in range(3)], [c[i]-a[i] for i in range(3)]
        cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        if sum(n*n for n in cross) <= 1e-16:
            raise ValueError("Degenerate triangle.")
        signed_volume += sum(a[i]*cross[i] for i in range(3))/6
        for start, end in ((a,b),(b,c),(c,a)):
            key = tuple(sorted((start,end)))
            edge_uses[key].append((index, 1 if start == key[0] else -1))
    adjacent = defaultdict(set)
    for uses in edge_uses.values():
        if len(uses) != 2 or uses[0][1] + uses[1][1] != 0:
            raise ValueError("Open/non-manifold edge or inconsistent winding.")
        a, b = uses[0][0], uses[1][0]
        adjacent[a].add(b)
        adjacent[b].add(a)
    reached, todo = set(), [0]
    while todo:
        current = todo.pop()
        if current not in reached:
            reached.add(current)
            todo.extend(adjacent[current] - reached)
    if len(reached) != len(triangles) or signed_volume <= 0:
        raise ValueError("Expected one connected component with positive winding.")
    lower = [min(v[i] for v in vertices) for i in range(3)]
    upper = [max(v[i] for v in vertices) for i in range(3)]
    return {
        "file_sha256": hashlib.sha256(data).hexdigest(), "file_bytes": len(data),
        "bounds_mm": {"min": lower, "max": upper},
        "extents_mm": [upper[i]-lower[i] for i in range(3)],
        "triangle_count": len(triangles), "vertex_count": len(vertices),
        "edge_count": len(edge_uses), "boundary_edge_count": 0,
        "non_manifold_edge_count": 0, "inconsistent_winding_edge_count": 0,
        "duplicate_triangle_count": 0, "degenerate_triangle_count": 0,
        "connected_component_count": 1, "signed_volume_mm3": round(signed_volume, 8),
    }


def report(directory=ROOT, parameter_file=ROOT / "parameters.json"):
    p = json.loads(parameter_file.read_text())
    if p["units"] != "mm":
        raise ValueError("Explicit mm units required. STL does not encode units.")
    length, width, height = p["outer_length"], p["outer_width"], p["base_height"]
    inner_l, inner_w = length-2*p["wall"], width-2*p["wall"]
    lip_l = inner_l-2*p["lid_clearance_per_side"]
    lip_w = inner_w-2*p["lid_clearance_per_side"]
    lip_inside_l, lip_inside_w = lip_l-2*p["lid_lip_wall"], lip_w-2*p["lid_lip_wall"]
    expected_volumes = {
        "base": length*width*height-inner_l*inner_w*(height-p["floor"])-p["cable_notch_width"]*p["wall"]*p["cable_notch_depth_from_rim"],
        "lid": length*width*p["lid_plate"]+(lip_l*lip_w-lip_inside_l*lip_inside_w)*p["lid_lip_depth"]-p["cable_notch_width"]*p["lid_lip_wall"]*p["lid_lip_depth"],
    }
    parts = {}
    for part in ("base", "lid"):
        name = f"enclosure-{part}.stl"
        observation = measure((directory / name).read_bytes())
        expected_bounds = [length, width, height if part == "base" else p["lid_plate"]+p["lid_lip_depth"]]
        if any(abs(a-b) > 1e-4 for a, b in zip(observation["extents_mm"], expected_bounds)):
            raise ValueError(f"{part}: dimensions differ from the parameter contract.")
        if any(abs(v) > 1e-4 for v in observation["bounds_mm"]["min"]):
            raise ValueError(f"{part}: expected model origin at [0,0,0].")
        if not math.isclose(observation["signed_volume_mm3"], expected_volumes[part], rel_tol=1e-6, abs_tol=1e-3):
            raise ValueError(f"{part}: measured volume differs from the analytic solid.")
        observation["analytic_volume_mm3"] = round(expected_volumes[part], 8)
        parts[name] = observation
    return {
        "schema_version": "1.0", "example": True, "source": "local_independent_ascii_stl_measurement",
        "units": "mm", "parameters_sha256": digest(parameter_file),
        "source_sha256": digest(ROOT / "enclosure.py"), "verifier_sha256": digest(ROOT / "verify.py"),
        "certifies_printability": False,
        "limitations": [
            "Checks bounds, edge incidence, orientation, connectedness and signed mesh volume only.",
            "Does not check self-intersections, vertex manifoldness, wall thickness, physical clearances or fit.",
            "Does not certify printability, strength, safety, or electronics/thermal suitability.",
            "STL has no embedded unit contract; coordinates are explicitly interpreted as mm.",
        ],
        "parts": parts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT)
    parser.add_argument("--parameters", type=Path, default=ROOT / "parameters.json")
    parser.add_argument("--check", action="store_true", help="Also require exact equality with committed geometry-report.json.")
    args = parser.parse_args()
    result = report(args.directory, args.parameters)
    if args.check and result != json.loads((ROOT / "geometry-report.json").read_text()):
        raise ValueError("Measured evidence differs from the committed report; review the revision.")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
