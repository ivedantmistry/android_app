from rest_framework.exceptions import APIException
from rest_framework import status

class InvalidEmail(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Kindly provide email"
    
class ErrorOccured(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occured."
    