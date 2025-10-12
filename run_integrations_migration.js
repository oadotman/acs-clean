/**
 * AdCopySurge - Run Integrations Migration Script
 * Executes the integrations system migration in Supabase
 */

const fs = require('fs');
const path = require('path');

// You'll need to install supabase: npm install @supabase/supabase-js
const { createClient } = require('@supabase/supabase-js');

// Supabase configuration - Update these with your actual values
const SUPABASE_URL = 'https://tqzlsajhhtkhljdbjkyg.supabase.co'; // From your error message
const SUPABASE_SERVICE_ROLE_KEY = 'your-service-role-key-here'; // You need to get this from Supabase dashboard

async function runMigration() {
    try {
        console.log('🚀 Starting AdCopySurge Integrations Migration...\n');

        // Create Supabase client with service role key for admin operations
        const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
            auth: {
                autoRefreshToken: false,
                persistSession: false
            }
        });

        // Read the migration SQL file
        const migrationPath = path.join(__dirname, 'database', 'migrations', '004_integrations_system.sql');
        
        if (!fs.existsSync(migrationPath)) {
            console.error(`❌ Migration file not found: ${migrationPath}`);
            console.error('Make sure you run this script from the project root directory.');
            process.exit(1);
        }

        const migrationSQL = fs.readFileSync(migrationPath, 'utf8');
        console.log('📄 Migration SQL loaded successfully');

        // Split SQL into individual statements (rough split by semicolons)
        const statements = migrationSQL
            .split(';')
            .map(stmt => stmt.trim())
            .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'))
            .filter(stmt => !stmt.includes('COMMENT ON')); // Skip comments for now

        console.log(`📝 Found ${statements.length} SQL statements to execute\n`);

        // Execute each statement
        let successCount = 0;
        let errorCount = 0;

        for (let i = 0; i < statements.length; i++) {
            const statement = statements[i].trim();
            
            if (statement.length === 0) continue;
            
            try {
                console.log(`⚡ Executing statement ${i + 1}/${statements.length}...`);
                
                const { data, error } = await supabase.rpc('exec_sql', {
                    sql: statement + ';'
                });

                if (error) {
                    throw error;
                }

                successCount++;
                console.log(`✅ Statement ${i + 1} executed successfully`);
                
            } catch (error) {
                console.error(`❌ Error executing statement ${i + 1}:`, error.message);
                console.error(`Statement: ${statement.substring(0, 100)}...`);
                errorCount++;
                
                // Continue with other statements even if one fails
                continue;
            }
        }

        console.log('\n📊 Migration Summary:');
        console.log(`✅ Successful: ${successCount}`);
        console.log(`❌ Failed: ${errorCount}`);

        if (errorCount === 0) {
            console.log('\n🎉 Migration completed successfully!');
            
            // Test the tables were created
            console.log('\n🔍 Verifying tables were created...');
            const { data: tables, error: tableError } = await supabase
                .from('information_schema.tables')
                .select('table_name')
                .like('table_name', '%integration%')
                .eq('table_schema', 'public');

            if (!tableError && tables) {
                console.log('✅ Integration tables found:', tables.map(t => t.table_name));
            }

            // Test the integrations were inserted
            const { data: integrations, error: intError } = await supabase
                .from('integrations')
                .select('id, name, status')
                .order('name');

            if (!intError && integrations) {
                console.log('✅ Available integrations:');
                integrations.forEach(int => {
                    console.log(`   - ${int.name} (${int.id}) - ${int.status}`);
                });
            }

        } else {
            console.log('\n⚠️  Migration completed with some errors. Check the logs above.');
            console.log('You may need to run some statements manually in the Supabase SQL editor.');
        }

    } catch (error) {
        console.error('\n💥 Migration failed:', error.message);
        console.error('\nPlease check:');
        console.error('1. Your SUPABASE_URL is correct');
        console.error('2. Your SUPABASE_SERVICE_ROLE_KEY is valid');
        console.error('3. You have admin permissions on the database');
        process.exit(1);
    }
}

// Alternative: Manual migration instructions
function printManualInstructions() {
    console.log('\n📋 MANUAL MIGRATION INSTRUCTIONS:');
    console.log('1. Go to your Supabase dashboard: https://supabase.com/dashboard');
    console.log('2. Select your project');
    console.log('3. Go to SQL Editor');
    console.log('4. Create a new query');
    console.log('5. Copy the contents of: database/migrations/004_integrations_system.sql');
    console.log('6. Paste and run the SQL');
    console.log('7. Check that the tables were created successfully\n');
}

// Check if we have the required dependencies
try {
    require('@supabase/supabase-js');
} catch (e) {
    console.log('❌ @supabase/supabase-js not found');
    console.log('Run: npm install @supabase/supabase-js\n');
    printManualInstructions();
    process.exit(1);
}

// Check if service role key is configured
if (!SUPABASE_SERVICE_ROLE_KEY || SUPABASE_SERVICE_ROLE_KEY === 'your-service-role-key-here') {
    console.log('⚠️  SUPABASE_SERVICE_ROLE_KEY not configured');
    console.log('You need to update this script with your actual service role key from Supabase dashboard.\n');
    printManualInstructions();
    process.exit(1);
}

// Run the migration
runMigration();