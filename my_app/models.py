import random
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=64, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class ProductPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с пользователем
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Связь с продуктом
    purchase_time = models.DateTimeField(auto_now_add=True)  # Время покупки
    delivery_time = models.DateTimeField(default=timezone.now() + timedelta(hours=2))  # Время доставки (2 часа от времени покупки)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    def get_delivery_time_str(self):
        return self.delivery_time.strftime("%Y-%m-%d %H:%M:%S")

class Card(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь с пользователем
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)  # Начальный баланс 10000
    card_number = models.CharField(max_length=16, unique=True, blank=True, null=True)  # Рандомный номер карты
    card_password = models.CharField(max_length=3)  # Пароль карты из 3 цифр

    def __str__(self):
        return f"Card of {self.user.username} with balance {self.balance}"

    # Метод для списания средств с карты
    def deduct(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False  # Если средств недостаточно

    # Генерация случайного номера карты и пароля
    def generate_card_details(self):
        self.card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        self.card_password = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        self.save()

class Entity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()



class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Изображение")
    category = models.CharField(max_length=50, verbose_name="Категория")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество товара на складе")  # Добавлено поле

    def __str__(self):
        return self.name

    def get_category(self):
        return self.category  # Просто возвращаем категорию как строку
