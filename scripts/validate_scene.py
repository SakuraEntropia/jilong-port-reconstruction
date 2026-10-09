"""Acceptance checks on a freshly reopened .blend, independent of builder."""
import bpy,json,sys,os,math,argparse
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent.parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser=argparse.ArgumentParser()
parser.add_argument('--geometry-only',action='store_true')
parser.add_argument('--report')
options=parser.parse_args(args)
geometry_only=options.geometry_only
scene=bpy.context.scene;bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
meshes=[o for o in scene.objects if o.type=='MESH']
verts=sum(len(o.data.vertices) for o in meshes)
faces=sum(len(o.data.polygons) for o in meshes)
cameras=[o for o in scene.objects if o.type=='CAMERA']
node_mats=[m for m in bpy.data.materials if m.use_nodes and any(n.type=='BSDF_PRINCIPLED' for n in m.node_tree.nodes)]
def ray(z,x=0):
    hit,loc,norm,idx,obj,mat=scene.ray_cast(dg,Vector((x,-1,z)),Vector((0,1,0)),distance=30)
    return {'hit':hit,'object':obj.name if hit else None,'location':list(loc) if hit else None}
clear=ray(3.0);upper=ray(13.8)
lane_rays=[{'x':x,**ray(3.0,x)} for x in [-4,-2,0,2,4]]
title=bpy.data.objects.get('Historic south inscription')
plaques=[o for o in scene.objects if o.name.startswith('White inscription plaque')]
title_bounds=[(title.matrix_world@Vector(c)).x for c in title.bound_box] if title else []
title_clear=bool(title_bounds and plaques)
for plaque in plaques:
    bounds=[(plaque.matrix_world@Vector(c)).x for c in plaque.bound_box]
    if not (max(title_bounds)<min(bounds)-.3 or min(title_bounds)>max(bounds)+.3):title_clear=False
checks={
 'substantial_real_mesh':len(meshes)>400 and verts>30000 and faces>30000,
 'road_passage_is_open':not clear['hit'],
 'five_lane_rays_are_open':all(not r['hit'] for r in lane_rays),
 'signage_clear_of_white_plaques':title_clear,
 'nested_elevated_facade_exists':upper['hit'],
 'multiple_cameras':len(cameras)>=5,
 'PBR_materials':len(node_mats)>=20,
 'fonts_packed':all(f.packed_file for f in bpy.data.fonts if f.filepath and not f.filepath.startswith('<')),
 'research_embedded':all(n in bpy.data.texts for n in ['architecture.md','source_index.md','dimensions.md','uncertainties.md']),
 'cycles_renderable':scene.render.engine=='CYCLES' and scene.camera is not None,
 'no_external_image_dependency':all(i.packed_file or i.source in ['GENERATED','VIEWER'] for i in bpy.data.images if i.type!='RENDER_RESULT'),
}
renders=[]
for p in sorted((BASE/'renders').glob('0*.png')):
    img=bpy.data.images.load(str(p),check_existing=False)
    # Examine true decoded pixels rather than accepting filename existence.
    pix=img.pixels
    step=4*max(1,(len(pix)//4)//1000)
    sample=[.2126*pix[i]+.7152*pix[i+1]+.0722*pix[i+2] for i in range(0,len(pix)-3,step)]
    variance=max(sample)-min(sample) if sample else 0
    renders.append({'name':p.name,'width':img.size[0],'height':img.size[1],'file_bytes':p.stat().st_size,'pixel_range':variance})
    bpy.data.images.remove(img)
if not geometry_only:
    checks['final_images_decoded']=len(renders)>=6 and all(r['width']>=1800 and r['pixel_range']>.08 for r in renders)
report={'blend':bpy.data.filepath,'blender_version':bpy.app.version_string,'objects':len(scene.objects),'mesh_objects':len(meshes),'vertices_base_meshes':verts,'faces_base_meshes':faces,'unique_meshes':len(bpy.data.meshes),'PBR_materials':len(node_mats),'cameras':[o.name for o in cameras],'fonts':[{'name':f.name,'packed':bool(f.packed_file)} for f in bpy.data.fonts],'road_ray':clear,'lane_rays':lane_rays,'upper_ray':upper,'inscription_width':title.dimensions.x if title else None,'checks':checks,'renders':renders,'passed':all(checks.values())}
report_path=Path(options.report) if options.report else BASE/'logs'/('geometry_validation.json' if geometry_only else 'validation.json')
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if not report['passed']:raise RuntimeError('Scene acceptance failed; inspect validation.json')
