# Changelog

All notable changes to the NASADEM package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.1] - 2026-11-20

### Fixed

- **Geographic `cell_size` Example (#18)**: Updated `README.md` and `docs/Migration-Guide.md` bounding box examples from `cell_size=30` (30 degrees) to `cell_size=0.00027778` (~30 m / 1 arc-second) in `EPSG:4326`.
- **Documentation Formatting (#24)**: Fixed nested list indentation in `docs/Release-Summary.md` and cleaned up accidental Markdown links inside `README.md` code blocks.

### Changed

- **CI & Tox Configuration (#25)**: Upgraded `.github/workflows/ci.yml` to `actions/checkout@v4` and `actions/setup-python@v5`, added `ruff check NASADEM tests`, and updated `tox.ini` to Python `3.11`–`3.14` excluding integration tests by default.

## [2.2.0] - 2026-11-20

### Fixed

- **MultiPoint Coordinate Extraction**: Normalized `_extract_point_values()` to read `.x` and `.y` coordinate arrays first with a fallback to `.geoms`, supporting all `rasters.MultiPoint` constructor forms.
- **Download Path Comparison**: Converted `pathlib.Path` results from `earthaccess.download()` with `abspath(str(...))` before comparing against target filenames, preventing redundant `shutil.move()` calls.
- **Exact Integer Bounding Box Boundaries**: Adjusted `tiles_intersecting_bbox()` so exact integer `lon_max` and `lat_max` values do not spill into adjacent 1°×1° tiles.
- **Nodata Comparison Guard**: Replaced redundant `value != data_layer.nodata` comparison with explicit `None` and `NaN` checks.

### Changed

- **Cleaned Up Dependencies**: Moved `ECOv002_calval_tables` from runtime `dependencies` to `[project.optional-dependencies] dev`, removed unused `sentinel-tiles`, and removed duplicate `pytest` entries in `pyproject.toml`.
- **Standardized Repository URLs**: Updated GitHub repository links across documentation to `https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM`.
- **Test & CI Hygiene**: Added offline unit tests for `NASADEMGranule`, integer bounding boxes, and `MultiPoint` extraction; moved integration script `test_nasadem_elevation.py` into `tests/`; updated GitHub Actions workflows to `@v4`/`@v5` with `ruff` linting.

## [2.1.0] - 2026-01-13

### Changed

- Updated minimum `rasters` dependency to `>=1.17.1` to fix bounding box handling and package interface compatibility.

## [2.0.1] - 2025-12-19

### Fixed

- Fixed single-point `elevation_m()` routing to use `_extract_point_values()`.
- Optimized multi-point extraction by grouping points by tile and sampling directly via pixel indices.

## [2.0.0] - 2025-12-19

### 🚀 Major Changes

This is a complete rewrite of the package to modernize data access using NASA's official `earthaccess` library.

### Added

- **earthaccess Integration**: Now uses NASA's official `earthaccess` package for reliable data access
- **Multiple Authentication Methods**: Support for `.netrc`, environment variables, interactive login, and direct credentials
- **Cloud-Optimized Access**: Direct access to NASA Earthdata Cloud infrastructure
- **Better Error Handling**: Automatic retries and improved error messages
- **Comprehensive Documentation**: Updated README with examples and migration guide
- **New Tests**: Test suite updated for v2.0.0 with mocking support

### Changed

- **BREAKING**: Removed `LPDAACDataPool` base class - now uses `earthaccess` directly
- **BREAKING**: Removed `remote` parameter from `NASADEMConnection` - URLs handled automatically
- **BREAKING**: Removed `offline_ok` parameter - earthaccess manages connectivity
- **BREAKING**: Removed `enforce_checksum` parameter - earthaccess handles validation
- Authentication now handled by `earthaccess` instead of custom implementation
- Tile downloads now use `earthaccess.download()` instead of custom HTTP requests
- Tile search now uses `earthaccess.search_data()` for better reliability
- Updated dependencies: removed `xmltodict`, added `earthaccess`, `numpy`, `shapely`

### Removed

- **BREAKING**: `LPDAACDataPool` class and `cksum.py`
- **BREAKING**: `filenames.csv` no longer required - data discovery is dynamic
- Custom URL construction logic
- Custom checksum validation (now handled by `earthaccess`)
- Custom authentication/session management

## [1.5.0] - 2025-11-18

- Switched to dynamic package versioning via `importlib.metadata`
- Cleaned up initialization logging and removed unused `Timer` subpackage

---

[2.2.1]: https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/releases/tag/v1.5.0
