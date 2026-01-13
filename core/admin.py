from django.contrib import admin

from users.models import User

from . import models

# Register your models here.
admin.site.register(models.Color)
admin.site.register(models.Fruit)
admin.site.register(models.Tag)
admin.site.register(models.Filter)
admin.site.register(User)
