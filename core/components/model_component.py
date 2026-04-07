import pandas as pd


class ModelComponent:
    def __init__(self, glacier, climate, dt):
        self.glacier = glacier
        self.climate = climate
        self.dt = dt

    def step(self, start_time, end_time):
        raise NotImplementedError(f"{self.__class__.__name__} must implement step(start_time, end_time)")

    def should_step(self, time: pd.Timestamp) -> bool:
        if self.dt == "daily":
            # Always step daily
            return True

        elif self.dt == "weekly":
            # Week starts on Monday (0 = Monday, 6 = Sunday)
            return time.weekday() == 0

        elif self.dt == "monthly":
            return time.is_month_start

        elif self.dt == "yearly":
            return time.is_year_start

        else:
            raise ValueError(f"Unknown timestep '{self.dt}'")

    def get_end_time(self, time: pd.Timestamp):
        if self.dt == "daily":
            return time + pd.offsets.Day()

        elif self.dt == "weekly":
            # Week starts on Monday (0 = Monday, 6 = Sunday)
            return time + pd.offsets.Week(weekday=0)

        elif self.dt == "monthly":
            return time + pd.offsets.MonthBegin()

        elif self.dt == "yearly":
            return time + pd.offsets.YearBegin()

        else:
            raise ValueError(f"Unknown timestep '{self.dt}'")
