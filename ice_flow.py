import os
import tensorflow as tf
import igm as igm

# IGM imports
from igm.processes.iceflow.iceflow import initialize
from igm.utils.grad.compute_divflux import compute_divflux
from igm.processes.iceflow.iceflow import update
from igm.common.core.src import State
from igm.common.runner.configuration.loader import load_yaml_recursive

config = '/home/johannes/Documents/johannes_glacier_modeling/configs/igm_default_config.yaml'


class IceFlow:
    def __init__(self):
        pass

    def init_igm(self, glacier_data):
        # Initialize the glacier variables in the IGM model state
        self.state = State()
        self.update_state(glacier_data)
        self.state.dX = tf.ones_like(self.state.thk) * float(glacier_data.data.dx)
        self.state.x = tf.constant(glacier_data.data.x)
        self.state.y = tf.constant(glacier_data.data.y)
        self.state.it = -1
        
        self.igm_cfg = load_yaml_recursive(os.path.join(igm.__path__[0], "conf"))
        
        initialize(self.igm_cfg, self.state)

    def update_state(self, glacier_data):
        self.state.thk = tf.Variable(glacier_data.data.ice_thickness.data)
        surface_elevation = glacier_data.data.ice_thickness.data + glacier_data.data.bed_topography.data
        self.state.usurf = tf.Variable(surface_elevation)

    def compute_flux_div(self, glacier_data, timestep):
        self.update_state(glacier_data)
        # Then we call the IGM solver with our Tensor
        igm_updated_flux = self.igm_update(timestep)

        return igm_updated_flux.numpy()


    def igm_update(self, timestep):
        # This function calls the iceflow module from IGM to update our glacier over the given timestep
        # IGM: compute ubar and vbar (the x- and y-components of the depth-averaged velocity)
        update(self.igm_cfg, self.state)

        # Compute flux divergence from IGM using upwind fluxes
        divflux = (
            compute_divflux(
                self.state.ubar,
                self.state.vbar,
                self.state.thk,
                self.state.dX,
                self.state.dX,
            )
        )

        print(divflux)

        return divflux
