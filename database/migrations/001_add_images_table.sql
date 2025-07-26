-- Migration: Add images table and update invoices table
-- Created: 2025-07-25

-- Create images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    image_data BYTEA NOT NULL,
    file_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add image_id column to invoices table
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS image_id INTEGER;

-- Add foreign key constraint
ALTER TABLE invoices ADD CONSTRAINT fk_invoices_image_id 
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET NULL;

-- Create index on image_id for better performance
CREATE INDEX IF NOT EXISTS idx_invoices_image_id ON invoices(image_id);

-- Remove old image_path column (if exists)
ALTER TABLE invoices DROP COLUMN IF EXISTS image_path;