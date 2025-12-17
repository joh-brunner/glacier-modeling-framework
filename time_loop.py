from glacier_data import GlacierData
from ice_flow import IceFlow
from climatic_mass_balance import ClimaticMassBalance
from downscaled_climate_data import DownscaledClimateData

ny, nx = 100, 100
dx = 10
glacier = GlacierData(ny, nx, dx)

iceflow = IceFlow()
clim_mb = ClimaticMassBalance()

climate_data = DownscaledClimateData()

# Simulation settings
time_period = 10
time_step = 1


def time_loop_sync():

    for year in range(time_period, step=time_step):

        # Ice flow update: grid-based
        glacier.data["divflux"].values[:] = iceflow.compute_flux_div(glacier, time_step)

        # Mass balance update: point-based
        # It is slower doing it like this, but it gives great advantage on modularity
        for i in range(ny):
            for j in range(nx):
                glacier.data["climatic_mb"].values[i, j] = clim_mb.compute_point_mb(
                    glacier.data["surface_h"].values[i, j],
                    climate_data,
                    time_step,
                )

        # Continuity equation update: combine ice flow and mass balance
        glacier.data["ice_thickness"].values += glacier.data["divflux"].values + glacier.data["climatic_mb"].values
        glacier.data["surface_h"].values += glacier.data["bed_topography"].values + glacier.data["ice_thickness"].values

        # Optional: store diagnosis output:
        glacier.data.to_netcdf(year)


def time_loop_async():
    # two separate time loops / update routines for ice flow and climatic mb
    # Maybe even a third for frontal ablation
    # ...
    pass
