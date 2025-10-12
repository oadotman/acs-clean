-- Credit System Database Schema for AdCopySurge
-- Run this in your Supabase SQL Editor to set up the credit system

-- User Credits Table
CREATE TABLE IF NOT EXISTS user_credits (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  current_credits INTEGER NOT NULL DEFAULT 0,
  monthly_allowance INTEGER NOT NULL DEFAULT 0,
  bonus_credits INTEGER NOT NULL DEFAULT 0,
  total_used INTEGER NOT NULL DEFAULT 0,
  subscription_tier TEXT NOT NULL DEFAULT 'free',
  last_reset TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Credit Transactions Table (for history tracking)
CREATE TABLE IF NOT EXISTS credit_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  operation TEXT NOT NULL,
  amount INTEGER NOT NULL, -- Positive for additions, negative for deductions
  description TEXT,
  analysis_id UUID REFERENCES ad_analyses(id) ON DELETE SET NULL, -- Optional link to analysis
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_credits_user_id ON user_credits(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON credit_transactions(created_at);

-- Row Level Security (RLS) Policies
ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;

-- Users can only access their own credit data
CREATE POLICY "Users can view own credits" ON user_credits
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own credits" ON user_credits
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "System can insert credits" ON user_credits
  FOR INSERT WITH CHECK (true);

-- Credit transactions policies
CREATE POLICY "Users can view own transactions" ON credit_transactions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can insert transactions" ON credit_transactions
  FOR INSERT WITH CHECK (true);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at on user_credits
CREATE TRIGGER update_user_credits_updated_at 
  BEFORE UPDATE ON user_credits 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to initialize credits for new users
CREATE OR REPLACE FUNCTION initialize_user_credits()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_credits (
    user_id,
    current_credits,
    monthly_allowance,
    bonus_credits,
    subscription_tier
  ) VALUES (
    NEW.id,
    10, -- Free tier gets 10 credits
    10, -- Monthly allowance of 10
    0,  -- No bonus credits initially
    'free'
  );
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically create credit record for new users
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION initialize_user_credits();

-- Function to reset monthly credits (to be called by cron job)
CREATE OR REPLACE FUNCTION reset_monthly_credits()
RETURNS void AS $$
BEGIN
  -- Update all users' credits based on their subscription tier
  UPDATE user_credits 
  SET 
    current_credits = CASE 
      WHEN subscription_tier = 'free' THEN 10
      WHEN subscription_tier = 'growth' THEN 200 + LEAST(current_credits, 100) -- Rollover up to 100
      WHEN subscription_tier = 'agency_standard' THEN 1000 + LEAST(current_credits, 500) -- Rollover up to 500
      WHEN subscription_tier = 'agency_premium' THEN 2000 + LEAST(current_credits, 1000) -- Rollover up to 1000
      WHEN subscription_tier = 'agency_unlimited' THEN 999999
      ELSE 10
    END,
    monthly_allowance = CASE 
      WHEN subscription_tier = 'free' THEN 10
      WHEN subscription_tier = 'growth' THEN 200
      WHEN subscription_tier = 'agency_standard' THEN 1000
      WHEN subscription_tier = 'agency_premium' THEN 2000
      WHEN subscription_tier = 'agency_unlimited' THEN 999999
      ELSE 10
    END,
    last_reset = NOW(),
    updated_at = NOW();
    
  -- Log the reset transactions
  INSERT INTO credit_transactions (user_id, operation, amount, description)
  SELECT 
    user_id,
    'MONTHLY_RESET',
    current_credits,
    'Monthly credit reset for ' || subscription_tier || ' plan'
  FROM user_credits;
END;
$$ language 'plpgsql';

-- Example: Schedule monthly reset (you'll need to set up pg_cron extension)
-- SELECT cron.schedule('reset-monthly-credits', '0 0 1 * *', 'SELECT reset_monthly_credits();');

COMMENT ON TABLE user_credits IS 'Stores user credit balances and allowances';
COMMENT ON TABLE credit_transactions IS 'Tracks all credit additions and deductions for audit trail';
COMMENT ON FUNCTION initialize_user_credits() IS 'Automatically creates credit record when new user signs up';
COMMENT ON FUNCTION reset_monthly_credits() IS 'Resets monthly credits for all users (run monthly via cron)';

-- Sample data for testing (optional)
-- INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier) 
-- VALUES 
--   ('sample-user-id', 150, 200, 'growth'),
--   ('another-user-id', 800, 1000, 'agency_standard');