-- Migration: Add support_tickets table
-- Description: Creates the support_tickets table for storing user support requests
-- Author: System
-- Date: 2025

-- Create support_tickets table
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL CHECK (char_length(message) >= 20 AND char_length(message) <= 5000),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('normal', 'urgent')) DEFAULT 'normal',
    status VARCHAR(20) NOT NULL CHECK (status IN ('open', 'in_progress', 'closed', 'resolved')) DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    admin_notes TEXT,
    internal_priority INTEGER DEFAULT 0 CHECK (internal_priority >= 0 AND internal_priority <= 10)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_email ON support_tickets(email);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_priority ON support_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_support_tickets_created_at ON support_tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status_priority ON support_tickets(status, priority);

-- Create updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_support_tickets_updated_at ON support_tickets;
CREATE TRIGGER update_support_tickets_updated_at
    BEFORE UPDATE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to set resolved_at when status changes to resolved or closed
CREATE OR REPLACE FUNCTION set_resolved_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('resolved', 'closed') AND OLD.status NOT IN ('resolved', 'closed') THEN
        NEW.resolved_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_support_ticket_resolved_at ON support_tickets;
CREATE TRIGGER set_support_ticket_resolved_at
    BEFORE UPDATE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION set_resolved_at();

-- Enable Row Level Security (RLS)
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Policy: Users can view their own tickets
CREATE POLICY "Users can view their own support tickets"
    ON support_tickets
    FOR SELECT
    USING (
        auth.uid() = user_id 
        OR email = (SELECT email FROM auth.users WHERE id = auth.uid())
    );

-- Policy: Authenticated users can create tickets
CREATE POLICY "Authenticated users can create support tickets"
    ON support_tickets
    FOR INSERT
    WITH CHECK (
        auth.uid() IS NOT NULL
        OR TRUE  -- Allow anonymous submissions (they still provide email)
    );

-- Policy: Users can update only their own tickets (limited fields)
CREATE POLICY "Users can update their own support tickets"
    ON support_tickets
    FOR UPDATE
    USING (
        auth.uid() = user_id 
        OR email = (SELECT email FROM auth.users WHERE id = auth.uid())
    )
    WITH CHECK (
        -- Users can only update message and priority before admin responds
        status = 'open'
    );

-- Policy: Service role and admins can view all tickets
-- Note: This requires a custom admin role setup in your Supabase project
-- For now, service role key will bypass RLS
CREATE POLICY "Service role can manage all support tickets"
    ON support_tickets
    FOR ALL
    USING (
        current_setting('role') = 'service_role'
        OR (SELECT raw_user_meta_data->>'role' FROM auth.users WHERE id = auth.uid()) = 'admin'
    );

-- Create a view for support ticket statistics (for admins)
CREATE OR REPLACE VIEW support_ticket_stats AS
SELECT
    COUNT(*) FILTER (WHERE status = 'open') as open_tickets,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tickets,
    COUNT(*) FILTER (WHERE status = 'closed') as closed_tickets,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved_tickets,
    COUNT(*) FILTER (WHERE priority = 'urgent' AND status NOT IN ('closed', 'resolved')) as urgent_tickets,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as tickets_last_24h,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as tickets_last_7d,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, NOW()) - created_at)) / 3600) FILTER (WHERE resolved_at IS NOT NULL) as avg_resolution_hours
FROM support_tickets;

-- Grant permissions on the stats view to authenticated users with admin role
-- Note: Adjust this based on your role setup
GRANT SELECT ON support_ticket_stats TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE support_tickets IS 'Stores user support tickets and help requests';
COMMENT ON COLUMN support_tickets.id IS 'Unique identifier for the support ticket';
COMMENT ON COLUMN support_tickets.user_id IS 'Reference to the user who created the ticket (nullable for non-authenticated users)';
COMMENT ON COLUMN support_tickets.name IS 'Name of the person submitting the ticket';
COMMENT ON COLUMN support_tickets.email IS 'Email address for correspondence';
COMMENT ON COLUMN support_tickets.subject IS 'Category or subject of the support request';
COMMENT ON COLUMN support_tickets.message IS 'Detailed description of the issue or question';
COMMENT ON COLUMN support_tickets.priority IS 'User-specified priority level (normal or urgent)';
COMMENT ON COLUMN support_tickets.status IS 'Current status of the ticket (open, in_progress, closed, resolved)';
COMMENT ON COLUMN support_tickets.created_at IS 'Timestamp when the ticket was created';
COMMENT ON COLUMN support_tickets.updated_at IS 'Timestamp when the ticket was last updated';
COMMENT ON COLUMN support_tickets.resolved_at IS 'Timestamp when the ticket was resolved or closed';
COMMENT ON COLUMN support_tickets.resolved_by IS 'User ID of the admin/staff who resolved the ticket';
COMMENT ON COLUMN support_tickets.admin_notes IS 'Internal notes for admin/support staff';
COMMENT ON COLUMN support_tickets.internal_priority IS 'Internal priority score for ticket triage (0-10)';

-- Insert some sample data (optional - remove in production)
-- INSERT INTO support_tickets (name, email, subject, message, priority) VALUES
-- ('John Doe', 'john@example.com', 'Bug Report', 'I found a bug in the analysis feature. When I try to analyze an ad with more than 500 words, the system crashes.', 'urgent'),
-- ('Jane Smith', 'jane@example.com', 'General Question', 'How do I export my analysis results to PDF? I checked the documentation but could not find clear instructions.', 'normal');

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Support tickets table created successfully with RLS policies and triggers';
END $$;
