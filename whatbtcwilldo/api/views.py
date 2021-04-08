from .models import Modelfactors, Intradaymarketdata

from rest_framework import generics
from .serializers import * 

from django.views import View
from django.db.models import Q
from django.http import HttpResponse

import json
import pandas as pd
import datetime
from datetime import timezone



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

class ReturnInfo(View):
    
    model = Intradaymarketdata  

    minutes_ago = [0, 15, 60, 3*60, 12*60, 24*60, 7*24*60, 30*24*60] 

    time_labels = ["-", "15m", "1H", "3H", "12H", "1D", "1W", "1M"]
    
    def get_required_dates(self):

        most_recent_update = self.model.objects.latest('dt').dt 

        most_recent_update = datetime.datetime(most_recent_update.year, most_recent_update.month, most_recent_update.day, most_recent_update.hour, most_recent_update.minute)

        required_dates = []

        for minutes_ago in self.minutes_ago:
            required_dates.append(most_recent_update-datetime.timedelta(minutes=minutes_ago)) 
        
        return required_dates

    def get(self, request): 

        #GET REQUIRED DATES FOR CALCULATING RETURNS
        required_dates = self.get_required_dates()
        
        #INSTANTIATE THE QUERY FILTER AND ADD ALL DATE FILTERS IN AN OR STATEMENT
        query_filter = Q(dt__year=required_dates[0].year, dt__month=required_dates[0].month, dt__day=required_dates[0].day, 
                        dt__hour=required_dates[0].hour, dt__minute=required_dates[0].minute) 

        for req_date in required_dates[1:]:

            query_filter.add(Q(dt__year=req_date.year, dt__month=req_date.month, dt__day=req_date.day, 
                        dt__hour=req_date.hour, dt__minute=req_date.minute), Q.OR) 
        
        #GET THE RAW DATA FROM THE DB
        raw_data = pd.DataFrame(self.model.objects.filter(query_filter).values()).sort_values(by='dt', ascending=True).reset_index(drop=True)
        
        #GET THE EXPECTED DATE SERIES AND MERGE TO GET PRICES (OR ELSE NAN) AT THOSE EXPECTED DATES
        expected_df = pd.DataFrame()

        expected_df['ExpectedDate'] = required_dates 

        expected_df['ExpectedDate'] = pd.to_datetime(expected_df['ExpectedDate'], utc=True) 

        expected_df = expected_df.sort_values(by='ExpectedDate', ascending=True).reset_index(drop=True)

        expected_df = pd.merge_asof(expected_df, raw_data, left_on='ExpectedDate', right_on='dt', 
        direction='nearest', tolerance=datetime.timedelta(minutes=1)) 

        expected_df = expected_df[['ExpectedDate', 'trade']]
        
        #GET THE RETURNS OVER EACH TIME PERIOD
        for i in range(1, len(required_dates)):
            expected_df[self.time_labels[i]] = (expected_df['trade']/expected_df['trade'].shift(i)).apply(lambda x: round((x-1)*100, 2))
        
        response_array = []
        
        #WE ARE ONLY INTERESTED IN THE VALUES FOR THE LAST ROW
        values_dict = expected_df.tail(1).reset_index(drop=True).to_dict()

        for label in self.time_labels[1:]:

            calculated_return = values_dict[label][0] 

            if str(calculated_return)!="nan":

                str_return = ("" if calculated_return <0 else "+") + str(calculated_return) + "%" 

                sentiment = "positive" if calculated_return>=0 else "negative" 

                response_array.append([label, str_return, sentiment]) 
        
        return HttpResponse(json.dumps(response_array))



    


        

        

        



  
        

        

    










