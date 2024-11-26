from django.db import models
from django.utils.html import format_html


class CategoryStore(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return f'{self.name}'


class Store(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(CategoryStore, on_delete=models.CASCADE)
    tg_username = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=12)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    address = models.TextField()
    description = models.TextField()
    open_close = models.BooleanField(default=True)
    on_main = models.BooleanField(default=True)
    image = models.ImageField(f'Store_{name}', blank=True, null=True, default='nopstorephoto.jpeg', upload_to='images/')
    
    def __str__(self) -> str:
        return f'{self.name}'


class CategoryProduct(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return f'{self.name}'


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # До 10 знаков, из них 2 после запятой
    category = models.ForeignKey(CategoryProduct, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    description = models.CharField(max_length=256)
    on_main = models.BooleanField(default=True)
    image = models.ImageField(f'Product_{name}', blank=True, null=True, default='noproductphoto.jpeg', upload_to='images/')
    
    def __str__(self) -> str:
        return f'{self.name}'


class Client(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    tg_username = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=12)
    address = models.TextField()
    photo = models.ImageField(f'Фото_{name}', blank=True, null=True, default='nophoto.jpeg', upload_to='images/')
    
    def __str__(self) -> str:
        return f'{self.name} | {self.phone_number}'
    
    def tg_link(self):
        return format_html('<a href="https://t.me/{}" target="_blank">{}</a>', self.tg_username, self.tg_username)
    
    tg_link.short_description = "Telegram"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    accepted = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id} by {self.client}"
    
    def get_products_list(self):
        items = OrderItem.objects.filter(order=self)
        return ", ".join([f"{item.product.name} ({item.quantity}шт)" for item in items])
    
    get_products_list.short_description = "Products"
    
    def client_tg_link(self):
        tg_username = self.client.tg_username
        return format_html(
            '<a href="https://t.me/{}" target="_blank">{}</a>',
            tg_username,
            tg_username
        )

    client_tg_link.short_description = "Telegram Link"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class WorkingHour(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Понедельник'),
        ('Tuesday', 'Вторник'),
        ('Wednesday', 'Среда'),
        ('Thursday', 'Четверг'),
        ('Friday', 'Пятница'),
        ('Saturday', 'Суббота'),
        ('Sunday', 'Воскресенье'),
    ]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='working_hours')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_opened = models.BooleanField(default=False)
