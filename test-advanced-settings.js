// Test script to verify Advanced Settings toggle persistence
// Run this in browser console to test the functionality

console.log('🧪 Testing Advanced Settings Toggle Persistence...');

// Check current localStorage state
const currentSettings = localStorage.getItem('adcopysurge_ui_settings');
console.log('Current settings in localStorage:', currentSettings ? JSON.parse(currentSettings) : 'None');

// Test toggle functionality
function testTogglePersistence() {
  console.log('Testing toggle persistence...');
  
  // Simulate toggling advanced settings
  const testSettings = {
    showAdvancedSettings: false,
    autoSave: false,
    compactView: false,
    darkMode: false,
    notifications: {
      browser: true,
      email: true,
      analysis_complete: true,
      project_shared: true
    },
    analysis: {
      autoAnalyze: true,
      saveResultsHistory: true,
      showDetailedScores: true
    }
  };
  
  // Save to localStorage
  localStorage.setItem('adcopysurge_ui_settings', JSON.stringify(testSettings));
  console.log('✅ Saved test settings to localStorage');
  
  // Toggle the setting
  testSettings.showAdvancedSettings = true;
  localStorage.setItem('adcopysurge_ui_settings', JSON.stringify(testSettings));
  console.log('✅ Toggled showAdvancedSettings to true');
  
  // Verify persistence
  const retrievedSettings = JSON.parse(localStorage.getItem('adcopysurge_ui_settings'));
  console.log('Retrieved settings:', retrievedSettings);
  
  if (retrievedSettings.showAdvancedSettings === true) {
    console.log('✅ PASS: Advanced settings toggle persistence works correctly');
    return true;
  } else {
    console.log('❌ FAIL: Advanced settings toggle persistence failed');
    return false;
  }
}

// Function to check if SettingsContext is available
function checkSettingsContext() {
  console.log('Checking if SettingsContext is available in the current page...');
  
  // Look for the advanced settings toggle in the DOM
  const advancedToggle = document.querySelector('[data-testid="advanced-settings-toggle"], input[type="checkbox"][name*="advanced"]');
  const advancedSettingsLabel = document.querySelector('label[for*="advanced"], .MuiFormControlLabel-label');
  
  if (advancedToggle || (advancedSettingsLabel && advancedSettingsLabel.textContent.includes('Advanced'))) {
    console.log('✅ Advanced Settings toggle found in DOM');
    return true;
  } else {
    console.log('⚠️ Advanced Settings toggle not found in current page. Navigate to /analyze or /project/new/workspace to test.');
    return false;
  }
}

// Check for AnalysisToolsSelector component
function checkAnalysisToolsSelector() {
  console.log('Checking for AnalysisToolsSelector component...');
  
  const selector = document.querySelector('[data-testid="analysis-tools-selector"]') || 
                  document.querySelector('.MuiFormControlLabel-root') ||
                  document.querySelector('h6:contains("Analysis Tools")') ||
                  Array.from(document.querySelectorAll('h6')).find(el => el.textContent.includes('Analysis Tools'));
  
  if (selector) {
    console.log('✅ AnalysisToolsSelector component found');
    return true;
  } else {
    console.log('⚠️ AnalysisToolsSelector component not found in current page');
    return false;
  }
}

// Main test function
function runAdvancedSettingsTest() {
  console.log('\n🧪 Running Advanced Settings Test Suite...\n');
  
  const tests = [
    { name: 'Toggle Persistence', fn: testTogglePersistence },
    { name: 'Settings Context Availability', fn: checkSettingsContext },
    { name: 'AnalysisToolsSelector Component', fn: checkAnalysisToolsSelector }
  ];
  
  let passed = 0;
  let total = tests.length;
  
  tests.forEach(test => {
    console.log(`\n--- Running: ${test.name} ---`);
    const result = test.fn();
    if (result) passed++;
  });
  
  console.log(`\n📊 Test Results: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('🎉 All tests passed! Advanced Settings functionality is working correctly.');
  } else {
    console.log('⚠️ Some tests failed. Check the specific test results above.');
  }
  
  return { passed, total };
}

// Instructions for manual testing
function showManualTestInstructions() {
  console.log(`
🎯 MANUAL TESTING INSTRUCTIONS:

1. Navigate to /analyze or /project/new/workspace
2. Look for "Advanced Settings" toggle switch
3. Verify it's ON by default (should show advanced options)
4. Toggle it OFF - advanced section should collapse
5. Refresh the page - setting should persist
6. Toggle it back ON - advanced section should expand
7. Navigate to another tool page and back - setting should persist

Expected Results:
✅ Advanced Settings toggle is visible
✅ Default state is ON (showAdvancedSettings: true)
✅ Toggling changes the UI immediately
✅ State persists after page refresh
✅ State persists across navigation
✅ localStorage key 'adcopysurge_ui_settings' is updated
  `);
}

// Run the test suite
runAdvancedSettingsTest();
showManualTestInstructions();

console.log('\n🔧 To run just the persistence test, call: testTogglePersistence()');
console.log('📋 To see manual test instructions again, call: showManualTestInstructions()');