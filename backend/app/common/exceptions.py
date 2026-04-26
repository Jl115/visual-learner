class DomainException(Exception):
    pass


class NotFoundError(DomainException):
    pass


class ValidationError(DomainException):
    pass
