def take_while(coll, func):
    """
    Takes from the list until func returns False.
    """
    i = 0
    while i < len(coll) and func(coll[i]):
        i += 1
    return coll[:i]

def drop_while(coll, func):
    """
    Doesn't takes from the list until func returns False.
    """ 
    i = 0
    while i < len(coll) and func(coll[i]):
        i += 1
    return coll[i:]