import pytest

# List of dependencies for v2.0.0
dependencies = [
    "colored_logging",
    "earthaccess",
    "numpy",
    "rasters",
    "shapely"
]

# Generate individual test functions for each dependency
@pytest.mark.parametrize("dependency", dependencies)
def test_dependency_import(dependency):
    __import__(dependency)
