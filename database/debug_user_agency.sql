-- Check your current user state
SELECT 
    up.id,
    up.email,
    up.agency_id,
    up.subscription_tier,
    up.can_create_agency,
    a.id as owns_agency_id,
    a.name as agency_name,
    atm.role as member_role,
    atm.status as member_status
FROM user_profiles up
LEFT JOIN agencies a ON a.owner_id = up.id
LEFT JOIN agency_team_members atm ON atm.user_id = up.id AND atm.status = 'active'
WHERE up.email = 'oadatascientist@gmail.com';
