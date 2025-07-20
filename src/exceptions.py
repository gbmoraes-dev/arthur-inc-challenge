class FreightError(Exception):
    pass


class InvalidCepError(FreightError):
    pass


class WeightInvalidError(FreightError):
    pass


class DistanceInvalidError(FreightError):
    pass


class FreightTypeInvalidError(FreightError):
    pass


class ExternalAPIError(FreightError):
    pass
