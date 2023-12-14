from django.urls import path,include
from my_app.API import views
from Ecommerce.api_router import router

router.register('customers',views.CustomerListCreateViewSet,basename='customers'),
router.register('products',views.ProductListCreateViewSet,basename='products'),
router.register('orders',views.OrderListCreateViewSet,basename='orders'),

urlpatterns = [
    path('', include(router.urls)),
]
