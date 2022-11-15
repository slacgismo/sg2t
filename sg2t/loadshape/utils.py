def get_daytype(x, daytypes):
    """Default grouping function:
    Get the day type for a datetime value
    """
    for daytype, weekdays in daytypes.items():
        if x.weekday() in weekdays:
            return daytype
    return None

def get_hour(x, dstrules ):
    """Default grouping function:
    Get the hour of day for a datetime value
    """
    if x.year in dstrules:
        rule = dstrules[x.year]
        if x > rule[0] and x <= rule[1]:
            return x.hour+1
    return x.hour