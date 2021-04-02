import datetime

from .models import Modelfactors, Intradaymarketdata
from rest_framework import generics
from .serializers import *

class PriceList(generics.ListCreateAPIView):  

    ##set the serializer class and the model - by default 
    model = Intradaymarketdata
    serializer_class = PriceSeriesSerializer 

    def get_queryset(self):   
        #print(self.request.GET["time"])
        query_set =  self.model.objects.filter(dt__gt=datetime.datetime.today()-datetime.timedelta(days=1))
        return query_set
        

        

    










