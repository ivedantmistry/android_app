from account.models import *
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import random
import datetime
from utils.mailer import Mailer

class UserOtp:
    def __init__(self, email, event):
        self.email = email
        self.event = event 
        self.otp = None
        
    def generate_otp(self):
        """Generate a 6-digit OTP."""
        self.otp = str(random.randint(100000, 999999))
        return self.otp
    
    def send_otp(self, user):
        assert self.otp != None, "call generate_otp() before send_otp()"
        # Check if an OTP already exists for the user and event
        content_type = ContentType.objects.get_for_model(user)
        existing_otp = OTP.objects.filter(content_type=content_type, object_id=user.id, event=self.event)

        # Generate a new OTP code
        mailer = Mailer(email=user.email) 
        mailer.send_otp(user=user, otp_code=self.otp, expiry_time=5, event=self.event) 

        # If an existing OTP is found, update it; otherwise, create a new OTP
        if existing_otp.exists():
            otp_record = existing_otp.first()
            otp_record.otp_code = self.otp
            otp_record.expires_at = timezone.now() + datetime.timedelta(minutes=10)  # Reset expiry time
            otp_record.is_used = False
            otp_record.save()
        else:
            otp_record = OTP.objects.create(
            content_type=ContentType.objects.get_for_model(user),
            object_id=user.id,
            otp_code=self.otp,
            event=self.event,
        )
        return 