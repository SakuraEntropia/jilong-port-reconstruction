"""Apply a photographed lettering correction and re-render its bounded region.

The surrounding pixels are existing full-frame Cycles renders of this same scene.
The patch is newly ray-traced 3D geometry, composited by Blender, not painted text.
Production files are saved without the temporary compositor or image dependency.
"""
import argparse, json, shutil, sys, time
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

BASE = Path(__file__).resolve().parent.parent
VIEWS = {
    '01_hero_daylight': ('CAM_01_Front_reference', 2200, 1467, 128),
    '02_oblique_daylight': ('CAM_02_Three_quarter', 1800, 1200, 96),
    '04_portal_detail': ('CAM_04_Portal_detail', 1800, 1200, 96),
    '05_site_overview': ('CAM_05_Site_overview', 1800, 1200, 96),
    '06_dusk': ('CAM_01_Front_reference', 1800, 1200, 128),
}

def correct_geometry():
    title = bpy.data.objects['Historic south inscription']
    bpy.context.view_layer.update()
    title.scale.x *= 17.3 / title.dimensions.x
    bpy.context.view_layer.update()
    assert abs(title.dimensions.x - 17.3) < .001
    return title

def make_compositor(scene, background):
    scene.use_nodes = True
    if hasattr(scene, 'node_tree'):
        tree = scene.node_tree
        tree.nodes.clear()
        output = tree.nodes.new('CompositorNodeComposite')
    else:
        tree = bpy.data.node_groups.new('Temporary lettering region composite', 'CompositorNodeTree')
        tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        scene.compositing_node_group = tree
        output = tree.nodes.new('NodeGroupOutput')
    image_node = tree.nodes.new('CompositorNodeImage')
    image_node.image = background
    render = tree.nodes.new('CompositorNodeRLayers')
    over = tree.nodes.new('CompositorNodeAlphaOver')
    factor = over.inputs.get('Factor') or over.inputs[0]
    factor.default_value = 1.0
    background_socket = over.inputs.get('Background') or over.inputs[1]
    foreground_socket = over.inputs.get('Foreground') or over.inputs[2]
    background_output = image_node.outputs['Image']
    if scene.view_settings.exposure:
        # Invert the exposure baked into the full-frame PNG; output applies it once.
        exposure = tree.nodes.new('CompositorNodeExposure')
        exposure.inputs['Exposure'].default_value = -scene.view_settings.exposure
        tree.links.new(background_output, exposure.inputs['Image'])
        background_output = exposure.outputs['Image']
    tree.links.new(background_output, background_socket)
    tree.links.new(render.outputs['Image'], foreground_socket)
    tree.links.new(over.outputs['Image'], output.inputs['Image'])
    return tree

def run(labels, save_only=False):
    scene = bpy.context.scene
    correct_geometry()
    # Save the corrected, independently re-renderable scene first.
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    if save_only:
        return
    original_camera = scene.camera
    original_resolution = (scene.render.resolution_x, scene.render.resolution_y)
    original_path = scene.render.filepath
    original_samples = scene.cycles.samples
    scene.cycles.device = 'CPU'
    stats = []
    for label in labels:
        name, width, height, samples = VIEWS[label]
        path = BASE/'renders'/f'{label}.png'
        if not path.is_file():
            raise FileNotFoundError(path)
        backup = BASE/'renders'/'iteration_02'/f'{label}_before_lettering.png'
        backup.parent.mkdir(exist_ok=True)
        if not backup.exists():
            shutil.copy2(path, backup)
        scene.camera = bpy.data.objects[name]
        scene.render.resolution_x, scene.render.resolution_y = width, height
        scene.render.resolution_percentage = 100
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        # Includes the old text, pale plaques, and ample shadow/denoising margins.
        points = [world_to_camera_view(scene, scene.camera, Vector((x, y, z)))
                  for x in (-11.1, 11.1) for y in (-.6, .3) for z in (18.25, 20.0)]
        pad_x, pad_y = 30/width, 30/height
        bounds = (max(0, min(p.x for p in points)-pad_x),
                  min(1, max(p.x for p in points)+pad_x),
                  max(0, min(p.y for p in points)-pad_y),
                  min(1, max(p.y for p in points)+pad_y))
        scene.render.use_border = True
        scene.render.use_crop_to_border = False
        (scene.render.border_min_x, scene.render.border_max_x,
         scene.render.border_min_y, scene.render.border_max_y) = bounds
        background = bpy.data.images.load(str(backup), check_existing=False)
        # These PNGs already carry the AgX display transform. Its inverse avoids
        # tone-mapping their pixels twice when combining the new rendered region.
        background.colorspace_settings.name = 'AgX Base sRGB'
        tree = make_compositor(scene, background)
        scene.render.filepath = str(path)
        start = time.time()
        bpy.ops.render.render(write_still=True)
        stats.append({'view': label, 'seconds': round(time.time()-start, 2),
                      'border': bounds, 'width': width, 'height': height,
                      'samples': samples, 'method': 'Blender 3D region re-render over original full Cycles frame'})
        print('LETTERING_REGION_FINISHED', stats[-1], flush=True)
        scene.use_nodes = False
        if hasattr(scene, 'compositing_node_group'):
            scene.compositing_node_group = None
            bpy.data.node_groups.remove(tree)
        else:
            tree.nodes.clear()
        bpy.data.images.remove(background)
    scene.render.use_border = False
    scene.render.use_crop_to_border = False
    scene.camera = original_camera
    scene.render.resolution_x, scene.render.resolution_y = original_resolution
    scene.render.filepath = original_path
    scene.cycles.samples = original_samples
    # Never save a compositor that depends on a previous image.
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    report = BASE/'logs'/'lettering_region_stats.json'
    prior = json.loads(report.read_text()) if report.exists() else []
    prior = [entry for entry in prior if entry['view'] not in labels]
    report.write_text(json.dumps(prior + stats, indent=2))

if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--views', nargs='*', default=[])
    parser.add_argument('--save-only', action='store_true')
    options = parser.parse_args(args)
    run(options.views, options.save_only)
