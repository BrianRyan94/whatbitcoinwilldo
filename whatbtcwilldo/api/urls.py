from django.urls import path
from .views import *


urlpatterns = [
    path('rawprices/', PriceList.as_view()),
    path('returninfo/', ReturnInfo.as_view())
]
