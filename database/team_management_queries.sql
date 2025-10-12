-- ============================================================================
-- Team Management End-to-End Queries for AdCopySurge
-- Complete set of queries for all team management operations
-- ============================================================================

-- ============================================================================
-- 1. AGENCY MANAGEMENT QUERIES
-- ============================================================================

-- Create new agency (converts individual user to agency owner)
-- Usage: Replace p_owner_id with actual user UUID and p_agency_name with desired name
SELECT create_agency(
  '00000000-0000-0000-0000-000000000000'::UUID, -- Replace with actual user ID
  'My Digital Agency', 
  'agency' -- or 'enterprise'
);

-- Get agency details by owner
SELECT 
  a.id,
  a.name,
  a.subscription_tier,
  a.max_team_members,
  a.max_projects,
  a.monthly_analyses_limit,
  a.status,
  a.created_at,
  -- Count current team members
  (SELECT COUNT(*) FROM team_members tm WHERE tm.agency_id = a.id AND tm.status = 'active') as current_team_size,
  -- Count current projects
  (SELECT COUNT(*) FROM projects p WHERE p.agency_id = a.id) as current_projects,
  -- Monthly analysis usage
  (SELECT COALESCE(SUM(tm.analyses_this_month), 0) FROM team_members tm WHERE tm.agency_id = a.id) as monthly_analyses_used
FROM agencies a
WHERE a.owner_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual user ID
  AND a.status = 'active';

-- Get agency by ID
SELECT 
  a.*,
  up.email as owner_email,
  up.company_name
FROM agencies a
JOIN user_profiles up ON a.owner_id = up.id
WHERE a.id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual agency ID

-- Update agency settings
UPDATE agencies SET
  name = 'Updated Agency Name',
  max_team_members = 15,
  branding_settings = '{"logo": "url", "primary_color": "#2563eb"}',
  updated_at = NOW()
WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual agency ID
  AND owner_id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual owner ID

-- ============================================================================
-- 2. TEAM MEMBER QUERIES
-- ============================================================================

-- Get all team members for an agency (for team management dashboard)
SELECT 
  tm.id,
  tm.user_id,
  up.email,
  up.company_name as member_company,
  COALESCE(up.email, 'Pending Invitation') as display_name,
  tm.role_id,
  tr.name as role_name,
  tr.description as role_description,
  tm.status,
  tm.invited_at,
  tm.joined_at,
  tm.last_login_at,
  tm.analyses_this_month,
  tm.total_analyses,
  inviter.email as invited_by_email,
  -- Activity metrics
  CASE 
    WHEN tm.last_login_at > NOW() - INTERVAL '24 hours' THEN 'Today'
    WHEN tm.last_login_at > NOW() - INTERVAL '7 days' THEN 'This Week'
    WHEN tm.last_login_at > NOW() - INTERVAL '30 days' THEN 'This Month'
    WHEN tm.last_login_at IS NULL THEN 'Never'
    ELSE 'Inactive'
  END as activity_status,
  -- Project access count
  (SELECT COUNT(DISTINCT pta.project_id) 
   FROM project_team_access pta 
   WHERE pta.team_member_id = tm.id) as accessible_projects_count
FROM team_members tm
JOIN team_roles tr ON tm.role_id = tr.id
LEFT JOIN user_profiles up ON tm.user_id = up.id
LEFT JOIN user_profiles inviter ON tm.invited_by = inviter.id
WHERE tm.agency_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual agency ID
  AND tm.status IN ('active', 'pending', 'suspended')
ORDER BY 
  CASE tm.status 
    WHEN 'active' THEN 1 
    WHEN 'pending' THEN 2 
    WHEN 'suspended' THEN 3 
  END,
  tm.joined_at DESC NULLS LAST;

-- Get team member details by user ID
SELECT 
  tm.*,
  tr.name as role_name,
  tr.permissions,
  a.name as agency_name,
  -- Check if user is agency owner
  up.is_agency_owner,
  -- Get project access summary
  array_agg(DISTINCT p.name) FILTER (WHERE p.name IS NOT NULL) as accessible_projects
FROM team_members tm
JOIN team_roles tr ON tm.role_id = tr.id
JOIN agencies a ON tm.agency_id = a.id
JOIN user_profiles up ON tm.user_id = up.id
LEFT JOIN project_team_access pta ON tm.id = pta.team_member_id
LEFT JOIN projects p ON pta.project_id = p.id
WHERE tm.user_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual user ID
GROUP BY tm.id, tr.name, tr.permissions, a.name, up.is_agency_owner;

-- Update team member role
UPDATE team_members SET
  role_id = 'editor', -- or 'admin', 'viewer', 'client'
  updated_at = NOW()
WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual team member ID
  AND agency_id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual agency ID

