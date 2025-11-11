# Minimal stand-in for Google's ADK so your code runs locally and on Cloud Run.
from functools import wraps

def action():
    """Decorator – no-op replacement for @action()"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


class Agent:
    """Very small stub of adk.Agent – just stores a name."""
    def __init__(self, name: str = "local-agent"):
        self.name = name
