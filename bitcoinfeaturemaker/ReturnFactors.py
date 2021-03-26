import pandas as pd
import datetime
import numpy as np




class ReturnFactors:
    
    from_minutes = [5, 30, 60, 180, 360, 720, 1440]

    to_minutes = [-60, -720, -1440] 

    matching_threshold_seconds = 30
    
    def __init__(self):
        pass

    def init_df(self, df):
        self.__raw_df = df[['dt','trade']].rename(columns={'dt':'base_dt',
        'trade':'base_price'}).sort_values(by='base_dt', ascending=True)
    
    def calc_returns(self, factors_df):

        factor_dict = {} 

        raw_data_dates = list(self.__raw_df['base_dt']) 

        factors_df = factors_df.sort_values(by='dt', ascending=True)

        for minute in self.from_minutes: 
            
            #get the column name
            if minute%60==0:
                col_name = "ret_{0}_hour".format(int(minute/60)) 
            else:
                col_name = "ret_{0}_min".format(minute) 
            
            #use this to just cleanup any working columns later
            filter_cols = list(factors_df.columns) + [col_name]
            
            #the merge time is the current time - the number of minutes
            factors_df['mergetime'] = factors_df['dt'].apply(lambda current_time: (current_time - datetime.timedelta(minutes=minute)).to_pydatetime())
            
            #merge the factors dataframe with the raw data dataframe on this merge time to get the price at that time
            factors_df = pd.merge_asof(factors_df, self.__raw_df, left_on='mergetime', right_on='base_dt', 
                                direction='nearest', tolerance=datetime.timedelta(seconds=self.matching_threshold_seconds))
            
            #define the return as the current price over the price at that time
            factors_df[col_name] = (factors_df['trade']/factors_df['base_price']).apply(lambda x: round(x-1, 5)) 
            
            #remove any junk columns used to merge etc.
            factors_df = factors_df[filter_cols] 

    
        return factors_df         



    
    

    