-- Suspend/Activate team member
UPDATE team_members SET
  status = 'suspended', -- or 'active'
  updated_at = NOW()
WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual team member ID
  AND agency_id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual agency ID

-- Remove team member (soft delete)
UPDATE team_members SET
  status = 'removed',
  updated_at = NOW()
WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual team member ID
  AND agency_id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual agency ID

-- Also update user profile to remove agency association
UPDATE user_profiles SET
  agency_id = NULL,
  updated_at = NOW()
WHERE id = (
  SELECT user_id FROM team_members 
  WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual team member ID
);

-- ============================================================================
-- 3. TEAM INVITATION QUERIES
-- ============================================================================

-- Send team invitation (using the function)
SELECT invite_team_member(
  '00000000-0000-0000-0000-000000000000'::UUID, -- agency_id
  'newmember@example.com', -- email
  'editor', -- role_id
  '00000000-0000-0000-0000-000000000000'::UUID, -- invited_by (user_id)
  'Welcome to our team! Looking forward to working with you.' -- optional message
);

-- Get pending invitations for an agency
SELECT 
  ti.id,
  ti.email,
  ti.role_id,
  tr.name as role_name,
  ti.invitation_token,
  ti.message,
  ti.expires_at,
  ti.created_at,
  inviter.email as invited_by_email,
  -- Time until expiry
  CASE 
    WHEN ti.expires_at < NOW() THEN 'Expired'
    WHEN ti.expires_at < NOW() + INTERVAL '1 day' THEN 'Expires Soon'
    ELSE 'Active'
  END as expiry_status,
  EXTRACT(DAYS FROM (ti.expires_at - NOW())) as days_until_expiry
FROM team_invitations ti
JOIN team_roles tr ON ti.role_id = tr.id
JOIN user_profiles inviter ON ti.invited_by = inviter.id
WHERE ti.agency_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual agency ID
  AND ti.status = 'pending'
  AND ti.expires_at > NOW()
ORDER BY ti.created_at DESC;

-- Get invitation by token (for accepting invitations)
SELECT 
  ti.*,
  a.name as agency_name,
  tr.name as role_name,
  tr.description as role_description,
  inviter.email as invited_by_email
FROM team_invitations ti
JOIN agencies a ON ti.agency_id = a.id
JOIN team_roles tr ON ti.role_id = tr.id
JOIN user_profiles inviter ON ti.invited_by = inviter.id
WHERE ti.invitation_token = 'TOKEN_FROM_EMAIL_LINK' -- Replace with actual token
  AND ti.status = 'pending'
  AND ti.expires_at > NOW();

-- Accept invitation (using the function)
SELECT accept_team_invitation(
  'TOKEN_FROM_EMAIL_LINK', -- invitation_token
  '00000000-0000-0000-0000-000000000000'::UUID -- user_id of person accepting
);

-- Cancel invitation
UPDATE team_invitations SET
  status = 'cancelled',
  updated_at = NOW()
WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual invitation ID
  AND agency_id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual agency ID

-- Resend invitation (extend expiry)
UPDATE team_invitations SET
  expires_at = NOW() + INTERVAL '7 days',
  updated_at = NOW()
WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual invitation ID
  AND status = 'pending';

-- ============================================================================
-- 4. PROJECT ACCESS CONTROL QUERIES
-- ============================================================================

-- Get projects accessible to a user (respects team access controls)
SELECT DISTINCT
  p.id,
  p.name,
  p.description,
  p.client_name,
  p.user_id as project_owner_id,
  owner.email as owner_email,
  p.is_shared,
  p.created_at,
  -- Access level for this user
  CASE 
    WHEN p.user_id = '00000000-0000-0000-0000-000000000000'::UUID THEN 'owner' -- Replace with actual user ID
    WHEN pta.access_level IS NOT NULL THEN pta.access_level
    WHEN p.is_shared AND tm.role_id = ANY(p.shared_with_roles) THEN 'view'
    ELSE 'none'
  END as access_level,
  -- Analysis count
  (SELECT COUNT(*) FROM ad_analyses aa WHERE aa.project_id = p.id) as analysis_count
FROM projects p
JOIN user_profiles owner ON p.user_id = owner.id
LEFT JOIN team_members tm ON tm.user_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual user ID
  AND tm.agency_id = p.agency_id 
  AND tm.status = 'active'
LEFT JOIN project_team_access pta ON pta.project_id = p.id 
  AND pta.team_member_id = tm.id
WHERE (
  -- User owns the project
  p.user_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual user ID
  OR
  -- User has specific project access
  pta.team_member_id IS NOT NULL
  OR
  -- Project is shared with user's role
  (p.is_shared AND tm.role_id = ANY(p.shared_with_roles))
)
ORDER BY p.created_at DESC;

