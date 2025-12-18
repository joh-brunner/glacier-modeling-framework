from glacier_data import GlacierData
from ice_flow import IceFlow
from climatic_mass_balance import ClimaticMassBalance
from downscaled_climate_data import DownscaledClimateData

ny, nx = 100, 100
dx = 10
glacier = GlacierData(ny, nx, dx)  # load from oggm shop

iceflow = IceFlow()
clim_mb = ClimaticMassBalance()
# frontal ablation object

climate_data = DownscaledClimateData()

# Simulation settings
time_period = 10
time_step = 1

# Firn model? surface type distinction?


def time_loop_sync():

    for time in range(time_period, step=time_step):

        # Climatic_mb update: grid-based
        glacier.data["climatic_mb"].values = clim_mb.compute_climatic_mb(
            glacier.data["surface_h"].values,
            climate_data,
            time_step,
        )

        # Ice_thickness update: mass balance
        glacier.data["ice_thickness"].values += glacier.data["climatic_mb"].values

        # Ice flow update: grid-based
        glacier.data["divflux"].values[:] = iceflow.compute_flux_div(glacier, time_step)

        # Ice_thickness update: mass balance
        glacier.data["ice_thickness"].values += glacier.data["divflux"].values

        # Here you could check for frontal ablation and update the glacier data again
        # 2D Frontal ablation modeling?

        # Optional: store diagnosis output:
        glacier.data.to_netcdf(time)


def time_loop_async():
    # two separate time loops / update routines for ice flow and climatic mb
    # ...
    pass
