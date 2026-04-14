from fastapi import Security
from ..core.security import get_current_user

def require_read_user():
    return Security(get_current_user, scopes=["read:user"])

def require_write_user():
    return Security(get_current_user, scopes=["write:user"])

def require_delete_user():
    return Security(get_current_user, scopes=["delete:user"])