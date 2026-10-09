"""Evidence-led gateway architecture. Every dimension is a proxy estimate."""
import bpy,math,random
from mathutils import Matrix,Vector
from common import *

def build_architecture(m,detail=True):
    random.seed(19)
    arch=collection('01 • Architecture');glazing=collection('02 • Curtain walls');signs=collection('03 • Signage and emblem')
    def b(name,loc,dim,mat='stone',bevel=.035):return move_to(box(name,loc,dim,m[mat],bevel),arch)
    # The front frame and recessed office bridge enclose genuine rectangular voids.
    for s in [-1,1]:
        b('Inferred central pier footing',(s*12.125,8,-.17),(5.8,16,.35),'concrete')
        b('Inferred tower footing',(s*21,8,-.17),(12,16,.35),'concrete')
        b('Inferred hall footing',(s*25,-.1,-.17),(20,8.2,.35),'concrete')
        b('Central monolithic pier '+str(s),(s*12.125,8,8),(5.75,16,16),'joint')
        b('Side tower inner wall '+str(s),(s*15.45,8,9.5),(.65,16,19.0))
        b('Side tower outer wall '+str(s),(s*26.65,8,9.5),(.7,16,19.0))
        b('Tower rear wall '+str(s),(s*21,15.7,9.5),(11.5,.6,19.0),'stone')
        b('Tower floor above entrance '+str(s),(s*21,8,6.0),(11.4,15.6,.30))
        b('Tower roof slab '+str(s),(s*21,8,19.25),(12,16,.5))
        b('Low wing base '+str(s),(s*25,-.1,.4),(20,8.2,.8))
        b('Low wing roof '+str(s),(s*25,-.1,5.25),(20,8.2,.6))
        b('Low wing outer wall '+str(s),(s*34.6,-.1,2.675),(.8,8.2,4.55))
        b('Low wing rear wall '+str(s),(s*25,3.8,2.9),(20,.6,4.9))
        for xx in [16.0,22.5,29.0,34.5]:
            b('Entrance square column',(s*xx,-3.65,2.85),(.75,.8,4.95))
            b('Column base',(s*xx,-3.65,.65),(1.0,1.0,.5))
            b('Column capital',(s*xx,-3.65,4.9),(1.02,1.02,.36))
        # 4 genuinely recessed vertical bays on each tower.
        for i in range(5):
            xx=s*(15.3+i*2.83)
            b('Tower pilaster',(xx,.0,12.25),(.62,.72,12.5),'joint')
        b('Tower lower spandrel',(s*21,0,6.25),(11.8,.7,.7))
        b('Tower upper spandrel',(s*21,0,18.65),(11.8,.7,.85))
        for zz in [6.2,10.2,14.3,18.35]:b('Hidden interior floor',(s*21,8,zz),(11.3,15.7,.22),'interior')
        b('Interior far shadow',(s*21,6.5,12),(11.3,.25,11),'interior',0)
    b('Raised lintel / south',(0,1.25,18.0),(30,2.5,4),'joint')
    b('Raised lintel / north',(0,15.2,17.65),(30,1.6,4.7),'joint')
    b('Central roof',(0,8.0,19.65),(29.7,15.7,.45))
    # A smaller nested road aperture behind the monumental front frame.
    for s in [-1,1]:b('Secondary passage pier',(s*7.4,11.0,3.6),(4.0,10,7.2),'joint')
    for zz in [7.2,10.2,13.1,16.1]:
        b('Recessed elevated office slab',(0,11,zz),(18.5,10,.3))
    for zz in [7.55,10.85,13.75,16.65]:
        b('Recessed horizontal wall band',(0,6.0,zz),(18.5,.5,1.0),'joint')
        b('Inferred rear office wall band',(0,15.7,zz),(18.5,.5,1.0),'stone')
    b('Inner passage lintel solid wall',(0,6.0,8.95),(10.8,.55,3.4),'stone')
    b('Inferred rear lower office wall',(0,15.7,8.8),(18.5,.55,3.1),'stone')
    for s in [-1,1]:
        for xx,ww in [(5.795,.79),(7.30,.98),(8.83,.84)]:
            b('Lower office window surround',(s*xx,6.0,8.75),(ww,.55,1.4),'stone')
        b('Lower office upper spandrel',(s*7.325,6.0,9.90),(3.85,.55,.90),'stone')
    for zz in [12.0,14.95]:
        for i in range(13):
            b('Recessed narrow window pier',(-9.1+i*1.517,6,zz),(.84,.55,2.1))
            b('Inferred rear office window pier',(-9.1+i*1.517,15.7,zz),(.84,.55,2.1))
    # Internal structural roof, not an unmodelled flat photo.
    b('Portal soffit',(0,3.8,16.05),(18.5,7.4,.2),'stone')
    for s in [-1,1]:b('Tunnel lining',(s*5.2,10.5,3.5),(.38,11,7),'stone')
    b('Tunnel soffit',(0,10.5,7.02),(10.4,11,.26),'stone')
    if not detail:
        for s in [-1,1]:
            for i in range(4):move_to(box('Blockout glazing',(s*(16.72+i*2.83),-.12,12.3),(2.15,.15,11.5),m['glass']),glazing)
        cornice(m,arch,0,30,8,16,20.15,central=True,simple=True)
        for s in [-1,1]:cornice(m,arch,s*21,12,8,16,19.4,simple=True)
        return
    stonevariants=[]
    for i in range(8):stonevariants.append(texture_material('Granite slab shade %02d'%i,tuple(v*(.96+.012*i) for v in (.57,.53,.48)),.55+(i%3)*.018,grain=88,bump=.006))
    def panels(name,x1,x2,z1,z2,y,front=True):
        nx=max(1,round(x2-x1));nz=max(1,round(z2-z1));w=(x2-x1)/nx;h=(z2-z1)/nz
        specs=[((x1+(i+.5)*w,y,z1+(j+.5)*h),(w-.017,.085,h-.017),random.randrange(8)) for i in range(nx) for j in range(nz)]
        return move_to(multi_boxes(name,specs,stonevariants,.007),arch)
    for s in [-1,1]:
        x1,x2=sorted([s*9.25,s*15])
        panels('Central granite grid south '+str(s),x1,x2,.75,16.05,-.058)
        panels('Central granite grid north '+str(s),x1,x2,.75,15.3,16.08)
        for i in range(5):
            xx=s*(15.3+i*2.83);panels('Granite pilaster grid',xx-.3,xx+.3,6.65,18.0,-.405)
        for i in range(4):
            xx=s*(16.715+i*2.83)
            window(m,glazing,xx,-.15,12.3,2.2,11.6,hrows=12,vcols=2)
            window(m,glazing,xx,16.08,12.3,2.2,11.6,hrows=12,vcols=2,reverse=True)
        # Lower curtain walls between columns, recessed behind canopy edge.
        for xx,w in [(18.8,4.55),(25.65,5.5),(31.7,4.6)]:
            window(m,glazing,s*xx,-3.3,2.8,w,4.2,hrows=4,vcols=4)
        for xx in [22.4,29.2]:
            for dx in [-.48,.48]:
                window(m,glazing,s*xx+dx,-3.48,1.8,.89,2.95,hrows=1,vcols=1)
                move_to(rod('Door pull',(s*xx+dx-.22,-3.56,1.2),(s*xx+dx-.22,-3.56,2.0),.025,m['metal']),glazing)
        # Side elevations retain a repeated office-window logic (depth is inferred).
        for yy in [3,6.3,9.6,12.9]:
            for zz in [3.2,8.2,12.4,16.6]:
                o=window(m,glazing,0,0,0,1.65,2.2,hrows=2,vcols=2)
                rot=Matrix.Rotation(s*math.pi/2,3,'Z')
                for child in o:
                    child.location=rot@child.location+Vector((s*27.06,yy,zz))
                    child.rotation_euler.z=s*math.pi/2
        cornice(m,arch,s*21,12.35,8,16.4,19.3)
        cornice(m,arch,s*25,20.3,-.1,8.6,5.4,low=True)
        # Raised projecting canopy portals on each low wing.
        cornice(m,arch,s*23.0,8.0,-3.7,2.4,6.25,low=True)
        for dx in [-3.4,3.4]:b('Canopy portico pier',(s*23+dx,-4.3,2.95),(.9,1.0,5.2))
        # Parapets and real roof membranes/drain tubes.
        b('Tower roof membrane',(s*21,8,20.54),(11.5,15.5,.08),'roof',0)
        b('Rear roof parapet',(s*21,15.8,20.7),(12,.4,.6))
        b('Outer roof parapet',(s*26.8,8,20.7),(.4,16,.6))
        for yy in [5,13]:
            move_to(rod('Rainwater downpipe',(s*27.45,yy,.2),(s*27.45,yy,19.9),.07,m['metal']),arch)
    panels('Upper lintel stone grid',-15,15,16.05,19.55,-.038)
    # Photo-matched broad chamfer inside the outer opening.
    chamfer(m,arch)
    for zz in [12.0,14.95]:
        for i in range(12):
            window(m,glazing,-8.34+i*1.517,5.68,zz,.60,1.55,hrows=1,vcols=1)
            window(m,glazing,-8.34+i*1.517,16.02,zz,.60,1.55,hrows=1,vcols=1,reverse=True)
    for s in [-1,1]:
        for xx in [6.5,8.1]:window(m,glazing,s*xx,5.68,8.8,.62,1.3,hrows=1,vcols=1)
    cornice(m,arch,0,18.5,6.0,.9,13.2,low=True,recessed=True)
    cornice(m,arch,0,30.4,8,16.5,20.0,central=True)
    b('Central roof membrane',(0,8,21.245),(29.5,15.5,.075),'roof',0)
    for xx in [-14.8,14.8]:b('Central side parapet',(xx,8,21.5),(.35,16,.6))
    b('Central rear parapet',(0,15.8,21.5),(30,.4,.6))
    # Small soffit lights and road soffit crossbeams.
    for yy in [2.3,5.2,8.5,12.3]:
        for xx in [-3.2,3.2]:b('Tunnel linear light',(xx,yy,6.84),(1.1,.18,.06),'light',.025)
    build_signs(m,signs,arch)
    for s in [-1,1]:
        b('Blue passage sign',(s*11.0,-.14,2.6),(1.75,.10,.64),'blue',.015)
        font=load_font('cjk')
        move_to(text_object('Vehicle lane plaque','入境车辆' if s<0 else '出境车辆',(s*11,-.211,2.70),.23,m['white'],font,width=1.33),signs)
        move_to(text_object('Lane English','VEHICLE ENTRY' if s<0 else 'VEHICLE EXIT',(s*11,-.211,2.42),.115,m['white'],width=1.37),signs)

