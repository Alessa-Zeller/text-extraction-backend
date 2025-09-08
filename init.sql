-- Initialize database for PDF Processing API

-- Create users table (example for future database integration)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create processed_files table (for tracking processed PDFs)
CREATE TABLE IF NOT EXISTS processed_files (
    id SERIAL PRIMARY KEY,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    total_pages INTEGER NOT NULL,
    total_text_length INTEGER NOT NULL,
    processed_by VARCHAR(50) REFERENCES users(user_id),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,
    metadata JSONB,
    status VARCHAR(20) DEFAULT 'completed'
);

-- Create batch_processing table (for tracking batch operations)
CREATE TABLE IF NOT EXISTS batch_processing (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) UNIQUE NOT NULL,
    total_files INTEGER NOT NULL,
    successful_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    processed_by VARCHAR(50) REFERENCES users(user_id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'processing'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_processed_files_hash ON processed_files(file_hash);
CREATE INDEX IF NOT EXISTS idx_processed_files_processed_by ON processed_files(processed_by);
CREATE INDEX IF NOT EXISTS idx_batch_processing_batch_id ON batch_processing(batch_id);
CREATE INDEX IF NOT EXISTS idx_batch_processing_processed_by ON batch_processing(processed_by);

-- Insert default admin user (password: admin123)
INSERT INTO users (user_id, email, hashed_password, full_name, is_admin) 
VALUES (
    'admin_123',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.0JvKLY.Ii',  -- admin123
    'Admin User',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Insert default regular user (password: user123)
INSERT INTO users (user_id, email, hashed_password, full_name, is_admin) 
VALUES (
    'user_456',
    'user@example.com',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',  -- user123
    'Regular User',
    FALSE
) ON CONFLICT (email) DO NOTHING;
