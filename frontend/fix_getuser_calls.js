// This script fixes all getUser() calls to use getSession() instead
// Run this to update apiService.js

const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'src', 'services', 'apiService.js');
let content = fs.readFileSync(filePath, 'utf8');

// Replace all getUser() calls with getSession() pattern
const replacements = [
  // Pattern 1: const { data: { user } } = await supabase.auth.getUser();
  {
    from: /const\s+\{\s*data:\s*\{\s*user\s*\}\s*\}\s*=\s*await\s+supabase\.auth\.getUser\(\);/g,
    to: "const { data: { session } } = await supabase.auth.getSession();"
  },
  // Pattern 2: if (!user) throw new Error('User not authenticated');
  {
    from: /if\s*\(!user\)\s*throw\s+new\s+Error\(['"]User not authenticated['"]\);/g,
    to: "if (!session?.user) throw new Error('User not authenticated');\n      const user = session.user;"
  },
  // Pattern 3: const { data: { user, session } } = await supabase.auth.getUser();
  {
    from: /const\s+\{\s*data:\s*\{\s*user,\s*session\s*\}\s*\}\s*=\s*await\s+supabase\.auth\.getUser\(\);/g,
    to: "const { data: { session } } = await supabase.auth.getSession();\n      const user = session?.user;"
  }
];

// Apply replacements
replacements.forEach(({ from, to }) => {
  content = content.replace(from, to);
});

// Write the fixed content back
fs.writeFileSync(filePath, content, 'utf8');

console.log('✅ Fixed all getUser() calls to use getSession() instead');
console.log('   This prevents 403 errors during authentication checks');