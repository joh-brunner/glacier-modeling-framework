import tensorflow as tf


class IceFlow:
    def __init__(self):
        pass

    def compute_flux_div(self, glacier_data, timestep):
        tensor_flow_glacier_data = self.to_tensorflow(glacier_data)

        # Then we call the IGM solver with our Tensor
        igm_updated_flux = self.igm_update(tensor_flow_glacier_data, timestep)

        return igm_updated_flux.numpy()

    def to_tensorflow(glacier_data):
        # This function transforms the xr GlacierData to a TensorFlow object
        # It should not be too computationally expensive
        tensor_flow_glacier_data = None
        return tensor_flow_glacier_data

    def igm_update(tensor_flow_glacier_data, timestep):
        # This function calls the iceflow module from IGM to update our glacier over the given timestep
        igm_updated_flux = None
        return igm_updated_flux
