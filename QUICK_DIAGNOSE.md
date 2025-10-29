# Quick Agency Diagnostic

## Run this in your browser console RIGHT NOW while on the Team Management page:

### Step 1: Copy and paste this code into browser console (F12):

```javascript
(async () => {
  console.log('\n🔍 STARTING DIAGNOSTIC...\n');
  
  // Import supabase
  const { createClient } = await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm');
  
  const SUPABASE_URL = localStorage.getItem('supabase.auth.url') || prompt('Enter your Supabase URL (check .env file):');
  const SUPABASE_ANON_KEY = localStorage.getItem('supabase.auth.anon') || prompt('Enter your Supabase Anon Key:');
  
  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  
  // Get current user
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    console.error('❌ Not authenticated');
    return;
  }
  
  console.log('✅ User:', user.email, '| ID:', user.id);
  
  // Check profile
  console.log('\n📋 Checking user_profiles...');
  const { data: profile, error: profileError } = await supabase
    .from('user_profiles')
    .select('*')
    .eq('id', user.id)
    .single();
  
  if (profileError) {
    console.error('❌ PROFILE ERROR:', profileError);
    console.log('\n🔥 PROBLEM: Cannot read user_profiles table!');
    console.log('SOLUTION: Check RLS policies on user_profiles table');
    return;
  }
  
  console.log('✅ Profile:', {
    email: profile.email,
    tier: profile.subscription_tier,
    canCreateAgency: profile.can_create_agency
  });
  
  // Check owned agency
  console.log('\n🏢 Checking owned agencies...');
  const { data: ownedAgency, error: ownedError } = await supabase
    .from('agencies')
    .select('*')
    .eq('owner_id', user.id)
    .maybeSingle();
  
  if (ownedError && ownedError.code !== 'PGRST116') {
    console.error('❌ AGENCY ERROR:', ownedError);
    console.log('\n🔥 PROBLEM: Cannot read agencies table!');
    console.log('Error details:', ownedError.message);
    return;
  }
  
  if (ownedAgency) {
    console.log('✅ FOUND OWNED AGENCY:', ownedAgency);
    console.log('\n✅ YOU SHOULD SEE YOUR TEAM MANAGEMENT NOW!');
    console.log('If not, there\'s a bug in the component. Check console logs.');
    return;
  }
  
  console.log('ℹ️ No owned agency found');
  
  // Check membership
  console.log('\n👥 Checking agency memberships...');
  const { data: membership, error: memberError } = await supabase
    .from('agency_team_members')
    .select('*, agencies(*)')
    .eq('user_id', user.id)
    .eq('status', 'active');
  
  if (memberError) {
    console.error('❌ MEMBERSHIP ERROR:', memberError);
    console.log('\n🔥 PROBLEM: Cannot read agency_team_members table!');
    console.log('Error details:', memberError.message);
    return;
  }
  
  if (membership && membership.length > 0) {
    console.log('✅ FOUND MEMBERSHIP:', membership);
    console.log('\n✅ YOU SHOULD SEE YOUR TEAM MANAGEMENT NOW!');
    return;
  }
  
  console.log('ℹ️ No memberships found');
  
  // Check if user can create agency
  const isAgencyTier = ['agency_standard', 'agency_premium', 'agency_unlimited'].includes(profile.subscription_tier);
  const canCreate = profile.can_create_agency || isAgencyTier;
  
  console.log('\n📊 ASSESSMENT:');
  console.log('Tier:', profile.subscription_tier);
  console.log('Can create agency?', canCreate ? 'YES' : 'NO');
  
  if (!canCreate) {
    console.log('\n❌ PROBLEM: Your tier does not allow agency creation');
    console.log('Current tier:', profile.subscription_tier);
    console.log('Required: agency_standard, agency_premium, or agency_unlimited');
    console.log('\n💡 SOLUTION: Upgrade your subscription tier to agency_unlimited in Supabase:');
    console.log('UPDATE user_profiles SET subscription_tier = \'agency_unlimited\' WHERE id = \'' + user.id + '\';');
    return;
  }
  
  console.log('\n⚠️ You have the right tier but NO agency exists!');
  console.log('Attempting to create agency automatically...\n');
  
  const agencyName = profile.full_name ? `${profile.full_name}'s Agency` : 'My Agency';
  
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
    console.error('❌ FAILED TO CREATE AGENCY:', createError);
    console.log('\n🔥 PROBLEM: Cannot insert into agencies table!');
    console.log('Error:', createError.message);
    console.log('Code:', createError.code);
    console.log('Details:', createError.details);
    console.log('\n💡 SOLUTION: Check RLS policies on agencies table');
    console.log('Make sure authenticated users can INSERT into agencies table');
    return;
  }
  
  console.log('✅ AGENCY CREATED:', newAgency);
  
  // Add user as admin
  const { error: memberError2 } = await supabase
    .from('agency_team_members')
    .insert({
      agency_id: newAgency.id,
      user_id: user.id,
      role: 'admin',
      status: 'active',
      invited_by: user.id
    });
  
  if (memberError2) {
    console.error('⚠️ Failed to add you as admin:', memberError2);
  } else {
    console.log('✅ Added you as admin');
  }
  
  console.log('\n🎉 SUCCESS! Refresh the page now.');
})();
```

### Step 2: Based on the output, apply the fix:

| Error Message | Solution |
|--------------|----------|
| "Cannot read user_profiles table" | RLS policy issue on `user_profiles` |
| "Cannot read agencies table" | RLS policy issue on `agencies` |
| "Cannot insert into agencies table" | RLS INSERT policy missing on `agencies` |
| "Your tier does not allow agency creation" | Run SQL: `UPDATE user_profiles SET subscription_tier = 'agency_unlimited' WHERE email = 'your@email.com';` |

---

## If the diagnostic shows RLS policy issues, run this SQL in Supabase:

```sql
-- Fix RLS policies for agencies table
DROP POLICY IF EXISTS "Users can view their own agencies" ON agencies;
DROP POLICY IF EXISTS "Users can create agencies" ON agencies;

