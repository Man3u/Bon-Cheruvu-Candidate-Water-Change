# Data provenance

## Sentinel-1A pair

Collection: `COPERNICUS/S1_GRD` (Google Earth Engine). Both exports are descending relative orbit 165, with VV and VH bands. Acquisition date, collection identifier, orbit and band descriptions are stored in the GeoTIFF metadata.

| Date | Input file |
|---|---|
| 9 October 2020 | `data/inputs/Sentinel1A_2020-10-09_VV_VH.tif` |
| 21 October 2020 | `data/inputs/Sentinel1A_2020-10-21_VV_VH.tif` |

Exact identifiers:

```text
COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20201009T003858_20201009T003923_034712_040B2C_3D53
COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20201021T003858_20201021T003923_034887_041153_BC76
```

The local exports have two float32 bands on the same UTM grid. The input data were exported before this repository was assembled. This repository reproduces the local analysis from the included exports; it does not claim to re-run or independently audit Earth Engine's upstream processing.

For the collection processing and data terms, see the [official dataset description](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD). Contains modified Copernicus Sentinel data (2020).

## Analysis polygon and QGIS artifacts

- `data/inputs/bon_cheruvu_analysis_area.gpkg`: one project-defined polygon, reused as the reporting zone. It is not an official cadastral, regulatory or surveyed shoreline boundary.
- `data/qgis_water_change_candidates.tif`: exact original mask produced in QGIS.
- `data/qgis_candidate_area_summary.gpkg`: exact saved QGIS zonal histogram output (`output_zones` layer).
- `maps/bon_cheruvu_water_change_oct2020.pdf`: original reviewed print export.
- `qgis/bon_cheruvu_oct2020.qgz`: portable copy of the working project, restricted to the four relevant layers and using repository-relative sources. Unrelated optical, exploratory and temporary layers have been removed from this copy. The working project on the user's computer remains intact.

## Checksums and outputs

`input_manifest.json` identifies all included data files by SHA-256 and byte count. `results/verification.json` records the source tags and recomputation checks. Outputs were verified on 26 November 2026. No Earth Engine credentials, personal local paths, temporary browser files or account identifiers are required to run the analysis.

## Rights

The repository includes clipped Copernicus-derived imagery and project-created analytical artifacts. Source imagery remains under the applicable Copernicus terms. No blanket licence covering third-party imagery is asserted. No software licence has been chosen for the original code; publishing a repository alone does not grant a general open-source licence.
