-- ============================================================================
-- FIX: Sync agency_id for ALL users and add prevention triggers
-- Run this in Supabase SQL Editor
-- ============================================================================

-- STEP 1: Sync ALL existing users who are agency members but have NULL agency_id
-- ============================================================================

UPDATE user_profiles up
SET agency_id = atm.agency_id
FROM agency_team_members atm
WHERE up.id = atm.user_id
  AND up.agency_id IS NULL
  AND atm.status = 'active';

-- Show how many users were fixed
SELECT 
    'Users synced' as action,
    COUNT(*) as affected_rows
FROM user_profiles up
JOIN agency_team_members atm ON up.id = atm.user_id
WHERE up.agency_id = atm.agency_id;

-- ============================================================================
-- STEP 2: Create trigger to auto-sync agency_id when team member is added
-- ============================================================================

CREATE OR REPLACE FUNCTION sync_user_agency_id()
RETURNS TRIGGER AS $$
BEGIN
  -- When a team member is added, update their user_profile.agency_id
  UPDATE user_profiles 
  SET agency_id = NEW.agency_id,
      updated_at = NOW()
  WHERE id = NEW.user_id;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS sync_agency_id_on_member_insert ON agency_team_members;

-- Create trigger on INSERT
CREATE TRIGGER sync_agency_id_on_member_insert
AFTER INSERT ON agency_team_members
FOR EACH ROW EXECUTE FUNCTION sync_user_agency_id();

-- ============================================================================
-- STEP 3: Also sync when team member status changes to active
-- ============================================================================

CREATE OR REPLACE FUNCTION sync_user_agency_id_on_update()
RETURNS TRIGGER AS $$
BEGIN
  -- When member becomes active, sync agency_id
  IF NEW.status = 'active' AND OLD.status != 'active' THEN
    UPDATE user_profiles 
    SET agency_id = NEW.agency_id,
        updated_at = NOW()
    WHERE id = NEW.user_id;
  END IF;
  
  -- When member is removed, clear agency_id
  IF NEW.status = 'removed' THEN
    UPDATE user_profiles 
    SET agency_id = NULL,
        updated_at = NOW()
    WHERE id = NEW.user_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS sync_agency_id_on_member_update ON agency_team_members;

-- Create trigger on UPDATE
CREATE TRIGGER sync_agency_id_on_member_update
AFTER UPDATE ON agency_team_members
FOR EACH ROW EXECUTE FUNCTION sync_user_agency_id_on_update();

-- ============================================================================
-- STEP 4: Verify the fix worked
-- ============================================================================

SELECT 
    'VERIFICATION' as section,
    up.id as user_id,
    up.email,
    up.agency_id as profile_agency_id,
    atm.agency_id as membership_agency_id,
    CASE 
        WHEN up.agency_id = atm.agency_id THEN '✅ SYNCED'
        WHEN up.agency_id IS NULL THEN '❌ NULL'
        ELSE '⚠️ MISMATCH'
    END as status
FROM user_profiles up
LEFT JOIN agency_team_members atm ON up.id = atm.user_id AND atm.status = 'active'
WHERE atm.agency_id IS NOT NULL
ORDER BY status DESC;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 
    '=== FIX COMPLETE ===' as message,
    'All users synced and triggers installed' as status,
    'New team members will auto-sync agency_id' as note;
