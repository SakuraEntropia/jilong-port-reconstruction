# Render and correction log

## A — blockout, 9 October 2026
Built and saved `checkpoints/01_blockout.blend`; rendered three actual Cycles CPU views at 900 × 600, 16 samples. The front, oblique and rear images were inspected directly.

The stepped silhouette, side glazing, deep central recess and nested road passage are recognizable. Black patches at the top corners reveal coplanar overlap between the tall piers and lintel; fixed by terminating piers at 16 m rather than overlapping the header. The front camera was widened by increasing distance from 88 to 97 m to include low-wing extremities. The rear camera moved into the valley corridor, clear of inferred slopes.

The initial Metal job detected Apple M5 GPU correctly but spent over five minutes in first-use kernel compilation without producing an image. The already successful CPU path was selected for production, and that tracked GPU job was terminated. Native Blender requires an execution outside the filesystem sandbox because sandbox GPU detection crashes before Python starts. A minimal native test passed. Blender 5.2 renamed Nishita to SINGLE_SCATTERING and dust_density to aerosol_density; its RNA properties were inspected and compatibility handling added.

## B — detailed model
Built `checkpoints/02_detailed.blend`, 3,302 scene objects. Packed two fonts. Real stone grids, stepped relief trim, curtain frames, lower hall glazing, emblem and signs, bridge railings, kiosks, solar lamps, generic cargo truck and contextual valley are present. The site-only native smoke build and environment-only smoke build passed. Detailed rendered comparison is the next acceptance gate; successful Python execution alone is not final acceptance.

## C — material/environment review and corrections

All three detailed 960 × 640 previews were inspected. The initial glass was too pale; darkened its tint and transmission to match reference contrast. The direct-mesh helper's face winding was corrected to outward normals. Several wall/roof faces overlapped at exterior planes; corrected wall terminations and inset roof geometry. The rear office facade lacked enclosing wall panels; added clearly inferred office bands and window piers instead of exposed shelves.

Initial terrain was a bare angular V with low ground beneath halls. Inspected previews justified a smooth supported bridgehead terrace, wider asymmetrical slopes, a distant closing ridge, richer rock/moss PBR and a clustered forest. The rebuilt scene contains 2,250 linked conifers and 1,200 linked shrubs. Original preview images remain in `renders/iteration_01` and the original detailed scene remains in `checkpoints/02_initial_materials.blend`.

The second front/oblique/rear previews verify that halls meet ground and dark glazing is clearer. A last visible gap between lower office windows was sealed with a lintel and proper window surrounds. Added an inferred north road continuation and small foundations; no surveyed plan is claimed. The primary front facade retains its 2019 gold text; rear red signage is explicitly marked later-reference inference.

## D — full-resolution lettering review

The first 2,200 × 1,467 hero and 1,800 × 1,200 oblique images exposed a genuine sign collision: the 19.4 m gold title intersected the inner white plaque tiles. Reference 01 places all Chinese characters between those tiles. An independent reference review confirmed reducing the title to 17.3 m, leaving about 0.4 m at both sides. The source builder and editable main scene now carry this correction.

A bounded region of each affected view is re-rendered from the corrected 3D text using the original Cycles samples, camera and lighting. Blender composites that ray-traced region over the original full-frame Cycles result. Original frames remain in renders/iteration_02/. This is a geometry correction, not painted lettering or photographic projection. The temporary compositor and background image are removed before saving the production scenes.

The alpha compositor changed its Alpha Over input order; inspecting native RNA established the named Background, Foreground and Factor sockets. The input full-frame PNG uses AgX Base sRGB so its display transform is inverted before output; outside-region differences after the roundtrip were at most one 8-bit channel value. Dusk exposure is compensated on the background input to prevent applying it twice. logs/lettering_region_stats.json records the actual regions and timings.
