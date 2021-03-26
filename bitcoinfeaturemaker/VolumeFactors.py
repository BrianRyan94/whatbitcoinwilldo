import pandas as pd
import datetime  
import time
import numpy as np
import math
from sqlalchemy import and_, extract
import traceback

class VolumeFactors:

    minutes = [5, 30, 60, 180, 360, 720, 1440]
    
    def __init__(self, session, modelfactors): 

        self.session = session
        self.modelfactors = modelfactors
        self.average_volumes = {}

    def init_df(self, df):
        self.__raw_df = df[['dt','volume','numtrades']]  

    def calc_volume_numtrades(self, volume_array):
    
        total_volume = 0.0
        
        for i in range(1, len(volume_array)):
            
            increment = volume_array[i]-volume_array[i-1] 
            
            if increment>=0:
                total_volume += increment
            else:
                total_volume += volume_array[i] 
        
        return total_volume

    def get_traded_interval(self, time_value, minute):

        COL_TYPE = list(time_value.columns)[1] 

        RAW_DATA = self.__raw_df[['dt', COL_TYPE]].sort_values(by='dt', ascending=True).reset_index(drop=True)

        time_value = time_value.sort_values(by='dt', ascending=True).reset_index(drop=True)
        
        #GET THE TIME YOU NEED THE VOLUME TRADED AT (OR NUM TRADES) E.G. 5 MINUTES AGO
        time_value['merge_time'] = time_value['dt']-datetime.timedelta(minutes=minute)
        
        #MAKE A NEW DATASET TO MERGE ON SO YOU CAN GET THIS VALUE
        MERGE_DATA = RAW_DATA[['dt']].rename(columns={'dt':'since_date'}) 
        
        #MERGE SO YOU NOW HAVE A COLUMN WITH THE SPECIFIC "SINCE" TIME
        time_value = pd.merge_asof(time_value, MERGE_DATA, left_on='merge_time', right_on='since_date',direction='nearest',
        tolerance = datetime.timedelta(seconds=10))

        return_values = []

        for current_time, since_time in zip(list(time_value['dt']), list(time_value['since_date'])):

            if(str(current_time)=='nan' or str(since_time)=='nan'):
                return_values.append(float("nan")) 
                continue 

            time_section_df = RAW_DATA[(RAW_DATA['dt']>=since_time)&(RAW_DATA['dt']<=current_time)]  

            time_section_df = time_section_df.dropna(how='any')

            values=list(time_section_df[COL_TYPE]) 

            required_length = max(1, minute*0.8) 

            if len(values)<required_length:
                return_values.append(float("nan")) 
                continue 

            traded = round(self.calc_volume_numtrades(values), 2)

            return_values.append(traded) 
        
        return return_values

    def volume_traded_intervals(self, factors_df):

        minutes = self.minutes

        minutes.sort()
        
        for minute in minutes: 
            if minute%60==0:
                new_col = 'volume_{0}_hour'.format(int(minute/60)) 
            else:
                new_col = 'volume_{0}_min'.format(int(minute))   
            
            factors_df[new_col] = self.get_traded_interval(factors_df[['dt', 'volume']], minute) 
        
        return factors_df
            
    def gettrades_intervals(self, factors_df):

        minutes = self.minutes

        minutes.sort()
        
        for minute in minutes:
            if minute%60==0:
                new_col = 'numtrades_{0}_hour'.format(int(minute/60)) 
            else:
                new_col = 'numtrades_{0}_min'.format(int(minute))   
                     
            factors_df[new_col] = self.get_traded_interval(factors_df[['dt', 'numtrades']], minute) 
        
        return factors_df 
    
    def get_average_trade_sizes(self, factors_df):
        
        for minute in self.minutes: 
            if minute%60==0:
                new_col = 'avg_trd_size_{0}_hour'.format(int(minute/60))  
                volume_col = 'volume_{0}_hour'.format(int(minute/60))  
                numtrades_col = 'numtrades_{0}_hour'.format(int(minute/60)) 
            else:
                new_col = 'avg_trd_size_{0}_min'.format(int(minute))  
                volume_col = 'volume_{0}_min'.format(int(minute))    
                numtrades_col = 'numtrades_{0}_min'.format(int(minute))  

            factors_df[new_col] = (factors_df[volume_col]/factors_df[numtrades_col]).apply(lambda x: round(x, 3)) 

        return factors_df  

    def calculate_average_volume(self, current_time, time_for_average, volume_column):

        ##SELECT THE REQUIRED INFORMATION 
        
        errors = 0

        while True: 
            
            if errors>=3:
                return float("nan")

            try:
                session = self.session()

                volume_data = pd.read_sql(session.query(self.modelfactors).filter(and_(extract('hour', self.modelfactors.dt)==time_for_average.hour, 
                extract('minute', self.modelfactors.dt)==time_for_average.minute,self.modelfactors.dt<current_time, 
                self.modelfactors.dt>=current_time-datetime.timedelta(days=15))).statement, session.bind)

                session.close() 

                break
            
            except Exception as e:  
                errors += 1
                time.sleep(2)

        volume_data = volume_data[[volume_column]].dropna(how='any')

        volumes = list(volume_data[volume_column]) 
        
        if len(volumes)<5:
            return float("nan") 
        
        volumes.sort() 

        if len(volumes)<8:
            volumes = volumes[1:-1] 
        else:
            volumes = volumes[2:-2] 
        
        average = sum(volumes)/len(volumes) 

        return average

    def get_avg_volume_for_timeframe(self, current_time, volume_column): 
        
        #GET THE CLOSEST 15 MINUTE INTERVAL TO THIS EXACT TIME SUCH THAT TIME_FOR_AVERAGE WILL BE (1, 15, 0), (1, 0, 0) ETC.
        time_minutes = current_time.minute
        
        remainder = time_minutes%15
        
        if time_minutes>45:
            closest_15 = 45 
        else:
            if remainder<=7:
                closest_15 = time_minutes - remainder 
            else:
                closest_15 = time_minutes +(15-remainder) 
        
        time_for_average = datetime.time(current_time.hour, closest_15, 0)   

        #CHECK IF THERE IS EITHER 1) NO ENTRY FOR THIS TIME AND AVERAGE VOLUME OR THE DIFFERENCE BETWEEEN NOW AND THAT LAST UPDATED TIME IS GREATER THAN 2 DAYS
        if self.average_volumes.get(volume_column, {}).get(time_for_average, None)==None or \
            abs((current_time-self.average_volumes.get(volume_column, {}).get(time_for_average, None)['updated_time']).days)>2:
            
            #IF EITHER OF THOSE IS TRUE THEN RECALCULATE THE AVERAGE VOLUME
            average_volume = self.calculate_average_volume(current_time, time_for_average, volume_column) 
            
            #CREATE ENTRY FOR THIS VOLUME COLUMN
            if self.average_volumes.get(volume_column, None)==None:
                self.average_volumes[volume_column] = {}
            
            #CREATE ENTRY FOR THIS VOLUME COLUMN FOR THIS TIME
            if self.average_volumes.get(volume_column).get(time_for_average)==None:
                self.average_volumes[volume_column][time_for_average] = {}
            
            #SET THE UPDATED TIME TO THE CURRENT TIME
            self.average_volumes[volume_column][time_for_average]['updated_time'] = current_time 
            
            #SET THE AVERAGE VOLUME TO THE CALCULATED AVERAGE VOLUME
            self.average_volumes[volume_column][time_for_average]['average_volume'] = average_volume 
        
        #THE DICTIONARY WILL NOW BE POPULATED WITH THE REQUIRED VOLUME SO RETURN IT
        return self.average_volumes[volume_column][time_for_average]['average_volume']
        
      
    def calc_volume_vs_normal(self, factors_df, minute): 
        
        values_to_return = []    
        
        #GET THE COLUMN WHICH CONTAINS THE DATA WE NEED TO GET AVERAGE VOLUMES TRADED FOR THIS INTERVAL AT THIS TIME
        if minute%60==0:
            associated_volume_col = 'volume_{0}_hour'.format(int(minute/60)) 
        else:
            associated_volume_col = 'volume_{0}_min'.format(int(minute))  

        for i in range(len(factors_df)):
            
            #GET THE DATETIME OF THIS ROW
            current_dt = factors_df['dt'][i] 
            
            #GET THE VOLUME TRADED FOR THIS INTERVAL FOR THIS ROW
            current_volume = factors_df[associated_volume_col][i]
            
            #GET THE AVERAGE VOLUME TRADED FOR THE TIME INTERVAL
            avg_volume = self.get_avg_volume_for_timeframe(current_dt, associated_volume_col)

            vol_v_norm = round(current_volume/avg_volume, 3) 
                
            values_to_return.append(vol_v_norm) 
    
        return values_to_return 
    
    def get_volume_traded_vs_normal(self, factors_df):
        #FOR EVERY MINUTE A NEW COLUMN MUST BE CREATED
        for minute in self.minutes: 
            
            if minute%60==0:
                new_col = 'volume_{0}_hour_vnorm'.format(int(minute/60)) 
            else:
                new_col = 'volume_{0}_min_vnorm'.format(int(minute))  
            
            factors_df[new_col] = self.calc_volume_vs_normal(factors_df, minute)
        
        return factors_df



    def calc_volumes(self, factors_df): 
        
        #THIS APPENDS COLUMNS LIKE VOLUME_1_HOUR, VOLUME_5_MINS SHOWING VOLUMES TRADED IN LAST X_MINUTES 

        factors_df = self.volume_traded_intervals(factors_df) 
        
        #THIS DOES THE SAME AS ABOVE BUT JUST GETS THE NUMBER OF TRADES DURING THE INTERVAL 
        factors_df = self.gettrades_intervals(factors_df) 
        
        #THIS SIMPLY DIVIDES THE ABOVE
        factors_df= self.get_average_trade_sizes(factors_df) 
        
        #THIS CALCULATES THE VOLUME TRADED VERSUS NORMAL AMOUNT TRADED DURING THE INTERVAL
        factors_df=self.get_volume_traded_vs_normal(factors_df)

        return factors_df





 