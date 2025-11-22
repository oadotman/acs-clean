/**
 * Agency Data Diagnostic Script
 * Run this in browser console on Team Management page to see exact issue
 */

import { supabase } from './src/lib/supabaseClientClean.js';

async function diagnoseAgencyIssue() {
  console.log('\n🔍 ========== AGENCY DIAGNOSTIC START ==========\n');
  
  try {
    // Get current user
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    
    if (authError || !user) {
      console.error('❌ AUTH ERROR:', authError);
      console.error('User not authenticated');
      return;
    }
    
    console.log('✅ User authenticated:', user.email);
    console.log('User ID:', user.id);
    
    // Check user profile
    console.log('\n📋 Step 1: Checking user_profiles table...');
    const { data: profile, error: profileError } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    
    if (profileError) {
      console.error('❌ PROFILE ERROR:', profileError);
      console.error('Error code:', profileError.code);
      console.error('Error message:', profileError.message);
      return;
    }
    
    console.log('✅ User Profile Found:');
    console.log('  - Email:', profile.email);
    console.log('  - Full Name:', profile.full_name);
    console.log('  - Subscription Tier:', profile.subscription_tier);
    console.log('  - Can Create Agency:', profile.can_create_agency);
    console.log('  - Agency ID:', profile.agency_id);
    
    // Check if user owns an agency
    console.log('\n🏢 Step 2: Checking agencies table (owned)...');
    const { data: ownedAgency, error: ownedError } = await supabase
      .from('agencies')
      .select('*')
      .eq('owner_id', user.id)
      .maybeSingle();
    
    if (ownedError && ownedError.code !== 'PGRST116') {
      console.error('❌ OWNED AGENCY ERROR:', ownedError);
      console.error('Error code:', ownedError.code);
      console.error('Error message:', ownedError.message);
    } else if (ownedAgency) {
      console.log('✅ User OWNS an agency:');
      console.log('  - Agency ID:', ownedAgency.id);
      console.log('  - Name:', ownedAgency.name);
      console.log('  - Tier:', ownedAgency.subscription_tier);
    } else {
      console.log('ℹ️ User does NOT own any agency');
    }
    
    // Check if user is a member of an agency
    console.log('\n👥 Step 3: Checking agency_team_members table...');
    const { data: membership, error: memberError } = await supabase
      .from('agency_team_members')
      .select(`
        *,
        agencies (*)
      `)
      .eq('user_id', user.id)
      .eq('status', 'active');
    
    if (memberError) {
      console.error('❌ MEMBERSHIP ERROR:', memberError);
      console.error('Error code:', memberError.code);
      console.error('Error message:', memberError.message);
    } else if (membership && membership.length > 0) {
      console.log(`✅ User is member of ${membership.length} agency/agencies:`);
      membership.forEach((m, i) => {
        console.log(`  [${i + 1}] Role: ${m.role}, Agency:`, m.agencies);
      });
    } else {
      console.log('ℹ️ User is NOT a member of any agency');
    }
    
    // Check permissions
    console.log('\n🔐 Step 4: Checking RLS permissions...');
    
    // Try to read agencies table
    const { data: allAgencies, error: agenciesError } = await supabase
      .from('agencies')
      .select('id, name')
      .limit(1);
    
    if (agenciesError) {
      console.error('❌ Cannot read agencies table:', agenciesError.message);
      console.log('  This might be an RLS policy issue');
    } else {
      console.log('✅ Can read agencies table');
    }
    
    // Try to read agency_team_members table
    const { data: allMembers, error: membersError } = await supabase
      .from('agency_team_members')
      .select('id')
      .limit(1);
    
    if (membersError) {
      console.error('❌ Cannot read agency_team_members table:', membersError.message);
      console.log('  This might be an RLS policy issue');
    } else {
      console.log('✅ Can read agency_team_members table');
    }
    
    // Final assessment
    console.log('\n📊 ASSESSMENT:');
    const isAgencyTier = ['agency_standard', 'agency_premium', 'agency_unlimited'].includes(profile?.subscription_tier);
    const canCreate = profile?.can_create_agency || isAgencyTier;
    
    console.log('Can access Team Management?', canCreate ? 'YES ✅' : 'NO ❌');
    
    if (canCreate && !ownedAgency && (!membership || membership.length === 0)) {
      console.log('\n⚠️ ISSUE FOUND: User has correct tier but NO agency exists!');
      console.log('ACTION: Try creating agency automatically...');
      
      // Try to create agency
      const agencyName = profile.full_name ? `${profile.full_name}'s Agency` : 'My Agency';
      console.log(`Creating agency: "${agencyName}"...`);
      
      const { data: newAgency, error: createError } = await supabase
        .from('agencies')
        .insert({
          name: agencyName,
          description: 'Main agency workspace',
          subscription_tier: profile.subscription_tier,
          owner_id: user.id
        })
        .select()
        .single();
      
      if (createError) {
        console.error('❌ FAILED to create agency:', createError);
        console.error('Error code:', createError.code);
        console.error('Error message:', createError.message);
        console.error('Error details:', createError.details);
        console.error('Error hint:', createError.hint);
      } else {
        console.log('✅ Agency created successfully:', newAgency);
        
        // Add user as admin
        const { error: memberError } = await supabase
          .from('agency_team_members')
          .insert({
            agency_id: newAgency.id,
            user_id: user.id,
            role: 'admin',
            status: 'active',
            invited_by: user.id
          });
        
        if (memberError) {
          console.error('⚠️ Failed to add user as team member:', memberError);
        } else {
          console.log('✅ User added as admin team member');
          console.log('\n🎉 SUCCESS! Refresh the page to see your team management.');
        }
      }
    } else if (!canCreate) {
      console.log('\n❌ ISSUE: User tier does not allow agency creation');
      console.log('Current tier:', profile?.subscription_tier);
      console.log('Required: agency_standard, agency_premium, or agency_unlimited');
    }
    
  } catch (error) {
    console.error('\n💥 UNEXPECTED ERROR:', error);
    console.error('Error stack:', error.stack);
  }
  
  console.log('\n🔍 ========== AGENCY DIAGNOSTIC END ==========\n');
}

// Auto-run if in browser
if (typeof window !== 'undefined') {
  window.diagnoseAgency = diagnoseAgencyIssue;
  console.log('📋 Diagnostic loaded! Run: window.diagnoseAgency()');
}

export default diagnoseAgencyIssue;
