from api.models import Food, User, Order, OrderItem
from django.contrib import admin

# Register your models here.

admin.site.register([User, Food, Order, OrderItem])
