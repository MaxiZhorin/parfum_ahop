from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

User = get_user_model()


def det_product_url(obj, view_name):
    ct_model = obj.__class__._meta.model_name
    return reverse(view_name, kwargs={'ct_model':ct_model, 'slug':obj.slug })


class MinResolutionErrorException(Exception):
   pass


class MaxResolutionErrorException(Exception):
   pass


class LatestProductManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:10]
            products.extend(model_products)
        return products


class LatestProducts:

    objects = LatestProductManager()


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class CategorySex(models.Model):

    name = models.CharField(max_length=255, verbose_name='Пол духов')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class ParfumVolume(models.Model):

    name = models.CharField(max_length=255, verbose_name='Объем')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    MIN_RESOLUTION = (300, 300)
    MAX_RESOLUTION = (4000, 4000)
    MAX_SIZE = 5242880

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    brand = models.CharField(max_length=255, verbose_name='Бренд', blank=True)
    title = models.CharField(max_length=255, verbose_name='Название')
    # article = models.CharField(max_length=100, blank=True, null=True, default=None, unique=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True)
    old_price = models.DecimalField(max_digits=9, decimal_places=0, verbose_name='Старая цена', null=True)
    price_opt = models.DecimalField(max_digits=9, decimal_places=0, verbose_name='Оптовая цена')
    price_retail = models.DecimalField(max_digits=9, decimal_places=0, verbose_name='Розничная цена')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise MinResolutionErrorException('Разрешение изображения меньше минимального')
        if img.height > max_height or img.width > max_width:
            raise MaxResolutionErrorException('Разрешение изображения больше минимального')
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE,related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Итоговая сумма')

    def __str__(self):
        return 'Продукт: {}, для корзины'.format(self.product.title)


class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True,related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Итоговая сумма')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    customer = models.ForeignKey(User, verbose_name='Пользователь', on_delete= models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    addres = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return 'Покупатель: {} {}'.format(self.user.first_name, self.user.last_name)


class Parfum(Product):
    sex = models.ForeignKey(CategorySex, verbose_name='Пол', on_delete=models.CASCADE)
    volume = models.ForeignKey(ParfumVolume, verbose_name='Объем флакона', on_delete=models.CASCADE)
    type_aroma = models.CharField(max_length=255, verbose_name='Тип аромата', blank=True)
    first_note = models.CharField(max_length=200, verbose_name='Начальная нота', blank=True)
    last_note = models.CharField(max_length=200, verbose_name='Конечная нота', blank=True)

    def __str__(self):
        return '{}: {}'.format(self.category.name, self.title)

    def get_absolute_url(self):
        return det_product_url(self, 'product_detail')

