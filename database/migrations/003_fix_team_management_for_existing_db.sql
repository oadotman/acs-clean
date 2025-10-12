-- ============================================================================
-- AdCopySurge - Fix Team Management for Existing Database
-- This migration works with your current database structure
-- Updates pricing tiers and creates missing team management components
-- ============================================================================

-- ============================================================================
-- STEP 1: Update user_profiles for new pricing structure
-- ============================================================================

-- Add missing columns to user_profiles
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS full_name TEXT,
ADD COLUMN IF NOT EXISTS avatar_url TEXT,
ADD COLUMN IF NOT EXISTS monthly_analysis_limit INTEGER NOT NULL DEFAULT 10,
ADD COLUMN IF NOT EXISTS monthly_analyses_used INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS can_create_agency BOOLEAN NOT NULL DEFAULT FALSE;

-- Update subscription tier constraint to support new pricing
ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS chk_user_profiles_subscription_tier;
ALTER TABLE user_profiles ADD CONSTRAINT chk_user_profiles_subscription_tier 
CHECK (subscription_tier IN ('free', 'growth', 'agency_standard', 'agency_premium', 'agency_unlimited'));

-- ============================================================================
-- STEP 2: Create subscription tiers table
-- ============================================================================

CREATE TABLE IF NOT EXISTS subscription_tiers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price_monthly INTEGER NOT NULL, -- Price in cents
    price_yearly INTEGER, -- Price in cents (NULL for free)
    analysis_limit INTEGER NOT NULL,
    can_create_agency BOOLEAN NOT NULL DEFAULT FALSE,
    max_team_members INTEGER NOT NULL DEFAULT 1,
    features JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Insert new pricing tiers
INSERT INTO subscription_tiers (id, name, price_monthly, price_yearly, analysis_limit, can_create_agency, max_team_members, features) VALUES
('free', 'Free', 0, NULL, 10, FALSE, 1, 
 '{"white_label": false, "priority_support": false, "api_access": false, "bulk_analysis": false}'),
 
('growth', 'Growth', 3900, 39000, 100, FALSE, 1, 
 '{"white_label": false, "priority_support": true, "api_access": false, "bulk_analysis": true}'),
 
('agency_standard', 'Agency Standard', 9900, 99000, 500, TRUE, 10, 
 '{"white_label": true, "priority_support": true, "api_access": true, "bulk_analysis": true, "team_management": true}'),
 
('agency_premium', 'Agency Premium', 19900, 199000, 2000, TRUE, 25, 
 '{"white_label": true, "priority_support": true, "api_access": true, "bulk_analysis": true, "team_management": true, "advanced_analytics": true}'),
 
('agency_unlimited', 'Agency Unlimited', 24900, 249000, 999999, TRUE, 100, 
 '{"white_label": true, "priority_support": true, "api_access": true, "bulk_analysis": true, "team_management": true, "advanced_analytics": true, "unlimited_analyses": true}')

ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    price_monthly = EXCLUDED.price_monthly,
    price_yearly = EXCLUDED.price_yearly,
    analysis_limit = EXCLUDED.analysis_limit,
    can_create_agency = EXCLUDED.can_create_agency,
    max_team_members = EXCLUDED.max_team_members,
    features = EXCLUDED.features,
    updated_at = NOW();

-- ============================================================================
-- STEP 3: Update existing agencies table
-- ============================================================================

-- Add missing columns to agencies table  
ALTER TABLE agencies 
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS subscription_tier TEXT NOT NULL DEFAULT 'agency_standard',
ADD COLUMN IF NOT EXISTS max_team_members INTEGER NOT NULL DEFAULT 10,
ADD COLUMN IF NOT EXISTS monthly_analysis_limit INTEGER NOT NULL DEFAULT 500,
ADD COLUMN IF NOT EXISTS settings JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active',
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Add constraints to agencies table
ALTER TABLE agencies DROP CONSTRAINT IF EXISTS chk_agencies_subscription_tier;
ALTER TABLE agencies ADD CONSTRAINT chk_agencies_subscription_tier 
CHECK (subscription_tier IN ('agency_standard', 'agency_premium', 'agency_unlimited'));

ALTER TABLE agencies DROP CONSTRAINT IF EXISTS chk_agencies_status;
ALTER TABLE agencies ADD CONSTRAINT chk_agencies_status 
CHECK (status IN ('active', 'suspended', 'cancelled'));

-- ============================================================================
-- STEP 4: Create new team management tables with correct names
-- ============================================================================