-- Grant specific project access to team member
INSERT INTO project_team_access (project_id, team_member_id, access_level, granted_by)
VALUES (
  '00000000-0000-0000-0000-000000000000'::UUID, -- project_id
  '00000000-0000-0000-0000-000000000000'::UUID, -- team_member_id
  'edit', -- access_level: view, edit, manage
  '00000000-0000-0000-0000-000000000000'::UUID  -- granted_by (user_id)
)
ON CONFLICT (project_id, team_member_id) 
DO UPDATE SET 
  access_level = EXCLUDED.access_level,
  granted_by = EXCLUDED.granted_by,
  granted_at = NOW();

-- Get team members with access to a specific project
SELECT 
  tm.id as team_member_id,
  up.email,
  tm.role_id,
  tr.name as role_name,
  COALESCE(pta.access_level, 
    CASE WHEN tm.role_id = ANY(p.shared_with_roles) THEN 'view' ELSE 'none' END
  ) as access_level,
  pta.granted_at,
  granter.email as granted_by_email
FROM projects p
LEFT JOIN team_members tm ON tm.agency_id = p.agency_id AND tm.status = 'active'
LEFT JOIN user_profiles up ON tm.user_id = up.id
LEFT JOIN team_roles tr ON tm.role_id = tr.id
LEFT JOIN project_team_access pta ON pta.project_id = p.id AND pta.team_member_id = tm.id
LEFT JOIN user_profiles granter ON pta.granted_by = granter.id
WHERE p.id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual project ID
  AND (
    pta.team_member_id IS NOT NULL 
    OR (p.is_shared AND tm.role_id = ANY(p.shared_with_roles))
  )
ORDER BY tr.name, up.email;

-- Update project sharing settings
UPDATE projects SET
  is_shared = true,
  shared_with_roles = ARRAY['admin', 'editor'], -- Roles that can access
  updated_at = NOW()
WHERE id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual project ID
  AND user_id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual owner ID

-- ============================================================================
-- 5. TEAM ANALYTICS AND REPORTING QUERIES
-- ============================================================================

-- Agency dashboard overview
SELECT 
  a.name as agency_name,
  a.subscription_tier,
  a.max_team_members,
  a.monthly_analyses_limit,
  -- Current usage stats
  (SELECT COUNT(*) FROM team_members tm WHERE tm.agency_id = a.id AND tm.status = 'active') as active_members,
  (SELECT COUNT(*) FROM team_members tm WHERE tm.agency_id = a.id AND tm.status = 'pending') as pending_invitations,
  (SELECT COUNT(*) FROM projects p WHERE p.agency_id = a.id) as total_projects,
  (SELECT COALESCE(SUM(tm.analyses_this_month), 0) FROM team_members tm WHERE tm.agency_id = a.id) as monthly_analyses_used,
  -- Analysis breakdown by month
  (SELECT COUNT(*) FROM ad_analyses aa 
   JOIN projects p ON aa.project_id = p.id 
   WHERE p.agency_id = a.id 
   AND aa.created_at >= date_trunc('month', NOW())
  ) as analyses_this_month,
  (SELECT COUNT(*) FROM ad_analyses aa 
   JOIN projects p ON aa.project_id = p.id 
   WHERE p.agency_id = a.id
  ) as total_analyses
FROM agencies a
WHERE a.id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual agency ID

-- Team performance metrics
SELECT 
  tm.id,
  up.email,
  tm.role_id,
  tm.analyses_this_month,
  tm.total_analyses,
  tm.last_login_at,
  -- Activity score (0-100)
  CASE 
    WHEN tm.last_login_at IS NULL THEN 0
    WHEN tm.last_login_at > NOW() - INTERVAL '1 day' THEN 100
    WHEN tm.last_login_at > NOW() - INTERVAL '7 days' THEN 80
    WHEN tm.last_login_at > NOW() - INTERVAL '30 days' THEN 50
    ELSE 20
  END as activity_score,
  -- Average analysis score
  (SELECT ROUND(AVG(aa.overall_score)) 
   FROM ad_analyses aa 
   WHERE aa.user_id = tm.user_id 
   AND aa.created_at >= date_trunc('month', NOW())
  ) as avg_analysis_score_this_month
FROM team_members tm
JOIN user_profiles up ON tm.user_id = up.id
WHERE tm.agency_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual agency ID
  AND tm.status = 'active'
ORDER BY tm.analyses_this_month DESC, tm.last_login_at DESC;

-- Monthly team analytics
SELECT 
  date_trunc('month', aa.created_at) as month,
  COUNT(*) as analyses_count,
  ROUND(AVG(aa.overall_score)) as avg_score,
  COUNT(DISTINCT aa.user_id) as active_users,
  array_agg(DISTINCT aa.platform) as platforms_used
