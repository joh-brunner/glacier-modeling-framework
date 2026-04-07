import numpy as np
import pandas as pd
from core.model_component import ModelComponent
from core.constants import *


class SurfaceType(ModelComponent):
    def step(self, start_time, end_time):
        # Firn vs Ice
        # Look at the 5 year cmb average of every pixel on the grid
        cmb_five_year_avg = self.glacier.history_db.aggregate_change("TIMassBalance", "ice_thickness", end_time - pd.DateOffset(years=5), end_time)
        # cmb_five_year_avg = self.glacier.history_db.aggregate_change("LinearMassBalance", "ice_thickness", end_time - pd.DateOffset(years=5), end_time)

        old = self.glacier.data.surface_type.values

        # Where 5 years cmb is positive -> Firn, else -> Ice
        new = np.where(cmb_five_year_avg > 0, FIRN, ICE)
        new = np.where(np.isnan(cmb_five_year_avg), OFF_GLACIER, new)

        change_map = np.where(old != new, old * 10 + new, 0)

        self.glacier.update(self, "surface_type", change_map.astype(np.int8), start_time, end_time)
