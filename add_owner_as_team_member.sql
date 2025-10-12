-- Add the agency owner as an admin team member
-- This fixes the issue where the owner isn't automatically added to the team

INSERT INTO agency_team_members (agency_id, user_id, role, status, invited_by)
SELECT 
    a.id as agency_id,
    a.owner_id as user_id,
    'admin' as role,
    'active' as status,
    a.owner_id as invited_by
FROM agencies a
LEFT JOIN agency_team_members atm ON (a.id = atm.agency_id AND a.owner_id = atm.user_id)
WHERE atm.id IS NULL  -- Only insert if owner is not already a team member
    AND a.owner_id = (SELECT id FROM user_profiles WHERE email = 'oadatascientist@gmail.com');

-- Verify the insert worked
SELECT 
    a.name as agency_name,
    up.email as owner_email,
    atm.role,
    atm.status,
    'Owner added as team member' as result
FROM agencies a
JOIN user_profiles up ON a.owner_id = up.id
JOIN agency_team_members atm ON (a.id = atm.agency_id AND a.owner_id = atm.user_id)
WHERE up.email = 'oadatascientist@gmail.com';

-- Also check total team members for your agency
SELECT 
    a.name as agency_name,
    COUNT(atm.id) as total_team_members,
    COUNT(CASE WHEN atm.status = 'active' THEN 1 END) as active_members,
    COUNT(CASE WHEN atm.status = 'pending' THEN 1 END) as pending_members
FROM agencies a
LEFT JOIN agency_team_members atm ON a.id = atm.agency_id
WHERE a.owner_id = (SELECT id FROM user_profiles WHERE email = 'oadatascientist@gmail.com')
GROUP BY a.id, a.name;