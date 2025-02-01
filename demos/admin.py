from django.contrib import admin
from .models import ParkingLot, LiveInfo, Comment, Post

admin.site.register(ParkingLot)
admin.site.register(LiveInfo)
admin.site.register(Comment)
admin.site.register(Post)