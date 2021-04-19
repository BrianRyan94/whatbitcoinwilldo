from .models import Modelfactors, Intradaymarketdata
from .utils import *

from rest_framework import generics
from .serializers import * 

from django.views import View
from django.db.models import Q, DurationField, F, ExpressionWrapper
from django.db.models.functions import ExtractMinute
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

import json
import pandas as pd
import datetime
from datetime import timezone
import numpy as np


#determines the "row" intervals for a given time period displayed on the map
#for e.g. if the lookback is 1 month (720 hours) then the interval is 720 minutes. That is
#only the row every 6 hours is returned

hours_offset_intervals = {
    1:1,
    24:30,
    168: 180,
    720: 720
}

class PriceList(generics.ListCreateAPIView):   

    """Returns a json array with each object having the form
    {dt, trade}"""

    #the model is the collection that we are selecting from
    model = Intradaymarketdata
    #the serializer is some automatic processing on the selection
    serializer_class = PriceSeriesSerializer  



    def get_queryset(self):    

        """Handles the query set returned in the GET request by extracting the
        end time and hours offset to define lower and upper datetime limits in the 
        table"""

        upper_timeframe = self.request.GET["endtime"] 

        hours_offset = int(self.request.GET["hoursoffset"]) 

        if upper_timeframe=="Now":
            #for consistency the model factors table is the bottleneck - whatever is available there is available in the raw data
            upper_timeframe = Modelfactors.objects.latest('dt').dt
        else:
            upper_timeframe = datetime.datetime.strptime(upper_timeframe, '%Y-%m-%d %H:%M:%S') 
        
        lower_timeframe = upper_timeframe - datetime.timedelta(hours = hours_offset)
        
        lower_timeframe.replace(tzinfo=timezone.utc)

        upper_timeframe.replace(tzinfo=timezone.utc)  
        
        #by generating a limited number of minute values for a given lookback we can control how much data is being rendered in the graphs resulting in significant speedup
        acceptable_minutes = acceptable_minute_values(upper_timeframe.minute, hours_offset_intervals[hours_offset])  

        acceptable_hours = acceptable_hour_values(upper_timeframe.hour, hours_offset_intervals[hours_offset])

        query_set =  self.model.objects.filter(dt__gte=lower_timeframe, dt__lte=upper_timeframe, dt__minute__in=acceptable_minutes, dt__hour__in=acceptable_hours) 

        return query_set  

