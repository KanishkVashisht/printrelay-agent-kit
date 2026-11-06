"""Original parametric, noncritical electronics fit-check enclosure.

Run inside Blender, not system Python. Numeric geometry is in millimeters;
the STL exporter deliberately preserves those coordinates without unit scaling.
This script only creates local files. No network, slicing, or printer calls.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent


def parameters(path):
    p = json.loads(path.read_text())
    expected = {
        "units", "outer_length", "outer_width", "base_height", "wall", "floor",
        "lid_plate", "lid_lip_depth", "lid_lip_wall", "lid_clearance_per_side",
        "cable_notch_width", "cable_notch_depth_from_rim",
    }
    if set(p) != expected or p["units"] != "mm":
        raise ValueError("Use the exact parameter schema with explicit mm units.")
    for key in expected - {"units"}:
        value = p[key]
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= 500:
            raise ValueError(f"{key} must be finite, positive, and at most 500 mm.")
    length, width, height = p["outer_length"], p["outer_width"], p["base_height"]
    inner_l, inner_w = length - 2 * p["wall"], width - 2 * p["wall"]
    lip_outer_l = inner_l - 2 * p["lid_clearance_per_side"]
    lip_outer_w = inner_w - 2 * p["lid_clearance_per_side"]
    if min(inner_l, inner_w) <= 0 or height <= p["floor"] + p["lid_lip_depth"]:
        raise ValueError("The base needs positive interior dimensions and room below the lip.")
    if min(lip_outer_l, lip_outer_w) <= 2 * p["lid_lip_wall"]:
        raise ValueError("The locator lip must have a positive inner opening.")
    if p["cable_notch_width"] >= lip_outer_l - 2 * p["lid_lip_wall"]:
        raise ValueError("The centered notch must fit between the lip's side walls.")
    if not p["lid_lip_depth"] < p["cable_notch_depth_from_rim"] < height - p["floor"]:
        raise ValueError("The notch must extend below the lip, but not reach the floor.")
    return p


def box(name, lower, upper):
    bpy.ops.mesh.primitive_cube_add(size=1, location=[(a + b) / 2 for a, b in zip(lower, upper)])
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = [b - a for a, b in zip(lower, upper)]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def boolean(target, tool, operation):
    modifier = target.modifiers.new(name=operation.lower(), type="BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = tool
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def finish_mesh(obj):
    """Triangulate once, then fail closed on a defective generated surface."""
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.triangulate(mesh, faces=list(mesh.faces))
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    if any(not edge.is_manifold for edge in mesh.edges):
        raise ValueError(f"{obj.name}: generated boundary or non-manifold edge")
    if any(face.calc_area() < 1e-8 for face in mesh.faces):
        raise ValueError(f"{obj.name}: generated degenerate face")
    if mesh.calc_volume(signed=True) <= 0:
        raise ValueError(f"{obj.name}: nonpositive signed volume")
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    if obj.data.validate(verbose=True):
        raise ValueError(f"{obj.name}: Blender had to repair mesh data")


def build(p):
    length, width, height = p["outer_length"], p["outer_width"], p["base_height"]
    wall, floor = p["wall"], p["floor"]
    plate, depth, lip_wall = p["lid_plate"], p["lid_lip_depth"], p["lid_lip_wall"]
    inset = wall + p["lid_clearance_per_side"]
    notch_x = (length - p["cable_notch_width"]) / 2
    # Cutters deliberately overrun exterior faces by 1 mm; no coincident outside faces.
    base = box("enclosure-base", (0, 0, 0), (length, width, height))
    boolean(base, box("cavity", (wall, wall, floor), (length-wall, width-wall, height+1)), "DIFFERENCE")
    boolean(base, box("base-cable-notch", (notch_x, -1, height-p["cable_notch_depth_from_rim"]),
                     (length-notch_x, wall+1, height+1)), "DIFFERENCE")
    lid = box("enclosure-lid", (0, 0, 0), (length, width, plate))
    # Overlap the plate instead of merely touching it. This is one connected solid.
    boolean(lid, box("lip-blank", (inset, inset, plate/2),
                    (length-inset, width-inset, plate+depth)), "UNION")
    boolean(lid, box("lip-interior", (inset+lip_wall, inset+lip_wall, plate),
                    (length-inset-lip_wall, width-inset-lip_wall, plate+depth+1)), "DIFFERENCE")
    boolean(lid, box("lid-cable-relief", (notch_x, -1, plate),
                    (length-notch_x, inset+lip_wall+1, plate+depth+1)), "DIFFERENCE")
    for obj in (base, lid):
        finish_mesh(obj)
    return base, lid


def export(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(
        filepath=str(path), check_existing=False, ascii_format=True,
        export_selected_objects=True, global_scale=1.0, use_scene_unit=False,
        forward_axis="Y", up_axis="Z", apply_modifiers=True,
    )


def preview(base, lid, p, output):
    """Render the actual model in an exploded assembly; never modify exported parts."""
    material = bpy.data.materials.new("matte-sage")
    material.diffuse_color = (0.28, 0.50, 0.39, 1)
    for obj in (base, lid):
        obj.data.materials.append(material)
    # Lid export is plate-down. Assembly rotates around Y: (x,y,z)->(L-x,y,H+plate-z).
    # Apply transforms to world vertices for an unambiguous exploded display.
    for vertex in lid.data.vertices:
        world = lid.matrix_world @ vertex.co
        vertex.co = Vector((p["outer_length"]-world.x, world.y,
                            p["base_height"]+p["lid_plate"]-world.z+15))
    lid.location = (0, 0, 0)
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=(115, -130, 100))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((30, 20, 19))-camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 100
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(20, -40, 100))
    bpy.context.object.data.energy = 400000
    bpy.context.object.data.shape = "DISK"
    bpy.context.object.data.size = 90
    scene.world.color = (0.12, 0.12, 0.12)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.render.resolution_x = 720
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output / "enclosure-preview.png")
    bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=ROOT / "parameters.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    p = parameters(args.parameters)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.unit_settings.length_unit = "MILLIMETERS"
    base, lid = build(p)
    export(base, output / "enclosure-base.stl")
    export(lid, output / "enclosure-lid.stl")
    if args.render:
        preview(base, lid, p, output)
    print(json.dumps({"blender": bpy.app.version_string, "units": "mm", "exported": ["enclosure-base.stl", "enclosure-lid.stl"]}))


if __name__ == "__main__":
    main()
