from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class UserAdmin(BaseUserAdmin):
    fieldsets=(
        (None, {'fields': ('username', 'password')}),
        (('Personal Info'), {'fields': ('first_name','last_name','email','phone_number')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff',)
    
admin.site.register(User, UserAdmin)
admin.site.register(OTP)
# Register your models here.
