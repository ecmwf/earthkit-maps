
def alias(**aliases):
    def decorator(function):
        def wrapper(*args, **kwargs):
            kwargs = {aliases.get(key, key): value for key, value in kwargs.items()}
            return function(*args, **kwargs)
        return wrapper
    return decorator
