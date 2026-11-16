-- Migration: Create roles_user join table

CREATE TABLE IF NOT EXISTS roles_user (
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    id_role INTEGER NOT NULL REFERENCES roles(id_role) ON DELETE CASCADE,
    PRIMARY KEY (id_user, id_role)
);

CREATE INDEX IF NOT EXISTS idx_roles_user_id_role ON roles_user (id_role);
