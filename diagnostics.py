import xarray as xr
import numpy as np

# Maybe Geometry should be split here from things like divflux and climatic_mb


class Diagnostics:
    def __init__(self):
        pass

    def init(self, nx, ny, timesteps, bed_topo, ice_thickness):
        self.data = xr.Dataset(
            {
                "divflux": (("y", "x"), bed_topo.data),
                "climatic_mb": (("y", "x"), ice_thickness.data),
            },
            coords={
                "x": np.arange(nx),
                "y": np.arange(ny),
            },
            attrs={
                "time": timesteps,
            },
        )

    def store_data(self, out_path):
        self.data.to_netcdf(out_path)

        
