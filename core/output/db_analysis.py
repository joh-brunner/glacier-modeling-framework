import sqlite3
import numpy as np
import io
from core.constants import *

# A script to test the queries on the database


def blob_to_array(blob: bytes) -> np.ndarray:
    buffer = io.BytesIO(blob)
    buffer.seek(0)
    return np.load(buffer)


def aggregate_change(
    conn,
    component: str,
    field: str,
    start_time: float,
    end_time: float,
):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT change
        FROM glacier_change_events
        WHERE component = ?
          AND field = ?
          AND start_time >= ?
          AND end_time <= ?
        """,
        (component, field, start_time, end_time),
    )

    # row_count = cursor.fetchone()[0]
    # print(row_count)

    total = None

    cnt = 0
    for (blob,) in cursor:
        cnt += 1
        arr = blob_to_array(blob)

        if total is None:
            total = arr.copy()
        else:
            total += arr

    print(cnt)
    return total


import xarray as xr
import numpy as np


def save_multiple_fields_to_netcdf(fields: dict, filename: str):
    """
    fields: dict of {name: 2D numpy array}
    """
    # Assume all arrays have same shape
    first = next(iter(fields.values()))
    ny, nx = first.shape

    data_vars = {name: (("y", "x"), arr) for name, arr in fields.items()}

    # Compute total field
    total = None
    for arr in fields.values():
        if total is None:
            total = arr.copy()
        else:
            total += arr

    # Add total field
    data_vars["dhdt"] = (("y", "x"), total)

    ds = xr.Dataset(
        data_vars,
        coords={
            "y": np.arange(ny),
            "x": np.arange(nx),
        },
    )

    ds.to_netcdf(filename)


# Code

conn = sqlite3.connect("glacier_history.db")

num_of_years = 1

result1 = aggregate_change(
    conn,
    component="LinearMassBalance",
    field="ice_thickness",
    start_time=0,
    end_time=ANNUAL_DT_SECONDS * num_of_years,
)

result2 = aggregate_change(
    conn,
    component="IceFlowIGM",
    field="ice_thickness",
    start_time=0,
    end_time=ANNUAL_DT_SECONDS * num_of_years,
    #end_time=32400000,
)

save_multiple_fields_to_netcdf(
    {
        "linear_mass_balance": result1,
        "ice_flow": result2,
    },
    "debug_change.nc",
)
