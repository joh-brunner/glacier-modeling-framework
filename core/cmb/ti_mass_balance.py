import numpy as np
from core.cmb.climatic_mass_balance import ClimaticMassBalance

ddf_ice = 4.5
precip_f = 1
temp_bias = 0
temp_melt = -1


class TIMassBalance(ClimaticMassBalance):

    def get_monthly_cmb(self, start_time):
        # Check if the current downscaled climate matches the start time:
        if self.climate.data.coords["time"].values != start_time:
            raise Exception("Downscaled climate time does not match MB update time")

        acc = self.climate.data.solid_precip.values * precip_f
        refreeze = np.zeros_like(acc)
        melt = (self.climate.data.scaled_temperature.values + temp_bias - temp_melt) * (ddf_ice * 365 / 12)
        melt = np.maximum(melt, 0)

        return (acc / 1000.0, melt / 1000.0, refreeze / 1000.0)

        """

        # AIR TEMPERATURE: Downscale the gcm temperature [deg C] to each bin
        # Downscale using gcm and glacier lapse rates
        #  T_bin = T_gcm + lr_gcm * (z_ref - z_gcm) + lr_glac * (z_bin - z_ref) + tempchange
        self.bin_temp[:, t_start : t_stop + 1] = self.glacier_gcm_temp[t_start : t_stop + 1] + self.glacier_gcm_lrgcm[t_start : t_stop + 1] * (self.glacier_rgi_table.loc[pygem_prms["mb"]["option_elev_ref_downscale"]] - self.glacier_gcm_elev) + self.glacier_gcm_lrglac[t_start : t_stop + 1] * (heights - self.glacier_rgi_table.loc[pygem_prms["mb"]["option_elev_ref_downscale"]])[:, np.newaxis] + self.modelprms["tbias"]

        # PRECIPITATION/ACCUMULATION: Downscale the precipitation (liquid and solid) to each bin
        # Precipitation using precipitation factor and precipitation gradient
        #  P_bin = P_gcm * prec_factor * (1 + prec_grad * (z_bin - z_ref))
        bin_precsnow[:, t_start : t_stop + 1] = self.glacier_gcm_prec[t_start : t_stop + 1] * self.modelprms["kp"] * (1 + self.modelprms["precgrad"] * (heights - self.glacier_rgi_table.loc[pygem_prms["mb"]["option_elev_ref_downscale"]]))[:, np.newaxis]
        # Option to adjust prec of uppermost 25% of glacier for wind erosion and reduced moisture content
        if pygem_prms["mb"]["option_preclimit"] == 1:
            # Elevation range based on all flowlines
            raw_min_elev = []
            raw_max_elev = []
            if len(fl.surface_h[fl.widths_m > 0]):
                raw_min_elev.append(fl.surface_h[fl.widths_m > 0].min())
                raw_max_elev.append(fl.surface_h[fl.widths_m > 0].max())
            elev_range = np.max(raw_max_elev) - np.min(raw_min_elev)
            elev_75 = np.min(raw_min_elev) + 0.75 * (elev_range)

            # If elevation range > 1000 m, apply corrections to uppermost 25% of glacier (Huss and Hock, 2015)
            if elev_range > 1000:
                # Indices of upper 25%
                glac_idx_upper25 = glac_idx_t0[heights[glac_idx_t0] >= elev_75]
                # Exponential decay according to elevation difference from the 75% elevation
                #  prec_upper25 = prec * exp(-(elev_i - elev_75%)/(elev_max- - elev_75%))
                # height at 75% of the elevation
                height_75 = heights[glac_idx_upper25].min()
                glac_idx_75 = np.where(heights == height_75)[0][0]
                # exponential decay
                bin_precsnow[glac_idx_upper25, t_start : t_stop + 1] = bin_precsnow[glac_idx_75, t_start : t_stop + 1] * np.exp(-1 * (heights[glac_idx_upper25] - height_75) / (heights[glac_idx_upper25].max() - heights[glac_idx_upper25].min()))[:, np.newaxis]
                # Precipitation cannot be less than 87.5% of the maximum accumulation elsewhere on the glacier
                # compute max values for each step over glac_idx_t0, compare, and replace if needed
                max_values = np.tile(
                    0.875 * np.max(bin_precsnow[glac_idx_t0, t_start : t_stop + 1], axis=0),
                    (8, 1),
                )
                uncorrected_values = bin_precsnow[glac_idx_upper25, t_start : t_stop + 1]
                corrected_values = np.max(np.stack([uncorrected_values, max_values], axis=0), axis=0)
                bin_precsnow[glac_idx_upper25, t_start : t_stop + 1] = corrected_values

    """
