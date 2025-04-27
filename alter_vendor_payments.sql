ALTER TABLE vendor_payments 
ADD COLUMN payment_type VARCHAR(20) NOT NULL DEFAULT 'party',
ADD COLUMN category VARCHAR(100) AFTER payment_mode; 