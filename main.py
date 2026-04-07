import pandas as pd
from core.states.glacier import Glacier
from core.states.climate import Climate
from core.components.cmb.ti_mass_balance import TIMassBalance
from core.components.climate_downscaling.climate_downscaling import ClimateDownscaling
from core.output.states_writer import StatesWriter
from core.components.surface_type.surface_type import SurfaceType
from core.components.iceflow.ice_flow import IceFlowIGM
from core.constants import *
import time

input_file = "data/input/gridded_data.nc"
output_file = "data/output/output_larsbreen.nc"
climate_data_file = "data/input/climate_historical.nc"

start_date = "2000-01-01"
simulation_duration_years = 10


def main():
    # 1. Init data states
    glacier = Glacier()
    glacier.init_from_gridded_data(input_file)
    climate = Climate(glacier.data.sizes["y"], glacier.data.sizes["x"], glacier.data.attrs["dx"], climate_data_file)

    # 2. Init model components with timesteps
    iceflow = IceFlowIGM(glacier, climate, "weekly")
    iceflow.init_igm()

    climate_downscaling = ClimateDownscaling(glacier, climate, "monthly")

    cmb = TIMassBalance(glacier, climate, "monthly")

    surface_type = SurfaceType(glacier, climate, "yearly")

    # toDo: frontal ablation component
    # frontal_abl = FrontalAblation(glacier, climate, front_abl_dt)

    # 3. Define the order of your components
    # If two components run on the same timestep, the one listed first will be executed first
    model_components = [iceflow, climate_downscaling, cmb, surface_type]

    # 4. Run the simulation
    # Track program execution timing start
    start_time = time.time()

    writer = StatesWriter(glacier, climate, output_file)  # add ncdf output writer
    run_model(model_components, start_date, simulation_duration_years, writer=writer)

    # 5. Store simulation output (so far only in memory)
    # Database output to disk
    glacier.history_db.mem_to_disk()
    glacier.history_db.close()

    # Ncdf output to disk
    writer.finalize()

    # Show program execution timing
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.3f} seconds")


def run_model(model_components, start_date, simulation_years, writer):
    # Create daily timeline (real calendar)
    start = pd.Timestamp(start_date)
    end = start + pd.DateOffset(years=simulation_years)
    times = pd.date_range(start=start, end=end, freq="D")

    update_counts = {comp: 0 for comp in model_components}
    last_ncdf_store_year = None

    for current_time in times:
        # Store NCDF once per year (Jan 1)
        if current_time.month == 1 and current_time.day == 1:
            if last_ncdf_store_year != current_time.year:
                writer.write(current_time)
                last_ncdf_store_year = current_time.year

        for comp in model_components:
            if comp.should_step(current_time):
                end_time = comp.get_end_time(current_time)
                comp.step(current_time, end_time)

                update_counts[comp] += 1
                print(f"{comp.__class__.__name__} updated at {current_time} " f"(count={update_counts[comp]})")


main()
