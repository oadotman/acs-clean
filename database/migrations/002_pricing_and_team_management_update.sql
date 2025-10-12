-- ============================================================================
-- AdCopySurge Pricing Update and Team Management Fix
-- Updates pricing tiers: Free, Growth $39, Agency Standard $99, Agency Premium $199, Agency Unlimited $249
-- Fixes team management tables and permissions
-- ============================================================================

-- ============================================================================
-- STEP 1: Update subscription tiers and pricing
-- ============================================================================

-- First, let's update user_profiles to support new pricing structure
DO $$ 
BEGIN
    -- Add columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='subscription_tier') THEN
        ALTER TABLE user_profiles ADD COLUMN subscription_tier TEXT NOT NULL DEFAULT 'free';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='monthly_analysis_limit') THEN
        ALTER TABLE user_profiles ADD COLUMN monthly_analysis_limit INTEGER NOT NULL DEFAULT 10;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='monthly_analyses_used') THEN
        ALTER TABLE user_profiles ADD COLUMN monthly_analyses_used INTEGER NOT NULL DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='can_create_agency') THEN
        ALTER TABLE user_profiles ADD COLUMN can_create_agency BOOLEAN NOT NULL DEFAULT FALSE;
    END IF;
END $$;

-- Update subscription tier constraint
ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS chk_user_profiles_subscription_tier;
ALTER TABLE user_profiles ADD CONSTRAINT chk_user_profiles_subscription_tier 
CHECK (subscription_tier IN ('free', 'growth', 'agency_standard', 'agency_premium', 'agency_unlimited'));

-- Create pricing tiers configuration table
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

-- Insert pricing tiers
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
-- STEP 2: Create or update agencies table
-- ============================================================================

CREATE TABLE IF NOT EXISTS agencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    owner_user_id UUID NOT NULL,
    subscription_tier TEXT NOT NULL DEFAULT 'agency_standard',
    
    -- Agency limits based on subscription
    max_team_members INTEGER NOT NULL DEFAULT 10,
    monthly_analysis_limit INTEGER NOT NULL DEFAULT 500,
    
    -- Agency settings
    settings JSONB DEFAULT '{}',
    
    -- Status
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_agencies_owner FOREIGN KEY (owner_user_id) REFERENCES user_profiles(id) ON DELETE RESTRICT,
    CONSTRAINT chk_agencies_subscription_tier CHECK (subscription_tier IN ('agency_standard', 'agency_premium', 'agency_unlimited')),
    CONSTRAINT chk_agencies_status CHECK (status IN ('active', 'suspended', 'cancelled'))
);

-- ============================================================================
-- STEP 3: Create team management tables with correct names
-- ============================================================================

-- Team roles configuration
CREATE TABLE IF NOT EXISTS team_roles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    permissions TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Insert team roles
INSERT INTO team_roles (id, name, description, permissions) VALUES
('admin', 'Admin', 'Full access to all features and settings', ARRAY['*']),
('editor', 'Editor', 'Can create and edit analyses, limited settings access', 
 ARRAY['create_analysis', 'edit_analysis', 'view_analysis', 'manage_projects']),
('viewer', 'Viewer', 'Read-only access to analyses and reports', 
 ARRAY['view_analysis']),
('client', 'Client', 'View-only access to specific projects (external client)', 
 ARRAY['view_analysis', 'view_reports'])
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    permissions = EXCLUDED.permissions;

-- Agency team members table
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

-- Agency invitations table
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

-- Team member analytics table
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
-- STEP 4: Update projects table for agency support
-- ============================================================================

DO $$ 
BEGIN
    -- Add agency_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='agency_id') THEN
        ALTER TABLE projects ADD COLUMN agency_id UUID;
        ALTER TABLE projects ADD CONSTRAINT fk_projects_agency FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================================
