-- ============================================================================
-- AdCopySurge Team Management System - Complete Migration
-- This extends the existing database with comprehensive team management
-- Maintains backward compatibility with existing user_profiles structure
-- ============================================================================

-- ============================================================================
-- STEP 1: Extend user_profiles for agency support
-- ============================================================================

-- Add agency-related columns to existing user_profiles
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS company_name TEXT;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS is_agency_owner BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS agency_id UUID;

-- Add comments for new columns
COMMENT ON COLUMN user_profiles.company_name IS 'Optional company/agency name';
COMMENT ON COLUMN user_profiles.is_agency_owner IS 'True if user owns an agency and can manage team members';
COMMENT ON COLUMN user_profiles.agency_id IS 'ID of agency this user belongs to (NULL for individual users)';

-- ============================================================================
-- STEP 2: Create agencies table
-- ============================================================================

CREATE TABLE IF NOT EXISTS agencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  owner_id UUID NOT NULL,
  subscription_tier TEXT NOT NULL DEFAULT 'agency', -- agency | enterprise
  max_team_members INTEGER NOT NULL DEFAULT 10,
  max_projects INTEGER NOT NULL DEFAULT 50,
  monthly_analyses_limit INTEGER NOT NULL DEFAULT 1000,
  
  -- Agency settings
  domain TEXT, -- For white-label (future feature)
  branding_settings JSONB DEFAULT '{}', -- Logo, colors, etc.
  billing_settings JSONB DEFAULT '{}', -- Billing contact, payment info
  
  -- Status and timestamps
  status TEXT NOT NULL DEFAULT 'active', -- active | suspended | cancelled
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT fk_agencies_owner FOREIGN KEY (owner_id) REFERENCES user_profiles(id) ON DELETE RESTRICT,
  CONSTRAINT chk_agencies_subscription_tier CHECK (subscription_tier IN ('agency', 'enterprise')),
  CONSTRAINT chk_agencies_status CHECK (status IN ('active', 'suspended', 'cancelled'))
);

COMMENT ON TABLE agencies IS 'Agency accounts that can have multiple team members';
COMMENT ON COLUMN agencies.max_team_members IS 'Maximum number of team members allowed';
COMMENT ON COLUMN agencies.monthly_analyses_limit IS 'Monthly analysis limit for the entire agency';

-- ============================================================================
-- STEP 3: Create team roles and permissions
-- ============================================================================

CREATE TABLE IF NOT EXISTS team_roles (
  id TEXT PRIMARY KEY, -- admin, editor, viewer, client
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  permissions TEXT[] NOT NULL, -- Array of permission strings
  is_system_role BOOLEAN NOT NULL DEFAULT TRUE, -- System vs custom roles
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE team_roles IS 'Available team member roles with permissions';
COMMENT ON COLUMN team_roles.permissions IS 'Array of permission strings like ["create_analysis", "view_all_projects"]';

-- Insert default roles
INSERT INTO team_roles (id, name, description, permissions) VALUES
  ('admin', 'Administrator', 'Full access to all agency features and settings', 
   ARRAY['*']), -- Wildcard means all permissions
  
  ('editor', 'Editor', 'Can create and edit analyses, manage assigned projects', 
   ARRAY['create_analysis', 'edit_analysis', 'view_analysis', 'manage_assigned_projects', 'create_project']),
   
  ('viewer', 'Viewer', 'Read-only access to assigned analyses and projects', 
   ARRAY['view_analysis', 'view_assigned_projects']),
   
  ('client', 'Client', 'External client with limited access to specific projects', 
   ARRAY['view_analysis', 'view_assigned_projects', 'export_reports'])
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  permissions = EXCLUDED.permissions;

-- ============================================================================
-- STEP 4: Create team members table
-- ============================================================================

CREATE TABLE IF NOT EXISTS team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agency_id UUID NOT NULL,
  user_id UUID NOT NULL, -- Links to user_profiles.id
  role_id TEXT NOT NULL DEFAULT 'viewer',
  
  -- Member status and info
  status TEXT NOT NULL DEFAULT 'pending', -- pending | active | suspended | removed
  invited_by UUID, -- Who invited this member
  invited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  joined_at TIMESTAMPTZ, -- When they accepted the invitation
  
  -- Activity tracking
  last_login_at TIMESTAMPTZ,
  analyses_this_month INTEGER NOT NULL DEFAULT 0,
  total_analyses INTEGER NOT NULL DEFAULT 0,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT fk_team_members_agency FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE,
  CONSTRAINT fk_team_members_user FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
  CONSTRAINT fk_team_members_role FOREIGN KEY (role_id) REFERENCES team_roles(id),
  CONSTRAINT fk_team_members_invited_by FOREIGN KEY (invited_by) REFERENCES user_profiles(id) ON DELETE SET NULL,
  CONSTRAINT chk_team_members_status CHECK (status IN ('pending', 'active', 'suspended', 'removed')),
  
  -- Unique constraint: user can only be in one agency at a time
  UNIQUE(user_id)
);

