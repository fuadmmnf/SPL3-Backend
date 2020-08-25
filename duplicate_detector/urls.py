from django.urls import path
from .views import *

urlpatterns = [
    path("test/", test_api, name="test_api"),
    path("check/duplicates", check_duplicates, name="check_prduplicates"),
]
