-- Migration: Seed initial roles

INSERT INTO roles (description, status)
VALUES
    ('admin', TRUE),
    ('writer', TRUE),
    ('student', TRUE)
ON CONFLICT (description) DO NOTHING;