COMMENT ON TABLE team_members IS 'Team members belonging to agencies with roles and permissions';
COMMENT ON COLUMN team_members.status IS 'pending (invited), active (joined), suspended (temporarily disabled), removed (left/kicked)';
COMMENT ON COLUMN team_members.analyses_this_month IS 'Number of analyses created by this member this month';

-- ============================================================================
-- STEP 5: Create team invitations table
-- ============================================================================

CREATE TABLE IF NOT EXISTS team_invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agency_id UUID NOT NULL,
  email TEXT NOT NULL,
  role_id TEXT NOT NULL DEFAULT 'viewer',
  invited_by UUID NOT NULL,
  
  -- Invitation details
  invitation_token TEXT NOT NULL UNIQUE, -- Secure token for email links
  message TEXT, -- Optional personal message
  
  -- Status and expiry
  status TEXT NOT NULL DEFAULT 'pending', -- pending | accepted | expired | cancelled
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
  accepted_at TIMESTAMPTZ,
  accepted_by UUID, -- The user_profile.id that accepted (may be different from invited email)
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT fk_team_invitations_agency FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE,
  CONSTRAINT fk_team_invitations_role FOREIGN KEY (role_id) REFERENCES team_roles(id),
  CONSTRAINT fk_team_invitations_invited_by FOREIGN KEY (invited_by) REFERENCES user_profiles(id) ON DELETE CASCADE,
  CONSTRAINT fk_team_invitations_accepted_by FOREIGN KEY (accepted_by) REFERENCES user_profiles(id) ON DELETE SET NULL,
  CONSTRAINT chk_team_invitations_status CHECK (status IN ('pending', 'accepted', 'expired', 'cancelled'))
);

COMMENT ON TABLE team_invitations IS 'Pending invitations to join agency teams';
COMMENT ON COLUMN team_invitations.invitation_token IS 'Secure token used in email invitation links';

-- ============================================================================
-- STEP 6: Extend projects table for team access control
-- ============================================================================

-- Add team access columns to existing projects table
ALTER TABLE projects ADD COLUMN IF NOT EXISTS agency_id UUID;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS is_shared BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS shared_with_roles TEXT[] DEFAULT ARRAY['admin', 'editor'];

-- Add foreign key constraint for agency_id
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'fk_projects_agency' AND table_name = 'projects'
  ) THEN
    ALTER TABLE projects 
    ADD CONSTRAINT fk_projects_agency 
    FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE SET NULL;
  END IF;
END $$;

-- Add comments for new columns
COMMENT ON COLUMN projects.agency_id IS 'Agency that owns this project (NULL for individual users)';
COMMENT ON COLUMN projects.is_shared IS 'Whether this project is shared with team members';
COMMENT ON COLUMN projects.shared_with_roles IS 'Array of role IDs that can access this project';

-- ============================================================================
-- STEP 7: Create project access permissions table (for fine-grained control)
-- ============================================================================

CREATE TABLE IF NOT EXISTS project_team_access (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL,
  team_member_id UUID NOT NULL,
  access_level TEXT NOT NULL DEFAULT 'view', -- view | edit | manage
  granted_by UUID NOT NULL,
  granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT fk_project_access_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  CONSTRAINT fk_project_access_member FOREIGN KEY (team_member_id) REFERENCES team_members(id) ON DELETE CASCADE,
  CONSTRAINT fk_project_access_granted_by FOREIGN KEY (granted_by) REFERENCES user_profiles(id) ON DELETE CASCADE,
  CONSTRAINT chk_project_access_level CHECK (access_level IN ('view', 'edit', 'manage')),
  
  -- Unique constraint: one access level per member per project
  UNIQUE(project_id, team_member_id)
);

COMMENT ON TABLE project_team_access IS 'Specific project access permissions for team members';
COMMENT ON COLUMN project_team_access.access_level IS 'view (read-only), edit (modify content), manage (full control)';

-- ============================================================================
-- STEP 8: Create indexes for performance
-- ============================================================================

