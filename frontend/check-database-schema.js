const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

// Initialize Supabase client
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing Supabase environment variables');
  console.log('Please check that REACT_APP_SUPABASE_URL and REACT_APP_SUPABASE_ANON_KEY are set in your .env file');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkDatabaseSchema() {
  console.log('🔍 Checking AdCopySurge Database Schema...\n');

  try {
    // Check if we can connect to the database
    console.log('📡 Testing database connection...');
    const { data, error } = await supabase.from('user_credits').select('count', { count: 'exact', head: true });
    if (error) {
      console.error('❌ Database connection failed:', error.message);
      return;
    }
    console.log('✅ Database connection successful\n');

    // List all tables in the public schema
    console.log('📋 Querying database tables...');
    const { data: tables, error: tablesError } = await supabase
      .from('information_schema.tables')
      .select('table_name, table_type')
      .eq('table_schema', 'public')
      .order('table_name');

    if (tablesError) {
      console.error('❌ Failed to fetch tables:', tablesError.message);
      return;
    }

    console.log(`\n📊 Found ${tables.length} tables in the database:\n`);
    
    const tableNames = tables.map(t => t.table_name);
    
    // Categorize tables
    const creditTables = tableNames.filter(name => 
      name.includes('credit') || name.includes('billing') || name.includes('transaction')
    );
    
    const analysisTables = tableNames.filter(name => 
      name.includes('analys') || name.includes('ad_') || name.includes('copy')
    );
    
    const userTables = tableNames.filter(name => 
      name.includes('user') || name.includes('profile') || name.includes('account')
    );
    
    const authTables = tableNames.filter(name => 
      name.includes('auth') || name.includes('session')
    );
    
    const otherTables = tableNames.filter(name => 
      !creditTables.includes(name) && 
      !analysisTables.includes(name) && 
      !userTables.includes(name) && 
      !authTables.includes(name)
    );

    // Display categorized tables
    if (creditTables.length > 0) {
      console.log('💰 CREDIT SYSTEM TABLES:');
      creditTables.forEach(table => console.log(`   ✅ ${table}`));
      console.log('');
    }

    if (analysisTables.length > 0) {
      console.log('📈 ANALYSIS TABLES:');
      analysisTables.forEach(table => console.log(`   ✅ ${table}`));
      console.log('');
    }

    if (userTables.length > 0) {
      console.log('👤 USER TABLES:');
      userTables.forEach(table => console.log(`   ✅ ${table}`));
      console.log('');
    }

    if (authTables.length > 0) {
      console.log('🔐 AUTH TABLES:');
      authTables.forEach(table => console.log(`   ✅ ${table}`));
      console.log('');
    }

    if (otherTables.length > 0) {
      console.log('📋 OTHER TABLES:');
      otherTables.forEach(table => console.log(`   ✅ ${table}`));
      console.log('');
    }

    // Check specific critical tables
    console.log('🔍 CHECKING CRITICAL TABLES FOR PRODUCTION:\n');

    const criticalTables = [
      { name: 'user_credits', required: true, description: 'User credit balances and allowances' },
      { name: 'credit_transactions', required: true, description: 'Credit transaction history' },
      { name: 'ad_analyses', required: true, description: 'Stored ad analyses and results' },
      { name: 'user_subscriptions', required: false, description: 'User subscription plans' },
      { name: 'projects', required: false, description: 'User projects/workspaces' }
    ];

    for (const table of criticalTables) {
      const exists = tableNames.includes(table.name);
      const status = exists ? '✅' : (table.required ? '❌' : '⚠️');
      const priority = table.required ? '[REQUIRED]' : '[OPTIONAL]';
      
      console.log(`${status} ${table.name} ${priority}`);
      console.log(`   ${table.description}`);
      
      if (exists) {
        // Get column information for existing tables
        try {
          const { data: columns, error: colError } = await supabase
            .from('information_schema.columns')
            .select('column_name, data_type, is_nullable')
            .eq('table_schema', 'public')
            .eq('table_name', table.name)
            .order('ordinal_position');

          if (!colError && columns && columns.length > 0) {
            console.log(`   Columns: ${columns.map(c => c.column_name).join(', ')}`);
          }
        } catch (e) {
          // Ignore column fetch errors
        }
      }
      console.log('');
    }

    // Check credit system functionality
    console.log('💳 TESTING CREDIT SYSTEM FUNCTIONALITY:\n');
    
    if (tableNames.includes('user_credits')) {
      const { data: creditData, error: creditError } = await supabase
        .from('user_credits')
        .select('*')
        .limit(1);
      
      if (!creditError) {
        console.log('✅ user_credits table is accessible');
        if (creditData && creditData.length > 0) {
          console.log(`   Sample record found with fields: ${Object.keys(creditData[0]).join(', ')}`);
        } else {
          console.log('   Table is empty (no users with credits yet)');
        }
      } else {
        console.log('❌ user_credits table access failed:', creditError.message);
      }
    }

    if (tableNames.includes('credit_transactions')) {
      const { data: transactionData, error: transactionError } = await supabase
        .from('credit_transactions')
        .select('*')
        .limit(1);
      
      if (!transactionError) {
        console.log('✅ credit_transactions table is accessible');
        if (transactionData && transactionData.length > 0) {
          console.log(`   Sample record found with fields: ${Object.keys(transactionData[0]).join(', ')}`);
        } else {
          console.log('   Table is empty (no transactions yet)');
        }
      } else {
        console.log('❌ credit_transactions table access failed:', transactionError.message);
      }
    }

    // Summary
    console.log('\n📋 PRODUCTION READINESS SUMMARY:\n');
    
    const hasUserCredits = tableNames.includes('user_credits');
    const hasCreditTransactions = tableNames.includes('credit_transactions');
    const hasAdAnalyses = tableNames.includes('ad_analyses');

    if (hasUserCredits && hasCreditTransactions) {
      console.log('✅ Credit System: READY FOR PRODUCTION');
      console.log('   - User credits tracking: Available');
      console.log('   - Transaction logging: Available');
      console.log('   - Credit widget will show live data');
    } else {
      console.log('❌ Credit System: INCOMPLETE');
      if (!hasUserCredits) console.log('   - Missing: user_credits table');
      if (!hasCreditTransactions) console.log('   - Missing: credit_transactions table');
    }

    if (hasAdAnalyses) {
      console.log('✅ Analysis System: READY FOR PRODUCTION');
      console.log('   - Analysis storage: Available');
      console.log('   - Recent analyses will show real data');
    } else {
      console.log('❌ Analysis System: NEEDS SETUP');
      console.log('   - Missing: ad_analyses table');
      console.log('   - Recent analyses currently showing mock data');
    }

    console.log('\n🚀 NEXT STEPS:');
    if (!hasAdAnalyses) {
      console.log('1. Create ad_analyses table for storing analysis results');
    }
    if (hasUserCredits && hasCreditTransactions && hasAdAnalyses) {
      console.log('1. Database schema is complete!');
      console.log('2. Replace mock data with real API calls');
      console.log('3. Set up AI analysis integration');
    }

  } catch (error) {
    console.error('❌ Error checking database schema:', error.message);
    console.error('Full error:', error);
  }
}

// Run the schema check
checkDatabaseSchema().then(() => {
  console.log('\n✨ Schema check completed!');
  process.exit(0);
}).catch((error) => {
  console.error('❌ Schema check failed:', error);
  process.exit(1);
});