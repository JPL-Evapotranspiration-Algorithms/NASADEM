# NASADEM - Digital Elevation Model (DEM) Access Utility

This Python package provides utilities for accessing and downloading Digital Elevation Model (DEM) data from the NASADEM dataset, which is a reprocessed version of the Shuttle Radar Topography Mission (SRTM) data.

**Version 2.x** modernizes the package to use NASA's official [`earthaccess`](https://earthaccess.readthedocs.io/) library for reliable and efficient data access from NASA's Earthdata Cloud.

[Gregory H. Halverson](https://github.com/gregory-halverson-jpl) (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G

## What's New in v2.x

- 🚀 **Modern Data Access**: Uses NASA's official `earthaccess` package (`v2.0.0+`)
- ⚡ **Optimized Point Queries**: Tile-grouped point and multipoint extraction with direct pixel indexing (`v2.0.1+`)
- 📐 **Updated Raster Interface**: Bumped `rasters>=1.17.1` for improved bounding box handling (`v2.1.0`)
- 🛠️ **Hardened Geometry & Downloads**: Normalized `MultiPoint` extraction, exact integer bounding-box tile bounds, and streamlined dependencies (`v2.2.0`)
- ✅ **Reliable Downloads**: Built-in retry logic and error handling via `earthaccess`
- ☁️ **Cloud-Optimized**: Direct access to NASA Earthdata Cloud
- 🔐 **Simplified Authentication**: Multiple authentication options (`.netrc`, environment variables, interactive)

## Installation

```bash
pip install NASADEM
```

Or install from source:

```bash
git clone https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM.git
cd NASADEM
pip install -e .
```

## Prerequisites

You need a [NASA Earthdata account](https://urs.earthdata.nasa.gov/users/new) to download NASADEM data.

## Authentication

There are several ways to authenticate:

### Option 1: Interactive Login (Recommended for first-time users)

```python
import earthaccess
earthaccess.login()  # Will prompt for credentials and optionally save them
```

### Option 2: `.netrc` File

Create a `~/.netrc` file with your credentials:

```
machine urs.earthdata.nasa.gov
    login YOUR_USERNAME
    password YOUR_PASSWORD
```

Then set proper permissions:
```bash
chmod 600 ~/.netrc
```

### Option 3: Environment Variables

```bash
export EARTHDATA_USERNAME=your_username
export EARTHDATA_PASSWORD=your_password
```

### Option 4: Direct Credentials

```python
from NASADEM import NASADEMConnection

nasadem = NASADEMConnection(
    username="your_username",
    password="your_password",
    persist_credentials=True  # Optionally save to .netrc
)
```

## Usage

### Basic Usage with Default Instance

```python
from NASADEM import NASADEM
from rasters import RasterGrid

# Define target area
geometry = RasterGrid.from_bbox(
    xmin=-118.5, ymin=33.5, xmax=-117.5, ymax=34.5,
    cell_size=30, crs="EPSG:4326"
)

# Get elevation data
elevation = NASADEM.elevation_m(geometry)
print(f"Elevation range: {elevation.min():.1f} to {elevation.max():.1f} meters")

# Get surface water body mask
water = NASADEM.swb(geometry)
```

### Custom Connection

```python
from NASADEM import NASADEMConnection

# Create connection with custom download directory
nasadem = NASADEMConnection(
    download_directory="~/my_nasadem_data"
)

# Use it the same way
elevation = nasadem.elevation_m(geometry)
```

### Point Extraction

```python
from rasters import Point, MultiPoint
from NASADEM import NASADEM

# Single point
point = Point(-118.0, 34.0)
elevation = NASADEM.elevation_m(point)
print(f"Elevation at point: {elevation:.1f} m")

# Multiple points
points = MultiPoint([
    (-118.0, 34.0),
    (-117.5, 33.8),
    (-118.2, 34.2)
])
elevations = NASADEM.elevation_m(points)
print(f"Elevations: {elevations}")
```

### Working with Tiles

```python
from NASADEM import NASADEM

# Get tiles covering an area
tiles = NASADEM.tiles(geometry)
print(f"Tiles needed: {tiles}")

# Download a specific tile
granule = NASADEM.download_tile("n34w118")
elevation = granule.elevation_m
swb = granule.swb
```

## API Reference

### `NASADEMConnection`

Main class for accessing NASADEM data.

**Methods:**
- `elevation_m(geometry)`: Get elevation in meters
- `elevation_km(geometry)`: Get elevation in kilometers  
- `swb(geometry)`: Get surface water body mask
- `download_tile(tile)`: Download a specific tile
- `tiles(geometry)`: Get list of tiles covering a geometry

**Parameters:**
- `username` (str, optional): NASA Earthdata username
- `password` (str, optional): NASA Earthdata password
- `working_directory` (str, optional): Working directory for temporary files
- `download_directory` (str, optional): Directory for downloaded tiles (default: `~/data/NASADEM`)
- `persist_credentials` (bool, optional): Save credentials to `.netrc` (default: False)
- `skip_auth` (bool, optional): Skip authentication (useful for testing, default: False)

### `NASADEMGranule`

Represents a single NASADEM tile.

**Properties:**
- `elevation_m`: Elevation raster in meters
- `swb`: Surface water body mask
- `geometry`: Raster geometry of the tile
- `tile`: Tile identifier (e.g., "n34w118")

## Data Description

NASADEM provides:
- **Elevation data**: 1 arc-second (~30m) resolution global coverage (60°N to 56°S)
- **Surface water body mask**: Boolean mask of water bodies
- **Void-filled**: Improved version of SRTM with fewer data voids
- **Accuracy**: Vertical accuracy typically better than 16m (absolute), 10m (relative)

## Tile Naming Convention

Tiles are named using latitude/longitude: `{n|s}XX{e|w}XXX`

Examples:
- `n34w118`: 34°N to 35°N, 118°W to 117°W (Los Angeles area)
- `s10e142`: 10°S to 9°S, 142°E to 143°E (Northern Australia)

## Release History

| Version | Release Date | Summary |
| :--- | :--- | :--- |
| **v2.2.0** | 2026-11-20 | Normalized `MultiPoint` extraction, fixed `Path` comparison and integer bbox tile boundaries, cleaned up dependencies |
| **v2.1.0** | 2026-01-13 | Fixed bounding box handling by updating `rasters>=1.17.1` |
| **v2.0.1** | 2025-12-19 | Fixed single-point `elevation_m()` routing and optimized multi-point extraction via tile grouping |
| **v2.0.0** | 2025-12-19 | Major rewrite replacing LP DAAC HTTP scraping with NASA's `earthaccess` package |
| **v1.5.0** | 2025-11-18 | Switched to dynamic package versioning (`importlib.metadata`) and cleaned up logging |
| **v1.4.0** | 2025-10-24 | Added `Point` and `MultiPoint` extraction and optional checksum enforcement |
| **v1.3.1** | 2025-09-28 | Fixed home directory (`~`) expansion in `NASADEMConnection` |
| **v1.3.0** | 2025-07-08 | Replaced `pycksum` with pure-Python POSIX `cksum` for Python 3.10–3.13 compatibility |
| **v1.2.1** | 2025-06-03 | Quieted directory initialization logging |
| **v1.2.0** | 2025-04-07 | Enabled `offline_ok=True` by default and local file existence checks |
| **v1.1.1** | 2025-03-25 | Added `NASADEM` singleton instance and warned instead of raising on missing credentials |
| **v1.0.1** | 2025-03-19 | Initial release |

See [notes/2026-11-20 NASADEM repository history.md](notes/2026-11-20%20NASADEM%20repository%20history.md) for the full commit-level development timeline.

## Migration from v1.x

If you're upgrading from v1.x:

1. **Authentication**: Update to use `earthaccess` authentication methods
2. **No more URL construction**: The package now handles data discovery automatically
3. **Deprecated**: `LPDAACDataPool` class is no longer used
4. **Same API**: The main `elevation_m()`, `elevation_km()`, and `swb()` methods work the same

Old code (v1.x):
```python
from NASADEM import NASADEMConnection

nasadem = NASADEMConnection(
    username="user",
    password="pass",
    remote="https://e4ftl01.cr.usgs.gov"  # Old URL
)
```

New code (v2.0+):
```python
from NASADEM import NASADEMConnection

# Simpler - earthaccess handles the URLs
nasadem = NASADEMConnection(
    username="user",
    password="pass"
)
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:
```python
import earthaccess
earthaccess.login(persist=True)  # Save credentials
```

### Download Failures

The package automatically retries failed downloads. If problems persist:
- Check your internet connection
- Verify your NASA Earthdata credentials
- Check NASA Earthdata system status: https://status.earthdata.nasa.gov/

### Tile Not Available

Some areas may not be covered by NASADEM (latitudes > 60°N or < 56°S). The error message will indicate this.

## References

- NASA JPL. (2013). *Shuttle Radar Topography Mission (SRTM) Digital Elevation Model (DEM)*. NASA Earthdata. Retrieved from [https://earthdata.nasa.gov](https://earthdata.nasa.gov).
- Farr, T. G., Rosen, P. A., Caro, E., Crippen, R., Duren, R., Hensley, S., ... & Alsdorf, D. (2007). The Shuttle Radar Topography Mission. *Reviews of Geophysics*, 45(2), RG2004. [https://doi.org/10.1029/2005RG000183](https://doi.org/10.1029/2005RG000183)
- NASADEM Data Product. (2020). NASA Jet Propulsion Laboratory. Retrieved from [https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001](https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001)
- earthaccess Documentation. Retrieved from [https://earthaccess.readthedocs.io/](https://earthaccess.readthedocs.io/)

## License

See [LICENSE](LICENSE) file.

## Documentation

- [Migration Guide](docs/Migration-Guide.md) - How to upgrade from v1.x to v2.x
- [Changelog](docs/Changelog.md) - Version history and changes
- [Release Summary](docs/Release-Summary.md) - Detailed v2.0.0 release notes
- [Repository History](notes/2026-11-20%20NASADEM%20repository%20history.md) - Full development and release timeline
- [Development Plan](notes/2026-11-20%20NASADEM%20development%20plan.md) - Engineering roadmap through v2.2.0
- [Known Issues](notes/2026-11-20%20known%20issues.md) - Audit log of bugs, packaging items, and technical debt

## Contributing

Issues and pull requests are welcome at https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM
