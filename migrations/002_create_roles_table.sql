-- Migration: Create roles table

CREATE TABLE IF NOT EXISTS roles (
    id_role SERIAL PRIMARY KEY,
    description VARCHAR(100) NOT NULL UNIQUE,
    status BOOLEAN NOT NULL DEFAULT TRUE
);
