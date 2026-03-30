import os
import xarray as xr

# This class is intended to store the current state of the glacier (e.g. once per year)


class GlacierWriter:
    def __init__(self, glacier, path):
        self.path = path
        if os.path.exists(self.path):
            os.remove(self.path)
        self.glacier = glacier

    def write(self, t):
        print("Storing fields")

        t = float(t)

        fields = ["ice_thickness", "surface_type"]

        # --- build new DataArrays ---
        da_new = {}

        for field in fields:
            data = self.glacier.data[field]

            da = xr.DataArray(
                data.values[None, :, :],
                dims=("t", "y", "x"),
                coords={
                    "t": [t],
                    "y": self.glacier.data.y,
                    "x": self.glacier.data.x,
                },
                name=field,
            )

            da_new[field] = da

        # --- first write ---
        if not os.path.exists(self.path):
            xr.Dataset(
                da_new,
                attrs=self.glacier.data.attrs,
            ).to_netcdf(self.path)
            return

        # --- update existing file ---
        with xr.open_dataset(self.path) as ds_old:

            da_updated = {}

            for field in fields:
                da_old = ds_old[field]
                da_field_new = da_new[field]

                if t in da_old.t.values:
                    # overwrite timestep
                    da_tmp = da_old.copy()
                    da_tmp.loc[dict(t=t)] = da_field_new.squeeze("t")
                else:
                    # append timestep
                    da_tmp = xr.concat([da_old, da_field_new], dim="t")

                da_updated[field] = da_tmp.sortby("t")

        # --- write back ---
        xr.Dataset(
            da_updated,
            attrs=self.glacier.data.attrs,
        ).to_netcdf(self.path)
