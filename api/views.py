from api.serializers import FoodSerializer, OrderSerializer, UserSerializer
from .models import User, Food, Order
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

# Create your views here.


@api_view()
def get_users(request):
    """Get the list of all users in the database
    """

    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view()
def get_foods(request):
    """Get the list of all the foods in the database

    Args:
        request ([type]): [description]
    """
    foods = Food.objects.all()
    serializer = FoodSerializer(foods, many=True)
    return Response(serializer.data)


@api_view(http_method_names=['POST'])
def order_food(request):
    """Order food and update the database accordingly

    Args:
        request ([type]): [description]
    """

    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        # use a transaction to ensure data integrity
        with transaction.atomic():
            serializer.save()
            # update user credit
            user = User.objects.get(pk=serializer.data["customer"])
            user.credit -= serializer.data["total"]
            user.save()
            return Response({"succeed": 1, "updated_user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view()
def orders(request, uid):
    order = Order.objects.get(pk=uid)
    serializer = OrderSerializer(order)
    return Response(serializer.data)
