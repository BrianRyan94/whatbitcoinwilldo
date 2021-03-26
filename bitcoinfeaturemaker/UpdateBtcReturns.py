import logging

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.sql import func
from sqlalchemy import and_

from dbmodels import ModelFactors 

import pandas as pd
import datetime
import time
import traceback

logger = logging.getLogger(__name__)

Session = None
META_DATA = None
RAW_DATA_TABLE = None
FACTORS_TABLE = None 

MAX_LOOKBACK = 100

HOURS_TO_GET = [1, 12, 24]

def initialise_db_setup(engine):

    global Session
    global META_DATA
    global RAW_DATA_TABLE
    global FACTORS_TABLE

    Session = sessionmaker(bind=engine) 

    META_DATA = MetaData(bind=engine)

    META_DATA.reflect()

    RAW_DATA_TABLE = META_DATA.tables['intradaymarketdata']  

    FACTORS_TABLE = META_DATA.tables['modelfactors']  
    

def get_relevant_dates(hours, engine):

    """Returns the datetimes from the modelfactors table where
    the return in this number of hours is null, but where there is now a 
    price available in the raw data table
    
    Parameters:
    
    hours - Integer - number of hours ahead for the return""" 
    
    connection = engine.connect()

    statement = select([FACTORS_TABLE.c.dt]).where(and_(FACTORS_TABLE.c['ret_in_{0}_hour'.format(int(hours))] == None, 
    FACTORS_TABLE.c.dt<datetime.datetime.now()-datetime.timedelta(hours=hours), FACTORS_TABLE.c.dt>datetime.datetime.now()-datetime.timedelta(days=MAX_LOOKBACK)))
    
    df = pd.read_sql(statement, connection).sort_values(by='dt', ascending = False).reset_index(drop=True) 

    connection.close() 

    return df

def get_raw_data(since_date, engine):

    """Retrieves raw data from the sql db from a specific date"""

    connection = engine.connect()

    statement = select([RAW_DATA_TABLE]).where(RAW_DATA_TABLE.c.dt >= since_date)
    
    df = pd.read_sql(statement, connection).sort_values(by='dt', ascending = False).reset_index(drop=True) 

    connection.close() 

    return df 

def get_returns(relevant_dates, raw_data, hours):

    relevant_dates['future_time'] = relevant_dates['dt'] + datetime.timedelta(hours=hours) 

    raw_data = raw_data[['dt', 'trade']].rename(columns={'trade':'pxnow'}) 
     
    relevant_dates = relevant_dates.sort_values(by='dt',ascending=True) 

    raw_data = raw_data.sort_values(by='dt', ascending=True)

    relevant_dates = pd.merge_asof(relevant_dates, raw_data, direction='nearest', left_on='dt', right_on='dt', tolerance=datetime.timedelta(seconds=5)) 

    raw_data = raw_data.rename(columns={'pxnow':'pxfuture', 'dt':'future_time'}) 

    relevant_dates = pd.merge_asof(relevant_dates, raw_data, direction='nearest', left_on='future_time', right_on='future_time', tolerance=datetime.timedelta(seconds=5)) 

    relevant_dates['ret_in_{0}_hour'.format(int(hours))] = (relevant_dates['pxfuture']/relevant_dates['pxnow']).apply(lambda x: round(x-1, 5))

    relevant_dates = relevant_dates[['dt', 'ret_in_{0}_hour'.format(int(hours))]]
    
    return relevant_dates

def insert_returns(returns): 

    ret_header = list(returns.columns)[1]

    returns = returns.reset_index(drop=True)
    
    session = Session() 

    for i in range(len(returns)):

        dt = returns.loc[i, 'dt']  

        ret = returns.loc[i, ret_header] 

        if str(ret)=='nan':
            continue

        factor_row = session.query(ModelFactors).filter(ModelFactors.dt==dt).first()

        setattr(factor_row, ret_header, ret)

        try:
            session.commit()  
        except Exception:
            traceback.print_exc()
    
    session.close()
        
        
def returns_in_x_hour(hours, engine):   
    
    relevant_dates = get_relevant_dates(hours, engine) 

    minimum_date = min(relevant_dates['dt'])
    
    raw_data = get_raw_data(minimum_date, engine) 

    returns = get_returns(relevant_dates, raw_data, hours) 

    return returns 


def main(engine):

    initialise_db_setup(engine)
    
    while True:
        
        for hour in HOURS_TO_GET:  
            
            try:

                returns = returns_in_x_hour(hour, engine)

                insert_returns(returns)   

                logger.info("{0} rows inserted for returns in {1} hours.".format(len(returns), hour))
            
            except Exception: 

                logger.exception("ERROR ENCOUNTERED IN MAIN LOOP")

        
        time.sleep(65)
        




