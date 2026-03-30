import numpy as np
import xarray as xr

from core.model_component import ModelComponent
from core.glacier_history import GlacierHistory
from core.constants import *


class SurfaceType(ModelComponent):
    def step(self, start_time):
        # Firn vs Ice
        # Look at the 5 year cmb average of every pixel on the grid
        cmb_five_year_avg = self.glacier.history_db.aggregate_change("LinearMassBalance", "ice_thickness", start_time - (ANNUAL_DT_SECONDS * 4), start_time + ANNUAL_DT_SECONDS)

        # Where 5 years cmb is positive -> Firn, else -> Ice
        new = np.where(cmb_five_year_avg > 0, FIRN, ICE)

        new = np.where(np.isnan(cmb_five_year_avg), OFF_GLACIER, new)

        old = self.glacier.data.surface_type

        change_map = xr.where(old != new, old * 10 + new, 0)

        self.glacier.update(self, "surface_type", change_map, start_time, start_time + self.dt)
