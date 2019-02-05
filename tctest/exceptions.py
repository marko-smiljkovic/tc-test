from rest_framework.exceptions import APIException


class InvalidEmailException(APIException):
    """
    Exception that should be thrown when provided email doesnt pass hunterio test
    """
    status_code = 400
    default_detail = 'Email provided does not seem valid'
    default_code = 'invalid_email'


class PasswordNotStrongEnough(APIException):
    """
    Exception that should be thrown when provided password is not strong enough
    """
    status_code = 400
    default_detail = 'Password provided is not strong enough, should contain at least ' \
                     '1 lowercase, 1 uppercase, 1 number and to have a total length of at least 8'
    default_code = 'weak_password'


class UserAlreadyExists(APIException):
    status_code = 400
    default_detail = 'User already exists'
    default_code = 'user_already_exists'


class CantLikeOwnPost(APIException):
    status_code = 400
    default_detail = 'User cannot like his own post'
    default_code = 'cant_like_own_post'


class EmptyPostException(APIException):
    status_code = 400
    default_detail = 'Cannot create empty post'
    default_code = 'empty_post'


class MissingParameters(APIException):
    status_code = 400
    default_detail = 'Missing API call params'
    default_code = 'missing_parameters'


class BadParameters(APIException):
    status_code = 400
    default_detail = 'Bad API call params'
    default_code = 'bad_parameters'
