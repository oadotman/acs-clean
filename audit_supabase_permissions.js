/**
 * AdCopySurge - Supabase Permissions Audit Script
 * Diagnoses and fixes permission issues with integration tables
 */

const fs = require('fs');
const path = require('path');

// Configuration - UPDATE THESE VALUES
const SUPABASE_URL = 'https://tqzlsajhhtkhljdbjkyg.supabase.co';
const SUPABASE_ANON_KEY = 'your-anon-key-here'; // Get from Supabase Dashboard > Settings > API
const SUPABASE_SERVICE_ROLE_KEY = 'your-service-role-key-here'; // Get from Supabase Dashboard > Settings > API

async function auditSupabasePermissions() {
    console.log('🔍 AdCopySurge Supabase Permissions Audit');
    console.log('=' * 50);
    
    try {
        // Check if we have the required module
        let supabase;
        try {
            const { createClient } = require('@supabase/supabase-js');
            
            // Create both anon and service role clients for testing
            const supabaseAnon = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
            const supabaseService = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
                auth: {
                    autoRefreshToken: false,
                    persistSession: false
                }
            });
            
            supabase = { anon: supabaseAnon, service: supabaseService };
        } catch (e) {
            console.error('❌ @supabase/supabase-js not found. Run: npm install @supabase/supabase-js');
            return;
        }

        console.log('\n🔧 Configuration Check:');
        console.log(`   URL: ${SUPABASE_URL}`);
        console.log(`   Anon Key: ${SUPABASE_ANON_KEY !== 'your-anon-key-here' ? '✅ Configured' : '❌ Not configured'}`);
        console.log(`   Service Key: ${SUPABASE_SERVICE_ROLE_KEY !== 'your-service-role-key-here' ? '✅ Configured' : '❌ Not configured'}`);

        // Step 1: Check if tables exist
        console.log('\n📊 Step 1: Checking if integration tables exist...');
        await checkTablesExist(supabase.service);

        // Step 2: Check table permissions
        console.log('\n🔐 Step 2: Checking table permissions...');
        await checkTablePermissions(supabase.service);

        // Step 3: Check RLS policies
        console.log('\n🛡️ Step 3: Checking Row Level Security policies...');
        await checkRLSPolicies(supabase.service);

        // Step 4: Test authenticated access
        console.log('\n👤 Step 4: Testing authenticated access...');
        await testAuthenticatedAccess(supabase.anon);

        // Step 5: Generate fix SQL
        console.log('\n🔧 Step 5: Generating permission fixes...');
        await generateFixSQL();

    } catch (error) {
        console.error('💥 Audit failed:', error.message);
    }
}

async function checkTablesExist(supabase) {
    try {
        const { data, error } = await supabase
            .from('information_schema.tables')
            .select('table_name, table_type')
            .eq('table_schema', 'public')
            .in('table_name', ['integrations', 'user_integrations', 'integration_logs']);

        if (error) {
            console.error('❌ Error checking tables:', error.message);
            return;
        }

        const expectedTables = ['integrations', 'user_integrations', 'integration_logs'];
        const foundTables = data?.map(t => t.table_name) || [];

        expectedTables.forEach(table => {
            if (foundTables.includes(table)) {
                console.log(`   ✅ ${table} - EXISTS`);
            } else {
                console.log(`   ❌ ${table} - MISSING`);
            }
        });

        if (foundTables.length < expectedTables.length) {
            console.log('\n⚠️  Some integration tables are missing. Run the migration first.');
        }

    } catch (error) {
        console.error('❌ Error checking tables:', error.message);
    }
}

async function checkTablePermissions(supabase) {
    try {
        // Check table privileges for different roles
        const { data, error } = await supabase.rpc('exec_sql', {
            sql: `
                SELECT 
                    schemaname,
                    tablename,
                    usename,
                    privilege_type,
                    is_grantable
                FROM information_schema.table_privileges 
                WHERE schemaname = 'public' 
                AND tablename IN ('integrations', 'user_integrations', 'integration_logs')
                ORDER BY tablename, usename;
            `
        });

        if (error) {
            console.error('❌ Error checking permissions:', error.message);
            return;
        }

        if (data && data.length > 0) {
            console.log('   Current table privileges:');
            data.forEach(row => {
                console.log(`   - ${row.tablename}: ${row.usename} has ${row.privilege_type}`);
            });
        } else {
            console.log('   ❌ No table privileges found - this is the problem!');
        }

    } catch (error) {
        console.error('❌ Error checking permissions:', error.message);
    }
}

