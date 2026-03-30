import numpy as np
from core.model_component import ModelComponent
from core.constants import *

# Make sure that the step function returns a updated cmb over the given timestep
# Eg. if the timestep is 1 month, your cmb model needs to return monthly cmb
# Options should be daily, monthly, annual


class ClimaticMassBalance(ModelComponent):

    # We only calculate the CMB on the glacier
    # That means that outline changes can only be caused by ice flow

    def step(self, start_time):
        if self.dt == ANNUAL_DT_SECONDS:
            cmb = self.get_annual_cmb()
        elif self.dt == MONTHLY_DT_SECONDS:
            cmb = self.get_monthly_cmb()
        elif self.dt == DAILY_DT_SECONDS:
            cmb = self.get_daily_cmb()

        self.glacier.update(self, "ice_thickness", cmb, start_time, start_time + self.dt)
