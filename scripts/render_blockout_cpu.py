"""Fast CPU fallback while first-run Metal kernels compile."""
import bpy
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
s=bpy.context.scene;s.cycles.device='CPU';s.cycles.samples=16
s.render.resolution_x=900;s.render.resolution_y=600
for name,label in [('CAM_01_Front_reference','blockout_front_cpu'),('CAM_02_Three_quarter','blockout_oblique_cpu'),('CAM_03_Rear_inspection','blockout_rear_cpu')]:
    s.camera=bpy.data.objects[name];s.render.filepath=str(BASE/'renders'/f'{label}.png')
    print('CPU_RENDER_START',label,flush=True);bpy.ops.render.render(write_still=True)
    print('CPU_RENDER_DONE',label,flush=True)
