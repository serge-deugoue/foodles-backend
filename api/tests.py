from django.test import TestCase

from .models import User, Food
from rest_framework.test import APIRequestFactory
from .views import get_foods
from rest_framework.test import APITestCase, URLPatternsTestCase
from django.urls import include, path, reverse
from rest_framework import status


class UserTestCase(TestCase):
    """Test for the user model
    """

    def setUp(self):
        User.objects.create(email="user1@foodles.com", credit=45)
        User.objects.create(email="user2@foodles.com", credit=125)

    def test_user_correctly_created(self):
        """The objects are correctly identified in the database"""
        user1 = User.objects.get(email="user1@foodles.com")
        user2 = User.objects.get(email="user2@foodles.com")
        self.assertEqual(user1.credit, 45)
        self.assertEqual(user2.credit, 125)


class FoodTestCase(TestCase):
    """Test for the food model
    """

    def setUp(self):
        Food.objects.create(title="Aiguillettes de poulet",
                            price=5.90, stock=5, image_name="1.jpg")

    def test_food_correctly_created(self):
        """The objects are correctly identified in the database"""
        food = Food.objects.get(title="Aiguillettes de poulet")
        self.assertEqual(food.title, "Aiguillettes de poulet")
        self.assertEqual(food.stock, 5)
        self.assertEqual(food.price, 5.90)
        self.assertEqual(food.image_name, '1.jpg')


class ApiTest(APITestCase, URLPatternsTestCase):
    """ Testing the various API Routes
    """
    urlpatterns = [
        path('api/', include('api.urls')),
    ]

    def setUp(self):
        # create 2 users
        User.objects.create(email="user1@foodles.com", credit=45)
        User.objects.create(email="user2@foodles.com", credit=125)

        self.user_emails = ["user1@foodles.com", "user2@foodles.com"]
        self.user_credits = [45, 125]

        # create 3 foods
        Food.objects.create(title="Aiguillettes de poulet",
                            price=5, stock=5, image_name="1.jpg")
        Food.objects.create(title="Riz au curry",
                            price=8, stock=10, image_name="2.jpg")
        Food.objects.create(title="Ratatouille",
                            price=10.30, stock=3, image_name="3.jpg")

        self.food_prices = [5, 8, 10.3]
        self.food_stocks = [5, 10, 3]

    def test_check_user_url(self):
        """get request for users
        """
        url = reverse('user')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for i, item in enumerate(response.data):
            self.assertEqual(item['email'], self.user_emails[i])

    def test_check_foods_url(self):
        """get request for foods
        """
        url = reverse('food')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for i, item in enumerate(response.data):
            self.assertEqual(item['price'], self.food_prices[i])

    def test_create_valid_order(self):
        """check if creating a valid order is successful
        """
        url = reverse('order')
        customer_id = 1
        # valid order (not exceeding stocks)
        order_items = [
            {
                "food": 1,
                "quantity": 3
            },
            {
                "food": 2,
                "quantity": 5
            },
            {
                "food": 3,
                "quantity": 2
            }
        ]
        order_contents = {
            "customer": customer_id,
            "orderItems": order_items
        }
        response = self.client.post(url, order_contents)
        # check for order success
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('succeed'), 1)

        # check for updated stocks
        for item in order_items:
            db_stock = Food.objects.get(pk=item['food']).stock
            calculated_stock = self.food_stocks[item['food'] -
                                                1] - item["quantity"]
            self.assertEqual(db_stock, calculated_stock)

        # check for updated user credit
        total_amt = sum([self.food_prices[item["food"]-1] * item["quantity"]
                         for item in order_items])
        calculated_user_credit = self.user_credits[customer_id-1]-total_amt
        db_user_credit = User.objects.get(pk=customer_id).credit
        self.assertEqual(db_user_credit, round(calculated_user_credit, 2))

    def test_exceeding_order(self):
        """check if ordering more than the stock would not succeed
        """
        url = reverse('order')
        customer_id = 1
        # valid order (not exceeding stocks)
        order_items = [
            {
                "food": 1,
                "quantity": 3
            },
            {
                "food": 2,
                "quantity": 5
            },
            {
                "food": 3,
                "quantity": 10  # there are only 3 of these
            }
        ]
        order_contents = {
            "customer": customer_id,
            "orderItems": order_items
        }
        response = self.client.post(url, order_contents)

        print(Food.objects.get(pk=3).stock)

        # check for order failure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('succeed'), 0)

        # check if stocks and user credit has not changed
        for item in order_items:
            db_stock = Food.objects.get(pk=item['food']).stock
            stock = self.food_stocks[item['food']-1]
            self.assertEqual(db_stock, round(stock, 2))

        user_credit = self.user_credits[customer_id-1]
        db_user_credit = User.objects.get(pk=customer_id).credit
        self.assertEqual(db_user_credit, user_credit)
