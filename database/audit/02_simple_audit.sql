-- ============================================================================
-- SIMPLIFIED AUDIT - ALL RESULTS IN ONE QUERY
-- Copy and paste this entire script into Supabase SQL Editor
-- ============================================================================

-- Create a temporary function to gather all audit data
DO $$
DECLARE
    v_output TEXT := E'\n=== DATABASE AUDIT RESULTS ===\n\n';
    v_temp TEXT;
    r RECORD;
BEGIN
    -- 1. CHECK IF TABLES EXIST
    v_output := v_output || E'1. TABLES EXISTENCE CHECK:\n';
    FOR r IN (
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
            AND table_name IN ('agencies', 'agency_team_members', 'agency_invitations', 
                              'user_profiles', 'user_credits', 'team_roles')
        ORDER BY table_name
    ) LOOP
        v_output := v_output || '   ✓ ' || r.table_name || E' exists\n';
    END LOOP;
    
    -- Check for missing tables
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agencies') THEN
        v_output := v_output || E'   ✗ agencies table MISSING\n';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agency_team_members') THEN
        v_output := v_output || E'   ✗ agency_team_members table MISSING\n';
    END IF;
    
    -- 2. RLS POLICIES CHECK
    v_output := v_output || E'\n2. RLS POLICIES:\n';
    FOR r IN (
        SELECT tablename, policyname, 
               CASE WHEN qual LIKE '%agency_team_members%' THEN '⚠️ RECURSIVE' ELSE '✓' END as status
        FROM pg_policies
        WHERE schemaname = 'public'
            AND tablename IN ('agencies', 'agency_team_members', 'agency_invitations')
        ORDER BY tablename, policyname
    ) LOOP
        v_output := v_output || '   ' || r.status || ' ' || r.tablename || '.' || r.policyname || E'\n';
    END LOOP;
    
    -- 3. HELPER FUNCTIONS CHECK
    v_output := v_output || E'\n3. HELPER FUNCTIONS:\n';
    FOR r IN (
        SELECT routine_name
        FROM information_schema.routines
        WHERE routine_schema = 'public'
            AND routine_name ~ '(agency|team|member)'
        ORDER BY routine_name
        LIMIT 10
    ) LOOP
        v_output := v_output || '   ✓ ' || r.routine_name || E'\n';
    END LOOP;
    
    -- 4. DATA COUNTS
    v_output := v_output || E'\n4. DATA VOLUMES:\n';
    
    BEGIN
        SELECT COUNT(*) INTO v_temp FROM agencies;
        v_output := v_output || '   Agencies: ' || COALESCE(v_temp, '0') || E'\n';
    EXCEPTION WHEN OTHERS THEN
        v_output := v_output || '   Agencies: ERROR - ' || SQLERRM || E'\n';
    END;
    
    BEGIN
        SELECT COUNT(*) INTO v_temp FROM agency_team_members;
        v_output := v_output || '   Team Members: ' || COALESCE(v_temp, '0') || E'\n';
    EXCEPTION WHEN OTHERS THEN
        v_output := v_output || '   Team Members: ERROR - ' || SQLERRM || E'\n';
    END;
    
    BEGIN
        SELECT COUNT(*) INTO v_temp FROM user_credits;
        v_output := v_output || '   User Credits: ' || COALESCE(v_temp, '0') || E'\n';
    EXCEPTION WHEN OTHERS THEN
        v_output := v_output || '   User Credits: ERROR - ' || SQLERRM || E'\n';
    END;
    
    -- 5. RECURSION TEST
    v_output := v_output || E'\n5. RECURSION TEST:\n';
    BEGIN
        PERFORM * FROM agency_team_members LIMIT 1;
        v_output := v_output || E'   ✓ Query successful - NO recursion error\n';
    EXCEPTION 
        WHEN OTHERS THEN
            IF SQLSTATE = '42P17' THEN
                v_output := v_output || E'   ✗ RECURSION ERROR DETECTED (42P17)\n';
            ELSE
                v_output := v_output || '   ✗ Error: ' || SQLERRM || E'\n';
            END IF;
    END;
    
    -- Output the complete report
    RAISE NOTICE '%', v_output;
    
END $$;

-- Now show the detailed policy information
SELECT 
    'DETAILED POLICY INFO' as report_section,
    tablename,
    policyname,
    cmd as operation,
    LEFT(qual::TEXT, 100) as policy_definition_preview
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename IN ('agencies', 'agency_team_members', 'agency_invitations')
ORDER BY tablename, policyname;
