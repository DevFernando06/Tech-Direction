from enum import StrEnum


class Permissions(StrEnum):
    READ_POST = 'READ_POST'
    CREATE_POST = 'CREATE_POST'
    UPDATE_POST = 'UPDATE_POST'
    DELETE_POST = 'DELETE_POST'
