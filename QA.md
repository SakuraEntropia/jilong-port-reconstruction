# Quality assurance record

Six local photographs were inspected: dated 2019 front views, supplemental front/opposite views and two official aerial photographs. Front silhouette, four glazed strips per side (the innermost partly concealed in the bridge photographs), the rectangular outer reveal, twelve narrow windows per upper recessed row and the smaller road passage guide the architecture. Hidden depth and terrain are inferred.

Three blockout views, three initial PBR views, three revised views and two polished views were rendered and inspected. Corrections covered coplanar faces, outward normals, pale glazing, rear office enclosure, lower window surrounds, rear mullions, overlapping apron surfaces, unsupported hall edges and bare terrain. The model uses actual meshes and procedural PBR, without photographic projections.

## Independent scene reopening

A fresh Blender process reopened the main file and passed geometry/resource checks:

| Item | Actual result |
|---|---:|
| Scene objects | 6,160 |
| Mesh objects | 6,142 |
| Unique mesh datablocks | 426 |
| Base vertices across instances | 686,295 |
| Base faces across instances | 765,123 |
| Principled PBR materials | 44 |
| Cameras | 5 |
| External fonts | 2, packed |
| External bitmap dependency | None |

Independent rays at x=−4, −2, 0, 2 and 4 m, z=3 m traverse the road opening without collision. The corrected 17.3 m Chinese title clears both inner white plaques by about 0.4 m. A higher ray hits the recessed upper structure. Research documents are embedded as Text blocks; references remain separate with attribution. Initial readout is in logs/geometry_validation.json; the refined geometry check is in logs/14_refined_geometry.json.

## Production rendering

Cycles CPU, adaptive sampling, denoising and AgX. The 2,200 × 1,467 hero uses 128 maximum samples; supporting views are 1,800 × 1,200. The dusk scene is saved separately with artistic lights. The tracked render job and actual image timing are recorded in logs/11_final_renders.log and logs/final_render_stats.json.

## Practical limits

This is an editable visual exterior, not a survey or complete interior. Body depth, bridge supports, hidden elevations, rear 2019 fittings and terrain have weaker evidence than the front. Small Tibetan text and emblem relief are approximations. Dusk illumination and atmosphere are art direction. The inner tower bay is more fully exposed than in the reference bridge photographs; uncalibrated facade depth and equal bay spacing limit the apparent match. Procedural vegetation and ground remain visibly synthetic at close inspection and can be replaced independently of the building.

The alpha build crashes during sandbox GPU detection; native execution was verified. Two native Metal trials were terminated after five and ten minutes respectively without producing an image; device detection succeeded but compilation did not complete within those limits. The verified CPU path produced the production frames. The second smoke-test log and script are retained in logs/. Logs preserve the sky API inspection and compatibility repair.
