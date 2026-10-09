"""Editable approach bridge and inspection-site details, 2019 appearance.

All sizes are proportional reconstruction estimates.  The reference establishes
stone open railings, a pale concrete road, small kiosks and solar street lights.
Vehicle design is generic and serves only as a three-dimensional scale cue.
Bridge underside supports are explicitly inferred: no source underside view or
structural survey is available.  Their spacing is only a plausible completion.
"""
import bpy
import math
from common import collection, mesh, box, cylinder, move_to, material, rod


def _pbr(name, base, alternate, scale=5.0, roughness=0.7, bump=0.018):
    """Metric-scale weathering, restrained enough to preserve broad stone color."""
    mat = material(name, (*base, 1), roughness=roughness)
    mat.use_nodes = True
    nt = mat.node_tree
    bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.name = 'Fine aggregate in metres'
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = 3.0
    tex.inputs['Roughness'].default_value = 0.68
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (*alternate, 1)
    ramp.color_ramp.elements[1].position = 0.83
    ramp.color_ramp.elements[1].color = (*base, 1)
    coords = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(coords.outputs['Object'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Fac'], ramp.inputs[0])
    nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    n = nt.nodes.new('ShaderNodeBump')
    n.inputs['Strength'].default_value = 0.24
    n.inputs['Distance'].default_value = bump
    nt.links.new(tex.outputs['Fac'], n.inputs['Height'])
    nt.links.new(n.outputs['Normal'], bs.inputs['Normal'])
    return mat


def _emissive(name, color, strength=0.15):
    mat = material(name, (*color, 1), roughness=0.35)
    bs = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value = (*color, 1)
        bs.inputs['Emission Strength'].default_value = strength
    elif 'Emission' in bs.inputs:
        bs.inputs['Emission'].default_value = (*color, 1)
    return mat


def _text(name, string, location, size, mat, col):
    curve = bpy.data.curves.new(name + ' lettering', 'FONT')
    curve.body = string
    curve.size = size
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    obj.location = location
    obj.rotation_euler.x = math.pi / 2
    curve.materials.append(mat)
    return obj


def build_site(materials):
    bridge = collection('04 Site • 2019 stone bridge')
    supports = collection('04B Site • INFERRED bridge supports')
    furniture = collection('05 Site • inspection furniture')
    vehicle = collection('06 Vehicle • generic freight truck')
    pavement = _pbr('Site • weathered pale concrete', (0.46, 0.45, 0.41),
                    (0.33, 0.33, 0.30), 6.5, 0.83, 0.007)
    cut_stone = _pbr('Site • cream cut granite railing', (0.72, 0.71, 0.63),
                    (0.57, 0.57, 0.51), 32.0, 0.74, 0.0035)
    deck_side = _pbr('Site • bridge structural concrete', (0.31, 0.31, 0.28),
                    (0.23, 0.24, 0.21), 10.0, 0.86, 0.012)
    metal = materials.get('metal') or material('Site • galvanized steel',
                                              (0.39, 0.43, 0.45, 1),
                                              roughness=0.33, metallic=0.75)
    black = materials.get('black') or material('Site • soft black rubber',
                                              (0.022, 0.025, 0.027, 1), 0.85)
    glass = materials.get('glass') or material('Site • kiosk blue glass',
                                              (0.04, 0.09, 0.11, 1), 0.14)
    white = materials.get('road_white') or material('Site • aged road marking',
                                                   (0.71, 0.71, 0.64, 1), 0.84)
    cream = materials.get('stone') or cut_stone
    blue = material('Site • small lane sign blue', (0.022, 0.10, 0.31, 1), 0.44)
    solar = material('Site • photovoltaic blue-black', (0.016, 0.038, 0.058, 1),
                     roughness=0.24, metallic=0.28)
    seam_mat = material('Site • recessed expansion seal', (0.10, 0.105, 0.095, 1), 0.9)
    lights = _emissive('Site • LED diffuser', (0.83, 0.88, 0.84), 0.08)

    box_cache = {}

    def B(name, loc, dim, mat, bevel=0.0, col=bridge):
        # Repeating stone components retain their own object transforms and
        # editable edge modifiers while sharing a mesh.  Avoiding 1,000 context
        # operator calls also keeps deterministic background builds practical.
        key = (tuple(round(v, 6) for v in dim), mat.name if mat else None, round(bevel, 6))
        if key in box_cache:
            obj = box_cache[key].copy()
            obj.data = box_cache[key].data
            obj.name = name
            obj.location = loc
        else:
            obj = box(name, loc, dim, mat, bevel)
            box_cache[key] = obj
        move_to(obj, col)
        return obj

    def C(name, loc, radius, depth, mat, vertices=12, col=furniture):
        obj = cylinder(name, loc, radius, depth, mat, vertices)
        move_to(obj, col)
        return obj

    def R(name, a, b, radius, mat, vertices=12, col=furniture):
        obj = rod(name, a, b, radius, mat, vertices)
        move_to(obj, col)
        return obj

    # Top of the carriageway is datum zero.  Deck thickness is visible in the
    # three-quarter view and does not rely on a projected background image.
    deck = B('Bridge continuous structural slab • 107m', (0, -56.5, -0.36),
             (12.0, 107.0, 0.72), deck_side, 0.035)
    deck['source_basis'] = '2019 photograph; dimensions inferred'
    # Underside structure is intentionally disclosed as a plausibility model,
    # not as source-confirmed engineering.  The river centre remains clear.
    supports['source_basis'] = 'INFERRED; no underside photograph or structural survey'
    for y in (-37.0, -73.0):
        for side in (-1, 1):
            pier = B(f'INFERRED bridge pier {side:+d} at {y:g}',
                     (side * 3.15, y, -6.85), (1.65, 2.20, 10.30),
                     deck_side, .09, supports)
            pier['source_basis'] = supports['source_basis']
            footing = B(f'INFERRED pier footing {side:+d} at {y:g}',
                        (side * 3.15, y, -12.15), (2.80, 3.45, .70),
                        deck_side, .055, supports)
            footing['source_basis'] = supports['source_basis']
        crosshead = B(f'INFERRED pier crosshead at {y:g}',
                      (0, y, -1.20), (10.80, 2.70, 1.0),
                      deck_side, .065, supports)
        crosshead['source_basis'] = supports['source_basis']
        for side in (-1, 1):
            bearing = B(f'INFERRED bridge bearing pad {side:+d} at {y:g}',
                        (side * 3.15, y, -.72), (1.3, 1.3, .14),
                        black, .015, supports)
            bearing['source_basis'] = supports['source_basis']
    for y in (-110.0, -3.0):
        abutment = B(f'INFERRED full-width bridge abutment at {y:g}',
                     (0, y, -6.60), (12.0, 3.0, 11.80),
                     deck_side, .055, supports)
        abutment['source_basis'] = supports['source_basis']
    B('Bridge carriageway finish', (0, -56.5, -0.012),
      (9.0, 107.0, 0.032), pavement, 0.005)
    for side in (-1, 1):
        # Segmented footway gives actual slab joints rather than wide black lines.
        for i in range(36):
            ya = -110.0 + i * 107.0 / 36.0
            B(f'Footway {side:+d} slab {i:02d}',
              (side * 5.25, ya + 107.0 / 72.0, 0.07),
              (1.48, 107.0 / 36.0 - 0.013, 0.20), cut_stone, 0.01)
        B(f'Raised inner curb {side:+d}', (side * 4.56, -56.5, 0.10),
          (0.22, 107.0, 0.23), cut_stone, 0.018)
        # Narrow worn edge paint is all the visible approach road requires.
        B(f'Worn carriageway edge line {side:+d}',
          (side * 4.20, -56.5, 0.008), (0.095, 106.5, 0.003), white)
    for y in (-107.5, -86, -64.5, -43, -21.5):
        B(f'Road expansion joint {y:g}', (0, y, 0.008),
          (8.99, 0.026, 0.006), seam_mat)

    # Reference: three stone rail courses with two rows of rectangular openings,
    # capped square main posts and slender intermediate dividers.  Everything is
    # a true solid mesh and can be edited individually in the final scene.
    count = 40
    step = 107.0 / count
    for side in (-1, 1):
        x = side * 5.80
        for j in range(count + 1):
            y = -110.0 + j * step
            B(f'Granite main post {side:+d}-{j:02d}', (x, y, 0.89),
              (0.34, 0.38, 1.43), cut_stone, 0.019)
            B(f'Granite post square cap {side:+d}-{j:02d}', (x, y, 1.64),
              (0.46, 0.48, 0.19), cut_stone, 0.034)
            B(f'Granite post footing {side:+d}-{j:02d}', (x, y, 0.25),
              (0.43, 0.44, 0.16), cut_stone, 0.015)
            if j == count:
                continue
            mid_y = y + step / 2
            for course, z, h in ((0, 0.46, 0.19), (1, 0.93, 0.18), (2, 1.40, 0.19)):
                B(f'Open railing course {side:+d}-{j:02d}-{course}',
                  (x, mid_y, z), (0.24, step - 0.36, h), cut_stone, 0.012)
            B(f'Open railing centre divider {side:+d}-{j:02d}',
              (x, mid_y, 0.88), (0.20, 0.145, 1.21), cut_stone, 0.011)

    # Supported little end aprons accommodate kiosk footings and light poles.
    # Forecourt slabs terminate outside facade footprints; the middle lane
    # remains continuous through the open gate at x=0.
    for side in (-1, 1):
        B(f'Inspection end apron {side:+d}', (side * 7.5, -10.5, -0.10),
          (3.0, 15.0, 0.20), pavement, 0.015)
        B(f'Forecourt side flank {side:+d}', (side * 37.6, 6.5, -0.15),
          (5.0, 19.0, 0.30), pavement, 0.025)
        B(f'Front entrance paved apron {side:+d}', (side * 22.15, -5.1, -0.12),
          (25.7, 2.2, 0.24), pavement, 0.018)
    B('Rear inspection yard paving', (0, 22.5, -0.15),
      (80.0, 13.0, 0.30), pavement, 0.03)
    road = B('Inferred north approach road continuation', (0, 99.5, -0.15),
             (9.0, 141.0, 0.36), pavement, 0.008)
    road['source_basis'] = 'INFERRED continuation beyond photographed immediate gate'
    for side in (-1,1):
        B(f'North road edge {side:+d}', (side*4.20,99.5,.035),
          (.09,140.8,.004),white)
    B('Continuous gate passage roadway', (0, 8.0, -0.045),
      (9.0, 22.0, 0.08), pavement, 0.01)
    # Small grated drainage channels placed near footway curb.
    for side in (-1, 1):
        for y in (-31.5, -62.5, -93.5):
            B(f'Curb drain recess {side:+d}-{y:g}', (side * 4.38, y, 0.008),
              (0.20, 0.80, 0.015), black)
            for k in range(7):
                B(f'Curb drain steel rung {side:+d}-{y:g}-{k}',
                  (side * 4.38, y - 0.34 + k * 0.113, 0.020),
                  (0.18, 0.026, 0.018), metal, 0.003)

    for side in (-1, 1):
        x, y = side * 7.1, -5.0
        prefix = f'Inspection kiosk {side:+d}'
        B(prefix + ' concrete footing', (x, y, 0.13), (1.9, 2.3, 0.26), cream, 0.025, furniture)
        B(prefix + ' opaque lower shell', (x, y, 0.67), (1.6, 2.0, 0.91), metal, 0.018, furniture)
        B(prefix + ' flat roof', (x, y, 2.69), (1.86, 2.24, 0.16), metal, 0.035, furniture)
        for yy in (-0.91, 0.91):
            B(prefix + f' front-rear glazing {yy}', (x, y + yy, 1.85),
              (1.47, 0.035, 1.50), glass, 0.008, furniture)
            for xx in (-0.745, 0, 0.745):
                B(prefix + f' upright {xx},{yy}', (x + xx, y + yy - 0.025, 1.87),
                  (0.055, 0.07, 1.65), metal, 0.003, furniture)
        for xx in (-0.775, 0.775):
            B(prefix + f' side glazing {xx}', (x + xx, y, 1.85),
              (0.035, 1.80, 1.50), glass, 0.008, furniture)
            B(prefix + f' door stile {xx}', (x + xx, y, 1.85),
              (0.065, 0.045, 1.58), metal, 0.005, furniture)
        for zz in (1.09, 2.61):
            B(prefix + f' window transom {zz}', (x, y - 0.94, zz),
              (1.58, 0.07, 0.065), metal, 0.005, furniture)
        B(prefix + ' door handle', (x + side * 0.81, y - 0.40, 1.40),
          (0.03, 0.22, 0.035), metal, 0.005, furniture)

    # Solar-powered street fixtures visible in the 2019 reference.  Panel cells
    # and frames are editable meshes.  Small street-light heads have restrained
    # daytime emission; the main builder controls the dusk scene light level.
    for side in (-1, 1):
        for index, y in enumerate((-12.0, -40.0)):
            x = side * (7.65 if index == 0 else 6.25)
            if index:
                B(f'Solar pole bracketed curb ledge {side:+d}', (side * 6.18, y, -0.05),
                  (1.00, 1.25, 0.23), deck_side, 0.02)
            B(f'Solar pole base plate {side:+d}-{index}', (x, y, 0.16),
              (0.31, 0.31, 0.11), metal, 0.01, furniture)
            C(f'Solar galvanized pole {side:+d}-{index}', (x, y, 2.95),
              0.057, 5.70, metal, 12)
            for dx, dy in ((-.10, -.10), (-.10, .10), (.10, -.10), (.10, .10)):
                C(f'Solar anchor bolt {side:+d}-{index}-{dx},{dy}',
                  (x + dx, y + dy, 0.23), .014, .04, metal, 6)
            # Panel has a shallow north-facing tilt and steel mounting arms.
            panel = B(f'Solar photovoltaic panel {side:+d}-{index}', (x, y, 5.86),
                      (1.04, 0.70, 0.045), solar, 0.01, furniture)
            panel.rotation_euler.x = math.radians(18)
            frame = B(f'Solar panel aluminium frame {side:+d}-{index}', (x, y, 5.825),
                      (1.11, 0.76, 0.045), metal, 0.008, furniture)
            frame.rotation_euler.x = panel.rotation_euler.x
            for gx in range(1, 6):
                cell_line = B(f'Solar cell grid {side:+d}-{index}-{gx}',
                              (x - .52 + gx * 1.04 / 6, y, 5.89),
                              (.006, .68, .003), metal, 0, furniture)
                cell_line.rotation_euler.x = panel.rotation_euler.x
            R(f'Solar light curved-arm base {side:+d}-{index}',
              (x, y, 5.45), (x - side * 0.35, y, 5.28), .043, metal)
            R(f'Solar light inward arm {side:+d}-{index}',
              (x - side * .35, y, 5.28), (x - side * .93, y, 5.20), .043, metal)
            B(f'Solar LED lamp case {side:+d}-{index}',
              (x - side * .92, y, 5.17), (.64, .24, .105), metal, .025, furniture)
            B(f'Solar LED underside diffuser {side:+d}-{index}',
              (x - side * .92, y, 5.108), (.48, .18, .015), lights, .015, furniture)
            B(f'Solar controller box {side:+d}-{index}', (x, y + .09, 3.65),
              (.18, .16, .30), metal, .017, furniture)

    # Low, small lane identifiers preserve the restrained reference foreground.
    for side in (-1, 1):
        x, y = side * 4.8, -6.8
        for dx in (-.42, .42):
            C(f'Lane sign support {side:+d}-{dx}', (x + dx, y, .72), .025, 1.42, metal, 8)
        B(f'Low lane number blue sign {side:+d}', (x, y, 1.56),
          (1.25, .055, .47), blue, .014, furniture)
        _text(f'Lane white identifier {side:+d}', '01' if side < 0 else '02',
              (x - .24, y - .032, 1.56), .25, white, furniture)
        arrow_verts = [(x+.15,y-.034,1.41), (x+.23,y-.034,1.41),
                       (x+.23,y-.034,1.59), (x+.35,y-.034,1.59),
                       (x+.19,y-.034,1.73), (x+.03,y-.034,1.59),
                       (x+.15,y-.034,1.59)]
        arr = mesh(f'Lane arrow {side:+d}', arrow_verts, [tuple(range(7))], white)
        move_to(arr, furniture)

    _truck(vehicle, B, C, R, metal, black, white, glass)
    return {'bridge': bridge, 'supports': supports, 'furniture': furniture, 'vehicle': vehicle,
            'road_surface_z': 0.0, 'bridge_width_m': 12.0}


def _truck(col, B, C, R, metal, black, white, glass):
    """Generic northbound box truck, with physically separate components."""
    tx, ty = -2.1, -45.0
    green = _pbr('Truck • aged deep green automotive paint', (.075, .19, .12),
                 (.037, .094, .063), 17, .39, .0025)
    faded = _pbr('Truck • faded green cargo corrugations', (.105, .23, .145),
                 (.062, .13, .082), 23, .53, .002)
    roofmat = _pbr('Truck • dusty box roof', (.15, .24, .17), (.09, .14, .10), 14, .73, .004)
    red = _emissive('Truck • red tail lamp lens', (.37, .012, .008), .10)
    amber = _emissive('Truck • amber marker lamp', (.65, .20, .01), .08)
    headlamp = _emissive('Truck • headlight clear lens', (.80, .82, .75), .10)
    yellow = material('Truck • muted yellow rear plate', (.66, .46, .06, 1), .55)
    chassis = material('Truck • aged chassis steel', (.07, .075, .072, 1), .70, .45)
    rubber = _pbr('Truck • tire sidewall rubber', (.035, .037, .036), (.014, .016, .015), 40, .84, .003)
    paint_bs = next(n for n in green.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if 'Coat Weight' in paint_bs.inputs:
        paint_bs.inputs['Coat Weight'].default_value = .28
        paint_bs.inputs['Coat Roughness'].default_value = .30

    def tb(name, loc, dim, mat, bevel=0):
        return B('Truck • ' + name, (tx+loc[0], ty+loc[1], loc[2]), dim, mat, bevel, col)

    def tc(name, loc, r, depth, mat, vertices=16):
        return C('Truck • ' + name, (tx+loc[0], ty+loc[1], loc[2]), r, depth, mat, vertices, col)

    def tr(name, a, b, r, mat, vertices=12):
        return R('Truck • ' + name,
                 (tx+a[0], ty+a[1], a[2]), (tx+b[0], ty+b[1], b[2]), r, mat, vertices, col)

    tb('ladder chassis', (0, -.10, .69), (2.10, 8.62, .28), chassis, .025)
    for x in (-.71, .71):
        tb(f'chassis longitudinal rail {x}', (x, -.3, .61), (.16, 8.42, .25), chassis, .018)
    for y in (-3.02, -1.91, 3.30):
        tr(f'wheel axle {y}', (-1.20,y,.56), (1.20,y,.56), .085, chassis)
    # Cargo box, rear toward the hero camera; the main portal remains visible.
    tb('cargo shell', (0, -.91, 2.47), (2.45, 6.58, 2.68), green, .035)
    tb('cargo roof cap', (0, -.91, 3.83), (2.51, 6.64, .07), roofmat, .017)
    tb('cargo bottom sill', (0, -.91, 1.13), (2.55, 6.71, .17), metal, .012)
    rib_template = None
    for side in (-1, 1):
        for i in range(44):
            loc = (tx+side*1.242, ty-4.16+i*.151, 2.48)
            if rib_template is None:
                rib_template = B('Truck • linked corrugation template', loc,
                                 (.038, .042, 2.59), faded, .010, col)
            else:
                rib = rib_template.copy()
                rib.data = rib_template.data
                rib.name = f'Truck • linked corrugation {side:+d}-{i:02d}'
                col.objects.link(rib)
                rib.location = loc
        for yy in (-4.23, 2.41):
            tb(f'cargo corner angle {side},{yy}', (side*1.245, yy, 2.49),
               (.072, .075, 2.72), metal, .008)
        for zz in (1.26, 3.73):
            tb(f'cargo side edge rail {side},{zz}', (side*1.249, -.91, zz),
               (.055, 6.57, .055), metal, .008)
        tb(f'underbody fuel toolbox {side}', (side*1.00, .05, .79),
           (.39, 1.2, .47), metal, .035)
        tb(f'rear wheel mudguard {side}', (side*1.14, -2.46, 1.13),
           (.47, 2.28, .095), black, .03)
        tb(f'rear rubber mudflap {side}', (side*1.18, -3.67, .57),
           (.44, .045, .60), black, .008)

    for side in (-1, 1):
        tb(f'rear cargo door {side}', (side*.604, -4.258, 2.47),
           (1.178, .065, 2.54), faded, .016)
        tb(f'rear vertical frame {side}', (side*1.19,-4.305,2.48),
           (.074, .066, 2.68), metal, .006)
        tr(f'rear door latch rod {side}', (side*.29,-4.344,1.35),
           (side*.29,-4.344,3.60), .021, metal)
        for z in (1.58, 2.45, 3.36):
            tb(f'rear door hinge {side},{z}', (side*1.17,-4.36,z),
               (.12,.05,.16), metal, .008)
            tb(f'rear latch bracket {side},{z}', (side*.29,-4.374,z),
               (.12,.045,.075), metal, .004)
        tb(f'latch handle {side}', (side*.42,-4.40,1.86),
           (.29,.035,.043), metal, .009)
        tb(f'rear tail light {side}', (side*.91,-4.45,.97),
           (.31,.065,.115), red, .016)
        tb(f'rear amber turn signal {side}', (side*1.13,-4.45,.97),
           (.09,.065,.115), amber, .014)
        for zz in (1.46, 3.57):
            tb(f'rear reflective strip {side},{zz}', (side*.63,-4.30,zz),
               (.97,.015,.046), yellow, .002)
    tb('rear centre door seal', (0,-4.306,2.47), (.018,.020,2.54), black)
    tb('rear bumper', (0,-4.44,.72), (2.38,.23,.18), metal, .023)
    tb('rear number plate', (0,-4.577,.85), (.57,.015,.145), yellow, .004)
    _text('Truck • rear plate characters', 'JL 0186', (tx,ty-4.592,.85), .088, black, col)

    # Cabin is a sloping prism rather than a decal over a box.  The windshield
    # and side windows are separate recessed surfaces on the actual shell.
    yrear, yfront = 2.44, 4.54
    verts = [(-1.19,yrear,.86),(1.19,yrear,.86),(1.19,yfront,.86),(-1.19,yfront,.86),
             (-1.19,yrear,3.16),(1.19,yrear,3.16),(1.19,4.13,3.16),(-1.19,4.13,3.16)]
    verts = [(tx+x,ty+y,z) for x,y,z in verts]
    cab = mesh('Truck • real sloped cab shell', verts,
               [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)], green)
    move_to(cab,col)
    mod = cab.modifiers.new('Cab soft painted edges','BEVEL'); mod.width=.045; mod.segments=2
    for side in (-1,1):
        win = mesh(f'Truck • side window {side:+d}',
                   [(tx+side*1.204,ty+2.68,2.02),(tx+side*1.204,ty+4.27,2.02),
                    (tx+side*1.204,ty+4.10,2.96),(tx+side*1.204,ty+2.68,2.96)],
                   [(0,1,2,3)] if side > 0 else [(3,2,1,0)],glass)
        move_to(win,col)
        tb(f'cabin window divider {side}', (side*1.22,2.94,2.49), (.028,.045,.98), metal,.004)
        tb(f'cab door lower panel {side}', (side*1.201,3.40,1.46), (.024,1.53,.86), green,.015)
        tb(f'cab door handle {side}', (side*1.228,2.90,1.94), (.035,.19,.035), metal,.009)
        tb(f'cab footstep {side}', (side*1.21,3.26,.82), (.35,1.2,.105), metal,.018)
        tr(f'mirror upper arm {side}', (side*1.18,4.03,2.82), (side*1.50,4.12,2.67), .025,metal)
        tr(f'mirror lower arm {side}', (side*1.18,4.25,2.19), (side*1.50,4.12,2.40), .025,metal)
        tb(f'mirror black housing {side}', (side*1.51,4.12,2.55), (.18,.13,.42), black,.032)
        tb(f'mirror reflective face {side}', (side*1.51,4.047,2.55), (.135,.012,.34), glass,.012)
        tb(f'front headlight {side}', (side*.86,4.57,1.18), (.45,.06,.22), headlamp,.029)
        tb(f'front turn signal {side}', (side*1.075,4.56,1.43), (.15,.05,.12),amber,.014)
    # Sloped windshield follows the sloping body surface exactly.
    winds = mesh('Truck • raked windshield',
                 [(tx-1.045,ty+4.352,1.94),(tx+1.045,ty+4.352,1.94),
                  (tx+1.045,ty+4.162,3.00),(tx-1.045,ty+4.162,3.00)], [(3,2,1,0)],glass)
    move_to(winds,col)
    tr('windshield centre division',(0,4.352,1.94),(0,4.162,3.00),.023,metal)
    for x in (-.49,.49):
        tr(f'windshield wiper {x}',(x-.27,4.38,1.96),(x+.14,4.30,2.17),.012,black,8)
    tb('front radiator grille',(0,4.574,1.35),(1.25,.045,.35),black,.024)
    for i in range(8):
        tb(f'radiator metal grille {i}',(-.53+i*.151,4.602,1.35),(.028,.018,.29),metal,.004)
    tb('front bumper',(0,4.64,.86),(2.36,.19,.22),metal,.029)
    tb('front yellow number plate',(0,4.748,.87),(.57,.02,.145),yellow,.004)
    # Front lettering reverses orientation, so it remains legible from north.
    plate=_text('Truck • front plate characters','JL 0186',(tx,ty+4.764,.87),.088,black,col)
    plate.rotation_euler.x = math.pi/2
    plate.rotation_euler.z = math.pi

    for side in (-1,1):
        for axle,y in enumerate((3.26,-1.91,-3.02)):
            xpos=[side*1.15] if axle==0 else [side*.94,side*1.22]
            for twin,x in enumerate(xpos):
                bpy.ops.mesh.primitive_torus_add(major_radius=.390,minor_radius=.135,
                                                major_segments=24,minor_segments=10,
                                                location=(tx+x,ty+y,.555))
                tire=bpy.context.object
                tire.name=f'Truck • actual tire {side:+d}-{axle}-{twin}'
                tire.rotation_euler.y=math.pi/2
                tire.data.materials.append(rubber)
                move_to(tire,col)
                for polygon in tire.data.polygons:
                    polygon.use_smooth=True
                rim=tc(f'wheel rim {side:+d}-{axle}-{twin}',
                       (x+side*.07,y,.555),.292,.15,metal,20)
                rim.rotation_euler.y=math.pi/2
                hub=tc(f'wheel hub {side:+d}-{axle}-{twin}',
                       (x+side*.158,y,.555),.115,.09,chassis,16)
                hub.rotation_euler.y=math.pi/2
                if twin == len(xpos)-1:
                    for k in range(8):
                        ang=k*math.tau/8
                        bolt=tc(f'wheel bolt {side:+d}-{axle}-{k}',
                                (x+side*.16,y+.19*math.cos(ang),.555+.19*math.sin(ang)),
                                .026,.025,metal,6)
                        bolt.rotation_euler.y=math.pi/2
                    # Visible low-relief individual treads around each outside tire.
                    for k in range(24):
                        ang=k*math.tau/24
                        tread=tb(f'tire tread {side:+d}-{axle}-{k}',
                                 (x,y+.521*math.cos(ang),.555+.521*math.sin(ang)),
                                 (.19,.07,.025),black,.006)
                        tread.rotation_euler.x=ang-math.pi/2
    col['description']='Generic editable weathered box cargo truck, northbound; no commercial logo'
    col['dimensions_estimate_m']='width 2.5; length 9.0; height 3.9'
