from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('apps.admin_dashboard.urls', namespace='admin_dashboard')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('', include('apps.storefront.urls', namespace='storefront')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
