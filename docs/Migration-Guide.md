# NASADEM v2.x Migration Guide

This guide helps you migrate from NASADEM v1.x to v2.x, which modernizes the package to use NASA's official `earthaccess` library.

## What Changed?

### Summary of Breaking Changes

1. **Authentication**: Now uses `earthaccess` instead of custom authentication
2. **Removed Parameters**: `remote`, `offline_ok`, `enforce_checksum` no longer used
3. **Dependency Changes**: Replaced `xmltodict` with `earthaccess`, added `numpy`, `shapely`
4. **Internal Changes**: `LPDAACDataPool` class removed

### What Stays the Same?

✅ Main API methods: `elevation_m()`, `elevation_km()`, `swb()`  
✅ Return types and data structures  
✅ Point and raster geometry support  
✅ Tile naming convention  
✅ Default download directory

## Step-by-Step Migration

### Step 1: Update Installation

```bash
pip install --upgrade NASADEM
```

This will automatically install `earthaccess` and other new dependencies.

### Step 2: Update Authentication

**Before (v1.x):**
```python
from NASADEM import NASADEMConnection

nasadem = NASADEMConnection(
    username="my_username",
    password="my_password",
    remote="https://e4ftl01.cr.usgs.gov"
)
```

**After (v2.0+):**

**Option A: Use .netrc file (Recommended)**
```bash
# Create ~/.netrc file
cat > ~/.netrc << EOF
machine urs.earthdata.nasa.gov
    login my_username
    password my_password
EOF

chmod 600 ~/.netrc
```

```python
from NASADEM import NASADEMConnection

# Automatically uses .netrc
nasadem = NASADEMConnection()
```

**Option B: Interactive login**
```python
import earthaccess
earthaccess.login(persist=True)  # Saves to .netrc after prompting

from NASADEM import NASADEMConnection
nasadem = NASADEMConnection()
```

**Option C: Direct credentials**
```python
from NASADEM import NASADEMConnection

nasadem = NASADEMConnection(
    username="my_username",
    password="my_password",
    persist_credentials=True  # Optional: save to .netrc
)
```

**Option D: Environment variables**
```bash
export EARTHDATA_USERNAME=my_username
export EARTHDATA_PASSWORD=my_password
```

```python
from NASADEM import NASADEMConnection
nasadem = NASADEMConnection()  # Uses env vars
```

### Step 3: Update Code

Most of your data access code should work without changes:

**Before and After (Same API):**
```python
from NASADEM import NASADEM
from rasters import RasterGeometry

# Define target area
geometry = RasterGeometry.from_bbox(
    xmin=-118.5, ymin=33.5, xmax=-117.5, ymax=34.5,
    cell_size=30, crs="EPSG:4326"
)

# Get elevation - works the same in both versions
elevation = NASADEM.elevation_m(geometry)
```

### Step 4: Remove Deprecated Parameters

**Before (v1.x):**
```python
nasadem = NASADEMConnection(
    remote="https://e4ftl01.cr.usgs.gov",  # REMOVE
    offline_ok=True,                        # REMOVE
)

granule = nasadem.download_tile("n34w118", enforce_checksum=True)  # REMOVE enforce_checksum
```

**After (v2.0+):**
```python
nasadem = NASADEMConnection()
# earthaccess handles URLs, connectivity, and validation automatically

granule = nasadem.download_tile("n34w118")
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'earthaccess'"

**Solution:** Install or upgrade NASADEM:
```bash
pip install --upgrade NASADEM
```

### Error: Authentication failures

**Solution:** Set up credentials properly:
```python
import earthaccess
earthaccess.login(persist=True)  # Interactive setup
```

### Error: "LPDAACDataPool has no attribute..."

**Solution:** Remove references to `LPDAACDataPool`. It was removed in v2.0.0.

## Need Help?

- **Documentation**: See the [README.md](../README.md) for full documentation
- **Issues**: Report bugs at https://github.com/JPL-Evapotranspiration-Algorithms/NASADEM/issues
- **Changelog**: See [Changelog.md](Changelog.md) for detailed changes
