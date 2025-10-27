-- ============================================================================
-- Enable Supabase Real-time for instant credit updates
-- Run this in Supabase SQL Editor
-- ============================================================================

-- Enable real-time replication for user_credits table
-- This allows the frontend to receive instant updates when credits change

ALTER PUBLICATION supabase_realtime ADD TABLE user_credits;

-- Verify real-time is enabled
SELECT 
    tablename,
    'Real-time enabled' as status
FROM pg_publication_tables
WHERE pubname = 'supabase_realtime'
  AND tablename = 'user_credits';

-- ============================================================================
-- INSTRUCTIONS
-- ============================================================================
-- After running this:
-- 1. Credits will update instantly in the UI when consumed
-- 2. No more 60-second delays
-- 3. Multiple tabs will stay in sync
-- 4. Check browser console for: "🔔 Setting up real-time credit subscription"
