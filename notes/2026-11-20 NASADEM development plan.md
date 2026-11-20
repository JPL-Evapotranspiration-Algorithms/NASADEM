# NASADEM Development Plan (`v2.1.0` → `v2.2.1`) (2026-11-20)

This document consolidates the complete development and release history of the **NASADEM** package through `v2.2.0` and defines the engineering roadmap to resolve the remaining documentation, CI/CD, and configuration items for the **`v2.2.1`** patch release.

---

## Part 1: Historical Development & Release Summary (`v1.0.1` – `v2.2.0`)

### Release Overview

| Version | Release Date (UTC) | Milestone Summary |
| :--- | :--- | :--- |
| **v1.0.1** | `2025-03-19` | Initial release using `LPDAACDataPool` HTTP scraping and `wget` downloads |
| **v1.1.1** | `2025-03-25` | Renamed core classes (`NASADEMConnection`, `NASADEMGranule`), added `NASADEM` singleton, tolerated missing credentials |
| **v1.2.0** | `2025-04-07` | Enabled `offline_ok=True` by default and local `.zip` tile existence caching |
| **v1.2.1** | `2025-06-03` | Quieted repetitive working/download directory logs during initialization |
| **v1.3.0** | `2025-07-08` | Replaced C-based `pycksum` with pure-Python POSIX CRC-32 (`NASADEM/cksum.py`) for Python 3.12+ compatibility |
| **v1.3.1** | `2025-09-28` | Restored `abspath(expanduser(...))` home directory expansion in `NASADEMConnection` |
| **v1.4.0** | `2025-10-24` | Added `Point` and `MultiPoint` extraction (`_extract_point_values`) and made checksum enforcement optional |
| **v1.5.0** | `2025-11-18` | Switched to dynamic versioning via `importlib.metadata`, flattened `LPDAACDataPool`, removed unused `timer` module |
| **v2.0.0** | `2025-12-19` | Major architectural rewrite migrating from LP DAAC HTTP scraping to NASA's `earthaccess` library with lazy CI-safe proxy initialization |
| **v2.0.1** | `2025-12-19` | Fixed single-point `elevation_m()` routing and optimized multi-point extraction via tile grouping and direct pixel indexing |
| **v2.1.0** | `2026-01-13` | Resolved bounding box and raster interface issues by bumping `rasters>=1.17.1` |
| **v2.2.0** | `2026-11-20` | Fixed `MultiPoint` extraction (#19), `Path` download comparison (#20), integer bbox boundaries (#21), nodata guards (#22), `pyproject.toml` dependencies (#23), and added unit tests (#25) |

---

## Part 2: Completed Work in `v2.2.0`

### Phase 1: Core Library Bug Fixes (`NASADEM/NASADEM.py`) — ✅ Completed
- **Normalized `MultiPoint` Coordinate Extraction (#19):** Inspected `.x` and `.y` coordinate arrays first with a fallback to `.geoms`.
- **Fixed `Path` vs. `str` Comparison in `download_tile()` (#20):** Normalized both paths with `abspath(str(...))` before calling `shutil.move()`.
- **Fixed Exact Integer Degree Boundary Off-by-One in `tiles_intersecting_bbox()` (#21):** Prevented integer `lon_max` and `lat_max` upper bounds from spilling into adjacent 1°×1° tiles.
- **Cleaned Up Redundant `NaN` Inequality Check (#22):** Guarded `data_layer.nodata` comparisons with explicit `None` and `NaN` checks.

### Phase 2: Packaging & Dependency Cleanup (`pyproject.toml`) — ✅ Completed
- Bumped `version = "2.2.0"`.
- Moved `ECOv002_calval_tables` to `[project.optional-dependencies] dev` (#23).
- Removed unused `sentinel-tiles` and duplicate `"pytest"` entries (#23).
- Standardized repository URL to `https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM` (#23).

### Phase 3: Unit Tests & Root Script Relocation — ✅ Completed
- Added offline unit tests in `tests/test_nasadem_v2.py` covering `NASADEMGranule`, integer bounding boxes, `Path` download handling, and `MultiPoint` constructors (#25).
- Relocated root `test_nasadem_elevation.py` into `tests/test_nasadem_elevation.py` as an `@pytest.mark.integration` test and removed root `debug.py` (#25).
- Updated `docs/Changelog.md`, `docs/Migration-Guide.md`, and `.github/workflows/python-publish.yml` (#24, #25).

---

## Part 3: `v2.2.1` Patch Release Plan & Remediation Roadmap

The **`v2.2.1`** micro-release addresses the remaining documentation examples, Markdown formatting, and CI/test runner configuration items without changing public APIs.

### 1. Fix Geographic `cell_size` Example (#18)
- **Files:** `README.md`, `docs/Migration-Guide.md`
- **Action:** Replace `cell_size=30, crs="EPSG:4326"` (which specifies 30 degrees per pixel and produces a `0×0` grid) with `cell_size=0.00027778, crs="EPSG:4326"` (~30 m / 1 arc-second).

### 2. Fix Markdown List Formatting & Duplicate Notes (#24)
- **Files:** `docs/Release-Summary.md`, `notes/`
- **Action:**
  - Indent nested bullet points under items `1.`, `2.`, and `3.` in `docs/Release-Summary.md` by 3 spaces so numbered list rendering does not reset.
  - Remove duplicate `notes/2026-11-20 NASADEM known issues.md` and consolidate tracking in `notes/2026-11-20 known issues.md`.

### 3. Update CI Workflow & `tox.ini` Matrix (#25)
- **Files:** `.github/workflows/ci.yml`, `tox.ini`
- **Action:**
  - Upgrade `.github/workflows/ci.yml` from `actions/checkout@v3` and `actions/setup-python@v4` to `@v4` and `@v5`.
  - Add a `ruff check NASADEM tests` lint job and pass `-m "not integration"` to `pytest`.
  - Update `tox.ini` `envlist` to `py311,py312,py313,py314` and exclude integration tests by default (`pytest -m "not integration" {posargs}`).

### 4. Release Metadata & Tagging (`v2.2.1`)
- Bump `version = "2.2.1"` in `pyproject.toml`.
- Add `v2.2.1` patch notes to `docs/Changelog.md` and `README.md`.
- Run `ruff check NASADEM tests` and `make test`, tag `v2.2.1`, push to `main --tags`, and close GitHub issues `#18`, `#24`, and `#25`.