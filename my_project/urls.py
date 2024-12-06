from django.urls import path
from my_app.views import RegisterView, LogoutView, ConfirmEmailView, ProductListView, purchase_product, LinkCardView , LinkCardView, PurchaseProductView# Добавьте правильный импорт
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="BUMPCoffee API",
        default_version='v1',
        description="API для кофе",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="talgat.temirov@alatoo.edu.kg"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,  # Сделать Swagger доступным публично
    permission_classes=(permissions.AllowAny,),  # Отключить аутентификацию
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/card/link/', LinkCardView.as_view(), name='link_card'),
    path('api/products/purchase/<int:product_id>/', PurchaseProductView.as_view(), name='purchase_product'),
    path('api/auth/confirm_email/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/card/link/', LinkCardView.as_view(), name='link_card'),  # Используйте импортированную ссылку
    path('api/products/purchase/<int:product_id>/', purchase_product, name='purchase_product'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/products/', ProductListView.as_view(), name='product_list'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair')
]
