import datetime
from datetime import timezone
from .models import Modelfactors, Intradaymarketdata
from rest_framework import generics
from .serializers import *

class PriceList(generics.ListCreateAPIView):  

    #the model is the collection that we are selecting from
    model = Intradaymarketdata
    #the serializer is some automatic processing on the selection
    serializer_class = PriceSeriesSerializer 

    def get_queryset(self):    

        """Handles the query set returned in the GET request by extracting the
        end time and hours offset to define lower and upper datetime limits in the 
        table"""

        upper_timeframe = self.request.GET["endtime"] 

        if upper_timeframe=="Now":
            upper_timeframe = datetime.datetime.now() 
        else:
            upper_timeframe = datetime.datetime.strftime(upper_timeframe, '%Y-%m-%d %H:%M:%S')
    
        lower_timeframe = upper_timeframe - datetime.timedelta(hours = int(self.request.GET["hoursoffset"]))
        
        lower_timeframe.replace(tzinfo=timezone.utc)

        upper_timeframe.replace(tzinfo=timezone.utc)

        query_set =  self.model.objects.filter(dt__gte=lower_timeframe, dt__lte=upper_timeframe) 

        return query_set 

  
        

        

    










