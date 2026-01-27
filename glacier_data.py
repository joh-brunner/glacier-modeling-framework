import xarray as xr
import numpy as np

# Maybe Geometry should be split here from things like divflux and climatic_mb


class GlacierData:
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
        ds = xr.open_dataset(gridded_nc, engine="netcdf4")
        nx = ds["x"].shape[0]
        ny = ds["y"].shape[0]
        dx = ds.attrs["dx"]
        bed_topo = ds["topo_smoothed"] - ds[thickness]
        ice_thickness = ds[thickness]
        self.init(nx,ny, dx, bed_topo, ice_thickness)
        ds.close()

    def store_data(self, out_path):
        self.data.to_netcdf(out_path)

glacier = GlacierData()
glacier.init_from_gridded_data("data/input/gridded_data.nc")
        
