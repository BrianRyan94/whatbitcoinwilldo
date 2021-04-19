def acceptable_minute_values(end_minute, interval_size):
    """Returns a list of desired minute values given the end minute and interval size.
    E.g. if last minute is 17 and we want 15 minute intervals then will return minute 2, 32, 
    47 etc"""

    acceptable_minutes = [] 

    start_point = end_minute 

    while(start_point-interval_size>0):
        start_point = start_point - interval_size

    while(start_point<60):
        acceptable_minutes.append(start_point) 
        start_point += interval_size 
    
    return acceptable_minutes

def acceptable_hour_values(end_hour, interval_size):
    """Returns the acceptable hours given an end hour and interval size.
    This means if our interval size is 720 minutes we will only return a row 
    every 6 hours"""
    
    acceptable_hours = []

    if interval_size<=60:
        return list(range(1, 24)) 
    else:
        interval_jump = int(round(interval_size/60, 0))  

        start_point = end_hour 

        while((start_point-interval_jump)>=0):
            start_point = start_point - interval_jump  
        
        while(start_point<24):

            acceptable_hours.append(start_point) 

            start_point += interval_jump 
        
        return acceptable_hours
        
        
        




