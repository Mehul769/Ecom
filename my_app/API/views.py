from rest_framework import viewsets
from base.renderers import BaseJSONRenderer
from my_app.API.serializers import CustomerSerializer, OrderListSerializer,ProductSerializer,OrderSerializer,OrderItemSerializer
from my_app.models import Customer,Product,Order,Orderitem
from datetime import date
from rest_framework.response import Response

class CustomerListCreateViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    
class ProductListCreateViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
class OrderListCreateViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    renderer_classes = [BaseJSONRenderer]
    
    def get_serializer_class(self):
        actions = {
            "list": OrderListSerializer,
            "create": OrderSerializer,
            "partial_update": OrderSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()
    
    def get_queryset(self):
        queryset = Order.objects.all().order_by("-id")
        product = self.request.query_params.get("product")
        customer = self.request.query_params.get("customer")
        if product:
            queryset = queryset.filter(order_product__product__name=product)
        if customer:
            queryset = queryset.filter(customer__name=customer)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Order Added Sucessfully..."})
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Order Updated Sucessfully..."})
        