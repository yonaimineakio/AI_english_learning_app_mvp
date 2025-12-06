-- Migration for new features:
-- 1. Streak tracking (current_streak, longest_streak, last_activity_date)
-- 2. Points system (total_points, point_histories table)

-- Add streak fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity_date TIMESTAMP WITH TIME ZONE;

-- Add points field to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0;

-- Create point_histories table
CREATE TABLE IF NOT EXISTS point_histories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on point_histories
CREATE INDEX IF NOT EXISTS idx_point_histories_user_id ON point_histories(user_id);
CREATE INDEX IF NOT EXISTS idx_point_histories_created_at ON point_histories(created_at DESC);

-- Create index on users for ranking queries
CREATE INDEX IF NOT EXISTS idx_users_total_points ON users(total_points DESC);
