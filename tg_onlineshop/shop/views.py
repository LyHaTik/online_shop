from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.db.models import Prefetch
from django.core.exceptions import ValidationError
from django.core.validators import validate_integer

from datetime import datetime, time
import json

from .models import Store, Product, Client, Order, OrderItem, CategoryStore, CategoryProduct


# Страница загрузки
def load(request):
    return render(request, 'load.html')


# Проверка user
def check_user(request):
    user_id = request.GET.get('user_id')
    
    # Проверка наличия user_id
    if not user_id:
        return JsonResponse({'error': 'User ID is missing'}, status=400)
    
    # Проверка, что user_id является целым числом
    try:
        validate_integer(user_id)
    except ValidationError:
        return JsonResponse({'error': 'User ID must be an integer'}, status=400)

    # Проверяем, существует ли пользователь
    user_exists = Client.objects.filter(id=user_id).exists()

    return JsonResponse({'is_registered': user_exists})


# Страница регистрации
def register(request):
    return render(request, 'registration.html')


@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    list_error = []
    telegram_id = request.POST.get('telegram_id')
    tg_username = request.POST.get('tg_username')
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    photo = request.FILES.get('photo')

    # Проверка обязательных полей
    if not telegram_id:
        list_error.append("Telegram ID is required.")
    if not name:
        list_error.append("Name is required.")
    if not phone:
        list_error.append("Phone number is required.")
    if not address:
        list_error.append("Address is required.")

    # Проверка уникальности telegram_id
    if telegram_id and Client.objects.filter(id=telegram_id).exists():
        list_error.append("User with this Telegram ID already exists.")

    # Дополнительные проверки
    if len(phone) < 10:
        list_error.append("Invalid phone number format.")
    if tg_username and len(tg_username) > 50:
        list_error.append("Telegram username is too long.")
    if name and len(name) > 100:
        list_error.append("Name is too long.")
    if address and len(address) > 255:
        list_error.append("Address is too long.")

    # Если есть ошибки, возвращаем их клиенту
    if list_error:
        return JsonResponse({'errors': list_error}, status=400)

    # Сохранение пользователя
    try:
        client = Client.objects.create(
            id=telegram_id,
            tg_username=tg_username,
            name=name,
            phone_number=phone,
            address=address,
            photo=photo
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        'success': True,
        'user': {
            'id': client.id,
            'name': client.name,
            'phone': client.phone_number,
            'address': client.address,
            'tg_username': client.tg_username
        }
    })

# Обновляем состояние магазинов
def update_open_close_store(stores):
    now = datetime.now()
    current_time = now.time()
    today = now.strftime("%A")  # Название дня недели

    # Подготовка магазинов для обновления
    stores_to_update = []

    for store in stores:
        try:
            # Получаем рабочие часы для текущего дня недели
            hours = store.working_hours.filter(day_of_week=today).get()
            open_hour = hours.opening_time
            close_hour = hours.closing_time
        except store.working_hours.model.DoesNotExist:
            # Если рабочие часы не указаны, считаем магазин всегда открытым
            open_hour = time(0, 0)
            close_hour = time(23, 59)

        # Проверяем, открыт ли магазин
        is_open = open_hour <= current_time <= close_hour if open_hour and close_hour else False

        # Обновляем значения в объекте
        store.open_close = is_open
        store.opening_time = open_hour
        store.closing_time = close_hour
        stores_to_update.append(store)

    # Сохраняем изменения в базе данных
    if stores_to_update:
        Store.objects.bulk_update(stores_to_update, ['open_close', 'opening_time', 'closing_time'])

# Страница с списком магазинов
def store_list(request):
    # Получаем ID выбранной категории
    selected_category_id = request.GET.get('category')

    # Предзагрузка связанных данных для минимизации запросов
    store_query = Store.objects.prefetch_related(
        Prefetch('category', queryset=CategoryStore.objects.only('id', 'name')),
        'working_hours'
    )

    # Применяем фильтр по категории, если он указан
    if selected_category_id:
        store_query = store_query.filter(category__id=selected_category_id)

    # Обновляем состояние открытости магазинов
    stores = list(store_query)  # Приводим QuerySet к списку для работы с объектами
    update_open_close_store(stores)

    # Получаем категории для отображения
    store_categories = CategoryStore.objects.all()

    return render(request, 'store_list.html', {
        'stores': stores,
        'store_categories': store_categories,
    })

# Страница списка товаров в магазине
def product_list(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        products = Product.objects.filter(store=store, category_id=selected_category_id)
    else:
        products = Product.objects.filter(store=store)
        
    # Получаем уникальные категории для товаров
    product_categories = CategoryProduct.objects.filter(product__in=products).distinct()

    return render(request, 'product_list.html', {
        'store': store,
        'products': products,
        'product_categories': product_categories,
    })


def get_filtered_products(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    category_id = request.GET.get('category')
    product_ids = request.GET.get('product_ids')

    if category_id:
        products = Product.objects.filter(store=store, category=category_id)
    else:
        if product_ids:
            product_ids = product_ids.split(',')
            products = Product.objects.filter(store=store, id__in=product_ids)
        else:
            products = Product.objects.filter(store=store)

    products_data = [
        {
            'id': str(product.id),
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url,
            'store_id': product.store.id,
            'store_name': product.store.name,
            'store_image': product.store.image.url,
        }
        for product in products
    ]
    
    return JsonResponse({'products': products_data})



def get_filtered_stores(request):
    category_id = request.GET.get('category')
    if category_id:
        stores = Store.objects.filter(category__id=category_id)
    else:
        stores = Store.objects.all()

    stores_data = [{
        'id': store.id,
        'name': store.name,
        'category': store.category.name,
        'image': store.image.url if store.image else '',
        'openClose': store.open_close,
        'onMain': store.on_main,
        'openingTime': store.opening_time.strftime('%H:%M') if store.opening_time else None,
        'closingTime': store.closing_time.strftime('%H:%M') if store.closing_time else None,
        } for store in stores]
    
    return JsonResponse({'stores': stores_data})


@csrf_exempt
def create_order(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid HTTP method'}, status=405)

    try:
        data = json.loads(request.body)
        client_id = data.get('clientId')
        if not client_id:
            return JsonResponse({'success': False, 'error': 'Missing clientId'}, status=400)

        client = get_object_or_404(Client, id=client_id)
        orders = {}

        # Используем транзакцию, чтобы гарантировать целостность данных
        with transaction.atomic():

            for item_store in data.get('stores', []):
                store_id = item_store.get('storeId')
                if not store_id:
                    return JsonResponse({'success': False, 'error': 'Missing storeId'}, status=400)
                store = get_object_or_404(Store, id=store_id)

                # Создание заказа
                order = Order.objects.create(client=client, store=store)
                orders[store.name] = order.id

                for item_product in item_store.get('products', []):
                    product_id = item_product.get('productId')
                    product_quantity = item_product.get('quantity')

                    if not product_id or product_quantity is None:
                        return JsonResponse({'success': False, 'error': 'Missing product data'}, status=400)

                    product = get_object_or_404(Product, id=product_id)

                    # Создание элементов заказа
                    OrderItem.objects.create(order=order, product=product, quantity=product_quantity)

        return JsonResponse({'success': True, 'orders': orders})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def cart(request, client_id):
    orders = Order.objects.prefetch_related('orderitem_set__product').filter(client=client_id).order_by('-created_at')
    return render(request, 'cart.html', {'orders': orders})

