import xarray as xr
import numpy as np


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
    def update(self, component, field, change, start_time, end_time):
        """
        Update a field in the dataset and log the change in history.

        Parameters
        ----------
        component : str
            Name of the model component responsible for the update.

        field : str
            Name of the field in the dataset to update.
            Must match a variable in self.data (e.g., "ice_thickness").

        change : array-like or float
            The value to apply to the field. Typically represents an increment
            (e.g., thickness change). Can be a scalar or an array with the same
            shape as the field.

        start_time : datetime or float
            The start time of the process causing the update.
            Can be a datetime object or a model time (e.g., years).

        end_time : datetime or float
            The end time of the process causing the update.
            Must be >= start_time.
        """

        # append the change to the glacier history object
