from django.urls import path
from . import views

app_name = 'storefront'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('newsletter/', views.newsletter_signup, name='newsletter_signup'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<str:order_number>/', views.order_success, name='order_success'),
    
    # Customer Authentication & Orders (Amazon / Flipkart Style)
    path('account/register/', views.user_register, name='user_register'),
    path('account/login/', views.user_login, name='user_login'),
    path('account/logout/', views.user_logout, name='user_logout'),
    path('account/orders/', views.my_orders, name='my_orders'),
    path('my-orders/', views.my_orders, name='my_orders_alias'),
    path('account/google/', views.google_login, name='google_login'),
    path('product/<int:product_id>/review/', views.add_product_review, name='add_product_review'),
]

