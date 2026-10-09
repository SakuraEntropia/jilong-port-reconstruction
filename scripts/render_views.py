"""Render the actual scene; saves final daylight file before any dusk variation."""
import bpy,sys,math,argparse,time,json
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'scripts'))
from build_scene import setup_renderer
from common import collection,look_at

def set_dusk(scene):
    n=scene.world.node_tree.nodes
    sky=next((a for a in n if a.type=='TEX_SKY'),None)
    if sky:sky.sun_elevation=math.radians(-3)
    bg=next(a for a in n if a.type=='BACKGROUND');bg.inputs['Strength'].default_value=.22
    scene.view_settings.exposure=1.0
    for o in scene.objects:
        if o.type=='LIGHT' and o.data.type=='SUN':o.data.energy=.04
        if o.name=='Soft bridge fill':o.data.energy=160
    for m in bpy.data.materials:
        if not m.use_nodes:continue
        for p in m.node_tree.nodes:
            if p.type=='BSDF_PRINCIPLED' and 'Emission Strength' in p.inputs:
                if 'LED' in m.name or 'diffuser' in m.name or m.name=='Warm LED diffuser':p.inputs['Emission Strength'].default_value=4
    col=collection('08 • Dusk architectural lighting')
    for s in [-1,1]:
        for x in [11.5,23.0]:
            d=bpy.data.lights.new('Warm architectural wall wash','AREA');d.energy=1800 if x<15 else 1100;d.color=(1,.72,.46);d.shape='DISK';d.size=5
            o=bpy.data.objects.new('Warm architectural wall wash',d);col.objects.link(o);o.location=(s*x,-5,3);look_at(o,(s*x,0,17 if x<15 else 11))
    for y in [2.5,9.5]:
        d=bpy.data.lights.new('Warm tunnel downlight','AREA');d.energy=500;d.color=(1,.79,.58);d.size=5
        o=bpy.data.objects.new('Warm tunnel downlight',d);col.objects.link(o);o.location=(0,y,6.8)

def run(mode,only,device='CPU'):
    s=bpy.context.scene;setup_renderer(s,preview=mode=='preview');s.cycles.device=device
    stats=[]
    if mode=='preview':
        setups=[('CAM_01_Front_reference','preview_front'),('CAM_02_Three_quarter','preview_oblique'),('CAM_03_Rear_inspection','preview_rear')]
    else:
        s.cycles.samples=128;s.cycles.adaptive_threshold=.025
        s.render.resolution_x=2200;s.render.resolution_y=1467
        s.camera=bpy.data.objects['CAM_01_Front_reference']
        s.render.filepath=str(BASE/'renders'/'01_hero_daylight.png')
        bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Jilong_Port_2019.blend'))
        setups=[('CAM_01_Front_reference','01_hero_daylight'),('CAM_02_Three_quarter','02_oblique_daylight'),('CAM_03_Rear_inspection','03_rear_daylight'),('CAM_04_Portal_detail','04_portal_detail'),('CAM_05_Site_overview','05_site_overview')]
    for name,label in setups:
        if only and label not in only:continue
        s.camera=bpy.data.objects[name]
        if mode!='preview' and label!='01_hero_daylight':s.render.resolution_x=1800;s.render.resolution_y=1200;s.cycles.samples=96
        s.render.filepath=str(BASE/'renders'/f'{label}.png');start=time.time();bpy.ops.render.render(write_still=True)
        stats.append({'view':label,'seconds':round(time.time()-start,2),'width':s.render.resolution_x,'height':s.render.resolution_y,'samples':s.cycles.samples})
        print('RENDER_FINISHED',stats[-1],flush=True)
    if mode=='final' and (not only or '06_dusk' in only):
        set_dusk(s);s.camera=bpy.data.objects['CAM_01_Front_reference'];s.render.resolution_x=1800;s.render.resolution_y=1200;s.cycles.samples=128
        s.render.filepath=str(BASE/'renders'/'06_dusk.png');start=time.time()
        bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Jilong_Port_2019_Dusk.blend'))
        bpy.ops.render.render(write_still=True)
        stats.append({'view':'06_dusk','seconds':round(time.time()-start,2),'width':1800,'height':1200,'samples':128,'art_direction':'Inferred artistic lighting, not verified real night appearance'})
    (BASE/'logs'/f'{mode}_render_stats.json').write_text(json.dumps(stats,indent=2))

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser();p.add_argument('--mode',default='preview');p.add_argument('--only',nargs='*');p.add_argument('--device',default='CPU',choices=['CPU','GPU']);a=p.parse_args(args)
    run(a.mode,a.only,a.device)
