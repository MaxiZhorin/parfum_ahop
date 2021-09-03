from django import forms
from django.forms import ModelForm, ValidationError
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *
from PIL import Image


class ParfumAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe(
            '<span style="color:red; font-size:14px;">Минимальное разрешение изображения {}x{}</span>'.format(
                *Product.MIN_RESOLUTION
            )
        )

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_height, min_width = Product.MIN_RESOLUTION
        max_height, max_width = Product.MAX_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise ValidationError('Разрешение изображения меньше минимального')
        if img.height > max_height or img.width > max_width:
            raise ValidationError('Разрешение изображения больше минимального')
        return image


class ParfumCategoryChoiceFields(admin.ModelAdmin):

    pass


class ParfumAdmin(admin.ModelAdmin):

    form = ParfumAdminForm

    # Класс для исключения других категорий при добавлении товара
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'categorys':
            return ParfumCategoryChoiceFields(Category.objects.filter(slug='parfum'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Parfum, ParfumAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(CategorySex)
admin.site.register(ParfumVolume)