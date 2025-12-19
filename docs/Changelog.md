# Changelog

All notable changes to the NASADEM package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-19

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

- **BREAKING**: `LPDAACDataPool` class (moved to `LPDAACDataPool_DEPRECATED.py` with deprecation warning)
- **BREAKING**: `filenames.csv` no longer required - data discovery is dynamic
- Custom URL construction logic
- Custom checksum validation (now handled by earthaccess)
- Custom authentication/session management

### Deprecated

- `LPDAACDataPool_DEPRECATED.py`: Old implementation kept for reference only

### Fixed

- Issues with authentication to updated NASA servers
- Broken download links due to NASA infrastructure changes
- Connection timeout issues with retry logic now built-in

### Migration Guide

**v1.x Code:**
```python
from NASADEM import NASADEMConnection

nasadem = NASADEMConnection(
    username="user",
    password="pass",
    remote="https://e4ftl01.cr.usgs.gov"
)
elevation = nasadem.elevation_m(geometry)
```

**v2.0 Code:**
```python
from NASADEM import NASADEMConnection

# Option 1: Let earthaccess handle auth (recommended)
nasadem = NASADEMConnection()  # Uses .netrc or prompts

# Option 2: Provide credentials
nasadem = NASADEMConnection(
    username="user",
    password="pass",
    persist_credentials=True
)

# Same API for data access
elevation = nasadem.elevation_m(geometry)
```

### Security

- Credentials can now be persisted securely to `.netrc` file
- Support for environment variables for CI/CD workflows
- No longer requires credentials in code

## [1.5.0] - Previous Release

- Legacy implementation using custom LP DAAC connection
- Direct HTTP downloads from `e4ftl01.cr.usgs.gov`
- Custom authentication and checksum validation

---

[2.0.0]: https://github.com/gregory-halverson/NASADEM/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/gregory-halverson/NASADEM/releases/tag/v1.5.0
