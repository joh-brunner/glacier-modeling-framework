import os
import numpy as np
import tensorflow as tf
import igm as igm
from core.constants import *

# IGM imports
from igm.common.core.src import State
from igm.processes.iceflow.iceflow import initialize
from igm.utils.grad.compute_divflux import compute_divflux
from igm.processes.iceflow.iceflow import update
from igm.common.runner.configuration.loader import load_yaml_recursive

from core.model_component import ModelComponent

# !!! toDo: pretraining is set to false here now
igm_config_path = "configs/igm"


class IceFlowIGM(ModelComponent):
    def init_igm(self):
        # Initialize the glacier variables in the IGM model state
        self.igm_state = State()
        self.update_igm_state()
        self.igm_state.dX = tf.ones_like(self.igm_state.thk) * float(self.glacier.data.dx)
        self.igm_state.x = tf.constant(self.glacier.data.x)
        self.igm_state.y = tf.constant(self.glacier.data.y)

        # Arrhenius and Sliding:
        arrhenius_factor = 78  # Default = 78 from IGM, MPa^-3 yr^-1 - # should be added to input parameters in config.yaml later?
        self.igm_state.arrhenius = tf.ones_like(self.igm_state.thk) * arrhenius_factor

        sliding_coefficient = 0.045  # default: 0.045. Should be added to input parameters in config.yaml later
        self.igm_state.slidingco = tf.ones_like(self.igm_state.thk) * sliding_coefficient

        self.igm_state.it = 0

        self.igm_cfg = load_yaml_recursive(os.path.join(os.getcwd(), igm_config_path))

        initialize(self.igm_cfg, self.igm_state)

    def update_igm_state(self):
        self.igm_state.thk = tf.Variable(np.nan_to_num(self.glacier.data.ice_thickness.values, nan=0.0))
        surface_elevation = self.glacier.data.ice_thickness.values + self.glacier.data.bed_topography.values
        self.igm_state.usurf = tf.Variable(np.nan_to_num(surface_elevation, nan=0.0))

    def step(self, start_time, end_time):
        self.update_igm_state()

        update(self.igm_cfg, self.igm_state)

        #  --- CFL handling ---
        velomax = (
            max(
                tf.math.reduce_max(tf.math.abs(self.igm_state.ubar)),
                tf.math.reduce_max(tf.math.abs(self.igm_state.vbar)),
            ).numpy()
            / ANNUAL_DT_SECONDS
        )

        dt_seconds = (end_time - start_time).total_seconds()

        # compute the maximum possible time step that complies with CFL condition
        cfl = 0.5  # hard-coded, could be added to input parameters in config.yaml later
        dt_cfl = cfl * int(float(self.glacier.data.dx)) / velomax
        if dt_seconds > dt_cfl:
            raise ValueError(f"Invalid timestep: dt={dt_seconds} > dt_cfl={dt_cfl} (CFL criterion violated)")

        #  --- Flux divergence ---

        # We calculate the divflux with IGM with a given glacier state
        # Compute flux divergence from IGM using upwind fluxes
        divflux = (
            compute_divflux(
                self.igm_state.ubar,
                self.igm_state.vbar,
                self.igm_state.thk,
                self.igm_state.dX,
                self.igm_state.dX,
            )
            / ANNUAL_DT_SECONDS
        )

        # Then we multiply this change over the timestep
        new_thickness = tf.maximum(self.igm_state.thk + dt_seconds * -divflux, 0.0).numpy()
        new_thickness[new_thickness == 0.0] = np.nan

        thickness_change = (dt_seconds * -divflux).numpy()

        # And apply it to the glacier
        self.glacier.update(self, "ice_thickness", thickness_change, start_time, end_time)

        # (Not sure why/if the follwing is needed)
        self.igm_state.it = self.igm_state.it + 1
