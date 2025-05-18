from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')

    readonly_fields = ('created_at', 'updated_at')

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': (
                'role',
                'bio',
                'profile_picture',
                'date_of_birth',
                'phone_number',
                'website',
                'twitter_handle',
                'linkedin_profile',
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'classes': ('wide',),
            'fields': (
                'first_name',
                'last_name',    
                'role',
                'bio',
                'profile_picture',
                'date_of_birth',
                'phone_number',
                'website',
                'twitter_handle',
                'linkedin_profile',
            ),
        }),
    )



    search_fields = ('username', 'email', 'role', 'first_name', 'last_name')
    ordering = ('-created_at',)
