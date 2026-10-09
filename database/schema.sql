-- Smart Canteen Database Schema (MySQL Compatible)
-- Database Name: smart_canteen

CREATE DATABASE IF NOT EXISTS smart_canteen;
USE smart_canteen;

-- 1. Users Table (Supports Students, Admins, Canteen Staff)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20),
    student_id VARCHAR(50) UNIQUE NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin', 'staff') NOT NULL DEFAULT 'student',
    wallet_balance DECIMAL(10,2) NOT NULL DEFAULT 500.00,
    dietary_pref VARCHAR(50) DEFAULT 'all',
    avatar_url VARCHAR(255) DEFAULT '/static/images/default-avatar.png',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Food Categories Table
CREATE TABLE IF NOT EXISTS food_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'fa-utensils',
    image_url VARCHAR(255),
    display_order INT DEFAULT 0
);

-- 3. Food Items Table
CREATE TABLE IF NOT EXISTS food_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    category_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    ingredients TEXT,
    is_veg TINYINT(1) NOT NULL DEFAULT 1,
    is_available TINYINT(1) NOT NULL DEFAULT 1,
    stock_quantity INT NOT NULL DEFAULT 50,
    prep_time_minutes INT NOT NULL DEFAULT 10,
    calories INT DEFAULT 250,
    spice_level VARCHAR(20) DEFAULT 'Medium',
    rating DECIMAL(3,2) DEFAULT 4.5,
    total_orders INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES food_categories(id) ON DELETE CASCADE
);

-- 4. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) NOT NULL UNIQUE,
    student_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    estimated_prep_time INT NOT NULL DEFAULT 15,
    pickup_time DATETIME NULL,
    special_instructions TEXT,
    cancellation_fee DECIMAL(10,2) DEFAULT 0.00,
    refund_amount DECIMAL(10,2) DEFAULT 0.00,
    cancellation_reason TEXT,
    cancelled_at DATETIME NULL,
    is_rescue_order TINYINT(1) DEFAULT 0,
    rescue_offer_id INT NULL,
    collection_pin VARCHAR(20) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    food_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
);

-- 6. Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    student_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    transaction_ref VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    current_stock DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    min_threshold DECIMAL(10,2) NOT NULL DEFAULT 10.00,
    max_capacity DECIMAL(10,2) NOT NULL DEFAULT 100.00,
    cost_per_unit DECIMAL(10,2) NOT NULL DEFAULT 20.00,
    expiry_days INT DEFAULT 7,
    status VARCHAR(30) DEFAULT 'IN_STOCK',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 8. Inventory Transactions Table
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inventory_id INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id) ON DELETE CASCADE
);

-- 9. Seat Tables Table
CREATE TABLE IF NOT EXISTS seat_tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_number VARCHAR(20) NOT NULL UNIQUE,
    capacity INT NOT NULL DEFAULT 4,
    section VARCHAR(50) DEFAULT 'Main Hall',
    is_active TINYINT(1) DEFAULT 1
);

-- 10. Seat Bookings Table
CREATE TABLE IF NOT EXISTS seat_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_code VARCHAR(20) NOT NULL UNIQUE,
    student_id INT NOT NULL,
    table_id INT NOT NULL,
    guests_count INT NOT NULL DEFAULT 1,
    booking_date DATE NOT NULL,
    time_slot VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'CONFIRMED',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES seat_tables(id) ON DELETE CASCADE
);

-- 11. Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    order_id INT NULL,
    rating INT NOT NULL DEFAULT 5,
    aspect VARCHAR(50) DEFAULT 'General',
    sentiment VARCHAR(20) DEFAULT 'POSITIVE',
    comment TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
);

-- 12. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(30) DEFAULT 'info',
    is_read TINYINT(1) DEFAULT 0,
    link VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 13. Coupons Table
CREATE TABLE IF NOT EXISTS coupons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    min_order_amount DECIMAL(10,2) DEFAULT 0.00,
    max_discount DECIMAL(10,2) DEFAULT 100.00,
    is_active TINYINT(1) DEFAULT 1,
    expiry_date DATE NOT NULL
);

-- 14. AI Predictions Table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_type VARCHAR(50) NOT NULL,
    target_date DATE NOT NULL,
    payload_json TEXT NOT NULL,
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 15. Food Rescue Offers Table (Anti-Waste Flash Deals)
CREATE TABLE IF NOT EXISTS food_rescue_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_order_id INT NOT NULL,
    original_student_id INT NOT NULL,
    food_id INT NOT NULL,
    food_name VARCHAR(120),
    quantity_available INT NOT NULL DEFAULT 1,
    quantity_claimed INT NOT NULL DEFAULT 0,
    original_price DECIMAL(10,2) NOT NULL,
    rescue_price DECIMAL(10,2) NOT NULL,
    discount_percent INT DEFAULT 10,
    offer_status VARCHAR(30) DEFAULT 'AVAILABLE',
    collection_point VARCHAR(120) DEFAULT 'College Canteen Central Counter',
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (original_student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
);

-- Indexes for lightning fast queries
CREATE INDEX idx_orders_student ON orders(student_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_food_category ON food_items(category_id);
CREATE INDEX idx_seat_bookings_date_slot ON seat_bookings(booking_date, time_slot);
CREATE INDEX idx_feedback_sentiment ON feedback(sentiment);
CREATE INDEX idx_rescue_offers_status ON food_rescue_offers(offer_status);
