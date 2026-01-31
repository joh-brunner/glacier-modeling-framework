import numpy as np
from climatic_mass_balance import ClimaticMassBalance


class LinearMassBalance(ClimaticMassBalance):
    def get_annual_cmb(self):
        surface_elevation = self.glacier.data.ice_thickness.values + self.glacier.data.bed_topography.values

        # Aletsch
        # cmb = self.climatic_mass_balance(surface_elevation, ela=3000.0, grad_acc=0.004, grad_abl=0.008, max_acc=2.0)
        cmb= self.ela_climatic_mass_balance(surface_elevation=surface_elevation, ela=650.0, grad_acc=0.003, grad_abl=0.015, max_acc=1.0)
        return cmb

    def ela_climatic_mass_balance(self, surface_elevation, ela, grad_acc=0.005, grad_abl=0.01, max_acc=None):

        dz = surface_elevation - ela

        cmb = np.where(
            dz >= 0,
            grad_acc * dz,  # accumulation
            grad_abl * dz,  # ablation (negative)
        )

        if max_acc is not None:
            cmb = np.minimum(cmb, max_acc)

        return cmb