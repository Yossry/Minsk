class PyPaystackError(Exception):
    """
    Python Paystack Error
    """


class MissingAuthKeyError(PyPaystackError):
    """
    We can't find the authentication key
    """


class InvalidMethodError(PyPaystackError):
    """
    Invalid or unrecoginised/unimplemented HTTP request method
    """


class InvalidDataError(PyPaystackError):
    """
    Invalid input recognised. Saves unecessary trip to server
    """