-- Create agency_team_members table (using your existing team_members as reference)
CREATE TABLE IF NOT EXISTS agency_team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    status TEXT NOT NULL DEFAULT 'pending',
    invited_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_agency_team_members_agency FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE,
    CONSTRAINT fk_agency_team_members_user FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_agency_team_members_role FOREIGN KEY (role) REFERENCES team_roles(id),
    CONSTRAINT fk_agency_team_members_invited_by FOREIGN KEY (invited_by) REFERENCES user_profiles(id) ON DELETE SET NULL,
    CONSTRAINT chk_agency_team_members_status CHECK (status IN ('pending', 'active', 'suspended', 'removed')),
    
    -- One user per agency
    UNIQUE(user_id)
);

-- Create agency_invitations table (using your existing team_invitations as reference)
CREATE TABLE IF NOT EXISTS agency_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    status TEXT NOT NULL DEFAULT 'pending',
    invitation_token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
    invited_by UUID NOT NULL,
    project_access TEXT[] DEFAULT ARRAY[]::TEXT[],
    client_access TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_agency_invitations_agency FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE,
    CONSTRAINT fk_agency_invitations_role FOREIGN KEY (role) REFERENCES team_roles(id),
    CONSTRAINT fk_agency_invitations_invited_by FOREIGN KEY (invited_by) REFERENCES user_profiles(id) ON DELETE CASCADE,
    CONSTRAINT chk_agency_invitations_status CHECK (status IN ('pending', 'accepted', 'expired', 'cancelled'))
);

-- Create team member analytics table
CREATE TABLE IF NOT EXISTS agency_team_member_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_member_id UUID NOT NULL,
    analyses_count INTEGER NOT NULL DEFAULT 0,
    credits_used INTEGER NOT NULL DEFAULT 0,
    last_active_at TIMESTAMPTZ,
    month_year TEXT NOT NULL DEFAULT TO_CHAR(NOW(), 'YYYY-MM'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_analytics_team_member FOREIGN KEY (team_member_id) REFERENCES agency_team_members(id) ON DELETE CASCADE,
    UNIQUE(team_member_id, month_year)
);

-- ============================================================================
-- STEP 5: Migrate data from old tables to new tables (if any exists)
-- ============================================================================

-- Copy data from team_members to agency_team_members
INSERT INTO agency_team_members (agency_id, user_id, role, status, invited_by, created_at, updated_at)
SELECT 
    agency_id, 
    user_id, 
    role_id as role, 
    status,
    invited_by,
    COALESCE(created_at, NOW()) as created_at,
    COALESCE(updated_at, NOW()) as updated_at
FROM team_members
WHERE agency_id IS NOT NULL
ON CONFLICT (user_id) DO NOTHING; -- Skip if user already exists

-- Copy data from team_invitations to agency_invitations  
INSERT INTO agency_invitations (agency_id, email, role, status, invitation_token, expires_at, invited_by, created_at, updated_at)
SELECT 
    agency_id,
    email,
    role_id as role,
    status,
    invitation_token,
    expires_at,
    invited_by,
    COALESCE(created_at, NOW()) as created_at,
    COALESCE(updated_at, NOW()) as updated_at
FROM team_invitations
WHERE agency_id IS NOT NULL
ON CONFLICT (invitation_token) DO NOTHING; -- Skip if invitation already exists

-- ============================================================================
-- STEP 6: Create indexes for performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_agencies_owner_user_id ON agencies(owner_id);
CREATE INDEX IF NOT EXISTS idx_agencies_status ON agencies(status) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_agency_team_members_agency_id ON agency_team_members(agency_id);
CREATE INDEX IF NOT EXISTS idx_agency_team_members_user_id ON agency_team_members(user_id);
CREATE INDEX IF NOT EXISTS idx_agency_team_members_status ON agency_team_members(status) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_agency_invitations_agency_id ON agency_invitations(agency_id);
CREATE INDEX IF NOT EXISTS idx_agency_invitations_email ON agency_invitations(email);
CREATE INDEX IF NOT EXISTS idx_agency_invitations_token ON agency_invitations(invitation_token);
CREATE INDEX IF NOT EXISTS idx_agency_invitations_status ON agency_invitations(status) WHERE status = 'pending';

-- ============================================================================
-- STEP 7: Create triggers for updated_at
-- ============================================================================

