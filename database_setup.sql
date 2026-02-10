-- Premier Medical And Technical Institute Database Setup
-- MySQL Database Creation Script

-- Create database
CREATE DATABASE IF NOT EXISTS nursing_center CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE nursing_center;

-- Grant privileges (adjust username/password as needed)
-- GRANT ALL PRIVILEGES ON nursing_center.* TO 'root'@'localhost';
-- FLUSH PRIVILEGES;

-- Note: Django migrations will create all tables automatically
-- Run: python manage.py migrate

-- Optional: Create a test batch for initial setup
-- This will be done through Django admin panel after migrations