def load_font(kind):
    path={'cjk':'/System/Library/Fonts/Hiragino Sans GB.ttc','tibetan':'/System/Library/Fonts/Supplemental/Kailasa.ttc'}[kind]
    try:return bpy.data.fonts.load(path,check_existing=True)
    except Exception:return None

def window(m,col,x,y,z,w,h,hrows=8,vcols=2,reverse=False):
    objs=[]
    outward=1 if reverse else -1
    def b(n,loc,dim,mat,bev=0):
        o=move_to(box(n,loc,dim,m[mat],bev),col);objs.append(o);return o
    b('Curtain glass pane',(x,y,z),(w,.065,h),'glass',.007)
    b('Dark window interior',(x,y+(.22 if not reverse else -.22),z),(w,.035,h),'interior')
    for xx in [x-w/2,x+w/2]:b('Window outer jamb',(xx,y+outward*.055,z),(.085,.16,h+.12),'metal',.014)
    for zz in [z-h/2,z+h/2]:b('Window head / sill',(x,y+outward*.055,zz),(w+.12,.16,.085),'metal',.014)
    for j in range(1,hrows):b('Curtain horizontal mullion',(x,y+outward*.061,z-h/2+h*j/hrows),(w,.13,.042),'metal',.005)
    for j in range(1,vcols):b('Curtain vertical mullion',(x-w/2+w*j/vcols,y+outward*.06,z),(.042,.13,h),'metal',.005)
    return objs

