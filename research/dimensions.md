# Dimension register

All values are in metres unless stated otherwise. **Every building dimension is a provisional modeling estimate.** This register is not a survey or as-built drawing. The 2019 bridge's reported dimensions are the only source-supported absolute dimensions selected for the model.

## Reported measurements

| Element | Reported value | Source | How it is used |
|---|---:|---|---|
| Rebuilt 2019 road bridge | Length 110; width 12 | S09, CNS-authored bridge report | Anchor the complete bridge span and total deck width where the scene context permits. |
| Bridge reconstruction project route | 270 | S08, contractor completion interview | Context only; includes approaches, not a 270 m deck. |
| Nepal approach roadbed | 8.5 | S08 | Context only; does not replace the reported total bridge width. |
| Older proposed main bridge | Approximately 103 long, 9 clear deck width | S10 | Excluded: an earlier project generation. |

The 110 × 12 m report is linked directly in `source_index.md`; it was not inferred by counting railing posts. Pier spacing, individual slab thickness and railing dimensions remain estimated even when the total deck uses the reported dimensions. A modeled visible approach must not be described as a complete measured bridge if the full span is omitted.

## Provisional architectural model

| Component | Starting modeling value | Basis / confidence |
|---|---:|---|
| High facade overall width | 54 | Front image proportions; medium proportional confidence, low absolute-scale confidence. |
| Central highest facade | Approximately 21.8 high in final builder | Starting proxy 22; revised roof/parapet connections, estimated. |
| Central stone-frame mass | 30 wide | About 56% of high facade width in S01/S03; estimated. |
| Tall front recess/opening | 18.5 wide × 16 high | Roughly 34% of width and 72% of height; estimated. |
| Deeper traversable road passage | 10 wide × 7 high | Distinct smaller clear opening below inner offices; perspective/truck-size proxy; estimated. |
| Overall footprint including low halls | 70 before cornice projections | Revised from starting 64 after comparing wing extension; estimated. |
| Main facade/roof depth | 16 before trim projections | Real aerial references S16/S17 confirm recession but do not reveal the complete roof; inferred. |
| Side-wing width | Approximately 12 each before trim | Residual of 54 minus 30, divided in two; modeling decomposition, not a measured boundary. |
| Stone panel module | Approximately 1 | Visual seam rhythm and conventional construction proxy; estimated. |
| Glazing, mullions, door and canopy depth | Set through visual iteration | No independent measurements; preserve observed spacing and hierarchy. |
| Roof/body depth and rear setbacks | Set through front/oblique/opposite-view iteration | S04 supports plausibility, not a surveyed footprint. |

These values are starting parameters and may change when render comparison reveals disproportion. When they change, update this table from the builder's actual parameters. Do not silently convert the starting values into claims about the real building.

## Proportional checks

Use front-reference ratios before adjusting absolute size: central width/high-facade width ≈0.56; tall recess width/high-facade width ≈0.34; recess height/highest facade ≈0.72. The inner office volume obscures the upper part of the visual recess; road clearance is a separate measurement. Count glazing and window rhythms from source images, while allowing partially hidden inner strips rather than treating every dark band as a separate full-width bay.

The S02 EXIF coordinate, 28.278667° N, 85.378056° E, is the photographer's position. It is useful for geographic identity but cannot locate corners or establish building height. Scene coordinates use a local modeling origin; this scene is not georeferenced terrain.

## Actual bridge representation
The model has a 107 m visible deck from local y=−110 to −3, plus the roughly 3 m bridgehead connection to the facade. Total width is 12 m. This approximates the reported 110 m bridge; it is not an exact bridge survey. The inferred concrete piers, crossheads and abutments are separately collected and carry source-basis metadata.

## Additional depth cross-check

The builder's proposed main body depth is 16 m. S16/S17, obtained after the first dimension register, confirm substantial vestibule recession and a separate inner passage. Both crop or conceal the full roof and side return. Thus 16 m is compatible with the visible spatial hierarchy but cannot be measured or independently validated from these photographs. Keep its confidence low for absolute accuracy and assess the oblique render for plausibility.
