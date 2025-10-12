// Simple test to verify the fix
console.log('🧪 Testing Credit System Fix...');

// Test 1: Credit System
import('./src/utils/creditSystem.js').then(creditSystem => {
  console.log('📊 Testing getUserCredits...');
  creditSystem.getUserCredits('test-user').then(result => {
    console.log('✅ getUserCredits result:', result);
    console.log('✅ Credits:', result.credits === 999999 ? 'UNLIMITED' : result.credits);
  }).catch(err => {
    console.error('❌ getUserCredits failed:', err);
  });
  
  console.log('📊 Testing consumeCredits...');
  creditSystem.consumeCredits('test-user', 'BASIC_ANALYSIS').then(result => {
    console.log('✅ consumeCredits result:', result);
    console.log('✅ Success:', result.success);
  }).catch(err => {
    console.error('❌ consumeCredits failed:', err);
  });
});

// Test 2: Credits Service
import('./src/services/creditsService.js').then(module => {
  const creditsService = module.default;
  console.log('📊 Testing creditsService.canPerformAction...');
  const canAnalyze = creditsService.canPerformAction('single_analysis', 1);
  console.log('✅ canPerformAction result:', canAnalyze);
});

console.log('🧪 Test completed - check results above');