# Known Issues (2026-11-20)

This document tracks known bugs, packaging issues, documentation inconsistencies, and repository hygiene items identified during the `v2.1.0` codebase review and resolved across `v2.2.0` and `v2.2.1`.

---

## 1. Core Library Bugs (`NASADEM/NASADEM.py`)

### 1.1 `MultiPoint` Iteration in `_extract_point_values` (#19 — Fixed in v2.2.0)
- **Location:** `NASADEM/NASADEM.py`
- **Issue:** `_extract_point_values` iterated exclusively over `geometry.geoms`, which does not behave uniformly across `rasters.MultiPoint` constructors (`MultiPoint(x=..., y=...)` vs. tuple coordinates vs. `Point` lists).
- **Resolution:** Normalized `MultiPoint` coordinate extraction using `geometry.x` and `geometry.y` arrays with a `.geoms` fallback.

### 1.2 `Path` vs. `str` Comparison in `download_tile` (#20 — Fixed in v2.2.0)
- **Location:** `NASADEM/NASADEM.py`
- **Issue:** `earthaccess.download()` returns `pathlib.Path` objects in `earthaccess>=0.8.0`, whereas `self.tile_filename(tile)` returns a `str`. Comparing `downloaded_file != filename` always evaluated to `True`, triggering `shutil.move()` onto the same path.
- **Resolution:** Normalized both paths with `abspath(str(downloaded_file)) != abspath(filename)` before moving.

### 1.3 Integer Degree Boundary Off-by-One in `tiles_intersecting_bbox` (#21 — Fixed in v2.2.0)
- **Location:** `NASADEM/NASADEM.py`
- **Issue:** When `lon_max` or `lat_max` lay on an exact integer degree boundary (e.g., `lon_max = -117.0`), `range(int(np.floor(lon_min)), int(np.floor(lon_max)) + 1)` included the adjacent eastern/northern tile.
- **Resolution:** Adjusted upper-bound floor logic so exact integer upper boundaries do not spill into the next 1°×1° tile unless `lon_max == lon_min` or `lat_max == lat_min`.

### 1.4 Redundant `NaN` Inequality Check in `_extract_point_values` (#22 — Fixed in v2.2.0)
- **Location:** `NASADEM/NASADEM.py`
- **Issue:** `granule.get_elevation_m(geometry=None)` replaces `nodata` values with `np.nan` and sets `data.nodata = np.nan`, making `value != data_layer.nodata` always `True` under IEEE 754 rules.
- **Resolution:** Guarded nodata comparisons with `nodata is not None and not np.isnan(nodata) and value == nodata`.

---

## 2. Packaging & Dependencies (`pyproject.toml`) (#23 — Fixed in v2.2.0)

- **Unnecessary Runtime Dependency (`ECOv002_calval_tables`):** Moved from `[project] dependencies` to `[project.optional-dependencies] dev`.
- **Unused Dependency (`sentinel-tiles`):** Removed from `[project] dependencies`.
- **Duplicate Dev Dependency:** Removed duplicate `"pytest"` entry under `[project.optional-dependencies] dev`.
- **Repository URL Mismatch:** Standardized repository URLs across `pyproject.toml`, `README.md`, and `docs/` to `https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM`.

---

## 3. Documentation Inconsistencies (#18, #24 — Fixed in v2.2.1)

- **Geographic `cell_size` Example in `README.md` and `docs/Migration-Guide.md` (#18):** Replaced `cell_size=30, crs="EPSG:4326"` (30 degrees per pixel, yielding an empty `0×0` grid) with `cell_size=0.00027778, crs="EPSG:4326"` (~30 m / 1 arc-second).
- **Stale File References & Formatting in `docs/` (#24):** Removed references to deleted files (`LPDAACDataPool.py`, `LPDAACDataPool_DEPRECATED.py`, `cksum.py`), fixed nested list indentation in `docs/Release-Summary.md`, and updated relative links to `../README.md`, `Changelog.md`, and `Migration-Guide.md`.

---

## 4. Testing & CI/CD Hygiene (#25 — Fixed in v2.2.0 / v2.2.1)

- **Root-Level `test_nasadem_elevation.py`:** Moved into `tests/test_nasadem_elevation.py` and wrapped in an `@pytest.mark.integration` test function.
- **Root-Level `debug.py`:** Removed scratch file from repository root.
- **Missing Unit Tests for `NASADEMGranule`:** Added offline unit tests in `tests/test_nasadem_v2.py` using an in-memory `.zip` archive containing synthetic `.hgt` and `.swb` rasters.
- **Outdated GitHub Actions & Tox Matrix:** Upgraded `.github/workflows/ci.yml` and `python-publish.yml` to `actions/checkout@v4` and `actions/setup-python@v5`, added `ruff` linting, and updated `tox.ini` to Python `3.11`–`3.14`.
