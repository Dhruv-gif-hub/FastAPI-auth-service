from fastapi import Security
from ..core.security import get_current_user

# These functions define the required scopes for different user roles.
def require_read_user():
    return Security(get_current_user, scopes=["read:user"])

# This function defines the required scope for users who can modify user information.
def require_write_user():
    return Security(get_current_user, scopes=["write:user"])

# This function defines the required scope for users who can delete user information.
def require_delete_user():
    return Security(get_current_user, scopes=["delete:user"])

# This function defines the required scope for admin users.
def require_admin():
    return Security(get_current_user, scopes=["read:user_profile"])