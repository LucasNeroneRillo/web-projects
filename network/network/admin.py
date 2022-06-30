from django.contrib import admin

from .models import *

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("posts_liked",)

class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ("likers",)
    
admin.site.register(Post, PostAdmin)
admin.site.register(User, UserAdmin)
