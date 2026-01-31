import os
import xarray as xr


class GlacierWriter:
    def __init__(self, glacier, path):
        self.path = path
        if os.path.exists(self.path):
            os.remove(self.path)
        self.glacier = glacier

    def write(self, t):
        # This function comes from ChatGPT but seems to work

        t = float(t)

        thk = self.glacier.data["ice_thickness"]

        da_new = xr.DataArray(
            thk.values[None, :, :],
            dims=("t", "y", "x"),
            coords={
                "t": [t],
                "y": self.glacier.data.y,
                "x": self.glacier.data.x,
            },
            name="ice_thickness",
        )

        # first write → create file
        if not os.path.exists(self.path):
            xr.Dataset(
                {"ice_thickness": da_new},
                attrs=self.glacier.data.attrs,
            ).to_netcdf(self.path)
            return

        # file exists
        with xr.open_dataset(self.path) as ds_old:
            da_old = ds_old["ice_thickness"]

            if t in da_old.t.values:
                # overwrite existing timestep
                da_updated = da_old.copy()
                da_updated.loc[dict(t=t)] = da_new.squeeze("t")
            else:
                # append new timestep
                da_updated = xr.concat([da_old, da_new], dim="t")

        # keep time sorted (optional but recommended)
        da_updated = da_updated.sortby("t")

        xr.Dataset(
            {"ice_thickness": da_updated},
            attrs=self.glacier.data.attrs,
        ).to_netcdf(self.path)
