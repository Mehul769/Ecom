from django.urls import path,include
from rest_framework.routers import DefaultRouter

# Create router object

router = DefaultRouter()

urlpatterns = [

    path("", include("my_app.API.urls"), name="my_app"),
]