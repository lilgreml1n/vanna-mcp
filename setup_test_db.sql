-- Setup script for a sample Inventory Database
-- Use this to test the Vanna AI MCP server

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS inventory_db;
USE inventory_db;

-- 2. Create the inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(100),
    description TEXT,
    gender VARCHAR(20),
    size VARCHAR(50),
    color VARCHAR(50),
    bin VARCHAR(50),
    sold_or_not ENUM('sold', 'not_sold') DEFAULT 'not_sold',
    active_listing VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Insert sample data
INSERT INTO inventory (brand, description, gender, size, color, bin, sold_or_not) VALUES
('Nike', 'Air Max 90 Running Shoes', 'Men', '10.5', 'Black/White', 'B-12', 'not_sold'),
('Adidas', 'Ultraboost 21', 'Women', '8', 'Cloud White', 'B-05', 'not_sold'),
('Levi''s', '501 Original Fit Jeans', 'Men', '32x34', 'Indigo', 'C-22', 'not_sold'),
('Patagonia', 'Better Sweater 1/4 Zip Pullover', 'Unisex', 'L', 'Oatmeal Heather', 'A-10', 'not_sold'),
('Lululemon', 'Align High-Rise Pant 25"', 'Women', '6', 'True Navy', 'D-14', 'not_sold'),
('The North Face', 'Nuptse Retro 1996 Jacket', 'Men', 'XL', 'Yellow/Black', 'E-01', 'sold'),
('Nike', 'Sportswear Tech Fleece Hoodie', 'Men', 'M', 'Dark Grey', 'B-12', 'sold'),
('Carhartt', 'Loose Fit Heavyweight T-Shirt', 'Men', 'L', 'Carhartt Brown', 'F-03', 'not_sold'),
('Birkenstock', 'Arizona Soft Footbed Sandals', 'Unisex', '42', 'Taupe Suede', 'G-08', 'not_sold'),
('Champion', 'Reverse Weave Hoodie', 'Unisex', 'S', 'Silver Grey', 'A-05', 'not_sold');

-- 4. Create a table for eBay Orders (for complex query testing)
CREATE TABLE IF NOT EXISTS ebay_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    item_id INT,
    order_date DATE,
    sale_price DECIMAL(10, 2),
    FOREIGN KEY (item_id) REFERENCES inventory(id)
);

-- Insert sample orders
INSERT INTO ebay_orders (order_id, item_id, order_date, sale_price) VALUES
('25-08123-9941', 6, '2024-02-15', 280.00),
('25-08124-9942', 7, '2024-02-18', 110.00);

-- Display the tables
SHOW TABLES;
SELECT * FROM inventory;