-- STEP 5: Create indexes for performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_agencies_owner_user_id ON agencies(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_agencies_status ON agencies(status) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_agency_team_members_agency_id ON agency_team_members(agency_id);
CREATE INDEX IF NOT EXISTS idx_agency_team_members_user_id ON agency_team_members(user_id);
CREATE INDEX IF NOT EXISTS idx_agency_team_members_status ON agency_team_members(status) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_agency_invitations_agency_id ON agency_invitations(agency_id);
CREATE INDEX IF NOT EXISTS idx_agency_invitations_email ON agency_invitations(email);
CREATE INDEX IF NOT EXISTS idx_agency_invitations_token ON agency_invitations(invitation_token);
CREATE INDEX IF NOT EXISTS idx_agency_invitations_status ON agency_invitations(status) WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_projects_agency_id ON projects(agency_id) WHERE agency_id IS NOT NULL;

-- ============================================================================
-- STEP 6: Create updated_at triggers
-- ============================================================================

-- Create trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables
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

-- ============================================================================
-- STEP 7: Update existing users based on new pricing structure
-- ============================================================================

-- Update existing users to Growth tier if they have more than free limit
UPDATE user_profiles SET 
    subscription_tier = 'growth',
    monthly_analysis_limit = 100,
    can_create_agency = FALSE
WHERE subscription_tier NOT IN ('growth', 'agency_standard', 'agency_premium', 'agency_unlimited')
    AND monthly_analyses_used > 10;

-- Update analysis limits for existing users based on their tier
UPDATE user_profiles SET monthly_analysis_limit = (
    SELECT analysis_limit FROM subscription_tiers WHERE id = user_profiles.subscription_tier
) WHERE subscription_tier IN ('free', 'growth', 'agency_standard', 'agency_premium', 'agency_unlimited');

-- ============================================================================
-- STEP 8: Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE agencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_team_member_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_tiers ENABLE ROW LEVEL SECURITY;

-- Agencies policies
CREATE POLICY "Users can view their own agencies" ON agencies
    FOR SELECT USING (owner_user_id = auth.uid() OR id IN (
        SELECT agency_id FROM agency_team_members WHERE user_id = auth.uid() AND status = 'active'
    ));

CREATE POLICY "Users can create agencies if allowed" ON agencies
    FOR INSERT WITH CHECK (
        owner_user_id = auth.uid() AND
        EXISTS (SELECT 1 FROM user_profiles WHERE id = auth.uid() AND can_create_agency = TRUE)
    );

CREATE POLICY "Agency owners can update their agencies" ON agencies
    FOR UPDATE USING (owner_user_id = auth.uid());

-- Team members policies
CREATE POLICY "Team members can view their agency's members" ON agency_team_members
    FOR SELECT USING (
        agency_id IN (SELECT agency_id FROM agency_team_members WHERE user_id = auth.uid() AND status = 'active')
    );

CREATE POLICY "Agency owners and admins can manage team members" ON agency_team_members
    FOR ALL USING (
        agency_id IN (
            SELECT id FROM agencies WHERE owner_user_id = auth.uid()
            UNION
            SELECT agency_id FROM agency_team_members 
            WHERE user_id = auth.uid() AND role = 'admin' AND status = 'active'
        )
    );

-- Invitations policies
CREATE POLICY "Team can view their agency's invitations" ON agency_invitations
    FOR SELECT USING (
        agency_id IN (SELECT agency_id FROM agency_team_members WHERE user_id = auth.uid() AND status = 'active')
    );

CREATE POLICY "Agency owners and admins can manage invitations" ON agency_invitations
    FOR ALL USING (
        agency_id IN (
            SELECT id FROM agencies WHERE owner_user_id = auth.uid()
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

-- Subscription tiers are public read-only
CREATE POLICY "Everyone can view subscription tiers" ON subscription_tiers
    FOR SELECT USING (true);

COMMENT ON TABLE agencies IS 'Agency workspaces for team collaboration';
COMMENT ON TABLE agency_team_members IS 'Team members belonging to agencies';
COMMENT ON TABLE agency_invitations IS 'Pending invitations to join agencies';
COMMENT ON TABLE agency_team_member_analytics IS 'Usage analytics for team members';
COMMENT ON TABLE subscription_tiers IS 'Available subscription plans and pricing';