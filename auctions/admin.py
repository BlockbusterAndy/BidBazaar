from django.contrib import admin

from .models import User, Listing, Watch, Bid, Comment

# Register your models here.
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "value")
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "comment")

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title")

class WatchAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing")

admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(User)
admin.site.register(Watch, WatchAdmin)