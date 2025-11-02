-- Create the database with proper character encoding
CREATE DATABASE IF NOT EXISTS pawfect
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create the application user with password
CREATE USER IF NOT EXISTS 'pawuser'@'localhost' 
IDENTIFIED BY 'StrongP@ssw0rd123';

-- Grant privileges to the user for the pawfect database
GRANT ALL PRIVILEGES ON pawfect.* TO 'pawuser'@'localhost';

-- Make sure privileges are applied
FLUSH PRIVILEGES;

-- Switch to the new database
USE pawfect;

-- Create initial tables (example - customize as needed)
CREATE TABLE IF NOT EXISTS pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    species VARCHAR(50),
    breed VARCHAR(120),
    age_years FLOAT,
    sex ENUM('male', 'female'),
    size ENUM('tiny', 'small', 'medium', 'large'),
    description TEXT,
    photo_url VARCHAR(1024),
    status ENUM('available', 'adopted', 'pending') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);