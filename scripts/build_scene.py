"""Run: Blender -b --python scripts/build_scene.py -- --phase blockout|detail."""
import bpy,sys,os,math,json,argparse
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'scripts'))
from common import *
from architecture import build_architecture

def setup_renderer(scene,preview=False):
    scene.render.engine='CYCLES'
    scene.cycles.samples=24 if preview else 96
    scene.cycles.use_denoising=True
    scene.cycles.max_bounces=8;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=4
    scene.cycles.transmission_bounces=5
    scene.render.resolution_x=960 if preview else 2000
    scene.render.resolution_y=640 if preview else 1333
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.render.image_settings.color_depth='8'
    scene.view_settings.view_transform='AgX'
    scene.view_settings.exposure=0
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='METAL';prefs.get_devices()
        available=[]
        for d in prefs.devices:
            d.use=d.type=='METAL';available.append((d.name,d.type,d.use))
        scene.cycles.device='GPU' if any(d.type=='METAL' for d in prefs.devices) else 'CPU'
        print('CYCLES_DEVICES',available,flush=True)
    except Exception as e:
        scene.cycles.device='CPU';print('GPU unavailable',repr(e),flush=True)

def lighting(scene):
    col=collection('08 • Lighting')
    world=bpy.data.worlds.new('Soft Himalayan daylight');world.use_nodes=True;scene.world=world
    n=world.node_tree.nodes;l=world.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.25
    sky=n.new('ShaderNodeTexSky')
    types=[i.identifier for i in sky.bl_rna.properties['sky_type'].enum_items]
    sky.sky_type='NISHITA' if 'NISHITA' in types else 'SINGLE_SCATTERING'
    sky.sun_disc=False;sky.sun_elevation=math.radians(31);sky.sun_rotation=math.radians(140);sky.altitude=1850;sky.air_density=1.1
    if hasattr(sky,'dust_density'):sky.dust_density=1.4
    else:sky.aerosol_density=1.4
    l.new(sky.outputs[0],bg.inputs['Color']);l.new(bg.outputs[0],out.inputs['Surface'])
    data=bpy.data.lights.new('Mountain sun','SUN');data.energy=2.0;data.angle=math.radians(9)
    o=bpy.data.objects.new('Mountain sun',data);col.objects.link(o);o.rotation_euler=(math.radians(30),math.radians(-25),math.radians(-25))
    data=bpy.data.lights.new('Soft bridge fill','AREA');data.energy=3800;data.shape='DISK';data.size=40
    o=bpy.data.objects.new('Soft bridge fill',data);col.objects.link(o);o.location=(-25,-35,38);look_at(o,(0,4,9))

def cameras(scene):
    col=collection('09 • Cameras')
    setups=[('CAM_01_Front_reference',(4,-97,8.5),(0,3,10.6),44),('CAM_02_Three_quarter',(57,-70,29),(0,3,10),43),('CAM_03_Rear_inspection',(24,78,31),(0,7,10),43),('CAM_04_Portal_detail',(11,-40,8),(0,3,11.0),46),('CAM_05_Site_overview',(108,-140,98),(0,-15,8),42)]
    for name,loc,target,lens in setups:
        d=bpy.data.cameras.new(name);d.lens=lens;d.clip_end=2500
        o=bpy.data.objects.new(name,d);col.objects.link(o);o.location=loc;look_at(o,target)
    scene.camera=bpy.data.objects['CAM_01_Front_reference']
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.clip_end=2500

def build(phase):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name=='Collection':bpy.data.collections.remove(c)
    s=bpy.context.scene;s.name='吉隆口岸 • 2019 exterior reconstruction'
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    m=materials();detail=phase!='blockout'
    build_architecture(m,detail=detail)
    if detail:
        from site_geometry import build_site
        build_site(m)
        from environment import build_environment
        build_environment()
    else:
        col=collection('04 • Bridge and site')
        move_to(box('Blockout bridge approach',(0,-55,-.4),(12,110,.8),m['concrete']),col)
        move_to(box('Blockout apron',(0,10,-.45),(76,35,.9),m['concrete']),col)
        for x in [-5.8,5.8]:move_to(box('Blockout railing',(x,-55,.75),(.28,110,1.5),m['white']),col)
        move_to(box('Blockout ground',(0,35,-1.5),(320,230,1),m['concrete']),col)
    lighting(s);cameras(s);setup_renderer(s,preview=not detail)
    s['reconstruction_epoch']='2019, historic intact exterior'
    s['target_identity']='Chinese Resuo gate / joint inspection building, Jilong–Rasuwagadhi land border crossing'
    s['dimensions']='Building dimensions inferred from photographs; bridge110m x12m reported, environment approximate'
    s['reference_camera_location']='28.278667 N,85.378056 E (source photo camera, not survey origin)'
    s['world_axes']='+Y toward Chinese side; -Y toward Nepal; approximate orientation'
    for path in [BASE/'README.md',BASE/'PLAN.md',*list((BASE/'research').glob('*.md'))]:
        txt=bpy.data.texts.new(path.name);txt.write(path.read_text())
    try:bpy.ops.file.pack_all()
    except Exception as e:print('PACK_INFO',repr(e))
    path=BASE/'checkpoints'/('01_blockout.blend' if not detail else '02_detailed.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    print('BUILD_SAVED',str(path),len(bpy.data.objects),'objects',flush=True)
    if not detail:
        for name,label in [('CAM_01_Front_reference','blockout_front'),('CAM_02_Three_quarter','blockout_oblique'),('CAM_03_Rear_inspection','blockout_rear')]:
            s.camera=bpy.data.objects[name];s.render.filepath=str(BASE/'renders'/f'{label}.png');bpy.ops.render.render(write_still=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser();p.add_argument('--phase',default='blockout');ns=p.parse_args(args)
    build(ns.phase)
