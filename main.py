from core.glacier_data import Glacier
from core.cmb.linear_mass_balance import LinearMassBalance
from core.output.glacier_writer import GlacierWriter
from core.constants import *
import numpy as np
import time

input_file = "data/input/gridded_data_larsbreen.nc"
output_file = "data/input/output_larsbreen.nc"
simulation_duration_years = 10


def main():
    glacier = Glacier()
    glacier.init_from_gridded_data(input_file)

    from core.iceflow.ice_flow import IceFlowIGM  # toDo: Late import needed, as IGM somehow changes ncdf library...

    # toDo: So far, we need to a adjust the timestep manually here to match the cfl criterion
    iceflow = IceFlowIGM(glacier, MONTHLY_DT_SECONDS / 2)
    iceflow.init_igm()

    cmb = LinearMassBalance(glacier, ANNUAL_DT_SECONDS)

    # toDo: frontal ablation object
    # frontal_abl = FrontalAblation(glacier, front_abl_dt)

    # Output writer
    writer = GlacierWriter(glacier, output_file)

    # Run the model

    start_time = time.time()

    model_components = [iceflow, cmb]
    run_model(model_components, t_end=(simulation_duration_years * ANNUAL_DT_SECONDS), writer=writer)

    # Database
    # glacier.history_db.bulk_add_event_list()
    glacier.history_db.mem_to_disk()
    glacier.history_db.close()

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.3f} seconds")


def run_model(model_components, t_end, writer: GlacierWriter):
    # Find the smallest timestep across all model components
    dt_min = min(comp.dt for comp in model_components)

    # Create a robust time loop
    times = np.arange(0.0, t_end + dt_min / 2, dt_min)

    for t in times:
        for comp in model_components:
            # update component only if it's time
            if np.isclose(t % comp.dt, 0.0) or np.isclose(comp.dt - (t % comp.dt), 0.0):
                comp.step(t)
                print(f"{comp.__class__.__name__} updated at t={t:.4f}")

                # toDo: Write output when updating the cmb since it is annual at the moment
                if comp.__class__.__name__ == "LinearMassBalance":
                    # writer.write(t)
                    pass

    # writer.write_history()


main()
