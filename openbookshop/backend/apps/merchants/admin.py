from django.contrib import admin

from .models import Merchant


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'user', 'status', 'business_license', 'created_at']
    list_filter = ['status']
    search_fields = ['store_name', 'user__username']
