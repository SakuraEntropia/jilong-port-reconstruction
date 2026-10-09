"""Small editable geometry and physically based material helpers (metres)."""
import bpy, math, random
from mathutils import Vector

def collection(name):
    c=bpy.data.collections.get(name)
    if not c:
        c=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def move_to(obj,col):
    if isinstance(col,str): col=collection(col)
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

def material(name,color,roughness=.5,metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color[:3],color[3] if len(color)>3 else 1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metallic
    m.diffuse_color=(*color[:3],1)
    return m

def texture_material(name,color,roughness=.55,metallic=0,grain=40,bump=.012):
    m=material(name,color,roughness,metallic)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    coord=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=grain;noise.inputs['Detail'].default_value=3
    l.new(coord.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.15
    ramp.color_ramp.elements[0].color=(*(v*.83 for v in color[:3]),1)
    ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[1].color=(*(min(v*1.08,1) for v in color[:3]),1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.25;b.inputs['Distance'].default_value=bump
    l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])
    return m

def mesh(name,vertices,faces,mat):
    d=bpy.data.meshes.new(name+'_Mesh');d.from_pydata(vertices,[],faces);d.update()
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o)
    if mat:d.materials.append(mat)
    return o

_box_cache={}
def box(name,loc,dim,mat,bevel=0):
    # Direct datablocks avoid a complete scene dependency update per panel.
    key=(tuple(dim),mat.name if mat else None)
    data=_box_cache.get(key)
    if data is None:
        w,d,h=dim
        vertices=[(a*w/2,b*d/2,c*h/2) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
        faces=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
        data=bpy.data.meshes.new(name+'_Mesh');data.from_pydata(vertices,[],faces);data.update()
        if mat:data.materials.append(mat)
        _box_cache[key]=data
    o=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(o);o.location=loc
    if bevel:
        mod=o.modifiers.new('Editable edge radii','BEVEL');mod.width=bevel;mod.segments=2
        mod=o.modifiers.new('Weighted facade normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,loc,radius,depth,mat,vertices=12):
    vs=[(radius*math.cos(i*math.tau/vertices),radius*math.sin(i*math.tau/vertices),z) for z in [-depth/2,depth/2] for i in range(vertices)]
    fs=[tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))]
    fs.extend((i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices))
    o=mesh(name,vs,fs,mat);o.location=loc
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o

def rod(name,a,b,radius,mat,vertices=12):
    a=Vector(a);b=Vector(b);o=cylinder(name,(a+b)/2,radius,(b-a).length,mat,vertices)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def multi_boxes(name,specs,mats,bevel=0):
    """One editable mesh of separate cuboids, with per-component material index."""
    verts=[];faces=[];indices=[]
    for spec in specs:
        (x,y,z),(w,d,h),mi=spec
        k=len(verts)
        verts.extend([(x+a*w/2,y+b*d/2,z+c*h/2) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]])
        faces.extend([tuple(k+i for i in f) for f in [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]])
        indices.extend([mi]*6)
    o=mesh(name,verts,faces,None)
    for m in mats:o.data.materials.append(m)
    for p,mi in zip(o.data.polygons,indices):p.material_index=mi
    if bevel:
        m=o.modifiers.new('Small seam edge bevel','BEVEL');m.width=bevel;m.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def look_at(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def text_object(name,body,loc,size,mat,font=None,width=None,face='south'):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.align_x='CENTER';c.align_y='CENTER'
    c.extrude=.008;c.bevel_depth=.002;c.bevel_resolution=1
    if font:c.font=font
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.location=loc
    o.rotation_euler=(math.pi/2,0,0) if face=='south' else (math.pi/2,0,math.pi)
    c.materials.append(mat);bpy.context.view_layer.update()
    if width and o.dimensions.x>0:o.scale.x=width/o.dimensions.x
    return o

def materials():
    d={}
    d['stone']=texture_material('Granite • warm grey slab',(.57,.53,.48),.56,grain=88,bump=.008)
    d['joint']=material('Shadow in granite joints',(.22,.205,.185),.76)
    d['white']=texture_material('Pale Tibetan relief stone',(.80,.78,.72),.49,grain=100,bump=.005)
    d['concrete']=texture_material('Concrete • weathered bridge',(.38,.38,.35),.64,grain=35,bump=.018)
    d['metal']=material('Anodized aluminium',(.27,.30,.31),.28,.85)
    d['black']=material('Graphite frames and rubber',(.023,.03,.032),.52,.05)
    d['gold']=material('Bronze / polished lettering',(.31,.19,.044),.30,.72)
    d['red']=material('Red enamel',(.56,.015,.022),.32,.12)
    d['paint']=material('Truck green enamel',(.13,.25,.15),.38,.25)
    d['road_white']=material('Weathered traffic white',(.62,.62,.55),.66)
    d['roof']=texture_material('Roof membrane',(.10,.105,.10),.82,grain=15,bump=.006)
    d['glass']=material('Architectural blue-green glazing',(.018,.045,.058),.145,.38)
    p=d['glass'].node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.18;p.inputs['IOR'].default_value=1.48
    p.inputs['Coat Weight'].default_value=.32;p.inputs['Coat Roughness'].default_value=.09
    d['interior']=material('Interior shadow',(.025,.034,.039),.82)
    d['blue']=material('Border lane blue enamel',(.009,.085,.30),.37,.12)
    d['light']=material('Warm LED diffuser',(.75,.64,.41),.3)
    p=d['light'].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.71,.35,1);p.inputs['Emission Strength'].default_value=.2
    return d
