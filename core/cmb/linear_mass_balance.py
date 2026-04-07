import numpy as np
from core.cmb.climatic_mass_balance import ClimaticMassBalance


class LinearMassBalance(ClimaticMassBalance):
    def get_annual_cmb(self):

        thk = self.glacier.data.ice_thickness.values
        bed = self.glacier.data.bed_topography.values

        # Only use on glacier surface elevation
        surface_elevation = np.where(thk != 0, thk + bed, np.nan)

        cmb = self.ela_climatic_mass_balance(surface_elevation=surface_elevation, ela=650.0, grad_acc=0.003, grad_abl=0.015, max_acc=1.0)
        
        # !!! toDo !!!
        acc = cmb
        melt = np.zeros_like(cmb)
        refreeze = np.zeros_like(cmb)

        return (acc, melt, refreeze)

    def ela_climatic_mass_balance(self, surface_elevation, ela, grad_acc=0.005, grad_abl=0.01, max_acc=None):
        # mask: valid glacier cells
        mask = ~np.isnan(surface_elevation)

        # initialize output
        cmb = np.full_like(surface_elevation, np.nan)

        # compute only where valid
        dz = surface_elevation[mask] - ela

        cmb_vals = np.where(
            dz >= 0,
            grad_acc * dz,
            grad_abl * dz,
        )

        if max_acc is not None:
            cmb_vals = np.minimum(cmb_vals, max_acc)

        cmb[mask] = cmb_vals

        # cmb[~mask] = 0

        return cmb
