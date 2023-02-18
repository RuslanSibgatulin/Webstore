from django.contrib import admin

from .models import Item, ItemsInOrder, Order


class ItemsInline(admin.TabularInline):
    model = ItemsInOrder


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = (
        "name", "description", "price"
    )
    # Поиск по полям
    search_fields = (
        "name", "description"
    )
    # Фильтрация в списке
    list_filter = (
        "price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (ItemsInline, )
    # Отображение полей в списке
    list_display = (
        "id", "session", "created_at"
    )
