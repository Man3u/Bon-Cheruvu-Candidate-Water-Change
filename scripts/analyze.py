"""Reproduce the October 2020 candidate mask and audit the original QGIS result."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_mask

ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    inputs = ROOT / 'data' / 'inputs'
    names = ['Sentinel1A_2020-10-09_VV_VH.tif', 'Sentinel1A_2020-10-21_VV_VH.tif']
    arrays, sources = [], []
    for name in names:
        with rasterio.open(inputs / name) as src:
            if arrays and (src.crs != crs or src.transform != transform or src.shape != shape):
                raise ValueError('The source grids differ; align them before comparing.')
            crs, transform, shape = src.crs, src.transform, src.shape
            profile = src.profile.copy()
            arrays.append(src.read(1, masked=True))
            sources.append({'file': name, 'sha256': hashlib.sha256((inputs / name).read_bytes()).hexdigest(),
                            'tags': src.tags(), 'band_descriptions': list(src.descriptions)})
    if crs.to_epsg() != 32644 or transform.b != 0 or transform.d != 0:
        raise ValueError('Expected an unrotated EPSG:32644 grid.')
    pre, post = arrays
    valid = ~(np.ma.getmaskarray(pre) | np.ma.getmaskarray(post))
    valid &= np.isfinite(pre.data) & np.isfinite(post.data)
    delta = post.data - pre.data
    candidates = valid & (pre.data >= -15) & (post.data < -15) & (delta <= -3)
    zones = gpd.read_file(inputs / 'bon_cheruvu_analysis_area.gpkg').to_crs(crs)
    if len(zones) != 1 or not zones.is_valid.all() or zones.geometry.is_empty.any():
        raise ValueError('Expected one valid, nonempty analysis polygon.')
    inside = geometry_mask(zones.geometry, out_shape=shape, transform=transform, invert=True,
                           all_touched=False)
    pixel_m2 = abs(transform.a * transform.e)
    rows = []
    for label, region in [('whole_raster', valid), ('analysis_polygon', valid & inside)]:
        count = int(np.count_nonzero(candidates & region))
        total = int(np.count_nonzero(region))
        rows.append(dict(scope=label, valid_pixels=total, candidate_pixels=count,
                         noncandidate_pixels=total-count, candidate_area_m2=count*pixel_m2,
                         candidate_area_ha=count*pixel_m2/10000))
    reference_path = ROOT / 'data' / 'qgis_water_change_candidates.tif'
    with rasterio.open(reference_path) as ref:
        if ref.crs != crs or ref.transform != transform or ref.shape != shape:
            raise ValueError('QGIS reference grid does not match the inputs.')
        ref_data = ref.read(1, masked=True)
        if np.any(np.ma.getmaskarray(ref_data)[valid]):
            raise ValueError('QGIS reference has missing cells where both sources are valid.')
        mismatches = int(np.count_nonzero((ref_data.data == 1)[valid] != candidates[valid]))
    if mismatches:
        raise ValueError(f'{mismatches} cells differ from the original QGIS mask.')
    saved = gpd.read_file(ROOT / 'data' / 'qgis_candidate_area_summary.gpkg')
    actual = rows[1]
    if int(saved.iloc[0]['HISTO_1']) != actual['candidate_pixels'] or int(saved.iloc[0]['HISTO_0']) != actual['noncandidate_pixels']:
        raise ValueError('The saved QGIS histogram disagrees with the reproduced counts.')
    # Byte output: 0 = noncandidate, 1 = candidate, 255 = NoData.
    profile.update(count=1, dtype='uint8', nodata=255, compress='deflate')
    with rasterio.open(out / 'water_change_candidates.tif', 'w', **profile) as dst:
        dst.write(np.where(valid, candidates.astype('uint8'), 255).astype('uint8'), 1)
        dst.set_band_description(1, 'Candidate water change: 0=no, 1=yes, 255=NoData')
        dst.update_tags(PRE_DATE='2020-10-09', POST_DATE='2020-10-21',
                        CRITERIA='pre_VV>=-15 AND post_VV<-15 AND post_VV-pre_VV<=-3 dB',
                        INTERPRETATION='Exploratory candidates; not validated flood extent')
    write_csv(out / 'area_summary.csv', rows)
    sensitivity = []
    for water in [-16, -15, -14]:
        for change in [-4, -3, -2]:
            mask = valid & (pre.data >= water) & (post.data < water) & (delta <= change)
            for label, region in [('whole_raster', valid), ('analysis_polygon', valid & inside)]:
                count = int(np.count_nonzero(mask & region))
                sensitivity.append(dict(water_threshold_db=water, darkening_threshold_db=change,
                                        scope=label, candidate_pixels=count,
                                        candidate_area_ha=count*pixel_m2/10000))
    write_csv(out / 'threshold_sensitivity.csv', sensitivity)
    report = dict(grid=dict(crs=str(crs), width=shape[1], height=shape[0],
                            transform=list(transform)[:6], pixel_area_m2=pixel_m2),
                  sources=sources, valid_pixel_count=int(valid.sum()),
                  qgis_mask_mismatches=mismatches, qgis_histogram_matches=True,
                  polygon_counting_rule='Pixel centre inside polygon (all_touched=False)',
                  results=rows)
    (out / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(rows, indent=2))
    print('PASS: exact agreement with original QGIS mask and polygon histogram.')


if __name__ == '__main__':
    main()
