from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('rawprices/', cache_page(60)(PriceList.as_view())),
    path('volumes/', cache_page(60)(VolumeList.as_view())),
    path('volatilities/', cache_page(60)(VolatilityList.as_view())),
    path('avgtradesizes/', cache_page(60)(TradeList.as_view())),
    path('returninfo/', cache_page(60)(ReturnInfo.as_view()))
]
