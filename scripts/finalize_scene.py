"""Embed the final review records without changing rendered geometry."""
import bpy
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent.parent
scene=bpy.context.scene
scene.camera=bpy.data.objects['CAM_01_Front_reference']
scene.render.use_border=False
scene.render.use_crop_to_border=False
scene.cycles.samples=128
scene.render.resolution_x=1800 if 'Dusk' in Path(bpy.data.filepath).name else 2200
scene.render.resolution_y=1200 if 'Dusk' in Path(bpy.data.filepath).name else 1467
scene.render.filepath=str(BASE/'renders'/('06_dusk.png' if 'Dusk' in Path(bpy.data.filepath).name else '01_hero_daylight.png'))
for path in [BASE/'README.md',BASE/'QA.md',BASE/'PLAN.md',*sorted((BASE/'research').glob('*.md'))]:
    txt=bpy.data.texts.get(path.name) or bpy.data.texts.new(path.name)
    txt.clear();txt.write(path.read_text())
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type!='VIEW_3D':continue
        space=area.spaces.active
        space.clip_end=1500
        space.shading.type='SOLID'
        space.shading.color_type='MATERIAL'
        space.region_3d.view_location=Vector((0,5,10))
        space.region_3d.view_distance=85
        space.region_3d.view_perspective='CAMERA'
        space.region_3d.view_camera_zoom=0
for obj in bpy.context.scene.objects:obj.select_set(False)
bpy.context.view_layer.objects.active=None
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('FINAL_DOCUMENTS_EMBEDDED',bpy.data.filepath,flush=True)
