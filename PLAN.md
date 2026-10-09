# Jilong Port Reconstruction Implementation Plan

> Agentic execution: the user explicitly authorizes autonomous research, modelling, rendering and correction. Use parallel research and context modelling, with root review of the building and rendered outputs. Available collaboration tools implement this workflow; the superpowers execution subskills are not installed.

**Goal:** Deliver a real editable PBR Blender reconstruction of the 2019 Jilong Port gate with visually evaluated final renders.

**Architecture:** A deterministic Blender Python builder creates a collection-organized model in metres. Architecture and immediate bridge form the evidence-led core; a separate environment module supplies inferred Himalayan terrain and vegetation. Phase checkpoints and camera renders make intermediate and final quality reviewable.

**Tech Stack:** Installed Blender 5.2 alpha, bpy, mathutils, Python standard library, Cycles, local CJK/Tibetan fonts.

**Spec:** `research/design.md` and the pasted user mission.

## Global constraints
- Deliver actual 3D geometry and PBR materials in `.blend`.
- Never present inferred dimensions as surveyed data.
- Preserve source URLs, dated image references, logs, checkpoints, scripts and iteration notes.
- Use background Blender and tracked terminal sessions; finish jobs before delivery.
- Do not mix the 2019 stone-railed bridge view with the 2026 temporary bridge.

## Component map
- `research/architecture.md`, `source_index.md`, `dimensions.md`, `uncertainties.md`: evidence and confidence.
- `scripts/common.py`: collection, mesh and shading helpers.
- `scripts/architecture.py`: facade, portal, office shell, glazing and roof detail.
- `scripts/site_geometry.py`: bridge deck, railings, inspection furniture and paving (name avoids Python's stdlib site module).
- `scripts/environment.py`: contextual terrain and instanced vegetation.
- `scripts/build_scene.py`: deterministic orchestration, cameras, lighting and checkpoints.
- `scripts/render_views.py`: preview and final render jobs.
- `scripts/validate_scene.py`: reopen final scene, assert resource/geometry/camera integrity and output a report.

## Task 1 — Evidence and architectural decomposition
- [x] Establish treaty identity, location, aliases and temporal ambiguity with primary sources.
- [x] Download and inspect dated front photographs; cross-check opposite elevation.
- [x] Document source attribution, photo directions, uncertainty and estimated component dimensions.
- [x] Record unavailable elevations, survey, satellite geometry and nighttime references.

## Task 2 — Blockout / milestone A
- [x] Create stepped 54 m high-facade footprint, raised central frame, tall opening and recessed elevated office volume; side towers and lower wings.
- [x] Use the starting helper interface `box(name, location, dimensions, material, bevel=0.0)` and `mesh(name, vertices, faces, material)`.
- [x] Add bridge deck, road passage and three review cameras.
- [x] Save `checkpoints/01_blockout.blend`, render front, oblique and rear previews, inspect image proportions against refs. Correct portal/silhouette before proceeding.

## Task 3 — Structure, PBR and details / milestone B
- [x] Recess curtain wall bays, provide real mullions, frames, sills and translucent PBR glazing.
- [x] Add stacked cornices, repeating white dentils, parapets, roof membranes, facade seams, entrance columns and doors.
- [x] Add Chinese/Tibetan signage, modelled emblem approximation, inspection kiosks, street/solar lights, lane signs and a scale vehicle.
- [x] Build bridge with editable stone posts, open railing slots, curbs, expansion joints and weathered concrete.
- [x] Materials: granite micro-grain and slab variation; roof bitumen; coated steel; clearcoat automotive paint; rough concrete; physically shaded glass. Surface noise amplitude remains subtle.
- [x] Save detailed checkpoint. Render a front and oblique preview; correct glazing, text, facade trim and material balance based on actual pixels.

## Task 4 — Context and final art direction / milestone C
- [x] Produce irregular triangulated terrain enclosing a valley, with rock and moss shaders and linked low-poly tree geometry; maintain building visibility.
- [x] Add approximate river/rock margins and mountain atmosphere. Label environment as contextual inference.
- [x] Use soft neutral daylight plus directional sun and controlled fill; dusk variant switches world and emissive/luminaire contribution.
- [x] Compose a reference-aligned hero, three-quarter view and opposite-side view. Avoid depth-of-field concealing geometry.
- [ ] Render final daylight hero at least 1800 pixels wide, supporting views at least 1200 pixels wide; use Cycles denoising. Save all settings and logs.

## Task 5 — Validation and delivery
- [ ] Reopen final .blend in a fresh process. Assert object count, geometry, opening clearance, material nodes, camera count, packed resources and render outputs.
- [ ] Inspect final images for floating/intersecting trim, flat/noisy shading, missing letters, cropped roofs and background artifacts.
- [ ] Save `Jilong_Port_2019.blend`, overview README, QA report and contact sheet. Embed research and README as Blender text blocks.

## Bottlenecks and iteration strategy
Unmeasured depth and hidden rear wall details are the main fidelity limits. Installed Blender is an alpha build, so capture API errors and use version-compatible shading settings. Try Metal Cycles; use CPU if device initialization fails. Keep preview resolutions/samples modest and use linked repeated meshes. If final rendering is slow, retain the scene checkpoint and continue tracked render sessions rather than delivering an untested blockout.

## Plan self-review
Every requested visible component maps to tasks 2–4. Visual comparison and re-opening are acceptance checks; geometry unit tests that merely duplicate builder code are omitted. The provided mission ends mid-sentence at the security-infrastructure bullet; its available requirements are preserved verbatim in `research/user_mission.txt`.
