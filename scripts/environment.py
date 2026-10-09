"""Inferred mountain context for the 2019 Jilong gate reconstruction.

The photographs establish a steep, humid green and exposed-rock valley, but
not a survey.  This deterministic terrain is contextual geometry in metres.
It intentionally leaves the main gateway and its north road corridor clear.
"""

import math
import random

import bpy
from mathutils import Vector

from common import collection, mesh, material, move_to


SEED = 19192024


def _hash(ix, iy):
    n = (ix * 374761393 + iy * 668265263 + 1447) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return (n ^ (n >> 16)) / 4294967295.0


def _noise(x, y):
    ix, iy = math.floor(x), math.floor(y)
    a, b = x - ix, y - iy
    a = a * a * (3.0 - 2.0 * a)
    b = b * b * (3.0 - 2.0 * b)
    p = _hash(ix, iy) * (1 - a) + _hash(ix + 1, iy) * a
    q = _hash(ix, iy + 1) * (1 - a) + _hash(ix + 1, iy + 1) * a
    return p * (1 - b) + q * b


def _fbm(x, y):
    return sum(_noise(x * f, y * f) * a for f, a in
               ((1.0, .55), (2.1, .26), (4.3, .13), (8.7, .06)))


def _smooth(a, b, value):
    t = max(0.0, min(1.0, (value - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def terrain_height(x, y):
    """Asymmetric ridges, erosion folds and a low road/river corridor."""
    if y < 24:
        # A real north bank supports the halls; the bridge alone spans the
        # lower transverse ravine.  This removes the formerly floating site.
        bank = max(0.0, abs(x) - 15.0)
        cliff = 46.0 * _smooth(30.0, 140.0, bank)
        front = _smooth(-115.0, 18.0, y)
        z = -12.5 + bank * .10 + cliff * (.25 + .75 * front)
        z += (_fbm(x * .06, y * .06) - .5) * min(7.0, bank * .2)
        river_y = -53.0 + 8.0 * math.sin(x * .018)
        trough = math.exp(-((y - river_y) / 12.0) ** 2)
        z = z * (1 - trough) - 13.2 * trough
        terrace = _smooth(-20.0, -10.0, y) * (1 - _smooth(42.0, 70.0, abs(x)))
        return z * (1 - terrace) - .3 * terrace

    center = 11.0 * math.sin(y * .011) - .025 * y
    half_width = 39.0 + .045 * max(0.0, y - 80.0)
    outside = max(0.0, abs(x - center) - half_width)
    rise = 1.0 - math.exp(-(outside / 61.0) ** 1.4)
    side = 1.0 if x > center else .85
    # Interlocking diagonally receding ridge spines create real silhouettes.
    spine_x = (119 + .105 * y) if x > center else (-125 - .17 * y)
    spine = math.exp(-((x - spine_x) / 54.0) ** 2)
    if x > center:
        peaks = (24.0 * math.exp(-((y - 115.0) / 88.0) ** 2)
                 + 43.0 * math.exp(-((y - 300.0) / 115.0) ** 2))
    else:
        peaks = (35.0 * math.exp(-((y - 210.0) / 108.0) ** 2)
                 + 25.0 * math.exp(-((y - 420.0) / 85.0) ** 2))
    geological = _fbm(x * .022 + y * .007, y * .017)
    ridge_fold = 1.0 - abs(2.0 * _noise(x * .047 + y * .013, y * .038) - 1.0)
    height = rise * (77.0 * side + 37.0 * spine + peaks
                     + 27.0 * geological + 12.0 * ridge_fold)
    height += rise * 4.0 * (_noise(x * .19, y * .17) - .5)
    valley_floor = max(0.0, y - 170.0) * .021
    # A complete remote massif closes the empty V.  Its main peak sits east
    # of the axis, with an uneven western shoulder, as contextual inference.
    remote = (163.0 * math.exp(-((y - 455.0) / 129.0) ** 2)
              + 52.0 * math.exp(-((x - 57.0) / 87.0) ** 2 - ((y - 425.0) / 109.0) ** 2)
              + 34.0 * math.exp(-((x + 103.0) / 76.0) ** 2 - ((y - 481.0) / 91.0) ** 2))
    remote += 19.0 * (_fbm(x * .025, y * .021) - .40)
    remote *= _smooth(205.0, 348.0, y)
    z = max(valley_floor + height, remote)
    # Preserve the editable road and the rear camera's clear valley floor.
    road = (1 - _smooth(35.0, 58.0, abs(x))) * (1 - _smooth(170.0, 215.0, y))
    z *= (1 - road)
    terrace = (1 - _smooth(24.0, 48.0, y)) * (1 - _smooth(42.0, 70.0, abs(x)))
    return max(-.3, z * (1 - terrace) - .3 * terrace)


def _terrain_shader():
    mat = bpy.data.materials.get("Context_Rock_and_Moss_PBR")
    if mat:
        return mat
    mat = material("Context_Rock_and_Moss_PBR", (.23, .25, .18, 1), .86)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = .88
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    rock_noise = nt.nodes.new("ShaderNodeTexNoise")
    rock_noise.inputs["Scale"].default_value = .16
    rock_noise.inputs["Detail"].default_value = 5.0
    rock_noise.inputs["Roughness"].default_value = .72
    nt.links.new(geo.outputs["Position"], rock_noise.inputs["Vector"])
    stone = nt.nodes.new("ShaderNodeValToRGB")
    stone.color_ramp.elements[0].position = .23
    stone.color_ramp.elements[0].color = (.055, .060, .058, 1)
    stone.color_ramp.elements[1].position = .78
    stone.color_ramp.elements[1].color = (.37, .36, .31, 1)
    stone.color_ramp.elements.new(.48).color = (.18, .17, .14, 1)
    nt.links.new(rock_noise.outputs["Fac"], stone.inputs["Fac"])
    moss = nt.nodes.new("ShaderNodeValToRGB")
    moss.color_ramp.elements[0].position = .18
    moss.color_ramp.elements[0].color = (.009, .055, .015, 1)
    moss.color_ramp.elements[1].position = .83
    moss.color_ramp.elements[1].color = (.10, .23, .035, 1)
    moss.color_ramp.elements.new(.50).color = (.035, .12, .018, 1)
    nt.links.new(rock_noise.outputs["Fac"], moss.inputs["Fac"])
    split = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], split.inputs["Vector"])
    slope = nt.nodes.new("ShaderNodeMapRange")
    slope.inputs["From Min"].default_value = .10
    slope.inputs["From Max"].default_value = .73
    slope.clamp = True
    nt.links.new(split.outputs["Z"], slope.inputs["Value"])
    coverage = nt.nodes.new("ShaderNodeTexNoise")
    coverage.inputs["Scale"].default_value = .035
    coverage.inputs["Detail"].default_value = 4.0
    coverage.inputs["Roughness"].default_value = .74
    nt.links.new(geo.outputs["Position"], coverage.inputs["Vector"])
    patches = nt.nodes.new("ShaderNodeMapRange")
    patches.inputs["From Min"].default_value = .42
    patches.inputs["From Max"].default_value = .60
    patches.inputs["To Min"].default_value = .04
    patches.inputs["To Max"].default_value = 1.0
    patches.clamp = True
    nt.links.new(coverage.outputs["Fac"], patches.inputs["Value"])
    patch = nt.nodes.new("ShaderNodeMath")
    patch.operation = "MULTIPLY"
    nt.links.new(slope.outputs["Result"], patch.inputs[0])
    nt.links.new(patches.outputs["Result"], patch.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    nt.links.new(patch.outputs[0], mix.inputs[0])
    nt.links.new(stone.outputs["Color"], mix.inputs[1])
    nt.links.new(moss.outputs["Color"], mix.inputs[2])
    nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    micro = nt.nodes.new("ShaderNodeTexNoise")
    micro.inputs["Scale"].default_value = 1.8
    micro.inputs["Detail"].default_value = 3.0
    micro.inputs["Roughness"].default_value = .8
    nt.links.new(geo.outputs["Position"], micro.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .38
    bump.inputs["Distance"].default_value = .22
    nt.links.new(micro.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _foliage_shader(name, dark, light):
    mat = material(name, (*dark, 1), .91)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    info = nt.nodes.new("ShaderNodeObjectInfo")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].color = (*light, 1)
    nt.links.new(info.outputs["Random"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = .06
    return mat


def _terrain_mesh(col, mat):
    rng = random.Random(SEED)
    nx, ny = 111, 147
    xmin, xmax, ymin, ymax = -270.0, 270.0, -145.0, 545.0
    dx, dy = (xmax - xmin) / (nx - 1), (ymax - ymin) / (ny - 1)
    vertices = []
    for j in range(ny):
        for i in range(nx):
            x, y = xmin + i * dx, ymin + j * dy
            if 0 < i < nx - 1:
                x += rng.uniform(-.23, .23) * dx
            if 0 < j < ny - 1:
                y += rng.uniform(-.23, .23) * dy
            vertices.append((x, y, terrain_height(x, y)))
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            b, c, d = a + 1, a + nx, a + nx + 1
            if (i + j) % 2:
                faces.extend(((a, b, c), (b, d, c)))
            else:
                faces.extend(((a, b, d), (a, d, c)))
    # Closed skirt prevents thin-sheet silhouettes in oblique/rear views.
    perimeter = (list(range(nx))
                 + [j * nx + nx - 1 for j in range(1, ny)]
                 + list(range((ny - 1) * nx + nx - 2, (ny - 1) * nx - 1, -1))
                 + [j * nx for j in range(ny - 2, 0, -1)])
    bottom = []
    for top in perimeter:
        bottom.append(len(vertices))
        vertices.append((vertices[top][0], vertices[top][1], -28.0))
    for k in range(len(perimeter)):
        following = (k + 1) % len(perimeter)
        faces.append((perimeter[k], bottom[k], bottom[following], perimeter[following]))
    faces.append(tuple(reversed(bottom)))
    obj = mesh("Inferred_valley_ridges_closed_triangulated", vertices, faces, mat)
    move_to(obj, col)
    obj["evidence_status"] = "Contextual inference; not surveyed terrain"
    obj["terrain_seed"] = SEED
    top_faces = 2 * (nx - 1) * (ny - 1)
    for poly in obj.data.polygons[:top_faces]:
        poly.use_smooth = True
    # Smooth macro slopes; rock detail comes from geometry folds and PBR.
    return obj


def _append_ring(vertices, center, radius, z, n, rng, squash=1.0):
    inds = []
    for k in range(n):
        angle = 2 * math.pi * k / n + rng.uniform(-.10, .10)
        r = radius * rng.uniform(.82, 1.15)
        inds.append(len(vertices))
        vertices.append((center[0] + math.cos(angle) * r,
                         center[1] + math.sin(angle) * r * squash,
                         z + rng.uniform(-.12, .12)))
    return inds


def _conifer_data(index, bark, leaves, lighter):
    rng = random.Random(SEED + index * 39)
    vertices, faces, slots = [], [], []
    # Trunk is real cylinder geometry, not a line or crossed image plane.
    for z, r in ((0, .17), (7.8, .065)):
        for k in range(8):
            a = k * math.tau / 8
            vertices.append((math.cos(a) * r, math.sin(a) * r, z))
    for k in range(8):
        faces.append((k, (k + 1) % 8, (k + 1) % 8 + 8, k + 8))
        slots.append(0)
    faces.extend((tuple(reversed(range(8))), tuple(range(8, 16))))
    slots.extend((0, 0))
    # Several asymmetric foliage skirts overlap around a central spine.
    for tier in range(6):
        z = 1.9 + tier * 1.17
        r = 2.4 - tier * .29 + rng.uniform(-.14, .14)
        center = (rng.uniform(-.20, .20), rng.uniform(-.20, .20))
        bottom = _append_ring(vertices, center, r * .55, z - .18, 11, rng)
        rim = _append_ring(vertices, center, r, z + .18, 11, rng)
        upper = _append_ring(vertices, center, r * .35, z + 1.20, 11, rng)
        tip = len(vertices)
        vertices.append((center[0] * .5, center[1] * .5, z + 1.65))
        for k in range(11):
            q = (k + 1) % 11
            faces.extend(((bottom[k], bottom[q], rim[q], rim[k]),
                          (rim[k], rim[q], upper[q], upper[k]),
                          (upper[k], upper[q], tip)))
            slots.extend((1, 1 + (k + tier) % 2, 1))
        faces.append(tuple(reversed(bottom)))
        slots.append(1)
    data = bpy.data.meshes.new("Linked_irregular_conifer_%02d" % index)
    data.from_pydata(vertices, [], faces)
    data.materials.append(bark)
    data.materials.append(leaves)
    data.materials.append(lighter)
    for poly, slot in zip(data.polygons, slots):
        poly.material_index = slot
        poly.use_smooth = True
    data.update()
    return data


def _icosahedron():
    t = (1 + math.sqrt(5)) / 2
    vertices = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
                (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
                (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    vertices = [tuple(Vector(v).normalized()) for v in vertices]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
             (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
             (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
             (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    return vertices, faces


def _shrub_data(index, leaves, lighter):
    rng = random.Random(SEED + 751 + index)
    base, triangles = _icosahedron()
    vertices, faces, slots = [], [], []
    for clump in range(9):
        angle = clump * 2.4
        radius = .6 if clump < 6 else .25
        center = (math.cos(angle) * radius, math.sin(angle) * radius,
                  .48 + (clump % 3) * .22)
        start = len(vertices)
        for x, y, z in base:
            scale = rng.uniform(.40, .64)
            vertices.append((center[0] + x * scale, center[1] + y * scale,
                             center[2] + z * scale * 1.05))
        faces.extend(tuple(start + k for k in tri) for tri in triangles)
        slots.extend([clump % 2] * len(triangles))
    data = bpy.data.meshes.new("Linked_broadleaf_shrub_%02d" % index)
    data.from_pydata(vertices, [], faces)
    data.materials.append(leaves)
    data.materials.append(lighter)
    for poly, slot in zip(data.polygons, slots):
        poly.material_index = slot
        poly.use_smooth = True
    data.update()
    return data


def _linked_object(name, data, col, loc, scale, angle):
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    obj.location = loc
    obj.scale = scale
    obj.rotation_euler.z = angle
    return obj


def _vegetation(col):
    rng = random.Random(SEED + 333)
    bark = material("Context_conifer_bark", (.10, .075, .044, 1), .92)
    leaves = _foliage_shader("Context_needles_deep_green", (.018, .047, .025), (.078, .135, .050))
    lighter = _foliage_shader("Context_needles_sunlit", (.031, .079, .028), (.10, .18, .062))
    broad = _foliage_shader("Context_shrub_leaves", (.037, .09, .025), (.12, .20, .055))
    conifers = [_conifer_data(i, bark, leaves, lighter) for i in range(5)]
    shrubs = [_shrub_data(i, broad, lighter) for i in range(3)]
    candidates = []
    for xbase in range(-240, 245, 4):
        for ybase in range(-110, 540, 4):
            candidates.append((xbase + rng.uniform(-1.9, 1.9),
                               ybase + rng.uniform(-1.9, 1.9)))
    rng.shuffle(candidates)
    count_tree = count_shrub = 0
    for x, y in candidates:
        # No trees in the hall footprint, road, or visible river water.
        if -22 < y < 38 and abs(x) < 48:
            continue
        if 24 <= y < 205 and abs(x) < 43:
            continue
        z = terrain_height(x, y)
        river_y = -53.0 + 8.0 * math.sin(x * .018)
        if z < -11.3 or (y < 24 and abs(y - river_y) < 7.0):
            continue
        dx = (terrain_height(x + 1, y) - terrain_height(x - 1, y)) * .5
        dy = (terrain_height(x, y + 1) - terrain_height(x, y - 1)) * .5
        slope = math.sqrt(dx * dx + dy * dy)
        # Larger clumps alternate with open rock gullies.  Tree spacing and
        # size are smaller than the first preview's scattered polygon trees.
        forest_patch = _fbm(x * .033 + 5, y * .031 + 8)
        density = .25 + .70 * _smooth(.30, .61, forest_patch)
        if slope > 3.8 or rng.random() > density:
            continue
        shrub = slope > 2.4 or y < 10 or rng.random() < .29
        if shrub:
            if count_shrub >= 1200:
                continue
            count_shrub += 1
            s = rng.uniform(.75, 1.9)
            _linked_object("Broadleaf_shrub_%04d" % count_shrub, rng.choice(shrubs), col,
                           (x, y, z - .10), (s, s * rng.uniform(.8, 1.3), s), rng.random() * math.tau)
        else:
            if count_tree >= 2250:
                continue
            count_tree += 1
            s = rng.uniform(.27, .59)
            _linked_object("Conifer_%04d" % count_tree, rng.choice(conifers), col,
                           (x, y, z - .18), (s * rng.uniform(.75, 1.12), s, s * rng.uniform(.9, 1.15)),
                           rng.random() * math.tau)
        if count_tree >= 2250 and count_shrub >= 1200:
            break
    col["evidence_status"] = "Inferred linked-mesh vegetation from mountain photographs"
    col["conifer_count"] = count_tree
    col["shrub_count"] = count_shrub
    return count_tree, count_shrub


def _river_and_boulders(col, rock):
    rng = random.Random(SEED + 991)
    water = material("Context_glacial_river_PBR", (.075, .13, .12, 1), .21)
    water.use_nodes = True
    bsdf = next(n for n in water.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["IOR"].default_value = 1.333
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = .18
    coord = water.node_tree.nodes.new("ShaderNodeTexNoise")
    coord.inputs["Scale"].default_value = 2.2
    coord.inputs["Detail"].default_value = 2.0
    geometry = water.node_tree.nodes.new("ShaderNodeNewGeometry")
    stretch = water.node_tree.nodes.new("ShaderNodeVectorMath")
    stretch.operation = "MULTIPLY"
    stretch.inputs[1].default_value = (.25, 1.0, .25)
    water.node_tree.links.new(geometry.outputs["Position"], stretch.inputs[0])
    water.node_tree.links.new(stretch.outputs["Vector"], coord.inputs["Vector"])
    bump = water.node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .26
    bump.inputs["Distance"].default_value = .10
    water.node_tree.links.new(coord.outputs["Fac"], bump.inputs["Height"])
    water.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    vertices, faces = [], []
    for i in range(76):
        x = -250 + i * 500 / 75
        center = -53 + 8 * math.sin(x * .018)
        width = 5.0 + 1.0 * math.sin(x * .042)
        vertices.extend(((x, center - width, -12.45), (x, center + width, -12.45)))
        if i:
            a = (i - 1) * 2
            faces.append((a, a + 2, a + 3, a + 1))
    river = mesh("Inferred_ravine_river_below_bridge", vertices, faces, water)
    move_to(river, col)
    river["evidence_status"] = "Approximate river position and width; not surveyed"
    base, tris = _icosahedron()
    for variant in range(4):
        vertices = [(x * rng.uniform(.8, 1.3), y * rng.uniform(.8, 1.2), z * rng.uniform(.65, 1.1))
                    for x, y, z in base]
        data = bpy.data.meshes.new("Linked_ravine_boulder_%d" % variant)
        data.from_pydata(vertices, [], tris)
        data.materials.append(rock)
        data.update()
        for i in range(34):
            x, y = rng.uniform(-180, 180), rng.uniform(-125, 18)
            if abs(x) < 13 or (abs(x) < 40 and y > -10):
                continue
            z = terrain_height(x, y)
            scale = rng.uniform(.8, 3.3)
            _linked_object("Ravine_boulder_%d_%02d" % (variant, i), data, col,
                           (x, y, z + scale * .20),
                           (scale, scale * rng.uniform(.65, 1.45), scale * rng.uniform(.5, 1)),
                           rng.random() * math.tau)


def build_environment():
    """Build physical inferred context; does not set cameras or render."""
    terrain = collection("Terrain")
    vegetation = collection("Vegetation")
    rock = _terrain_shader()
    ground = _terrain_mesh(terrain, rock)
    _river_and_boulders(terrain, rock)
    trees, shrubs = _vegetation(vegetation)
    # Bounded, very low-density atmosphere gives distant ridges a humid
    # valley scale cue.  It is art direction rather than measured weather.
    from common import box
    haze=bpy.data.materials.new('Context • thin mountain atmosphere')
    haze.use_nodes=True
    nt=haze.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    vol=nt.nodes.new('ShaderNodeVolumeScatter')
    vol.inputs['Color'].default_value=(.64,.72,.79,1)
    vol.inputs['Density'].default_value=.0007
    vol.inputs['Anisotropy'].default_value=.22
    nt.links.new(vol.outputs[0],out.inputs['Volume'])
    fog=box('Inferred humid valley atmosphere',(0,280,110),(600,620,260),haze)
    move_to(fog,terrain);fog.display_type='WIRE'
    fog['evidence_status']='Art-directed atmosphere; unmeasured weather'
    terrain["evidence_status"] = "Contextual inference, separate from photographic architecture"
    return {"terrain": ground, "conifers": trees, "shrubs": shrubs}
