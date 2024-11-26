
from django.urls import path

from . import views

urlpatterns = [
    path('', views.load, name='load'),
    path('check_user/', views.check_user, name='check_user'),
    path('store_list/', views.store_list, name='store_list'),
    path('filtered_stores/', views.get_filtered_stores, name='filtered_stores'),
    path('store/<int:store_id>/', views.product_list, name='product_list'),
    path('store/<int:store_id>/filtered_products/', views.get_filtered_products, name='filtered_products'),
    path('cart/<int:client_id>/', views.cart, name='cart'),
    path('create_order/', views.create_order, name='create_order'),
    path('register/', views.register, name='register'),
    path('register_user/', views.register_user, name='register_user'),
]
