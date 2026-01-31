from glacier_data import Glacier
from linear_mass_balance import LinearMassBalance
from glacier_writer import GlacierWriter
from constants import *
import numpy as np

input_file = "data/input/gridded_data.nc"
output = "data/output.nc"
simulation_duration_years = 5


def main():
    glacier = Glacier()
    glacier.init_from_gridded_data("data/input/gridded_data.nc")

    # toDo: So far, we need to a adjust the timestep manually here to match the cfl criterion
    from ice_flow import IceFlowIGM  # toDo: Late import needed, as IGM somehow changes ncdf library...

    iceflow = IceFlowIGM(glacier, MONTHLY_DT_SECONDS / 2)
    iceflow.init_igm()

    cmb = LinearMassBalance(glacier, ANNUAL_DT_SECONDS)

    # toDo: frontal ablation object
    # frontal_abl = FrontalAblation(glacier, front_abl_dt)

    # Output writer
    writer = GlacierWriter(glacier, "data/output.nc")

    model_components = [iceflow, cmb]
    run_model(model_components, t_end=(simulation_duration_years * ANNUAL_DT_SECONDS), writer=writer)


def run_model(model_components, t_end, writer):
    # Find the smallest timestep across all model components
    dt_min = min(comp.dt for comp in model_components)

    # Create a robust time loop
    times = np.arange(0.0, t_end + dt_min / 2, dt_min)

    for t in times:
        for comp in model_components:
            # update component only if it's time
            if np.isclose(t % comp.dt, 0.0) or np.isclose(comp.dt - (t % comp.dt), 0.0):
                comp.step(comp.dt)
                print(f"{comp.__class__.__name__} updated at t={t:.4f}")

                # toDo: Write output when updating the cmb since it is annual at the moment
                if comp.__class__.__name__ == "ClimaticMassBalance":
                    writer.write(t)


main()
