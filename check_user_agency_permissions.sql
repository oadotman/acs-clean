-- Run this query to check if your current user can create agencies
-- Replace 'your-user-id-here' with your actual user ID from auth.users

SELECT 
    id,
    email,
    subscription_tier,
    can_create_agency,
    monthly_analysis_limit,
    monthly_analyses_used,
    CASE 
        WHEN can_create_agency = TRUE THEN 'Can create agency ✓'
        ELSE 'Cannot create agency - need to upgrade to Agency tier'
    END as agency_status
FROM user_profiles 
WHERE id = auth.uid(); -- This will show your current user

-- Also check what subscription tiers allow agency creation:
SELECT 
    name,
    price_monthly / 100.0 as price_monthly_dollars,
    can_create_agency,
    max_team_members,
    analysis_limit
FROM subscription_tiers
WHERE can_create_agency = TRUE
ORDER BY price_monthly;