import numpy as np
import pandas as pd
from core.components.model_component import ModelComponent
from core.constants import *

# Make sure that the step function returns a updated cmb over the given timestep
# Eg. if the timestep is 1 month, your cmb model needs to return monthly cmb
# Options should be daily, monthly, annual


class ClimaticMassBalance(ModelComponent):

    # We only calculate the CMB on the glacier
    # That means that outline changes can only be caused by ice flow

    def step(self, start_time, end_time):
        if self.dt == "yearly":
            acc, melt, refreeze = self.get_annual_cmb()
        elif self.dt == "monthly":
            acc, melt, refreeze = self.get_monthly_cmb(start_time)
        elif self.dt == "daily":
            cmb = self.get_daily_cmb()

        # Only use on glacier
        acc = np.where(self.glacier.data.ice_thickness.values != 0, acc, np.nan)
        self.glacier.update(self, "ice_thickness", acc, start_time, end_time, "acc")

        melt = np.where(self.glacier.data.ice_thickness.values != 0, melt, np.nan)
        self.glacier.update(self, "ice_thickness", -melt, start_time, end_time, "melt")

        refreeze = np.where(self.glacier.data.ice_thickness.values != 0, refreeze, np.nan)
        self.glacier.update(self, "ice_thickness", refreeze, start_time, end_time, "refreeze")
