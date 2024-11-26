from django.contrib import admin
from django.utils.html import format_html

from .models import Store, Product, Client, Order, CategoryStore, CategoryProduct, WorkingHour, OrderItem


class CategoryStoreAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CategoryProductAdmin(admin.ModelAdmin):
    list_display = ('name',)


class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'tg_username', 'phone_number', 'address', 'opening_time', 'closing_time', 'open_close', 'description', 'on_main', 'image_preview',)
    list_editable = ('on_main',)
    list_filter = ('category', 'on_main',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit": cover;"/>', obj.image.url)
        return 'нет фото'
    image_preview.short_description = 'Фото'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'store', 'description', 'on_main', 'image_preview')
    list_filter = ('name', 'price', 'category', 'store', 'description', 'on_main',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit": cover;"/>', obj.image.url)
        return 'нет фото'
    image_preview.short_description = 'Фото'


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'tg_link', 'name', 'phone_number', 'address', 'photo_preview')
    list_filter = ('tg_username', 'name', 'phone_number', 'address', 'photo',)
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit": cover;"/>', obj.photo.url)
        return 'нет фото'
    photo_preview.short_description = 'Фото'
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'client', 'store', 'get_products_list', 'accepted', 'sent', 'completed')
    list_filter = ('store', 'created_at')
    search_fields = ('client__name', 'store__name')
    inlines = [OrderItemInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['client', 'store', 'created_at']
        return []


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')


class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ('store','day_of_week', 'opening_time', 'closing_time', 'is_opened')
    list_filter = ('store', 'day_of_week', 'opening_time', 'closing_time', 'is_opened',)


admin.site.register(CategoryStore, CategoryStoreAdmin)
admin.site.register(CategoryProduct, CategoryProductAdmin) 
admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin) 
admin.site.register(Client, ClientAdmin) 
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(WorkingHour, WorkingHourAdmin)
