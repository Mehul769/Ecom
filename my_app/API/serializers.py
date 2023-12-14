import datetime
import json
from rest_framework import serializers
from my_app.models import Customer,Product,Order,Orderitem
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id','name','contact_number','email']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','weight']
        
        extra_kwargs = {
            'weight': {
                'validators': [MinValueValidator(0),MaxValueValidator(25)]
            }
        }
        
    def validate_name(self,value):
        if Product.objects.filter(name=value).exists():
            raise serializers.ValidationError("Name Must be unique")
        return value
    
# class OrderItemSerializer(serializers.Serializer):
#     product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
#     quantity = serializers.IntegerField(default=0)

class OrderItemSerializer(serializers.ModelSerializer):
    
    id=serializers.ReadOnlyField()
    product = serializers.SerializerMethodField()
    class Meta:
        model = Orderitem
        fields = ['id','product','quantity']
        
    def get_product(self,obj):
        return obj.product.name if obj.product else None
        
class OrderSerializer(serializers.ModelSerializer):
    
    order_item = serializers.ListField()
    
    class Meta:
        model = Order
        fields = ['order_number','customer','order_date','address','order_item']
        
        extra_kwargs = {
            'order_number': {'read_only': True},
        }
        
    def create(self, validated_data):
        order_item = validated_data.pop("order_item",None)
        order_obj = Order(**validated_data)
        last_order = Order.objects.order_by('-id').first()
        try:
            if last_order:
                last_order_number = int(last_order.order_number[3:])
                new_order_number = f"ORD{last_order_number + 1}"
            else:
                new_order_number = "ORD00001"
        except Exception:
            new_order_number = "ORD00001"
        order_obj.order_number = new_order_number
        order_obj.save()
        for item in order_item:
            product_obj = Product.objects.filter(id=json.loads(item).get("product_id")).last()
            qty=json.loads(item).get("quantity")
            Orderitem.objects.create(order=order_obj,product=product_obj,quantity=qty)
        
        return order_obj
    
    def update(self, instance, validated_data):
        order_item = validated_data.pop("order_item",None)
        if order_item:
            for item in order_item:
                id = json.loads(item).get("id")
                if id:
                    product_obj = Orderitem.objects.filter(id=id).last()
                    product_obj.product = Product.objects.filter(id=json.loads(item).get("product_id")).last()
                    product_obj.quantity = json.loads(item).get("quantity")
                else:
                    product_obj = Orderitem()
                    product_obj.product = Product.objects.filter(id=json.loads(item).get("product_id")).last()
                    product_obj.quantity = json.loads(item).get("quantity")
                    product_obj.order = instance
                product_obj.save()
                
        for key,value in validated_data.items():
            setattr(instance,key,value)
            
        return instance
                   
    def validate_order_date(self,value):
        today = datetime.date.today()
        if value<today:
             raise serializers.ValidationError("Past Date Is Not Allowed...") 
        return value
                
    
    def validate_order_item(self,value):
        products = []
        total_weight = 0
        for item in value:
            products.append(json.loads(item).get("product_id"))
            products_data = Product.objects.filter(id__in=products).aggregate(total_weight=Sum("weight"))
            total_weight += products_data.get("total_weight") * json.loads(item).get("quantity")
        if total_weight>150:
            raise serializers.ValidationError("Total weigh must be under 150") 
        return value
        
class OrderListSerializer(serializers.ModelSerializer):
    order_item = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id','order_number','customer','order_date','address','order_item']
        
        extra_kwargs = {
            'order_number': {'read_only': True},
        }
        
    def get_order_item(self,obj):
        return OrderItemSerializer(Orderitem.objects.filter(order__id=obj.id),many=True).data
    
    def get_customer(self,obj):
        return obj.customer.name
    
    def create(self, validated_data):
        return super().create(validated_data)