-- Create trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DO $$
BEGIN
    -- Drop existing triggers if they exist
    DROP TRIGGER IF EXISTS update_agencies_updated_at ON agencies;
    DROP TRIGGER IF EXISTS update_agency_team_members_updated_at ON agency_team_members;
    DROP TRIGGER IF EXISTS update_agency_invitations_updated_at ON agency_invitations;
    DROP TRIGGER IF EXISTS update_agency_team_member_analytics_updated_at ON agency_team_member_analytics;
    DROP TRIGGER IF EXISTS update_subscription_tiers_updated_at ON subscription_tiers;

    -- Create new triggers
    CREATE TRIGGER update_agencies_updated_at
        BEFORE UPDATE ON agencies
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_agency_team_members_updated_at
        BEFORE UPDATE ON agency_team_members
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_agency_invitations_updated_at
        BEFORE UPDATE ON agency_invitations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_agency_team_member_analytics_updated_at
        BEFORE UPDATE ON agency_team_member_analytics
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_subscription_tiers_updated_at
        BEFORE UPDATE ON subscription_tiers
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
END $$;

-- ============================================================================
-- STEP 8: Update existing users based on new pricing structure
-- ============================================================================

-- Set analysis limits based on current subscription tiers
UPDATE user_profiles SET 
    monthly_analysis_limit = CASE 
        WHEN subscription_tier = 'free' THEN 10
        WHEN subscription_tier = 'growth' THEN 100
        WHEN subscription_tier = 'agency_standard' THEN 500
        WHEN subscription_tier = 'agency_premium' THEN 2000
        WHEN subscription_tier = 'agency_unlimited' THEN 999999
        ELSE 10
    END,
    can_create_agency = CASE 
        WHEN subscription_tier IN ('agency_standard', 'agency_premium', 'agency_unlimited') THEN TRUE
        ELSE FALSE
    END;

-- ============================================================================
-- STEP 9: Enable Row Level Security (RLS)
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE subscription_tiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_team_member_analytics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies

-- Subscription tiers are public read-only
CREATE POLICY "Everyone can view subscription tiers" ON subscription_tiers
    FOR SELECT USING (true);

-- Agency team members policies
CREATE POLICY "Team members can view their agency's members" ON agency_team_members
    FOR SELECT USING (
        agency_id IN (SELECT agency_id FROM agency_team_members WHERE user_id = auth.uid() AND status = 'active')
    );

CREATE POLICY "Agency owners and admins can manage team members" ON agency_team_members
    FOR ALL USING (
        agency_id IN (
            SELECT id FROM agencies WHERE owner_id = auth.uid()
            UNION
            SELECT agency_id FROM agency_team_members 
            WHERE user_id = auth.uid() AND role = 'admin' AND status = 'active'
        )
    );

-- Agency invitations policies  
CREATE POLICY "Team can view their agency's invitations" ON agency_invitations
    FOR SELECT USING (
        agency_id IN (SELECT agency_id FROM agency_team_members WHERE user_id = auth.uid() AND status = 'active')
    );

CREATE POLICY "Agency owners and admins can manage invitations" ON agency_invitations
    FOR ALL USING (
        agency_id IN (
            SELECT id FROM agencies WHERE owner_id = auth.uid()
            UNION
            SELECT agency_id FROM agency_team_members 
            WHERE user_id = auth.uid() AND role = 'admin' AND status = 'active'
        )
    );

-- Analytics policies
CREATE POLICY "Team can view their agency's analytics" ON agency_team_member_analytics
    FOR SELECT USING (
        team_member_id IN (
            SELECT id FROM agency_team_members 
            WHERE agency_id IN (
                SELECT agency_id FROM agency_team_members WHERE user_id = auth.uid() AND status = 'active'
            )
        )
    );

-- Add comments
COMMENT ON TABLE subscription_tiers IS 'Available subscription plans and pricing';
COMMENT ON TABLE agency_team_members IS 'Team members belonging to agencies';
COMMENT ON TABLE agency_invitations IS 'Pending invitations to join agencies';
COMMENT ON TABLE agency_team_member_analytics IS 'Usage analytics for team members';

-- ============================================================================
-- FINAL STEP: Update your current user to agency tier (UNCOMMENT TO RUN)
-- ============================================================================

-- Uncomment and run this to upgrade your user to agency tier:
-- UPDATE user_profiles SET 
--     subscription_tier = 'agency_standard',
--     can_create_agency = TRUE,
--     monthly_analysis_limit = 500
-- WHERE id = auth.uid();