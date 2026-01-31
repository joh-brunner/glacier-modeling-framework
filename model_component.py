class ModelComponent:
    def __init__(self, glacier, dt):
        self.glacier = glacier
        self.dt = dt

    def step(self, dt):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement step(dt)"
        )