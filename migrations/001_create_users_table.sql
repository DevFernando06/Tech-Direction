-- Migration: Create users table

CREATE TABLE IF NOT EXISTS users (
    id_user SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    date_birth DATE NOT NULL,
    status BOOLEAN NOT NULL DEFAULT TRUE
);
