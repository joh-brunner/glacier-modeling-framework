import xarray as xr
import numpy as np
from core.model_component import ModelComponent
from core.glacier_history import GlacierHistory, GlacierChangeEvent


class Glacier:
    def __init__(self):
        pass

    def init(self, nx, ny, dx, bed_topo, ice_thickness):
        self.data = xr.Dataset(
            {
                "bed_topography": (("y", "x"), bed_topo.data),
                "ice_thickness": (("y", "x"), ice_thickness.data),
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
        self.init(nx, ny, dx, bed_topo, ice_thickness)
        ds.close()

    def store_data(self, out_path):
        self.data.to_netcdf(out_path)

    # Here we update the glacier data and need to provide some information as well (for the glacier history)
    def update(self, component: ModelComponent, field: str, change: np.ndarray, start_time: int, end_time: int):
        # Store the change in history

        #g = GlacierChangeEvent(component, field, change, start_time, end_time)
        #self.history_db.add_event(g)

        self.data[field] = np.maximum(self.data[field] + change, 0.0)
