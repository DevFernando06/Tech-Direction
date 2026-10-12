from permissions import Permissions

roles = {
    "admin": [Permissions.READ_TRAIL, Permissions.CREATE_TRAIL, Permissions.UPDATE_TRAIL, Permissions.DELETE_TRAIL],
    "writer": [Permissions.READ_TRAIL, Permissions.CREATE_TRAIL, Permissions.UPDATE_TRAIL, Permissions.DELETE_TRAIL],
    "student": [Permissions.READ_TRAIL] 
}

def validate_access(user_roles: list, permission_expected: str) -> bool:
    for role in user_roles:
        if permission_expected in roles.get(role, []):
            return True
    return False