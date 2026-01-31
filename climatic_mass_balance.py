import numpy as np
from model_component import ModelComponent
from constants import *

# Make sure that the step function returns a updated cmb over the given timestep
# Eg. if the timestep is 1 month, your cmb model needs to return monthly cmb
# Options should be daily, monthly, annual

class ClimaticMassBalance(ModelComponent):

    def step(self, dt):
        if dt == ANNUAL_DT_SECONDS:
            cmb = self.get_annual_cmb()
        elif dt == MONTHLY_DT_SECONDS: 
            cmb = self.get_monthly_cmb()
        elif dt == DAILY_DT_SECONDS:
            cmb = self.get_daily_cmb()

        self.glacier.data.ice_thickness.values = np.maximum(self.glacier.data.ice_thickness.values + cmb, 0.0)