class VolatilityList(View):

    model = Modelfactors 
    
    #what column to use for what time period
    offset_col_mappings = {
        1:"volatility_1_hour",
        24:"volatility_1_hour",
        168:"volatility_3_hour",
        720:"volatility_12_hour"
    }

    select_cols = ["volatility_1_hour", "volatility_3_hour", "volatility_6_hour", "volatility_12_hour", "volatility_24_hour"] 

    col_info_mappings = [
        {'volatility_1_hour':'1H'},
        {'volatility_3_hour':'3H'},
        {'volatility_12_hour':'12H'},
        {'volatility_24_hour':'24H'}
    ] 
    

    def smooth_vol(self, volatilities):

        smoothed_vol = []

        for i in range(len(volatilities)):

            vols = volatilities[max(i-4, 0):i+1]

            smoothed_vol.append(sum(vols)/len(vols)) 
        
        return smoothed_vol

    def calc_volatility_info_array(self, last_row, average_volatility, weekly_volatility, monthly_volatility): 

        """Creates the information array for the header of the visual cards"""

        info_array = []

        for col_info in self.col_info_mappings:
            
            colname = list(col_info.keys())[0] 
            
            colinfoname = col_info[colname]  
            
            try:
                
                value = list(last_row[colname])[0]  

                value = round(value*100, 1) 

                if value>=average_volatility:
                    sentiment = "positive" 
                else:
                    sentiment = "negative" 
                
                value = str(value) + "%" 

                info_array.append([colinfoname, value, sentiment])
            except (IndexError, TypeError):
                pass  

        #add in the weekly and monthly volatility calculated using a non-standard method     
        for vol, description in zip([weekly_volatility, monthly_volatility], ["1W","1M"]):
            
            value = round(vol*100, 1)  

            if value>=average_volatility:
                    sentiment = "positive" 
            else:
                sentiment = "negative" 
                
            value = str(value) + "%" 

            info_array.append([description, value, sentiment])

        return info_array


    def get(self, request):

        upper_timeframe = request.GET["endtime"]

        hours_offset = int(request.GET["hoursoffset"])  
        
        if upper_timeframe=="Now":
            upper_timeframe = self.model.objects.latest('dt').dt
        else:
            upper_timeframe = datetime.datetime.strptime(upper_timeframe, '%Y-%m-%d %H:%M:%S')   
        
        lower_timeframe = upper_timeframe - datetime.timedelta(hours = hours_offset)

        lower_timeframe.replace(tzinfo=timezone.utc)

        upper_timeframe.replace(tzinfo=timezone.utc)  

        acceptable_minutes = acceptable_minute_values(upper_timeframe.minute, hours_offset_intervals[hours_offset])  

        acceptable_hours = acceptable_hour_values(upper_timeframe.hour, hours_offset_intervals[hours_offset])
        
        volatility_column = self.offset_col_mappings[hours_offset]
        
        #retrieves pandas dataframe of all required volume columns sorted by date(ascending) filtered for rows within the timeframe specified and minute value specified
        volatility_data = pd.DataFrame(self.model.objects.filter(dt__minute__in=acceptable_minutes, dt__hour__in=acceptable_hours, dt__gte=lower_timeframe, 
        dt__lte=upper_timeframe).values('dt', *tuple(self.select_cols))).sort_values(by='dt', ascending=True).reset_index(drop=True)
        
        most_recent_row = volatility_data.tail(1)   
        
        #get historical volatility using 30 day period ending at end time 
        historical_vol = pd.DataFrame(self.model.objects.filter(dt__minute__in=[0, 30], dt__gte=datetime.datetime.today()-datetime.timedelta(days=30),  
        dt__lte=upper_timeframe).values('dt', 'volatility_6_hour')).sort_values(by='dt', ascending=True).reset_index(drop=True) 

        historical_vol = historical_vol.dropna(how="any")
        
        #calculate the monthly historical volatility to include in the information array
        monthly_volatility = np.mean(historical_vol['volatility_6_hour']) 
        
        #calculate the weekly historical volatility to include in the information array
        weekly_volatility = np.mean(historical_vol[historical_vol['dt']>max(historical_vol['dt']-datetime.timedelta(hours=168))]['volatility_6_hour'])
        
        #get historical average
        average_volatility = round(np.mean(historical_vol['volatility_6_hour'])*100, 1)
        
        #color code array based on the volatility vs historical average 
        volatility_info_array = self.calc_volatility_info_array(most_recent_row, average_volatility, weekly_volatility, monthly_volatility)

        volatility_data['volatility'] = volatility_data[volatility_column]  

        volatility_data['volatility'] = self.smooth_vol(list(volatility_data['volatility']))
        
        volatility_data = volatility_data[['dt', 'volatility']]

        volatility_data['dt'] = volatility_data['dt'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ')) 
        
        volatility_data = volatility_data.dropna(how="any")   

        volatility_data['volatility'] = volatility_data['volatility'].apply(str)

        #constructing the json object to send back - object with the jsonified chart series, and volume info array

        response_data = {}

        chart_series = volatility_data.to_json(orient='records')

        chart_series = json.loads(chart_series)

        response_data['chart_series'] = chart_series 

        response_data['info_array'] = volatility_info_array
        
        response_data = json.dumps(response_data)

        return HttpResponse(response_data, content_type = 'application/json')


class TradeList(View):

    model = Modelfactors 
    
    #what column to use for what time period
    offset_col_mappings = {
        1:"avg_trd_size_5_min",
        24:"avg_trd_size_1_hour",
        168:"avg_trd_size_6_hour",
        720:"avg_trd_size_12_hour"
    }

    select_cols = ["avg_trd_size_5_min", "avg_trd_size_1_hour","avg_trd_size_3_hour",
    "avg_trd_size_6_hour","avg_trd_size_12_hour","avg_trd_size_24_hour"]

    col_info_mappings = [
        {'avg_trd_size_5_min':'5m'},
        {'avg_trd_size_1_hour':'1H'},
        {'avg_trd_size_3_hour':'3H'},
        {'avg_trd_size_6_hour':'6H'},
        {'avg_trd_size_12_hour':'12H'},
        {'avg_trd_size_24_hour':'24H'}
    ] 
    

    def calc_trdsize_info_array(self, last_row, average_trdsize): 

        """Creates the information array for the header of the visual cards"""

        info_array = []

        for col_info in self.col_info_mappings:
            
            colname = list(col_info.keys())[0] 
            
            colinfoname = col_info[colname]  
            
            try:
                
                value = round(list(last_row[colname])[0]  , 2)

                if value>=average_trdsize:
                    sentiment = "positive" 
                else:
                    sentiment = "negative" 
                
                value = str(value) 

                info_array.append([colinfoname, value, sentiment])

            except (IndexError, TypeError):
                pass 
        
        return info_array


    def get(self, request):

        upper_timeframe = request.GET["endtime"]

        hours_offset = int(request.GET["hoursoffset"])  
        
        if upper_timeframe=="Now":
            upper_timeframe = self.model.objects.latest('dt').dt
        else:
            upper_timeframe = datetime.datetime.strptime(upper_timeframe, '%Y-%m-%d %H:%M:%S')   
        
        lower_timeframe = upper_timeframe - datetime.timedelta(hours = hours_offset)

        lower_timeframe.replace(tzinfo=timezone.utc)

        upper_timeframe.replace(tzinfo=timezone.utc)  

        acceptable_minutes = acceptable_minute_values(upper_timeframe.minute, hours_offset_intervals[hours_offset])  

        acceptable_hours = acceptable_hour_values(upper_timeframe.hour, hours_offset_intervals[hours_offset])
        
        trd_size_column = self.offset_col_mappings[hours_offset]
        
        #retrieves pandas dataframe of all required volume columns sorted by date(ascending) filtered for rows within the timeframe specified and minute value specified
        trd_size_data = pd.DataFrame(self.model.objects.filter(dt__minute__in=acceptable_minutes, dt__hour__in=acceptable_hours, dt__gte=lower_timeframe, 
        dt__lte=upper_timeframe).values('dt', *tuple(self.select_cols))).sort_values(by='dt', ascending=True).reset_index(drop=True)
        
        most_recent_row = trd_size_data.tail(1)   
        
        #get historical avg trade size using 30 day period ending at end time 
        historical_trd_size = pd.DataFrame(self.model.objects.filter(dt__minute__in=[0, 30], dt__gte=datetime.datetime.today()-datetime.timedelta(days=30),  
        dt__lte=upper_timeframe).values('dt', 'avg_trd_size_12_hour')).sort_values(by='dt', ascending=True).reset_index(drop=True) 

        historical_trd_size = historical_trd_size.dropna(how="any")
        
        #get historical average
        average_trd_size = np.mean(historical_trd_size['avg_trd_size_12_hour'])  
        
        #color code array based on the trade size vs average 
        avg_trd_size_info_array = self.calc_trdsize_info_array(most_recent_row, average_trd_size)

        trd_size_data['avg_trade_size'] = trd_size_data[trd_size_column]  
        
        trd_size_data = trd_size_data[['dt', 'avg_trade_size']]

        trd_size_data['dt'] = trd_size_data['dt'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ')) 
        
        trd_size_data = trd_size_data.dropna(how="any")   

        trd_size_data['avg_trade_size'] = trd_size_data['avg_trade_size'].apply(str)

        #constructing the json object to send back - object with the jsonified chart series, and volume info array

        response_data = {}

        chart_series = trd_size_data.to_json(orient='records')

        chart_series = json.loads(chart_series)

        response_data['chart_series'] = chart_series 

        response_data['info_array'] = avg_trd_size_info_array

        response_data['historical_average'] = average_trd_size
        
        response_data = json.dumps(response_data) 

        return HttpResponse(response_data, content_type = 'application/json')

class VolumeList(View):

    model = Modelfactors 

    offset_col_mappings = {
        1: 'volume_5_min_vnorm',
        24: 'volume_30_min_vnorm', 
        168: 'volume_3_hour_vnorm', 
        720: 'volume_24_hour_vnorm'
    } 
    
    select_cols = ['volume_5_min_vnorm', 'volume_30_min_vnorm', 'volume_1_hour_vnorm', 'volume_3_hour_vnorm', 'volume_6_hour_vnorm', 'volume_12_hour_vnorm', 'volume_24_hour_vnorm']
    col_info_mappings =[
        {'volume_5_min_vnorm':'5m'},
        {'volume_1_hour_vnorm':'1H'},
        {'volume_3_hour_vnorm':'3H'},
        {'volume_6_hour_vnorm':'6H'},
        {'volume_12_hour_vnorm':'12H'},
        {'volume_24_hour_vnorm':'24H'}
    ]

    def make_volume_info_array(self, last_row): 

        """Creates the information array for the header of the visual cards"""

        info_array = []

        for col_info in self.col_info_mappings:
            
            colname = list(col_info.keys())[0] 
            
            colinfoname = col_info[colname]  
            
            try:
                
                value = list(last_row[colname])[0]  

                value = int(round(value*100, 0)) 

                if value>=100:
                    sentiment = "positive" 
                else:
                    sentiment = "negative" 
                
                value = str(value) + "%" 

                info_array.append([colinfoname, value, sentiment])
            except (IndexError, TypeError):
                pass 
        
        return info_array


    def get(self, request):

        upper_timeframe = request.GET["endtime"]

        hours_offset = int(request.GET["hoursoffset"])  
        
        if upper_timeframe=="Now":
            upper_timeframe = self.model.objects.latest('dt').dt
        else:
            upper_timeframe = datetime.datetime.strptime(upper_timeframe, '%Y-%m-%d %H:%M:%S')   
        
        lower_timeframe = upper_timeframe - datetime.timedelta(hours = hours_offset)

        lower_timeframe.replace(tzinfo=timezone.utc)

        upper_timeframe.replace(tzinfo=timezone.utc)  

        acceptable_minutes = acceptable_minute_values(upper_timeframe.minute, hours_offset_intervals[hours_offset])  

        acceptable_hours = acceptable_hour_values(upper_timeframe.hour, hours_offset_intervals[hours_offset])
        
        volume_column = self.offset_col_mappings[hours_offset]
        
        #retrieves pandas dataframe of all required volume columns sorted by date(ascending) filtered for rows within the timeframe specified and minute value specified
        volume_data = pd.DataFrame(self.model.objects.filter(dt__minute__in=acceptable_minutes, dt__hour__in=acceptable_hours, dt__gte=lower_timeframe, 
        dt__lte=upper_timeframe).values('dt', *tuple(self.select_cols))).sort_values(by='dt', ascending=True).reset_index(drop=True)
        
        most_recent_row = volume_data.tail(1)  

        volume_info_array = self.make_volume_info_array(most_recent_row)

        #make the return format consistent with the django serializer

        volume_data['volume_vnorm'] = volume_data[volume_column]  
        
        volume_data = volume_data[['dt', 'volume_vnorm']]

        volume_data['dt'] = volume_data['dt'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ')) 
        
        volume_data = volume_data.dropna(how="any")   

        volume_data['volume_vnorm'] = volume_data['volume_vnorm'].apply(str)

        #constructing the json object to send back - object with the jsonified chart series, and volume info array

        response_data = {}

        chart_series = volume_data.to_json(orient='records')

        chart_series = json.loads(chart_series)

        response_data['chart_series'] = chart_series 

        response_data['info_array'] = volume_info_array
        
        response_data = json.dumps(response_data)

        return HttpResponse(response_data, content_type = 'application/json')

class ReturnInfo(View):
    
    model = Intradaymarketdata  

    minutes_ago = [0, 60, 3*60, 12*60, 24*60, 7*24*60, 30*24*60] 

    time_labels = ["-", "1H", "3H", "12H", "1D", "1W", "1M"]
    
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
        
        return HttpResponse(json.dumps(response_array), content_type = 'application/json')



    


        

        

        



  
        

        

    










