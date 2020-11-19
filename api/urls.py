from django.urls import path
from .views import get_users, get_foods, order_food, orders

urlpatterns = [
    path("user/", get_users, name='user'),
    path("food/", get_foods, name='food'),
    path("order/", order_food, name='order'),
    path("order/<int:uid>", orders)
]