def cornice(m,col,x,w,y,d,z,central=False,low=False,simple=False,recessed=False):
    height=1.4 if not low else .95
    def b(n,loc,dim,mat='stone',bev=.025):return move_to(box(n,loc,dim,m[mat],bev),col)
    for zz,ww,dd,hh in [(0,w,d,.22),(.26,w+.28,d+.25,.25),(.56,w+.68,d+.62,.38),(.88,w+.8,d+.78,.16),(1.08,w+.7,d+.7,.25)]:
        factor=.71 if low else 1
        b('Stepped granite cornice',(x,y,z+zz*factor),(ww,dd,hh*factor))
    if simple:return
    yf=y-d/2-.28
    # Separate relief squares alternate with smaller pendant stems.
    count=max(4,int(w/.67))
    specs=[]
    for i in range(count):
        xx=x-w/2+(i+.5)*w/count
        specs.append(((xx,yf,z+.23),(w/count*.46,.20,.25),0))
        if i%2==0:specs.append(((xx,yf-.015,z+.03),(.14,.23,.16),0))
    move_to(multi_boxes('White Tibetan cornice relief',specs,[m['white']],.008),col)
    # Tight classic dentils on upper horizontal shadow belt.
    count=int(w/.23)
    specs=[((x-w/2+(i+.5)*w/count,yf-.03,z+.77*(.71 if low else 1)),(.105,.19,.12),0) for i in range(count)]
    move_to(multi_boxes('Fine repeated cornice dentils',specs,[m['stone']],.006),col)
    if not recessed:
        # Opposite-elevation photo also shows the white relief frieze.
        yr=y+d/2+.28
        count=max(4,int(w/.67))
        specs=[]
        for i in range(count):
            xx=x-w/2+(i+.5)*w/count
            specs.append(((xx,yr,z+.23),(w/count*.46,.20,.25),0))
            if i%2==0:specs.append(((xx,yr+.015,z+.03),(.14,.23,.16),0))
        move_to(multi_boxes('North-facing white cornice relief',specs,[m['white']],.008),col)
        count=int(w/.23)
        specs=[((x-w/2+(i+.5)*w/count,yr+.03,z+.77*(.71 if low else 1)),(.105,.19,.12),0) for i in range(count)]
        move_to(multi_boxes('North-facing fine cornice dentils',specs,[m['stone']],.006),col)
        # Continue trim on both returns; hidden rear is simplified rather than faked.
        for s in [-1,1]:
            specs=[((x+s*(w/2+.29),y-d/2+(i+.5)*d/max(3,int(d/.68)),z+.23),(.20,.3,.25),0) for i in range(max(3,int(d/.68)))]
            move_to(multi_boxes('Cornice relief return',specs,[m['white']],.006),col)

