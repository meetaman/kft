-- Table for vendor payments
CREATE TABLE vendor_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    bill_id INT,                     -- Reference to incoming_bills (can be NULL for misc payments)
    payment_type VARCHAR(20) NOT NULL, -- 'party' or 'misc'
    payment_date DATE NOT NULL,
    payment_mode VARCHAR(50) NOT NULL, -- Cash/Bank Transfer/Cheque/UPI
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),           -- For categorizing misc payments
    reference_no VARCHAR(100),       -- Cheque no, transaction id, etc.
    bank_account VARCHAR(100),       -- Bank account used for payment
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES incoming_bills(s_no) ON DELETE CASCADE
);

-- Table for cash purchases
CREATE TABLE cash_purchases (
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,
    party_id INT,                     -- Optional link to party_master
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_mode VARCHAR(50) NOT NULL, -- Cash/UPI/Card
    reference_no VARCHAR(100),         -- For digital payments
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (party_id) REFERENCES party_master(p_id) ON DELETE SET NULL
);

-- Table for cash purchase items
CREATE TABLE cash_purchase_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    purchase_id INT NOT NULL,
    product_id INT,                   -- Optional link to prod_master
    description VARCHAR(255) NOT NULL, -- For items not in product master
    qty DECIMAL(10,2) NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    gst_percent DECIMAL(5,2) DEFAULT 0,
    gst_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES cash_purchases(purchase_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES prod_master(prod_id) ON DELETE SET NULL
);

-- Table for miscellaneous payments
CREATE TABLE misc_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_date DATE NOT NULL,
    payment_mode VARCHAR(50) NOT NULL,  -- Cash/Bank Transfer/Cheque/UPI
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),              -- Optional category for grouping
    reference_no VARCHAR(100),          -- Cheque no, transaction id, etc.
    bank_account VARCHAR(100),          -- Bank account used for payment
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 