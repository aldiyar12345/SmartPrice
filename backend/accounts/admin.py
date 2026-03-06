from django.contrib import admin
from .models import AccountCredential

@admin.register(AccountCredential)
class AccountCredentialAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'generated_code', 'user_code', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('email', 'generated_code', 'user_code')