FROM ad_analyses aa
JOIN projects p ON aa.project_id = p.id
WHERE p.agency_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual agency ID
  AND aa.created_at >= NOW() - INTERVAL '12 months'
GROUP BY date_trunc('month', aa.created_at)
ORDER BY month DESC;

-- Project usage analytics
SELECT 
  p.id,
  p.name,
  p.client_name,
  COUNT(aa.id) as analysis_count,
  ROUND(AVG(aa.overall_score)) as avg_score,
  COUNT(DISTINCT aa.user_id) as contributors,
  MAX(aa.created_at) as last_activity,
  -- Team members with access
  array_agg(DISTINCT up.email) FILTER (WHERE up.email IS NOT NULL) as team_members_with_access
FROM projects p
LEFT JOIN ad_analyses aa ON p.id = aa.project_id
LEFT JOIN project_team_access pta ON p.id = pta.project_id
LEFT JOIN team_members tm ON pta.team_member_id = tm.id
LEFT JOIN user_profiles up ON tm.user_id = up.id
WHERE p.agency_id = '00000000-0000-0000-0000-000000000000'::UUID -- Replace with actual agency ID
GROUP BY p.id, p.name, p.client_name
ORDER BY analysis_count DESC;

-- ============================================================================
-- 6. PERMISSION AND ACCESS QUERIES
-- ============================================================================

-- Check if user has specific permission
SELECT user_has_permission(
  '00000000-0000-0000-0000-000000000000'::UUID, -- user_id
  'create_analysis', -- permission to check
  '00000000-0000-0000-0000-000000000000'::UUID  -- optional project_id
);

-- Get all permissions for a user
SELECT 
  up.email,
  CASE 
    WHEN up.agency_id IS NULL THEN 'Individual User (Full Access)'
    ELSE a.name
  END as context,
  CASE 
    WHEN up.agency_id IS NULL THEN ARRAY['*'] -- Individual users have all permissions
    ELSE tr.permissions
  END as permissions,
  tm.role_id,
  tr.name as role_name
FROM user_profiles up
LEFT JOIN agencies a ON up.agency_id = a.id
LEFT JOIN team_members tm ON tm.user_id = up.id AND tm.status = 'active'
LEFT JOIN team_roles tr ON tm.role_id = tr.id
WHERE up.id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual user ID

-- Get user's complete agency info
SELECT * FROM get_user_agency_info('00000000-0000-0000-0000-000000000000'::UUID); -- Replace with actual user ID

-- ============================================================================
-- 7. CLEANUP AND MAINTENANCE QUERIES
-- ============================================================================

-- Clean up expired invitations (run periodically)
UPDATE team_invitations SET
  status = 'expired',
  updated_at = NOW()
WHERE status = 'pending' 
  AND expires_at < NOW();

-- Update monthly analysis counts (reset monthly - run on 1st of each month)
UPDATE team_members SET
  analyses_this_month = (
    SELECT COUNT(*)
    FROM ad_analyses aa
    JOIN projects p ON aa.project_id = p.id
    WHERE aa.user_id = team_members.user_id
      AND aa.created_at >= date_trunc('month', NOW())
      AND p.agency_id = team_members.agency_id
  ),
  updated_at = NOW()
WHERE agency_id IS NOT NULL;

-- Update user last login timestamp (call from your authentication system)
UPDATE team_members SET
  last_login_at = NOW(),
  updated_at = NOW()
WHERE user_id = '00000000-0000-0000-0000-000000000000'::UUID; -- Replace with actual user ID

-- Get all team roles and their permissions (for UI dropdowns)
SELECT 
  id,
  name,
  description,
  permissions,
  array_length(permissions, 1) as permission_count
FROM team_roles
WHERE is_system_role = true
ORDER BY 
  CASE id 
    WHEN 'admin' THEN 1
    WHEN 'editor' THEN 2
    WHEN 'viewer' THEN 3
    WHEN 'client' THEN 4
    ELSE 5
  END;

-- ============================================================================
-- SAMPLE USAGE EXAMPLES
-- ============================================================================

/*
-- Example 1: Create an agency and invite team members
SELECT create_agency(
  'user-uuid-here',
  'Digital Marketing Pro',
  'agency'
);

-- Example 2: Invite a team member
SELECT invite_team_member(
  'agency-uuid-here',
  'designer@example.com',
  'editor',
  'owner-user-uuid-here',
  'Welcome to the team!'
);

-- Example 3: Check user permissions before allowing action
SELECT user_has_permission(
  'user-uuid-here',
  'create_analysis',
  'project-uuid-here'
);

-- Example 4: Get team dashboard data
-- (Use the team performance metrics query above)
*/