def chamfer(m,col):
    # Four sloping solid reveals lead to a narrower, deeper interior frame.
    for s in [-1,1]:
        x=s*9.25;xi=s*8.5
        v=[(x,-.10,.7),(x,-.10,16),(xi,.80,15.15),(xi,.80,.7),(x,.04,.7),(x,.04,16),(xi,.94,15.15),(xi,.94,.7)]
        o=mesh('Broad inward portal reveal',v,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],m['stone']);move_to(o,col)
    v=[(-9.25,-.1,16),(9.25,-.1,16),(8.5,.8,15.15),(-8.5,.8,15.15),(-9.25,.04,16),(9.25,.04,16),(8.5,.94,15.15),(-8.5,.94,15.15)]
    move_to(mesh('Portal chamfer overhead',v,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],m['stone']),col)

def build_signs(m,col,arch):
    font=load_font('cjk');tfont=load_font('tibetan')
    move_to(text_object('Historic south inscription','中 华 人 民 共 和 国 吉 隆 口 岸',(0,-.14,19.12),.60,m['gold'],font,width=17.3),col)
    move_to(text_object('Tibetan inscription • inferred transcription','ཀྲུང་ཧྭ་མི་དམངས་སྤྱི་མཐུན་རྒྱལ་ཁབ། སྐྱིད་གྲོང་འགག་སྒོ།',(0,-.14,17.93),.245,m['gold'],tfont,width=12.0),col)
    for xx in [-13,-10,10,13]:move_to(box('White inscription plaque',(xx,-.10,19.08),(1.9,.1,.58),m['white'],.015),arch)
    # North facade based on supplementary opposite elevation, scaled/inferred.
    move_to(box('North sign background',(0,16.17,18.0),(22,.16,2.0),m['white'],.02),col)
    move_to(text_object('North Chinese sign','中华人民共和国吉隆口岸',(0,16.29,18.03),.64,m['red'],font,width=20,face='north'),col)
    emblem(m,col,(0,-.72,20.60),.76,'south')
    emblem(m,col,(0,16.72,20.60),.76,'north')

def emblem(m,col,pos,r,face):
    x,y,z=pos;s=-1 if face=='south' else 1
    def disk(name,rr,dd,yy,mat):
        o=cylinder(name,(x,yy,z),rr,dd,m[mat],64);o.rotation_euler.x=math.pi/2;move_to(o,col);return o
    disk('Emblem bronze rim',r,.11,y,'gold');disk('Emblem red enamel field',r*.88,.12,y+s*.045,'red')
    # Raised wheat wreath, five stars and Tiananmen silhouette. Approximate relief.
    specs=[]
    for a in list(range(205,336,10)):
        aa=math.radians(a);xx=x+r*.77*math.cos(aa);zz=z+r*.77*math.sin(aa)
        o=box('Emblem wheat relief',(xx,y+s*.13,zz),(.09,.075,.18),m['gold'],.035);o.rotation_euler.y=aa-.4;move_to(o,col)
    def star(xx,zz,rad):
        verts=[(xx+math.sin(i*math.pi/5)*rad*(1 if i%2==0 else .43),y+s*.15,zz+math.cos(i*math.pi/5)*rad*(1 if i%2==0 else .43)) for i in range(10)]
        move_to(mesh('National emblem star',verts,[tuple(range(10))],m['gold']),col)
    star(x,z+.30*r,.19*r)
    for xx,zz in [(-.36,.20),(.36,.20),(-.23,.47),(.23,.47)]:star(x+xx*r,z+zz*r,.075*r)
    for zz,w,hh in [(-.25,.85,.12),(-.10,.7,.10),(.01,.92,.065)]:
        move_to(box('Emblem gate relief',(x,y+s*.14,z+zz*r),(w*r,.05,hh*r),m['gold'],.009),col)
