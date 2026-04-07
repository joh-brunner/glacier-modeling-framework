import numpy as np
import xarray as xr


class Climate:
    def __init__(self, ny, nx, dx, climate_data_file):
        self.gcm_data = xr.open_dataset(climate_data_file)

        self.data = xr.Dataset(
            {
                "scaled_temperature": (("y", "x"), np.zeros((ny, nx))),
                "solid_precip": (("y", "x"), np.zeros((ny, nx))),
                "liquid_precip": (("y", "x"), np.zeros((ny, nx))),
            },
            coords={
                "x": np.arange(nx),
                "y": np.arange(ny),
                "time": 0,  # time is just included for safety reasons, so the mass balance can check if it's calculated for the right downscaled climate data
            },
            attrs={
                "dx": dx,
            },
        )
