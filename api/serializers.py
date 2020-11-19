from rest_framework import serializers
from django.db import transaction

from .models import User, Food, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'credit')


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('id', 'title', 'price', 'stock', 'image_name')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'quantity', 'food')
        read_only = ('order')


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    total = serializers.FloatField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'date', 'total', 'order_items')

    def create(self, validated_data):
        # use transaction to ensure data integrity
        with transaction.atomic():
            order_items = validated_data.pop("order_items")
            total = sum([item['food'].price * item['quantity']
                         for item in order_items])
            order = Order.objects.create(**validated_data, total=total)
            for item in order_items:
                # create order item
                OrderItem.objects.create(order=order, **item)
                # subtract from food stock
                food = Food.objects.get(pk=item['food'].id)
                food.stock -= item['quantity']
                food.save()
            return order