-- Agencies indexes
CREATE INDEX IF NOT EXISTS idx_agencies_owner_id ON agencies(owner_id);
CREATE INDEX IF NOT EXISTS idx_agencies_status ON agencies(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_agencies_created_at ON agencies(created_at DESC);

-- Team members indexes
CREATE INDEX IF NOT EXISTS idx_team_members_agency_id ON team_members(agency_id);
CREATE INDEX IF NOT EXISTS idx_team_members_user_id ON team_members(user_id);
CREATE INDEX IF NOT EXISTS idx_team_members_status ON team_members(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_team_members_role_id ON team_members(role_id);

-- Team invitations indexes
CREATE INDEX IF NOT EXISTS idx_team_invitations_agency_id ON team_invitations(agency_id);
CREATE INDEX IF NOT EXISTS idx_team_invitations_email ON team_invitations(email);
CREATE INDEX IF NOT EXISTS idx_team_invitations_token ON team_invitations(invitation_token);
CREATE INDEX IF NOT EXISTS idx_team_invitations_status ON team_invitations(status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_team_invitations_expires_at ON team_invitations(expires_at);

-- Project access indexes
CREATE INDEX IF NOT EXISTS idx_projects_agency_id ON projects(agency_id) WHERE agency_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_project_team_access_project_id ON project_team_access(project_id);
CREATE INDEX IF NOT EXISTS idx_project_team_access_member_id ON project_team_access(team_member_id);

-- User profiles indexes for agency queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_agency_id ON user_profiles(agency_id) WHERE agency_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_profiles_is_agency_owner ON user_profiles(is_agency_owner) WHERE is_agency_owner = TRUE;

-- ============================================================================
-- STEP 9: Add updated_at triggers
-- ============================================================================

-- Apply updated_at triggers to new tables
CREATE TRIGGER update_agencies_updated_at
  BEFORE UPDATE ON agencies
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_members_updated_at
  BEFORE UPDATE ON team_members
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_invitations_updated_at
  BEFORE UPDATE ON team_invitations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- STEP 10: Create utility functions for team management
-- ============================================================================

-- Function to check if a user has permission for a specific action
CREATE OR REPLACE FUNCTION user_has_permission(
  p_user_id UUID,
  p_permission TEXT,
  p_project_id UUID DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
  user_permissions TEXT[];
  is_agency_member BOOLEAN;
  member_role TEXT;
BEGIN
  -- Check if user is an individual user (not in agency)
  SELECT agency_id IS NULL INTO is_agency_member
  FROM user_profiles
  WHERE id = p_user_id;
  
  -- Individual users have full permissions on their own content
  IF is_agency_member THEN
    RETURN TRUE;
  END IF;
  
  -- Get user's role permissions in their agency
  SELECT tr.permissions INTO user_permissions
  FROM team_members tm
  JOIN team_roles tr ON tm.role_id = tr.id
  WHERE tm.user_id = p_user_id AND tm.status = 'active';
  
  -- If no permissions found, deny access
  IF user_permissions IS NULL THEN
    RETURN FALSE;
  END IF;
  
  -- Check for wildcard permission (admin)
  IF '*' = ANY(user_permissions) THEN
    RETURN TRUE;
  END IF;
  
  -- Check specific permission
  IF p_permission = ANY(user_permissions) THEN
    -- For project-specific permissions, check project access
    IF p_project_id IS NOT NULL AND p_permission LIKE '%project%' THEN
      RETURN EXISTS (
        SELECT 1 FROM project_team_access pta
        JOIN team_members tm ON pta.team_member_id = tm.id
        WHERE tm.user_id = p_user_id 
          AND pta.project_id = p_project_id
          AND tm.status = 'active'
      );
    END IF;
    
    RETURN TRUE;
  END IF;
  
  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's agency info
CREATE OR REPLACE FUNCTION get_user_agency_info(p_user_id UUID)
RETURNS TABLE(
  agency_id UUID,
  agency_name TEXT,
  role_id TEXT,
  role_name TEXT,
  status TEXT,
  is_owner BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    a.id as agency_id,
    a.name as agency_name,
    tm.role_id,
    tr.name as role_name,
    tm.status,
    up.is_agency_owner as is_owner
  FROM user_profiles up
  LEFT JOIN agencies a ON up.agency_id = a.id
  LEFT JOIN team_members tm ON tm.user_id = up.id AND tm.agency_id = a.id
  LEFT JOIN team_roles tr ON tm.role_id = tr.id
  WHERE up.id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create agency and set owner
CREATE OR REPLACE FUNCTION create_agency(
  p_owner_id UUID,
  p_agency_name TEXT,
  p_subscription_tier TEXT DEFAULT 'agency'
) RETURNS UUID AS $$
DECLARE
  agency_uuid UUID;
BEGIN
  -- Create the agency
  INSERT INTO agencies (owner_id, name, subscription_tier)
  VALUES (p_owner_id, p_agency_name, p_subscription_tier)
  RETURNING id INTO agency_uuid;
  
  -- Update owner's profile
  UPDATE user_profiles SET
    agency_id = agency_uuid,
    is_agency_owner = TRUE,
    subscription_tier = p_subscription_tier,
    updated_at = NOW()
  WHERE id = p_owner_id;
  
  -- Add owner as admin team member
  INSERT INTO team_members (agency_id, user_id, role_id, status, joined_at)
  VALUES (agency_uuid, p_owner_id, 'admin', 'active', NOW());
  
  RETURN agency_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to invite team member
CREATE OR REPLACE FUNCTION invite_team_member(
  p_agency_id UUID,
  p_email TEXT,
  p_role_id TEXT,
  p_invited_by UUID,
  p_message TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
  invitation_uuid UUID;
  invitation_token TEXT;
BEGIN
  -- Generate secure token
  invitation_token := encode(gen_random_bytes(32), 'base64');
  
  -- Create invitation
  INSERT INTO team_invitations (
    agency_id, email, role_id, invited_by, invitation_token, message
  ) VALUES (
    p_agency_id, p_email, p_role_id, p_invited_by, invitation_token, p_message
  ) RETURNING id INTO invitation_uuid;
  
  RETURN invitation_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to accept invitation
CREATE OR REPLACE FUNCTION accept_team_invitation(
  p_invitation_token TEXT,
  p_user_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
  invitation_record team_invitations%ROWTYPE;
BEGIN
  -- Get invitation details
  SELECT * INTO invitation_record
  FROM team_invitations
  WHERE invitation_token = p_invitation_token
    AND status = 'pending'
    AND expires_at > NOW();
  
  -- Check if invitation exists and is valid
  IF NOT FOUND THEN
    RETURN FALSE;
  END IF;
  
  -- Update invitation status
  UPDATE team_invitations SET
    status = 'accepted',
    accepted_at = NOW(),
    accepted_by = p_user_id,
    updated_at = NOW()
  WHERE id = invitation_record.id;
  
  -- Update user profile
  UPDATE user_profiles SET
    agency_id = invitation_record.agency_id,
    updated_at = NOW()
  WHERE id = p_user_id;
  
  -- Add team member
  INSERT INTO team_members (agency_id, user_id, role_id, status, invited_by, joined_at)
  VALUES (
    invitation_record.agency_id,
    p_user_id,
    invitation_record.role_id,
    'active',
    invitation_record.invited_by,
    NOW()
  );
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- STEP 11: Grant permissions
-- ============================================================================

-- Grant permissions to new tables
GRANT ALL ON agencies TO anon, authenticated, service_role;
GRANT ALL ON team_roles TO anon, authenticated, service_role;
GRANT ALL ON team_members TO anon, authenticated, service_role;
GRANT ALL ON team_invitations TO anon, authenticated, service_role;
GRANT ALL ON project_team_access TO anon, authenticated, service_role;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION user_has_permission(UUID, TEXT, UUID) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_user_agency_info(UUID) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION create_agency(UUID, TEXT, TEXT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION invite_team_member(UUID, TEXT, TEXT, UUID, TEXT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION accept_team_invitation(TEXT, UUID) TO anon, authenticated, service_role;

-- ============================================================================
-- STEP 12: Disable RLS (consistent with existing setup)
-- ============================================================================

ALTER TABLE agencies DISABLE ROW LEVEL SECURITY;
ALTER TABLE team_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE team_members DISABLE ROW LEVEL SECURITY;
ALTER TABLE team_invitations DISABLE ROW LEVEL SECURITY;
ALTER TABLE project_team_access DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- STEP 13: Verification queries
-- ============================================================================

-- Check new tables exist
SELECT 
  table_name,
  (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_name IN ('agencies', 'team_roles', 'team_members', 'team_invitations', 'project_team_access')
ORDER BY table_name;

-- Check foreign key relationships
SELECT
  tc.table_name,
  tc.constraint_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name IN ('agencies', 'team_members', 'team_invitations', 'project_team_access')
ORDER BY tc.table_name, tc.constraint_name;

-- Check team roles were inserted
SELECT id, name, array_length(permissions, 1) as permission_count
FROM team_roles
ORDER BY id;

-- Summary
SELECT 
  '✅ Team Management Setup Complete!' as status,
  'Tables: agencies, team_roles, team_members, team_invitations, project_team_access created with full functionality' as details;