from django.contrib import admin
from .models import User, Listings, Auctions, Comments, Bids, Trash
# Register your models here.

admin.site.register(User)
admin.site.register(Auctions)
admin.site.register(Listings)
admin.site.register(Comments)
admin.site.register(Bids)
admin.site.register(Trash)
