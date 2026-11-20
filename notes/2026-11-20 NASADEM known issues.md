# Known Issues (2026-11-20)

This document tracks known bugs, packaging issues, documentation inconsistencies, and repository hygiene items identified during the `v2.1.0` codebase review.

---

## 1. Core Library Bugs (`NASADEM/NASADEM.py`)

### 1.1 `MultiPoint` Iteration in `_extract_point_values`
- **Location:** `NASADEM/NASADEM.py`, line 330
- **Issue:** `_extract_point_values` iterates over `geometry.geoms`:
  ```python
  points = [Point(geom.x, geom.y) for geom in geometry.geoms]
  ```
  Depending on how `rasters.MultiPoint` is constructed (e.g., `rt.MultiPoint(x=x_coords, y=y_coords)` in `test_nasadem_elevation.py` vs. tuple coordinates in `tests/test_nasadem_v2.py` vs. `Point` objects in `README.md`), `.geoms` may not behave uniformly across `rasters` and `shapely` versions.
- **Action:** Normalize `MultiPoint` coordinate extraction using `geometry.x` and `geometry.y` arrays (or standard Shapely `.geoms` fallback) and update `README.md` examples to match the supported `MultiPoint` constructor signature.

### 1.2 `Path` vs. `str` Comparison in `download_tile`
- **Location:** `NASADEM/NASADEM.py`, lines 240–248
- **Issue:** `earthaccess.download()` returns a list of `pathlib.Path` objects in `earthaccess>=0.8.0`, whereas `self.tile_filename(tile)` returns a `str`. Comparing `downloaded_file != filename` always evaluates to `True`, triggering `shutil.move()` onto the exact same file path.
- **Action:** Normalize both paths with `abspath(str(downloaded_file)) != abspath(filename)` before moving.

### 1.3 Integer Degree Boundary Off-by-One in `tiles_intersecting_bbox`
- **Location:** `NASADEM/NASADEM.py`, lines 183–187
- **Issue:** When `lon_max` or `lat_max` lies on an exact integer degree boundary (for example, `lon_max = -117.0`), `range(int(np.floor(lon_min)), int(np.floor(lon_max)) + 1)` includes the adjacent eastern/northern tile (`-117` covering `-117°` to `-116°`), triggering unnecessary searches and downloads.
- **Action:** Adjust upper-bound floor logic so exact integer upper boundaries do not spill into the next 1°×1° tile unless `lon_max == lon_min` or `lat_max == lat_min`.

### 1.4 Redundant `NaN` Inequality Check in `_extract_point_values`
- **Location:** `NASADEM/NASADEM.py`, line 378
- **Issue:** `granule.get_elevation_m(geometry=None)` replaces `nodata` values with `np.nan` and assigns `data.nodata = np.nan`. The subsequent check `value != data_layer.nodata` always evaluates to `True` under IEEE 754 floating-point rules (`x != np.nan`).
- **Action:** Rely on `not np.isnan(value)` (and check `data_layer.nodata is not None and not np.isnan(data_layer.nodata)` before comparing).

---

## 2. Packaging & Dependencies (`pyproject.toml`)

- **Unnecessary Runtime Dependency (`ECOv002_calval_tables`):** Listed under `[project] dependencies`, but never imported in `NASADEM/`. It is only used in the standalone root script `test_nasadem_elevation.py`. Move to `[project.optional-dependencies] dev`.
- **Unused Dependency (`sentinel-tiles`):** Listed under `[project] dependencies`, but not imported anywhere in the codebase. Remove if no longer needed.
- **Duplicate Dev Dependency:** `"pytest"` is listed twice under `[project.optional-dependencies] dev`.
- **Repository URL Mismatch:** `pyproject.toml` lists `https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM`, while `README.md`, `docs/Changelog.md`, and `docs/Migration-Guide.md` reference `https://github.com/gregory-halverson/NASADEM`. Standardize across all files.

---

## 3. Documentation Inconsistencies

- **Stale File References in `docs/Release-Summary.md`:** Lists `NASADEM/LPDAACDataPool.py`, `NASADEM/LPDAACDataPool_DEPRECATED.py`, and `NASADEM/cksum.py` as preserved/created files, none of which exist in the repository.
- **Release Date Discrepancy:** `docs/Release-Summary.md` lists the `v2.0.0` release date as `December 19, 2025`, whereas `docs/Changelog.md` lists `2024-12-19`.
- **Broken Relative Links in `docs/`:** `docs/Migration-Guide.md` and `docs/Release-Summary.md` link to `(README.md)`, `(CHANGELOG.md)`, and `(MIGRATION.md)` instead of `(../README.md)`, `(Changelog.md)`, and `(Migration-Guide.md)`.

---

## 4. Testing & CI/CD Hygiene

- **Root-Level `test_nasadem_elevation.py`:** Sits in the repository root instead of `tests/` and runs top-level imports (`ECOv002_calval_tables`) during `pytest` collection without defining `test_*` functions. Move to `examples/` or `debug/` (or convert into an `@pytest.mark.integration` test inside `tests/`).
- **Root-Level `debug.py`:** Scratch file left in the repository root alongside `debug/`. Move into `debug/` or remove.
- **Missing Unit Tests for `NASADEMGranule`:** `test_granule_properties` in `tests/test_nasadem_v2.py` is an empty `pass` stub. Add unit tests using an in-memory `.zip` archive containing synthetic `.hgt` and `.swb` rasters.
- **Outdated GitHub Actions:** `.github/workflows/ci.yml` and `.github/workflows/python-publish.yml` still reference `actions/checkout@v3` and `actions/setup-python@v3`/`v4`. Upgrade to `v4`/`v5`.