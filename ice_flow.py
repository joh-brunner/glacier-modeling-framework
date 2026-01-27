import tensorflow as tf
import igm as igm

# IGM imports
from igm.utils.grad.compute_divflux import compute_divflux
from igm.processes.iceflow.iceflow import update
from igm.common.core.src import State


class IceFlow:
    def __init__(self):
        pass

    def compute_flux_div(self, glacier_data, timestep):
        tensor_flow_glacier_data = self.to_igm_state(glacier_data)

        # Then we call the IGM solver with our Tensor
        igm_updated_flux = self.igm_update(tensor_flow_glacier_data, timestep)

        return igm_updated_flux.numpy()

    def to_igm_state(self, glacier_data):
        # This function transforms the xr GlacierData to a TensorFlow object
        # It should not be too computationally expensive
        self.igm_state_obj = State()

        # Initialize the glacier variables in the IGM model state
        self.igm_state_obj.thk = tf.Variable(glacier_data.data.ice_thickness.data)
        surface_elevation = glacier_data.data.ice_thickness.data + glacier_data.data.bed_topography.data
        self.igm_state_obj.usurf = tf.Variable(surface_elevation)
        
        # Set grid spacing and coordinates
        return
        self.igm_state_obj.dX = tf.ones_like(self.igm_state_obj.thk) * self.dx
        self.igm_state_obj.x = tf.constant(self.x)
        self.igm_state_obj.y = tf.constant(self.y)




        tensor_flow_glacier_data = None
        return tensor_flow_glacier_data

    def igm_update(self, tensor_flow_glacier_data, timestep):
        # This function calls the iceflow module from IGM to update our glacier over the given timestep
        # IGM: compute ubar and vbar (the x- and y-components of the depth-averaged velocity)
        update(self.cfg, self.igm_state_obj)

        # Compute flux divergence from IGM using upwind fluxes
        divflux = (
            compute_divflux(
                self.igm_state_obj.ubar,
                self.igm_state_obj.vbar,
                self.igm_state_obj.thk,
                self.igm_state_obj.dX,
                self.igm_state_obj.dX,
            )
            / SEC_IN_YEAR
        )

        igm_updated_flux = None
        return igm_updated_flux
