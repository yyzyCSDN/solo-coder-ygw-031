class DomainRules:
    """Axis, wind and profile input checks used by the existing bridge runtime."""
    AXES={"extend","height","angle","lateral"}
    @classmethod
    def axis(cls,value: str) -> str:
        if value not in cls.AXES: raise ValueError("unknown motion axis")
        return value
    @staticmethod
    def wind_speed(value: float) -> float:
        value=float(value)
        if value<0: raise ValueError("negative wind speed")
        return value
    @staticmethod
    def profile_version(value: int) -> int:
        value=int(value)
        if value<1: raise ValueError("invalid profile version")
        return value