CREATE POLICY "Users can view their own agencies" 
ON agencies FOR SELECT 
USING (auth.uid() = owner_id);

CREATE POLICY "Users can create agencies" 
ON agencies FOR INSERT 
WITH CHECK (auth.uid() = owner_id);

-- Fix RLS policies for agency_team_members
DROP POLICY IF EXISTS "Users can view team members" ON agency_team_members;
DROP POLICY IF EXISTS "Users can manage team members" ON agency_team_members;

CREATE POLICY "Users can view team members" 
ON agency_team_members FOR SELECT 
USING (
  auth.uid() = user_id 
  OR auth.uid() IN (
    SELECT owner_id FROM agencies WHERE id = agency_id
  )
);

CREATE POLICY "Users can manage team members" 
ON agency_team_members FOR ALL 
USING (
  auth.uid() IN (
    SELECT owner_id FROM agencies WHERE id = agency_id
  )
);

-- Fix RLS policies for user_profiles
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;

CREATE POLICY "Users can view their own profile" 
ON user_profiles FOR SELECT 
USING (auth.uid() = id);
```

---

## Quick Fix - If you just want it working NOW:

Run this SQL in Supabase (temporarily disable RLS for testing):

```sql
-- Disable RLS temporarily for debugging
ALTER TABLE agencies DISABLE ROW LEVEL SECURITY;
ALTER TABLE agency_team_members DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Set your user to agency_unlimited tier
UPDATE user_profiles 
SET subscription_tier = 'agency_unlimited' 
WHERE email = 'oadatascientist@gmail.com';
```

**WARNING:** This disables security! Only for debugging. Re-enable after fixing.

---

## After running the diagnostic, tell me what error you see and I'll fix it permanently.
