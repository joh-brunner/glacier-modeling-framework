import xarray as xr
import numpy as np
from core.model_component import ModelComponent
from core.glacier_history import GlacierHistory, GlacierChangeEvent
from core.constants import *


class Glacier:
    def __init__(self):
        pass

    def init(self, nx, ny, dx, bed_topo, ice_thickness, surface_type):
        self.data = xr.Dataset(
            {
                "bed_topography": (("y", "x"), bed_topo.data),
                "ice_thickness": (("y", "x"), ice_thickness.data),
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

        self.init(nx, ny, dx, bed_topo, ice_thickness, initial_surface_types)
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

        return initial_surface_types

    def store_data(self, out_path):
        self.data.to_netcdf(out_path)

    # Here we update the glacier data and need to provide some information as well (for the glacier history)
    def update(self, component: ModelComponent, field: str, change: np.ndarray, start_time: int, end_time: int):

        # Store the change in history
        g = GlacierChangeEvent(component, field, change, start_time, end_time)
        self.history_db.add_event(g)

        # Update the glacier state
        if field == "ice_thickness":
            # Thickness can never be negative
            change[np.isnan(change)] = 0
            self.data[field] = np.maximum(self.data[field] + change, 0.0)

        elif field == "surface_type":
            # Decode surface_type change
            self.data[field] = xr.where(change == 0, self.data[field], change % 10)
