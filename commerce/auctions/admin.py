from django.contrib import admin

from .models import *

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlisted",)
    
admin.site.register(Listings)
admin.site.register(User, UserAdmin)
admin.site.register(Bids)
admin.site.register(Comments)