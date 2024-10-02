from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from account.models import *

def custom_response(status, message, data=None, http_status=status.HTTP_200_OK):
    return Response({
        "status": status,
        "message": message,
        "data": data
    }, status=http_status)
    
    
def verify_otp(user, event, otp_code):
    """
    Verify if the provided OTP is correct, not expired, and not used.
    """
    try:
        # Retrieve the latest OTP for the given user and event
        otp_instance = OTP.objects.filter(
            content_type=ContentType.objects.get_for_model(user),
            object_id=user.id,
            event=event,
            is_used=False,  # Ensure the OTP hasn't been used yet
        ).latest('generated_at')  # Get the latest OTP by creation time
        print("OTP", otp_instance.otp_code)
        
        # Check if the OTP has expired
        if otp_instance.has_expired():
            raise ValidationError("OTP has expired.")

             # Convert both to strings for comparison and strip whitespace
        if str(otp_instance.otp_code).strip() != str(otp_code).strip():
            print(f"Stored OTP: '{otp_instance.otp_code}', Provided OTP: '{otp_code}'")
            raise ValidationError("Invalid OTP code.")
        
        # If all checks pass, mark the OTP as used
        otp_instance.is_used = True
        otp_instance.save()

        return True  # OTP is valid

    except OTP.DoesNotExist:
        raise ValidationError("OTP not found.")