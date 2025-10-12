const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Your Supabase credentials
const SUPABASE_URL = 'https://zbsuldhdwtqmvgqwmjno.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpic3VsZGhkd3RxbXZncXdtam5vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjY2Mzk5NSwiZXhwIjoyMDcyMjM5OTk1fQ.QD8D4Tsu2FcFzU0ApZwWDR8x6rkU4-TZKFctqzWqODE';

console.log('🚀 Setting up AdCopySurge Database Schema...\n');

async function setupDatabase() {
  try {
    // Create Supabase client with service role key for admin operations
    console.log('1. Creating Supabase admin client...');
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    });
    console.log('✅ Admin client created successfully');

    // Read the schema file
    console.log('\n2. Reading database schema...');
    const schemaPath = path.join(__dirname, '..', 'supabase-schema.sql');
    
    if (!fs.existsSync(schemaPath)) {
      throw new Error(`Schema file not found at: ${schemaPath}`);
    }
    
    const schemaSQL = fs.readFileSync(schemaPath, 'utf8');
    console.log(`✅ Schema loaded (${schemaSQL.length} characters)`);

    // Split SQL into individual statements (basic splitting)
    console.log('\n3. Processing SQL statements...');
    const statements = schemaSQL
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--') && !stmt.startsWith('/*'));
    
    console.log(`✅ Found ${statements.length} SQL statements to execute`);

    // Execute each statement
    console.log('\n4. Executing SQL statements...');
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      
      // Skip comments and empty statements
      if (!statement.trim() || statement.trim().startsWith('--')) {
        continue;
      }
      
      try {
        console.log(`   Executing statement ${i + 1}/${statements.length}...`);
        
        // Use the RPC function to execute raw SQL
        const { data, error } = await supabase.rpc('exec_sql', {
          sql: statement + ';'
        });
        
        if (error) {
          // Some errors are expected (like "already exists")
          if (error.message.includes('already exists') || 
              error.message.includes('duplicate key') ||
              error.message.includes('relation already exists')) {
            console.log(`   ⚠️ Statement ${i + 1}: ${error.message} (continuing...)`);
          } else {
            console.log(`   ❌ Statement ${i + 1} failed: ${error.message}`);
            errorCount++;
          }
        } else {
          console.log(`   ✅ Statement ${i + 1} executed successfully`);
          successCount++;
        }
        
      } catch (err) {
        console.log(`   ❌ Statement ${i + 1} exception: ${err.message}`);
        errorCount++;
      }
      
      // Small delay to avoid overwhelming the server
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    console.log(`\n📊 Execution Summary:`);
    console.log(`   • Successful: ${successCount}`);
    console.log(`   • Errors: ${errorCount}`);
    console.log(`   • Total: ${statements.length}`);

    // If we can't use exec_sql, try alternative approach
    if (errorCount === statements.length) {
      console.log('\n⚠️ SQL execution failed - trying alternative approach...');
      return await setupDatabaseAlternative(supabase);
    }

    return successCount > errorCount;

  } catch (error) {
    console.log('💥 Critical error during database setup:', error.message);
    return false;
  }
}

// Alternative setup using individual table creation
async function setupDatabaseAlternative(supabase) {
  console.log('\n🔄 Using alternative setup method...');
  
  try {
    // Create enum type
    console.log('   Creating subscription_tier enum...');
    await supabase.rpc('exec_sql', {
      sql: "CREATE TYPE subscription_tier AS ENUM ('free', 'basic', 'pro');"
    });

    // Create tables one by one using the REST API approach
    console.log('   Tables will need to be created manually in Supabase Dashboard');
    console.log('\n📋 Manual Setup Instructions:');
    console.log('   1. Go to your Supabase Dashboard: https://supabase.com/dashboard');
    console.log('   2. Open your project: zbsuldhdwtqmvgqwmjno');
    console.log('   3. Go to SQL Editor');
    console.log('   4. Paste and run the contents of supabase-schema.sql');
    console.log('   5. Come back and run: bun run test-supabase-bun.js');
    
    return false; // Manual intervention needed

  } catch (error) {
    console.log('💥 Alternative setup also failed:', error.message);
    return false;
  }
}

// Test the database after setup
async function testDatabaseAfterSetup() {
  console.log('\n5. Testing database setup...');
  
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    
    const tables = ['user_profiles', 'ad_analyses', 'competitor_benchmarks', 'ad_generations'];
    let workingTables = 0;
    
    for (const table of tables) {
      try {
        const { data, error, count } = await supabase
          .from(table)
          .select('*', { count: 'exact', head: true });
        
        if (error) {
          console.log(`   ❌ Table '${table}': ${error.message}`);
        } else {
          console.log(`   ✅ Table '${table}': accessible (${count || 0} rows)`);
          workingTables++;
        }
      } catch (err) {
        console.log(`   ❌ Table '${table}': ${err.message}`);
      }
    }
    
    return workingTables === tables.length;
    
  } catch (error) {
    console.log('   💥 Test failed:', error.message);
    return false;
  }
}

// Main execution
async function main() {
  console.log('💡 This script will set up your AdCopySurge database schema in Supabase\n');
  
  const setupSuccess = await setupDatabase();
  
  if (setupSuccess) {
    console.log('\n🎉 Database setup completed successfully!');
    
    const testSuccess = await testDatabaseAfterSetup();
    
    if (testSuccess) {
      console.log('\n✅ All tables are working correctly!');
      console.log('\n🚀 Next steps:');
      console.log('   • Run: bun run start');
      console.log('   • Your dashboard should now load with data!');
      console.log('   • Sign up for a new account to test the full flow');
    } else {
      console.log('\n⚠️ Some tables are still not working. Check the Supabase Dashboard.');
    }
  } else {
    console.log('\n💡 Manual setup required:');
    console.log('   1. Open Supabase Dashboard: https://supabase.com/dashboard/project/zbsuldhdwtqmvgqwmjno');
    console.log('   2. Go to SQL Editor');  
    console.log('   3. Copy and paste the entire contents of supabase-schema.sql');
    console.log('   4. Click "Run" to execute all statements');
    console.log('   5. Then run: bun run test-supabase-bun.js');
  }
  
  process.exit(0);
}

// Run the setup
main().catch((error) => {
  console.error('💥 Unhandled error:', error.message);
  process.exit(1);
});
