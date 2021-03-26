import pandas as pd
import datetime  
import numpy as np
import math


class VolatilityFactors:

    hours = [1, 3, 6, 12, 24] 

    def __init__(self):
        pass

    def init_df(self, df):
        self.__raw_df = df[['dt','trade']].rename(columns={'dt':'base_dt',
        'trade':'base_price'}).sort_values(by='base_dt', ascending=True)  

    def get_ten_minute_intervals(self):

        min_time_dataset = min(self.__raw_df['base_dt'])
        
        min_time_dataset = datetime.datetime.combine(min_time_dataset, datetime.time(min_time_dataset.hour, min_time_dataset.minute, 0))
        
        max_time_dataset = max(self.__raw_df['base_dt'])
        
        max_time_dataset = datetime.datetime.combine(max_time_dataset, datetime.time(max_time_dataset.hour, max_time_dataset.minute, 0))
        
        times = []
        
        current_time = min_time_dataset
        
        while(current_time<=max_time_dataset):
            
            times.append(current_time) 
            
            current_time = current_time + datetime.timedelta(minutes = 10)
        
        ten_minute_interval_data = pd.DataFrame()
        
        ten_minute_interval_data['interval_times'] = times  

        ten_minute_interval_data = pd.merge_asof(ten_minute_interval_data, self.__raw_df, left_on='interval_times', right_on='base_dt', 
                                direction='nearest',tolerance=datetime.timedelta(seconds=60)) 
        
        ten_minute_interval_data = ten_minute_interval_data.sort_values(by='interval_times', ascending=True)

        ten_minute_interval_data['return'] = (ten_minute_interval_data['base_price']/ten_minute_interval_data['base_price'].shift(1)).apply(lambda x: math.log(x))
        
        ten_minute_interval_data = ten_minute_interval_data[['interval_times', 'return']] 

        return ten_minute_interval_data

    def get_interval_volatilities(self, interval_returns):

        interval_returns = interval_returns.sort_values(by='interval_times', ascending=True).reset_index(drop=True)

        for hour in self.hours:
            
            new_col = "volatility_{0}_hour".format(int(hour))

            new_col_values = [] 
            
            for i in range(len(interval_returns)):

                upper_time = interval_returns.loc[i, 'interval_times'] 
                
                lower_time = upper_time-datetime.timedelta(hours=hour) + datetime.timedelta(minutes=10) 

                time_section_df = interval_returns[(interval_returns['interval_times']>=lower_time)&
                (interval_returns['interval_times']<=upper_time)] 

                time_section_df = time_section_df.dropna(how='any')

                required_number_returns = hour*6*0.8

                if len(time_section_df)<required_number_returns:
                    new_col_values.append(float("nan")) 
                    continue 

                returns_array = np.array(time_section_df['return'])

                stdev = np.std(returns_array)

                implied_daily = np.sqrt(((24*60)/10))*stdev  

                new_col_values.append(round(implied_daily, 4))

            interval_returns[new_col] = new_col_values 

        interval_returns = interval_returns[['interval_times'] + [x for x in 
        list(interval_returns.columns) if 'volatility_' in x]]
        
        return interval_returns
                

    def calc_volatilities(self, factors_df):
        
        ten_minute_interval_returns = self.get_ten_minute_intervals()

        interval_volatilities = self.get_interval_volatilities(ten_minute_interval_returns) 

        factors_df = factors_df.sort_values(by='dt', ascending=True)

        factors_df = pd.merge_asof(factors_df, interval_volatilities, left_on='dt', right_on='interval_times', 
                               direction='backward', tolerance=datetime.timedelta(minutes=(11))) 

        factors_df = factors_df.drop(columns=['interval_times'])

        return factors_df 





