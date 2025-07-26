-- Initialize database for Invoice OCR system

-- Create extension for UUID generation if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    image_data BYTEA NOT NULL,
    file_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_code VARCHAR(100),
    payment_date TIMESTAMP,
    total_amount DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_id INTEGER REFERENCES images(id) ON DELETE SET NULL,
    raw_text TEXT
);

-- Create invoice_items table
CREATE TABLE IF NOT EXISTS invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
    item_name VARCHAR(255),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_date ON invoices(payment_date);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_code ON invoices(invoice_code);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at);
CREATE INDEX IF NOT EXISTS idx_invoices_image_id ON invoices(image_id);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);

-- Insert sample data (optional)
-- INSERT INTO invoices (invoice_code, payment_date, total_amount, image_path, raw_text)
-- VALUES 
--     ('HD001', '2024-01-15 10:30:00', 150000.00, '/uploads/sample1.jpg', 'Sample OCR text 1'),
--     ('HD002', '2024-01-16 14:45:00', 275000.00, '/uploads/sample2.jpg', 'Sample OCR text 2');

COMMIT;