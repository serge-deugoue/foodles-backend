from django.urls import path
from .views import get_users, get_foods, order_food, orders

urlpatterns = [
    path("user/", get_users),
    path("food/", get_foods),
    path("order/", order_food),
    path("order/<int:uid>", orders)
]
