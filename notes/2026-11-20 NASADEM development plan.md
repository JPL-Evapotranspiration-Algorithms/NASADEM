# NASADEM Development Plan (`v2.1.0` → `v2.2.0`) (2026-11-20)

This document consolidates the complete development and release history of the **NASADEM** package through `v2.1.0` and defines the engineering roadmap to resolve all known bugs, packaging issues, documentation drift, and test/CI gaps for the **`v2.2.0`** release.

---

## Part 1: Historical Development & Release Summary (`v1.0.1` – `v2.1.0`)

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

---

## Part 2: `v2.2.0` Release Plan & Remediation Roadmap

### Phase 1: Core Library Bug Fixes (`NASADEM/NASADEM.py`)
- **Normalize `MultiPoint` Coordinate Extraction:** Inspect `.x` and `.y` coordinate arrays first with a fallback to `.geoms`.
- **Fix `Path` vs. `str` Comparison in `download_tile()`:** Normalize both paths with `abspath(str(...))` before calling `shutil.move()`.
- **Fix Exact Integer Degree Boundary Off-by-One in `tiles_intersecting_bbox()`:** Prevent integer `lon_max` and `lat_max` upper bounds from spilling into adjacent 1°×1° tiles.
- **Clean Up Redundant `NaN` Inequality Check:** Guard `data_layer.nodata` comparisons with explicit `None` and `NaN` checks.

### Phase 2: Packaging & Dependency Cleanup (`pyproject.toml`)
- Bump `version = "2.2.0"`.
- Move `ECOv002_calval_tables` to `[project.optional-dependencies] dev`.
- Remove unused `sentinel-tiles` and duplicate `"pytest"` entries.
- Standardize repository URL to `https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM`.

### Phase 3: Testing, Repository Hygiene & CI/CD
- Add offline unit tests in `tests/test_nasadem_v2.py` covering `NASADEMGranule`, integer bounding boxes, `Path` download handling, and `MultiPoint` constructors.
- Relocate root `test_nasadem_elevation.py` into `tests/test_nasadem_elevation.py` as an `@pytest.mark.integration` test and remove root `debug.py`.
- Upgrade `.github/workflows/ci.yml` and `python-publish.yml` to `actions/checkout@v4` and `actions/setup-python@v5`, adding `ruff` linting.

### Phase 4: Documentation Synchronization
- Update `docs/Changelog.md`, `docs/Release-Summary.md`, `docs/Migration-Guide.md`, `README.md`, and `notes/`.
