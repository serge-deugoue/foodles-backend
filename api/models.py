from django.db import models
from datetime import date
from django.utils.timezone import now

# Create your models here.

IMAGE_NAMES = ('Aiguillettes_de_poulet_au_miel_et_nouilles_soba_aux_legumes.jpg',
               'Aiguillettes_de_poulet_au_miel_semoule_epicee_et_carottes_roties.jpg',
               'Poulet_coco_curry_ecrase_patate_douce.jpg')


class User(models.Model):
    email = models.EmailField(unique=True)
    credit = models.FloatField()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # limiting to 2 decimal places
        self.credit = round(self.credit, 2)
        super(User, self).save(*args, **kwargs)


class Food(models.Model):

    title = models.CharField(max_length=200)
    price = models.FloatField()
    stock = models.PositiveIntegerField(default=0)
    image_name = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # limiting to 2 decimal places
        self.price = round(self.price, 2)
        super(Food, self).save(*args, **kwargs)


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.FloatField()
    date = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.customer.name}  at {self.date}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='order_items', on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f' food: {self.food.title}, quantity: {self.quantity}'
