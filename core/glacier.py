import pandas as pd
import xarray as xr
import numpy as np
from core.model_component import ModelComponent
from core.glacier_history import GlacierHistory, GlacierChangeEvent
from core.constants import *


class Glacier:
    def init(self, nx, ny, dx, bed_topo, ice_thickness, surface_type):
        self._check_datatype(bed_topo, "bed_topo", np.float32)
        self._check_datatype(ice_thickness, "ice_thickness", np.float32)
        self._check_datatype(surface_type, "surface_type", np.int8)

        self.data = xr.Dataset(
            {
                "bed_topography": (("y", "x"), bed_topo),
                "ice_thickness": (("y", "x"), ice_thickness),
                "surface_type": (("y", "x"), surface_type),
            },
            coords={
                "x": np.arange(nx),
                "y": np.arange(ny),
            },
            attrs={
                "dx": dx,
            },
        )
        self.history_db = GlacierHistory()

    def init_from_gridded_data(self, gridded_nc, thickness="consensus_ice_thickness"):
        ds = xr.open_dataset(gridded_nc)
        nx = ds["x"].shape[0]
        ny = ds["y"].shape[0]
        dx = ds.attrs["dx"]
        bed_topo = ds["topo_smoothed"] - ds[thickness]
        ice_thickness = ds[thickness]
        initial_surface_types = self.get_init_surface_type(bed_topo, ice_thickness)

        self.init(nx, ny, dx, bed_topo.data, ice_thickness.data, initial_surface_types)

        ds.close()

    def get_init_surface_type(self, bed_topo, ice_thickness):
        surface_elevation = bed_topo + ice_thickness

        # glacier only
        glacier_elevation = np.where(ice_thickness == 0, np.nan, surface_elevation)

        # get median glacier evolution
        median_elevation = np.nanmedian(glacier_elevation)

        # classify glacier into ICE / FIRN
        initial_surface_types = np.where(glacier_elevation <= median_elevation, ICE, FIRN)

        # mark off-glacier
        initial_surface_types = np.where(np.isnan(glacier_elevation), OFF_GLACIER, initial_surface_types)

        return initial_surface_types.astype(np.int8)

    # Here we update the glacier data and need to provide some information as well (for the glacier history)
    def update(self, component: ModelComponent, field: str, change: np.ndarray, start_time: pd.Timestamp, end_time: pd.Timestamp, subcomponent: str = ""):

        # Safety check
        self._check_datatype(change, field, self.data[field].values.dtype)

        # Store the change in history, it may include NaNs where no change was computed
        g = GlacierChangeEvent(component, field, change, start_time, end_time, subcomponent)
        self.history_db.add_event(g)

        # Update the glacier state
        if field == "ice_thickness":
            # Possible NaNs, e.g. where cmb was not computed, are set to 0
            change[np.isnan(change)] = 0.0
            # Thickness can never be negative
            self.data[field].values = np.maximum(self.data[field].values + change, 0.0)

        elif field == "surface_type":
            # Decode surface_type change
            self.data[field].values = np.where(change == 0, self.data[field].values, change % 10)

    def _check_datatype(self, arr, name, dtype):
        if not isinstance(arr, np.ndarray):
            raise TypeError(f"{name} must be np.ndarray")

        if arr.dtype != dtype:
            raise TypeError(f"{name} must be one of {dtype}, got {arr.dtype}")
