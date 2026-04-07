import numpy as np
from core.components.model_component import ModelComponent

lapse_rate = -0.0065
t_solid = 0
t_liq = 2


class ClimateDownscaling(ModelComponent):

    def step(self, start_time, end_time):
        surface_elevation = self.glacier.data.bed_topography.values + self.glacier.data.ice_thickness.values
        self.scale_climate_data(surface_elevation, start_time)

    def scale_climate_data(self, surface_elevation, time):
        # This function loads the precip and temperature from an nc file and distributes it to a 2D grid applying corrections

        temp = self.climate.gcm_data["temp"].sel(time=time).values
        prcp = self.climate.gcm_data["prcp"].sel(time=time).values

        # Temperature lapse rates
        lr_corected_temp = np.ones_like(surface_elevation) * temp + lapse_rate * (surface_elevation - self.climate.gcm_data.ref_hgt)
        self.climate.data.scaled_temperature.values = lr_corected_temp

        # Precipitation splitting (using lr corrected temperature)
        fac = 1 - (lr_corected_temp - t_solid) / (t_liq - t_solid)
        prcp_solid = prcp * np.clip(fac, 0, 1)
        self.climate.data.solid_precip.values = prcp_solid

        prcp_liquid = prcp - prcp_solid
        self.climate.data.liquid_precip.values = prcp_liquid

        self.climate.data = self.climate.data.assign_coords(time=time)
