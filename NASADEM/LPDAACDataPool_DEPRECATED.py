"""
DEPRECATED: This module is no longer used in NASADEM v2.0.0+

The LPDAACDataPool class has been replaced by earthaccess for accessing NASA data.
This file is kept for reference only.

For new code, use:
    import earthaccess
    earthaccess.login()
    
See: https://earthaccess.readthedocs.io/
"""

import warnings

warnings.warn(
    "LPDAACDataPool is deprecated in NASADEM v2.0.0+. "
    "Use the earthaccess package instead for accessing NASA data.",
    DeprecationWarning,
    stacklevel=2
)
