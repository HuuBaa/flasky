from .errors import forbidden
from flask import g
from functools import wraps

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_func(*args,**kw):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args,**kw)
        return decorated_func
    return decorator
