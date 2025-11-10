def setdefaultmany(obj, keys, func, default = None):
    for k in keys:
        obj[k] = func(obj[k]) if obj.get(k) else default

