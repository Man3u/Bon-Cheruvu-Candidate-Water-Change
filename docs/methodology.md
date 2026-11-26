# Method and QGIS workflow

## Inputs and alignment

The paired GeoTIFFs contain band 1 = VV (dB) and band 2 = VH (dB); only VV is used. Both have CRS EPSG:32644, 467 columns, 224 rows and 10 m square cells. Bounds are E 229700 to 234370 and N 1932710 to 1934950. The upper-left origin is (229700, 1934950). Both bands' stored NoData is -9999; the analysis explicitly masks missing or nonfinite VV values.

The raster footprint is rectangular and should not be confused with a clipped lake boundary. The polygon supplies the reporting zone. Python uses pixel-centre inclusion (`all_touched=False`), which reproduces the QGIS counts here. Boundary-cell counting is a raster approximation to polygon coverage.

## QGIS processing

The original working layer names are retained below to explain the expressions; the packaged project keeps only the input pair, final candidate mask and summary polygon.

1. Calculate `s1_vv_change_oct09_oct21`:

   ```text
   "Sentinel1A_2020-10-21_VV_VH@1" - "Sentinel1A_2020-10-09_VV_VH@1"
   ```

2. Calculate `oct2020_darkening_candidates`:

   ```text
   "s1_vv_change_oct09_oct21@1" <= -3
   ```

3. Calculate `water_pre_oct09_test`:

   ```text
   "Sentinel1A_2020-10-09_VV_VH@1" < -15
   ```

4. Calculate `oct2020_darkening_excluding_prewater`:

   ```text
   ("oct2020_darkening_candidates@1" = 1) AND ("water_pre_oct09_test@1" = 0)
   ```

5. Calculate `oct2020_water_change_candidates`:

   ```text
   ("oct2020_darkening_excluding_prewater@1" = 1)
   AND ("Sentinel1A_2020-10-21_VV_VH@1" < -15)
   ```

Use the source raster extent and exact source grid for all calculations. Values are unrounded: a difference of -2.992888 does not meet `<= -3`.

6. Run **Raster layer unique values report**, Band 1: value 1 gives 251 cells over the full raster.
7. Run **Zonal histogram**, using the analysis polygon and final mask, Band 1: `HISTO_0 = 1557`, `HISTO_1 = 168`.
8. Convert counts to hectares: `count * 10 * 10 / 10000`. Save the histogram polygon as a GeoPackage.
9. Style candidate value 0 as transparent and value 1 as cyan; show the polygon with no fill and a red outline. Use the 21 October VV layer underneath, grayscale range -25 to 0 dB. This display stretch affects appearance, not calculated values.
10. Create and export the print layout. Report the polygon candidate area and the absence of independent flood validation on the map.

The original QGIS candidate mask is a floating-point GeoTIFF containing exact 0 and 1 values. Python preserves it as an audit reference and writes a compact byte raster with 255 as NoData. This avoids the floating-point warning in future categorical histogram operations.

## Independent implementation check

`scripts/analyze.py` recomputes the combined Boolean expression from the source VV bands. It checks source grids, the reference mask grid, every valid mask cell and both histogram counts. The supplied `results/verification.json` records zero mask mismatches and matching zonal counts. Source-file SHA-256 hashes are included so inputs can be identified precisely.

## Threshold sensitivity

For each water threshold W in {-16, -15, -14} dB and change threshold D in {-4, -3, -2} dB, the script evaluates:

```text
(pre >= W) AND (post < W) AND (post - pre <= D)
```

Both the pre and post water criteria change together. These runs explore parameter sensitivity; they do not select an optimal threshold or establish accuracy. No spatial sieve or minimum patch size was applied.

## Interpretation

The method screens for a transition to a darker, water-like radar response. Some pixels may lie within pre-existing water because the initial water mask is imperfect. The resulting area cannot be interpreted as total water area, new flooding, permanent lake expansion, encroachment or independently confirmed flood damage.
