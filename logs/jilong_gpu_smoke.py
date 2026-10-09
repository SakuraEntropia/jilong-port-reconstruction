import bpy
import time
import os

start = time.perf_counter()
scene = bpy.context.scene
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
devices = []
for device in prefs.devices:
    device.use = device.type == 'METAL'
    devices.append((device.name, device.type, device.use))
print('GPU_SMOKE_DEVICES', devices, flush=True)
if not any(d.type == 'METAL' and d.use for d in prefs.devices):
    raise RuntimeError('No enabled native Metal device')
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 8
scene.cycles.use_denoising = True
scene.render.resolution_x = 320
scene.render.resolution_y = 213
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = '/private/tmp/jilong_gpu_smoke.png'
scene.camera = bpy.data.objects.get('CAM_01_Front_reference', scene.camera)
print('GPU_SMOKE_BEGIN', time.strftime('%Y-%m-%dT%H:%M:%S'), 'GPU',
      scene.camera.name, scene.render.resolution_x, scene.render.resolution_y,
      scene.cycles.samples, flush=True)
render_start = time.perf_counter()
bpy.ops.render.render(write_still=True)
print('GPU_SMOKE_SUCCESS', 'render_seconds', round(time.perf_counter()-render_start,3),
      'script_seconds', round(time.perf_counter()-start,3),
      'bytes', os.path.getsize(scene.render.filepath), flush=True)
