from NASADEM import NASADEM
from rasters import RasterGeometry

# Define target area
geometry = RasterGeometry.from_bbox(
    xmin=-118.5, ymin=33.5, xmax=-117.5, ymax=34.5,
    cell_size=30, crs="EPSG:4326"
)
