-- PostgreSQL Database Setup for NIRO Policy Engine
-- Run this script to create the database and user

-- Create database
CREATE DATABASE niro_policies;

-- Create user (optional, you can use existing user)
-- CREATE USER niro_user WITH PASSWORD 'niro_password';

-- Grant permissions
-- GRANT ALL PRIVILEGES ON DATABASE niro_policies TO niro_user;

-- Connect to the database
\c niro_policies;

-- Create schema (optional, tables will be created by SQLAlchemy)
-- CREATE SCHEMA IF NOT EXISTS policy_engine;

-- The application will automatically create tables using SQLAlchemy migrations
