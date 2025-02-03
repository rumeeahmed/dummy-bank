class ServiceError(Exception):
    pass


class AlreadyExistsError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass


class InvalidRequestError(ServiceError):
    pass
