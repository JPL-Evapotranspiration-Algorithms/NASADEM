# NASADEM v2.0.0 Migration Guide

This guide helps you migrate from NASADEM v1.x to v2.0.0, which modernizes the package to use NASA's official `earthaccess` library.

## What Changed?

### Summary of Breaking Changes

1. **Authentication**: Now uses `earthaccess` instead of custom authentication
2. **Removed Parameters**: `remote`, `offline_ok`, `enforce_checksum` no longer used
3. **Dependency Changes**: Replaced `xmltodict` with `earthaccess`, added `numpy`, `shapely`
4. **Internal Changes**: `LPDAACDataPool` class removed (deprecated)

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

**After (v2.0):**

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

**After (v2.0):**
```python
nasadem = NASADEMConnection()
# earthaccess handles URLs, connectivity, and validation automatically

granule = nasadem.download_tile("n34w118")
```

## Common Migration Scenarios

### Scenario 1: Script with Hardcoded Credentials

**Before:**
```python
from NASADEM import NASADEMConnection

nasadem = NASADEMConnection(
    username="user",
    password="pass"
)
elevation = nasadem.elevation_m(geometry)
```

**After:**
```python
from NASADEM import NASADEMConnection

# Best practice: Use .netrc or environment variables
nasadem = NASADEMConnection()
elevation = nasadem.elevation_m(geometry)
```

### Scenario 2: Using Default Global Instance

This works exactly the same:

```python
from NASADEM import NASADEM

# Works in both v1.x and v2.0
elevation = NASADEM.elevation_m(geometry)
swb = NASADEM.swb(geometry)
```

### Scenario 3: Custom Download Directory

```python
# Works the same in both versions
from NASADEM import NASADEMConnection

nasadem = NASADEMConnection(
    download_directory="~/my_data/nasadem"
)
```

### Scenario 4: Point Extraction

```python
from NASADEM import NASADEM
from rasters import Point

# Works the same in both versions
point = Point(-118.0, 34.0)
elevation = NASADEM.elevation_m(point)
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

**Solution:** Remove references to `LPDAACDataPool`. It's no longer used in v2.0.

**Before:**
```python
from NASADEM.LPDAACDataPool import LPDAACDataPool
```

**After:**
```python
# Don't import LPDAACDataPool - use NASADEMConnection instead
from NASADEM import NASADEMConnection
```

### Downloads are slow or timing out

**Solution:** This should be improved in v2.0 with `earthaccess`. If problems persist:
- Check NASA Earthdata system status: https://status.earthdata.nasa.gov/
- Verify your internet connection
- Try again later (may be temporary server issues)

## Testing Your Migration

After migrating, test with this simple script:

```python
from NASADEM import NASADEM
from rasters import Point

# Test point extraction
point = Point(-118.0, 34.0)
elevation = NASADEM.elevation_m(point)
print(f"Elevation at ({point.x}, {point.y}): {elevation:.1f} m")

# If this works, your migration is successful!
```

## Benefits of v2.0

- ✅ **More Reliable**: Uses NASA's official infrastructure
- ✅ **Better Error Handling**: Automatic retries and clear error messages
- ✅ **Cloud-Optimized**: Direct access to NASA Earthdata Cloud
- ✅ **Actively Maintained**: `earthaccess` is officially supported by NASA
- ✅ **Simpler Authentication**: Multiple options, no URL management needed

## Need Help?

- **Documentation**: See the [README.md](README.md) for full documentation
- **Issues**: Report bugs at https://github.com/gregory-halverson/NASADEM/issues
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for detailed changes

## Rollback (If Needed)

If you need to temporarily use v1.x:

```bash
pip install NASADEM==1.5.0
```

However, note that v1.x may stop working as NASA updates their infrastructure.
