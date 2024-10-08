import random
from django.core.mail import send_mail,get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from rest_framework.exceptions import APIException
from rest_framework import status

from utils.exception import *


class Mailer:
    def __init__(self, email=None, service=None):
        self.sender_email = 'babyductss@gmail.com' #default sender email
        self.email = email #receiver email
        self.service = service #service
        
        try:
            #ensure the email is correct
            assert self.email.endswith('.com'), "Incorrect Email Address"
            #create the receivers email list as it should be
            self.receiver_email_list = [self.email] 
        except AssertionError as err:
            #catch and handle the resulting Assertion Error
            raise InvalidEmail(detail=str(err))
        
        #email subject, the value will be provided by the method that handles the mail process
        self.subject = None 
        #email message, the value will be provided by the method that handles the mail process
        self.message = None 
        self.html_content = None
    
    
    def send(self):
        try:
            #ensure that the email subject was provided
            assert self.subject is not None, "provide a mail subject"
            #ensure that the email message was provided
            assert self.message is not None, "provide a mail message"
            console_connection = get_connection('django.core.mail.backends.console.EmailBackend')
            test_connection = get_connection('django.core.mail.backends.locmem.EmailBackend')
            send_mail(self.subject,self.message,self.sender_email,self.receiver_email_list, connection=test_connection, fail_silently=False)
            
        except AssertionError as err:
            #catch and handle the resulting Assertion Error
            raise ErrorOccured(detail= str(err))

    
    def send_with_template(self):
        try:
            #ensure that the email subject was provided
            assert self.subject is not None, "provide a mail subject"
            #ensure that the html content was provided
            assert self.html_content is not None, "provide a html content"
            
            text_content = strip_tags(self.html_content)
            
            email = EmailMultiAlternatives(subject=self.subject, body=text_content, from_email=self.sender_email, to=self.receiver_email_list)
            email.attach_alternative(self.html_content, "text/html")
            email.send()
            
        except AssertionError as err:
            #catch and handle the resulting Assertion Error
            raise ErrorOccured(detail= str(err))
        
    def send_otp(self, user, otp_code, expiry_time, event="OTP Verification"):
        """
        Generates an OTP and sends it to the user.
        
        Args:
            user: The user object (Seller/Buyer) who will receive the OTP.
            otp_code: The generated OTP code.
            expiry_time: The expiry time for the OTP.
            event: Event name for which the OTP is generated (default is 'OTP Verification').
        """
        # Subject of the OTP email
        self.subject = f"{event}: Your One-Time Password (OTP)"

        # Email content
        self.message = f"Hello {user.full_name},\n\n"
        self.message += f"Your One-Time Password (OTP) for {event} is: {otp_code}\n"
        self.message += f"This OTP is valid for the next {expiry_time} minutes. Please do not share this OTP with anyone.\n\n"
        self.message += "Thank you."

        # Send the email using the `send()` method
        self.send()
