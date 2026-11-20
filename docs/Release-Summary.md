# NASADEM v2.0.0 Release Summary

## Overview

NASADEM was overhauled in version 2.0.0, modernizing the package to use NASA's official `earthaccess` library for reliable and efficient data access from NASA's Earthdata Cloud infrastructure.

## Status: ✅ COMPLETE

All components of the v2.0.0 overhaul have been implemented and superseded by `v2.0.1`, `v2.1.0`, `v2.2.0`, and `v2.2.1`.

## What Was Changed in v2.0.0

### Core Implementation

1. **NASADEM/NASADEM.py**
   - Removed dependency on `LPDAACDataPool`
   - Integrated `earthaccess` for data search (`search_tile`) and download (`download_tile`)
   - Simplified authentication (`.netrc`, environment variables, interactive login, direct credentials, and `skip_auth` / CI auto-detection)
   - Maintained backward-compatible API for `elevation_m()`, `elevation_km()`, and `swb()`

2. **pyproject.toml**
   - Added `earthaccess>=0.8.0`, `numpy`, and `shapely`
   - Removed `xmltodict` and `pycksum`

3. **Legacy Module Cleanup**
   - Removed obsolete `LPDAACDataPool.py`, `cksum.py`, and `filenames.csv`

## Support

- **Documentation**: [README.md](../README.md)
- **Migration Guide**: [Migration-Guide.md](Migration-Guide.md)
- **Changelog**: [Changelog.md](Changelog.md)
- **Issues**: https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/issues

---

**v2.0.0 Release Date**: December 19, 2025  
**Current Target Version**: 2.2.1
