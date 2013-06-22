def curry(func, x):
    def curried(y):
        return func(x, y)
    return curried

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

def partition_by(coll, func):
    """
    Takes and drops to create groups.
    """
    i = 0
    to_return = []
    while i < len(coll):
        curried_func = curry(func, coll[i])
        taken = take_while(coll[i:], curried_func)
        to_return.append(taken)
        i += len(taken)
    return to_return