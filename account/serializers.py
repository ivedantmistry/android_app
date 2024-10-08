from rest_framework import serializers
from .models import *

class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type":"password"}, write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "password2"]
        extra_kwargs = {
            "password" : {"write_only": True}
        }

    def save(self, *args, **kwargs):
        email = self.validated_data["email"].lower()
        password1 = self.validated_data["password"]
        password2 = self.validated_data["password2"]
    
        if User.objects.filter(email=email).exists(): #if the email already exist in database
            raise serializers.ValidationError({"error": "email already in use by another user"}) #raise validation errow
        
        if password1 != password2: #check if password correlate
            raise serializers.ValidationError({"error": "Password and confirm Password does not match"})

        self.validated_data['email'] = self.validated_data['email'].lower()
        self.validated_data.pop('password2')
        user = super().save(*args, **kwargs)
        user.set_password(password1)
        user.save()
        return user

class AvatarSerializer(serializers.Serializer):
    avatar = serializers.FileField()
    
class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only = True)
    new_password = serializers.CharField(write_only = True)

class DeleteAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
