from permissions import Permissions

roles = {
    "admin": [Permissions.READ_POST, Permissions.CREATE_POST, Permissions.UPDATE_POST, Permissions.DELETE_POST],
    "writer": [Permissions.READ_POST, Permissions.CREATE_POST, Permissions.UPDATE_POST, Permissions.DELETE_POST],
    "student": [Permissions.READ_POST],
}


def validate_access(user_roles: list, permission_expected: str) -> bool:
    for role in user_roles:
        if permission_expected in roles.get(role, []):
            return True
    return False
