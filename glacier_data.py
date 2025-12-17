import xarray as xr
import numpy as np


class GlacierData:
    def __init__(self, ny, nx, dx):
        self.ny = ny
        self.nx = nx
        self.dx = dx
        self.data = xr.Dataset(
            {
                "bed_topography": (("y", "x"), np.zeros((ny, nx), dtype=np.float32)),
                "ice_thickness": (("y", "x"), np.zeros((ny, nx), dtype=np.float32)),
                "surface_h": (("y", "x"), np.zeros((ny, nx), dtype=np.float32)),
                "divflux": (("y", "x"), np.zeros((ny, nx), dtype=np.float32)),
                "climatic_mb": (("y", "x"), np.zeros((ny, nx), dtype=np.float32)),
            },
            coords={"x": np.arange(nx), "y": np.arange(ny)},
        )
