from enum import StrEnum


class Permissions(StrEnum):
    READ_POST = 'READ_POST'
    CREATE_POST = 'CREATE_POST'
    UPDATE_POST = 'UPDATE_POST'            # editar os PRÓPRIOS posts
    DELETE_POST = 'DELETE_POST'            # excluir os PRÓPRIOS posts
    UPDATE_ANY_POST = 'UPDATE_ANY_POST'    # editar posts de QUALQUER autor -> novo
    DELETE_ANY_POST = 'DELETE_ANY_POST'    # excluir posts de QUALQUER autor -> novo
    MANAGE_WRITERS = 'MANAGE_WRITERS'      # cadastrar e gerenciar escritores -> novo