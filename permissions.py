from enum import StrEnum

class Permissions(StrEnum): 
    READ_TRAIL = 'READ_TRAIL'
    CREATE_TRAIL = 'CREATE_TRAIL'
    UPDATE_TRAIL = 'UPDATE_TRAIL'
    DELETE_TRAIL = 'DELETE_TRAIL'