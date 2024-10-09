from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import user_logged_in

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from utils.mailer import Mailer
from utils.otp import UserOtp
from utils.helper import *
from utils.token import CustomRefreshToken

from .serializers import *
from .models import User

class SignupView(APIView): 
    authentication_classes = []
    permission_classes=[AllowAny]

    @swagger_auto_schema(
        operation_summary="Sign Up Endpoint",
        operation_description="This is to create an account",
        operation_id="account-creation",
        request_body=RegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='success'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='otp is sent to your email address for your account verification'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='error'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='An error occured.'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            )
        }
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #send email verification message
            otp = UserOtp(user.email, 'registration')
            otp.generate_otp()
            otp.send_otp(user)
            return custom_response(
                status="success",
                message=f"{user.first_name}, otp is sent to your email address for your account verification.",
                data={'id': user.id},
                http_status=status.HTTP_201_CREATED
            )
        else:
            return custom_response(
                status="error",
                message=f"An error occured.",
                data=serializer.errors,
                http_status=status.HTTP_403_FORBIDDEN
            )
        

class AccountVerificationView(APIView):
    authentication_classes = []
    permission_classes=[AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Account Email Verification Endpoint",
        operation_description="This is to verify user email with otp",
        operation_id="email-otp-verification",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='success'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='Account email verified'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='error'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='Invalid OTP'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            )
        }
    )
    def get(self, request, id, otp):
        user = get_object_or_404(User, id=id)
        if not verify_otp(user, 'registration', otp):
            return custom_response(
                status="error",
                message=f"Invalid OTP.",
                data={},
                http_status=status.HTTP_403_FORBIDDEN
            )
        
        user.email_verified = True #This toogles to True
        user.status = 'active'
        user.save()
        return custom_response(
            status="success",
            message=f"Account email verified.",
            data={},
        )
            
        
class SigninView(APIView):
    authentication_classes = []
    permission_classes=[AllowAny] 
    @swagger_auto_schema(
        operation_summary="Login Endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
            required=['email', 'password'],
        ),
        operation_id="login",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='success'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='Login successful, User Authenticated!'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='error'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='Wrong Password.'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='error'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='Email not verified.'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            ),
            404: openapi.Response(
                description="Not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example='error'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example='No user found with this email.'),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT, example="{}"),
                    }
                )
            )
        }
    )
    def post(self, request):
        password = request.data["password"]
        data = {}
        try:
            user = User.objects.get(email=request.data['email'].lower())
            if user.check_password(password):
                if user.email_verified:
                    refresh = CustomRefreshToken(user_id=user.id, email=user.email, user_type='buyer')
                    
                    user_logged_in.send(sender=user.__class__, request=request, user=user)
                    data["message"] = "Login successful, User Authenticated!"
                    data["token"] = str(refresh.access_token)
                    data['refresh'] = str(refresh)
                    
                    return custom_response(
                        status="success",
                        message=f"Login successful",
                        data=data,
                    )
    
                else:
                    data["message"] = "Email not verified"
                    return custom_response(
                        status="error",
                        message=f"Forbidden",
                        data=data,
                        http_status=status.HTTP_403_FORBIDDEN
                    )
            else:
                data["message"] = "Wrong Password"
                return custom_response(
                    status="error",
                    message=f"Bad Request",
                    data=data,
                    http_status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            data["message"] = "No user found with this email"
            return custom_response(
                status="error",
                message=f"Not found",
                data=data,
                http_status=status.HTTP_404_NOT_FOUND
            )

# Create your views here.
