-- PostgreSQL Initialization Script for Vault Course Labs
-- This script sets up the database for dynamic secrets engine exercises

-- Create the vault admin user (used by Vault to create dynamic credentials)
CREATE USER vault_admin WITH PASSWORD 'vault_admin_password' CREATEROLE;

-- Create application database
CREATE DATABASE appdb_production;

-- Connect to the application database
\c appdb

-- Create schema for application
CREATE SCHEMA IF NOT EXISTS app;

-- Create sample tables for exercises
CREATE TABLE app.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app.secrets_audit (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    username VARCHAR(100),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

CREATE TABLE app.configurations (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO app.users (username, email) VALUES
    ('alice', 'alice@techcorp.example'),
    ('bob', 'bob@techcorp.example'),
    ('charlie', 'charlie@techcorp.example');

INSERT INTO app.configurations (key, value) VALUES
    ('app.name', 'TechCorp Application'),
    ('app.version', '1.0.0'),
    ('app.environment', 'development');

-- Grant permissions to vault_admin for creating roles
GRANT ALL PRIVILEGES ON DATABASE appdb TO vault_admin;
GRANT ALL PRIVILEGES ON SCHEMA app TO vault_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA app TO vault_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA app TO vault_admin;

-- Grant vault_admin ability to grant permissions to dynamically created users
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO vault_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT USAGE ON SEQUENCES TO vault_admin;

-- Create read-only role template (Vault will create users with this role)
CREATE ROLE readonly_role;
GRANT CONNECT ON DATABASE appdb TO readonly_role;
GRANT USAGE ON SCHEMA app TO readonly_role;
GRANT SELECT ON ALL TABLES IN SCHEMA app TO readonly_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT ON TABLES TO readonly_role;

-- Create read-write role template
CREATE ROLE readwrite_role;
GRANT CONNECT ON DATABASE appdb TO readwrite_role;
GRANT USAGE ON SCHEMA app TO readwrite_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO readwrite_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA app TO readwrite_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO readwrite_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT USAGE ON SEQUENCES TO readwrite_role;

-- Output confirmation
\echo 'Database initialization complete!'
\echo 'Users: vault_admin (Vault connection), postgres (admin)'
\echo 'Roles: readonly_role, readwrite_role'
\echo 'Tables: app.users, app.secrets_audit, app.configurations'
