-- Run this to upgrade your current user to Agency Standard tier
-- This will allow you to create agencies and test team management

UPDATE user_profiles SET 
    subscription_tier = 'agency_standard',
    can_create_agency = TRUE,
    monthly_analysis_limit = 500
WHERE id = auth.uid();

-- Verify the update worked
SELECT 
    id,
    email,
    subscription_tier,
    can_create_agency,
    monthly_analysis_limit,
    'Ready to create agency!' as status
FROM user_profiles 
WHERE id = auth.uid();