async function checkRLSPolicies(supabase) {
    try {
        const { data, error } = await supabase.rpc('exec_sql', {
            sql: `
                SELECT 
                    schemaname,
                    tablename,
                    policyname,
                    permissive,
                    roles,
                    cmd,
                    qual,
                    with_check
                FROM pg_policies 
                WHERE schemaname = 'public' 
                AND tablename IN ('integrations', 'user_integrations', 'integration_logs')
                ORDER BY tablename, policyname;
            `
        });

        if (error) {
            console.error('❌ Error checking RLS policies:', error.message);
            return;
        }

        if (data && data.length > 0) {
            console.log('   Current RLS policies:');
            data.forEach(row => {
                console.log(`   - ${row.tablename}.${row.policyname}: ${row.cmd} for ${row.roles?.join(', ')}`);
            });
        } else {
            console.log('   ℹ️  No RLS policies found (RLS might be disabled)');
        }

        // Check if RLS is enabled
        const { data: rlsData, error: rlsError } = await supabase.rpc('exec_sql', {
            sql: `
                SELECT 
                    schemaname,
                    tablename,
                    rowsecurity
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('integrations', 'user_integrations', 'integration_logs');
            `
        });

        if (!rlsError && rlsData) {
            console.log('   RLS Status:');
            rlsData.forEach(row => {
                console.log(`   - ${row.tablename}: RLS ${row.rowsecurity ? 'ENABLED' : 'DISABLED'}`);
            });
        }

    } catch (error) {
        console.error('❌ Error checking RLS policies:', error.message);
    }
}

async function testAuthenticatedAccess(supabase) {
    try {
        // Test reading from integrations table
        console.log('   Testing integrations table access...');
        const { data: intData, error: intError } = await supabase
            .from('integrations')
            .select('id, name')
            .limit(1);

        if (intError) {
            console.log(`   ❌ integrations: ${intError.message}`);
        } else {
            console.log(`   ✅ integrations: Can read (${intData?.length || 0} records)`);
        }

        // Test reading from user_integrations table
        console.log('   Testing user_integrations table access...');
        const { data: userIntData, error: userIntError } = await supabase
            .from('user_integrations')
            .select('id')
            .limit(1);

        if (userIntError) {
            console.log(`   ❌ user_integrations: ${userIntError.message}`);
        } else {
            console.log(`   ✅ user_integrations: Can read (${userIntData?.length || 0} records)`);
        }

    } catch (error) {
        console.error('❌ Error testing access:', error.message);
    }
}

async function generateFixSQL() {
    const fixSQL = `
-- ============================================================================
-- SUPABASE PERMISSIONS FIX FOR INTEGRATION TABLES
-- Run this in Supabase SQL Editor to fix permission issues
-- ============================================================================

-- Step 1: Grant basic permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- Step 2: Grant table permissions
GRANT ALL ON TABLE public.integrations TO authenticated;
GRANT ALL ON TABLE public.user_integrations TO authenticated;
GRANT ALL ON TABLE public.integration_logs TO authenticated;

GRANT SELECT ON TABLE public.integrations TO anon;
GRANT SELECT ON TABLE public.integrations TO authenticated;

-- Step 3: Grant sequence permissions (for UUID generation)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Step 4: Ensure RLS is disabled (matching your existing pattern)
ALTER TABLE public.integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.integration_logs DISABLE ROW LEVEL SECURITY;

-- Step 5: Grant permissions to service role (for admin operations)
GRANT ALL ON TABLE public.integrations TO service_role;
GRANT ALL ON TABLE public.user_integrations TO service_role;
GRANT ALL ON TABLE public.integration_logs TO service_role;

-- Step 6: Ensure public schema permissions
GRANT CREATE ON SCHEMA public TO authenticated;

-- Step 7: Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION public.update_updated_at_column() TO authenticated;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if permissions were granted
SELECT 
    schemaname,
    tablename,
    usename,
    privilege_type
FROM information_schema.table_privileges 
WHERE schemaname = 'public' 
AND tablename IN ('integrations', 'user_integrations', 'integration_logs')
AND usename IN ('authenticated', 'anon')
ORDER BY tablename, usename;

-- Test table access
SELECT 'integrations' as table_name, count(*) as record_count FROM integrations
UNION ALL
SELECT 'user_integrations' as table_name, count(*) as record_count FROM user_integrations
UNION ALL  
SELECT 'integration_logs' as table_name, count(*) as record_count FROM integration_logs;
`;

    console.log('✨ Permission Fix SQL generated. Copy and paste this into Supabase SQL Editor:\n');
    console.log('─'.repeat(80));
    console.log(fixSQL);
    console.log('─'.repeat(80));

    // Also save to file
    try {
        const fixFilePath = path.join(__dirname, 'fix_integration_permissions.sql');
        fs.writeFileSync(fixFilePath, fixSQL);
        console.log(`\n💾 Fix SQL saved to: ${fixFilePath}`);
    } catch (error) {
        console.log('⚠️  Could not save fix SQL to file:', error.message);
    }
}

// Check configuration and run audit
function main() {
    if (SUPABASE_ANON_KEY === 'your-anon-key-here' || SUPABASE_SERVICE_ROLE_KEY === 'your-service-role-key-here') {
        console.log('⚠️  Please update the configuration at the top of this script:');
        console.log('1. Get your keys from Supabase Dashboard > Settings > API');
        console.log('2. Update SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY');
        console.log('3. Run the script again\n');
        
        console.log('🔧 Or run the manual fix:');
        console.log('1. Go to Supabase Dashboard > SQL Editor');
        console.log('2. Run the generated fix SQL (see above)');
        return;
    }

    auditSupabasePermissions();
}

main();