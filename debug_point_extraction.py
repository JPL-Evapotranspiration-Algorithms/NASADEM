# %%
from rasters import Point
from NASADEM import NASADEM

# %%
geometry = Point(-118, 35)
geometry

# %%
value = NASADEM.elevation_km(geometry=geometry)
print(value)
# %%



