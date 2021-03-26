import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base

import datetime


Base = declarative_base()

class ModelFactors(Base):

    __tablename__ = 'modelfactors'

    dt = Column(DateTime, primary_key=True) 

    #returns from time period columns
    ret_5_min = Column(Numeric(6, 5)) 
    ret_30_min = Column(Numeric(6, 5))  
    ret_1_hour = Column(Numeric(6, 5))  
    ret_3_hour = Column(Numeric(6, 5))  
    ret_6_hour = Column(Numeric(6, 5)) 
    ret_12_hour = Column(Numeric(6, 5))   
    ret_24_hour = Column(Numeric(6, 5))  

    #volume traded interval columns
    volume_5_min  = Column(Numeric(10, 2))  
    volume_30_min  = Column(Numeric(10, 2))  
    volume_1_hour  = Column(Numeric(10, 2))  
    volume_3_hour  = Column(Numeric(12, 2))  
    volume_6_hour  = Column(Numeric(12, 2))  
    volume_12_hour  = Column(Numeric(12, 2)) 
    volume_24_hour  = Column(Numeric(15, 2))    

    #volume vs normal columns
    volume_5_min_vnorm = Column(Numeric(8, 3)) 
    volume_30_min_vnorm = Column(Numeric(8, 3))  
    volume_1_hour_vnorm = Column(Numeric(8, 3))  
    volume_3_hour_vnorm = Column(Numeric(8, 3))  
    volume_6_hour_vnorm = Column(Numeric(8, 3)) 
    volume_12_hour_vnorm = Column(Numeric(8, 3))    
    volume_24_hour_vnorm = Column(Numeric(8, 3))   

    #volatility columns
    volatility_1_hour = Column(Numeric(5, 4)) 
    volatility_3_hour = Column(Numeric(5, 4)) 
    volatility_6_hour = Column(Numeric(5, 4)) 
    volatility_12_hour = Column(Numeric(5, 4)) 
    volatility_24_hour = Column(Numeric(5, 4)) 

    #avg trade size columns
    avg_trd_size_5_min = Column(Numeric(4, 3))  
    avg_trd_size_30_min = Column(Numeric(4, 3))   
    avg_trd_size_1_hour = Column(Numeric(4, 3))     
    avg_trd_size_3_hour = Column(Numeric(4, 3)) 
    avg_trd_size_6_hour = Column(Numeric(4, 3)) 
    avg_trd_size_12_hour = Column(Numeric(4, 3)) 
    avg_trd_size_24_hour = Column(Numeric(4, 3))  

    #future return columns
    ret_in_1_hour = Column(Numeric(6, 5)) 
    ret_in_12_hour = Column(Numeric(6, 5)) 
    ret_in_24_hour = Column(Numeric(6, 5))   



def makeEngine(user, password, host, database): 

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}:3306/{3}".format(user, password, host, database)) 

    return engine 








