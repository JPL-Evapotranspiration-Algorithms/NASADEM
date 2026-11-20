# NASADEM Repository Development and Release History (2026-11-20)

This document summarizes the complete development and release timeline of the **NASADEM** Python package from its initial release (`v1.0.1`) in March 2025 through `v2.2.0` in November 2026.

---

## Release Overview

| Version | Release Date (UTC) | Summary |
| :--- | :--- | :--- |
| **v1.0.1** | `2025-03-19` | Initial release |
| **v1.1.1** | `2025-03-25` | Singleton `NASADEM` instance, class renames (`NASADEMConnection`), graceful missing credentials |
| **v1.2.0** | `2025-04-07` | Offline mode enabled by default; local file existence caching |
| **v1.2.1** | `2025-06-03` | Quieted directory initialization logs |
| **v1.3.0** | `2025-07-08` | Replaced C-based `pycksum` with pure Python implementation; expanded `~` path handling |
| **v1.3.1** | `2025-09-28` | Restored home directory expansion in `NASADEMConnection` |
| **v1.4.0** | `2025-10-24` | Added `Point` and `MultiPoint` extraction; made checksum enforcement optional |
| **v1.5.0** | `2025-11-18` | Dynamic package versioning via `importlib.metadata`; removed bundled `Timer` utility |
| **v2.0.0** | `2025-12-19` | Major rewrite migrating from legacy LP DAAC HTTP scraping to NASA `earthaccess` |
| **v2.0.1** | `2025-12-19` | Optimized point/multipoint queries via tile grouping and direct pixel indexing |
| **v2.1.0** | `2026-01-13` | Fixed bounding box handling by bumping `rasters` minimum version to `>=1.17.1` |
| **v2.2.0** | `2026-11-20` | Normalized `MultiPoint` extraction, fixed `Path` comparison & integer bbox tile boundaries, cleaned up dependencies & CI |

---

## Detailed Development & Release Timeline

### Phase 1: Foundation & LP DAAC Architecture (`v1.0.1` – `v1.2.1`)

- **`v1.0.1` (2025-03-19) — Initial Release**
  - Established the baseline package architecture (`7e274d7`) using `LPDAACDataPool` to scrape directories, retrieve `.xml` metadata, and download zipped tiles via `wget` from `e4ftl01.cr.usgs.gov`.
- **`v1.1.1` (2025-03-25) — Refactoring & Credential Tolerance**
  - Renamed `SRTM` to `NASADEMConnection` and `SRTMGranule` to `NASADEMGranule`, changing default storage to `~/data/NASADEM` (`faf875c`).
  - Instantiated a default module-level singleton (`NASADEM = NASADEMConnection()`) and briefly bumped `pyproject.toml` to `1.1.0`.
  - Changed missing `LPDAAC_USERNAME` / `LPDAAC_PASSWORD` environment variables from raising a `RuntimeError` to emitting a warning (`435c7ef`).
- **`v1.2.0` (2025-04-07) — Offline-First Defaults**
  - Enabled `offline_ok=True` by default in both `LPDAACDataPool` and `NASADEMConnection` so instantiating the package would not fail without network access (`273ba07`).
  - Added `tile_filename()` to skip remote checks when local `.zip` tiles already exist on disk.
- **`v1.2.1` (2025-06-03) — Logging Cleanup**
  - Commented out repetitive `logger.info` messages for working and download directories during connection initialization (`df1b3d2`).

### Phase 2: Python Compatibility & Point Queries (`v1.3.0` – `v1.5.0`)

- **`v1.3.0` (2025-07-08) — Python 3.12+ Support & Path Expansion**
  - Replaced the external `pycksum` dependency (which failed to build on modern Python versions) with a pure-Python POSIX CRC-32 implementation in `NASADEM/cksum.py` and added unit tests in `tests/test_cksum.py` (`880d876`, `aeda872`).
  - Wrapped file operations in `LPDAACDataPool.py` with `abspath(expanduser(...))` (`862fa84`).
- **`v1.3.1` (2025-09-28) — Home Directory Expansion Fix**
  - Re-enabled `abspath(expanduser(...))` on `working_directory` and `download_directory` inside `NASADEMConnection.__init__` after they had been commented out in `v1.3.0` (`8379234`).
- **`v1.4.0` (2025-10-24) — Point Extraction & Optional Checksums**
  - Added `Point` and `MultiPoint` support to `tiles()`, `elevation_m()`, `elevation_km()`, and `swb()` via `_extract_point_values()` (`34ebbed`).
  - Added `enforce_checksum: bool = False` to `download_URL()` and `download_tile()` so downloads validate file size without failing on legacy checksum mismatches.
- **`v1.5.0` (2025-11-18) — Package Metadata & Cleanup**
  - Replaced static `version.txt` reading with dynamic `importlib.metadata.version("NASADEM")` in `NASADEM/version.py` (`9e3fe73`).
  - Flattened `NASADEM/LPDAAC/LPDAACDataPool.py` into `NASADEM/LPDAACDataPool.py` and removed the unused `NASADEM/timer/` subpackage.

### Phase 3: `earthaccess` Rewrite & Stabilization (`v2.0.0` – `v2.2.0`)

- **`v2.0.0` (2025-12-19) — Migration to NASA `earthaccess`**
  - Rewrote `NASADEMConnection` to authenticate via `earthaccess.login()` and discover/download `NASADEM_HGT` v001 granules via `earthaccess.search_data()` and `earthaccess.download()` (`4fd6d84`).
  - Deleted legacy `LPDAACDataPool.py` (`475` lines), `cksum.py`, `filenames.csv`, and `xmltodict` dependencies (`f63987a`, `668a93d`).
  - Introduced lazy initialization via `_NASADEMProxy` and `skip_auth` / CI environment detection (`CI`, `GITHUB_ACTIONS`, `TRAVIS`, `CIRCLECI`) so importing `NASADEM` in CI pipelines does not trigger interactive login prompts (`9357598`).
  - Added the `tests/test_nasadem_v2.py` mock test suite and excluded `notebooks`, `debug`, `docs`, and `tests` from wheel packaging (`3e0d449`, `91802e7`, `c884fc6`).
- **`v2.0.1` (2025-12-19) — Point Query Performance & Bug Fix**
  - Fixed `elevation_m()` routing so single `Point` geometries use `_extract_point_values()` alongside `MultiPoint` (`86127d0`).
  - Rewrote `_extract_point_values()` to group points by tile (loading each tile once) and compute direct row/column array indices rather than calling `to_point()` per point.
- **`v2.1.0` (2026-01-13) — Bounding Box & `rasters` Interface Fix**
  - Upgraded the minimum `rasters` dependency from `>=1.14.0` to `>=1.17.1` across two commits (`d4fc8bd`, `040a7a2`) to resolve upstream bounding box and package interface issues.
- **`v2.2.0` (2026-11-20) — Edge-Case Hardening, Packaging Cleanup & Test Expansion**
  - Normalized `MultiPoint` extraction, fixed `Path` vs. `str` comparisons in `download_tile()`, fixed integer degree boundary off-by-one errors in `tiles_intersecting_bbox()`, moved `ECOv002_calval_tables` to `dev` dependencies, and expanded unit tests and CI checks.
