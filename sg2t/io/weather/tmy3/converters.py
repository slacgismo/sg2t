import datetime

"""This module handles the conversion of various datatypes 
from NREL's TMY3 data to datetime objects.
"""
def get_date(date, coerce_year=coerce_year):
    if coerce_year:
        return datetime.datetime.strptime(dt, "%m/%d/%Y").replace(year=coerce_year).date()
    else:
        return datetime.datetime.strptime(dt, "%m/%d/%Y").date()


def get_time(time):
    return datetime.time(hour=int(time.split(':')[0]) - 1)