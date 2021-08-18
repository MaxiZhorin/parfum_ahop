from django import forms
from django.contrib import admin
from .models import *


class ParfumCategoryChoiceFields(admin.ModelAdmin):

    pass


class ParfumAdmin(admin.ModelAdmin):
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