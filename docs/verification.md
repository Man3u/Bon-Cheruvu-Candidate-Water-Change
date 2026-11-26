# Verification record

Checked on 26 November 2026.

- Source CRS, dimensions and affine transforms match exactly.
- Both VV inputs have 104,608 valid pixels.
- Recomputed candidate mask agrees at every valid cell with the original QGIS mask.
- Whole-raster count: 251 candidate pixels, 2.51 ha.
- Polygon count: 168 candidate and 1,557 noncandidate pixels, 1.68 ha candidates.
- Polygon counts agree with the saved QGIS zonal histogram.
- Nine threshold combinations reproduce a polygon sensitivity range of 1.21 to 1.94 ha.
- Packaged QGIS project loads successfully after relocation to a separate directory; all four retained layers resolve inside that directory and are valid.
- Print layout renders successfully from the packaged project and was visually checked.
- Original PDF and generated PNG preview were visually checked for clipping and overlap.

Local analysis environment: NumPy 2.5.3, Rasterio 1.5.1, GeoPandas 1.1.4. Dependency ranges in requirements.txt allow compatible installations; this is the environment actually exercised.

These checks establish computational consistency and map portability. They do not validate water or flood classification accuracy.
