import logging 

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.sql import func

import config 

from bitcoinfeaturemaker.dbmodels import ModelFactors 

import datetime
import time
import pandas as pd
import traceback

from bitcoinfeaturemaker.ReturnFactors import *
from bitcoinfeaturemaker.VolatilityFactors import *
from bitcoinfeaturemaker.VolumeFactors import * 

logger = logging.getLogger(__name__)

META_DATA = None
RAW_DATA_TABLE = None
FACTORS_TABLE = None
Session = None

#FACTOR CALCULATION CLASSES
RetFact = None
VolatilityFact = None
VolumeFact = None

DAYS_REQUIRED_RAW_DATA = 3


def initialise_db_setup(engine):

    global META_DATA
    global RAW_DATA_TABLE
    global FACTORS_TABLE 
    global Session
    global RetFact
    global VolatilityFact
    global VolumeFact
    
    META_DATA = MetaData(bind=engine)

    META_DATA.reflect()

    RAW_DATA_TABLE = META_DATA.tables['intradaymarketdata']  

    FACTORS_TABLE = META_DATA.tables['modelfactors'] 

    Session = sessionmaker(bind=engine) 

    RetFact = ReturnFactors()

    VolatilityFact = VolatilityFactors()

    VolumeFact = VolumeFactors(Session, ModelFactors) 

def get_raw_data(last_update_time, engine): 

    """Retrieves raw data from the sql db. Filters for data from now - DAYS_REQUIRED_RAW_DATA days"""
    
    connection = engine.connect()

    statement = select([RAW_DATA_TABLE]).where(RAW_DATA_TABLE.c.dt > last_update_time-datetime.timedelta(days=DAYS_REQUIRED_RAW_DATA))
    
    df = pd.read_sql(statement, connection).sort_values(by='dt', ascending = False).reset_index(drop=True) 

    connection.close()

    return df

def get_last_factor_update(engine): 

    """Retrieves the datetime of the most recently updated row 
    in the model factors db"""

    connection = engine.connect()

    statement = select([func.max(FACTORS_TABLE.c.dt)]) 

    res = connection.execute(statement) 

    connection.close()

    return res.fetchone()[0] 

def get_factor_columns():

    """Gets the column names in the ModelFactors table in the SQL db"""

    factor_columns = [str(x).replace('modelfactors.','') for x in FACTORS_TABLE.c]  

    factor_columns = [x for x in factor_columns if 'ret_in' not in x] 

    return factor_columns

def construct_factors(raw_data, last_update): 

    """Creates a dataframe of model factors for all new raw data.

    Parameters:
    raw_data - pd.DataFrame - the raw data returned from get_raw_data
    last_update - datetime - a datetime object representing the time
    of the last observation in the model factors table

    returns:

    factors_df - pd.DataFrame - the dataframe of model factors for all of the
    new rows"""
    
    ###CALCULATE RETURN FACTORS###
    RetFact.init_df(raw_data)

    factors_df = raw_data[raw_data['dt']>last_update].reset_index(drop=True)

    factors_df = RetFact.calc_returns(factors_df) 

    ###CALCULATE VOLATILITY FACTORS###
    VolatilityFact.init_df(raw_data) 

    factors_df = VolatilityFact.calc_volatilities(factors_df)  

    ##CALCULATE VOLUME FACTORS 
    VolumeFact.init_df(raw_data) 

    factors_df = VolumeFact.calc_volumes(factors_df) 
    
    #GET RID OF ANY COLUMNS WHICH MAY HAVE BEEN DEVELOPED IN PROCESS
    factor_columns = get_factor_columns()

    factors_df = factors_df[factor_columns] 

    factors_df.sort_values(by='dt', ascending=True)  

    return factors_df
    
def insert_new_factors(factors_df): 

    """Takes the dataframe of new model factor rows and 
    inserts into the SQL table"""

    factors_df = factors_df.reset_index(drop=True) 
    
    session = Session()

    for i in range(len(factors_df)):
        
        row_col_values = {}   

        for col in list(factors_df.columns): 

            value = factors_df.loc[i, col] 
            
            if str(value)!="nan":
                row_col_values[col] = value
        
        new_factor = ModelFactors(**row_col_values)  

        session.add(new_factor) 

        try:
            session.commit()  
        except Exception:  
            logger.exception("ERROR ENCOUNTERED TRYING TO INSERT NEW FACTORS")
            traceback.print_exc()
            session.rollback() 
    
    logger.info("{0} rows added to model factors".format(len(factors_df)))
            
    session.close()

def main(engine): 

    initialise_db_setup(engine) 
    
    while True: 
        
        try:
            last_factor_update_time = get_last_factor_update(engine) 
            
            raw_data = get_raw_data(last_factor_update_time, engine)  
            
            factors_df = construct_factors(raw_data, last_factor_update_time)  
            
            insert_new_factors(factors_df) 
            
        
        except Exception as e:  

            logger.exception("ERROR ENCOUNTERED IN MAIN LOOP")

        
        time.sleep(65)
    


