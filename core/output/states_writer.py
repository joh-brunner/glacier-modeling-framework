import os
import pandas as pd
import xarray as xr

# This class is intended to store the current state of the glacier and climate (e.g. once per year)


class StatesWriter:
    def __init__(self, glacier, climate, path):
        self.glacier = glacier
        self.climate = climate
        self.path = path
        if os.path.exists(self.path):
            os.remove(self.path)

        # buffer to store all timesteps
        self.buffer = []

    def write(self, t):
        print("Storing fields")

        da_step = {}

        # collect all fields
        data_fields = list(self.glacier.data.data_vars) + list(self.climate.data.data_vars)

        for field in data_fields:
            if field in self.glacier.data:
                data = self.glacier.data[field]
            else:
                data = self.climate.data[field]

            data = data.drop_vars("time", errors="ignore")

            # add time dimension (no copy-heavy .values!)
            da = data.expand_dims(t=[t])
            da_step[field] = da

        # store dataset snapshot in memory
        ds_step = xr.Dataset(
            da_step,
            attrs={**self.glacier.data.attrs, **self.climate.data.attrs},
        )

        self.buffer.append(ds_step)

    def finalize(self):

        for i, ds in enumerate(self.buffer):
            print(i, ds.t.values, ds.t.dtype)
        print("Writing all data to disk...")

        if not self.buffer:
            print("No data to write.")
            return

        # concatenate along time dimension
        ds = xr.concat(self.buffer, dim="t")

        # optional: sort by time (safe)
        ds = ds.sortby("t")

        # write once
        ds.to_netcdf(self.path)

        print(f"Data written to {self.path}")
