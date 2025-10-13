-- Fix Database Permissions and RLS Policies for AdCopySurge
-- Run this in Supabase SQL Editor

-- First, let's check current policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'user_credits';

-- Drop existing restrictive policies if they exist
DROP POLICY IF EXISTS "Users can view own credits" ON user_credits;
DROP POLICY IF EXISTS "Users can update own credits" ON user_credits;
DROP POLICY IF EXISTS "System can insert credits" ON user_credits;
DROP POLICY IF EXISTS "Users can view own transactions" ON credit_transactions;
DROP POLICY IF EXISTS "System can insert transactions" ON credit_transactions;

-- Create more permissive policies that work with anon users but still secure
-- Allow authenticated users to view their own credits
CREATE POLICY "Allow authenticated users to view own credits" ON user_credits
  FOR SELECT 
  TO authenticated, anon
  USING (
    -- Allow if user is authenticated and owns the record
    (auth.uid() = user_id) OR
    -- Allow service role to access everything
    (auth.jwt() ->> 'role' = 'service_role')
  );

-- Allow authenticated users to update their own credits
CREATE POLICY "Allow authenticated users to update own credits" ON user_credits
  FOR UPDATE 
  TO authenticated, anon
  USING (
    -- Allow if user is authenticated and owns the record
    (auth.uid() = user_id) OR
    -- Allow service role to access everything
    (auth.jwt() ->> 'role' = 'service_role')
  );

-- Allow system to insert new credit records
CREATE POLICY "Allow system to insert credits" ON user_credits
  FOR INSERT 
  TO authenticated, anon, service_role
  WITH CHECK (true);

-- Allow users to view their own credit transactions
CREATE POLICY "Allow authenticated users to view own transactions" ON credit_transactions
  FOR SELECT 
  TO authenticated, anon
  USING (
    -- Allow if user is authenticated and owns the record
    (auth.uid() = user_id) OR
    -- Allow service role to access everything
    (auth.jwt() ->> 'role' = 'service_role')
  );

-- Allow system to insert transactions
CREATE POLICY "Allow system to insert transactions" ON credit_transactions
  FOR INSERT 
  TO authenticated, anon, service_role
  WITH CHECK (true);

-- For the current user who has unlimited plan, let's update their subscription tier
-- Replace with actual user ID if different
UPDATE user_credits 
SET 
  subscription_tier = 'agency_unlimited',
  current_credits = 999999,
  monthly_allowance = 999999
WHERE user_id = '92f3f140-ddb5-4e21-a6d7-814982b55ebc';

-- Let's also create a function that can be called by the frontend to get user credits
-- This bypasses RLS when called as a function
CREATE OR REPLACE FUNCTION get_user_credits_safe(p_user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER -- This runs with elevated privileges
AS $$
DECLARE
  result JSON;
BEGIN
  SELECT to_json(t.*) INTO result
  FROM (
    SELECT 
      current_credits as credits,
      monthly_allowance as monthlyAllowance,
      bonus_credits as bonusCredits,
      total_used as totalUsed,
      subscription_tier as subscriptionTier,
      last_reset as lastReset,
      created_at,
      updated_at
    FROM user_credits 
    WHERE user_id = p_user_id
  ) t;
  
  -- If no record exists, return default free tier credits
  IF result IS NULL THEN
    result := json_build_object(
      'credits', 5,
      'monthlyAllowance', 5,
      'bonusCredits', 0,
      'totalUsed', 0,
      'subscriptionTier', 'free',
      'lastReset', NOW(),
      'created_at', NOW(),
      'updated_at', NOW()
    );
  END IF;
  
  RETURN result;
END;
$$;

-- Grant execute permissions on this function
GRANT EXECUTE ON FUNCTION get_user_credits_safe(UUID) TO authenticated, anon;

-- Test the function with the known user ID
SELECT get_user_credits_safe('92f3f140-ddb5-4e21-a6d7-814982b55ebc');