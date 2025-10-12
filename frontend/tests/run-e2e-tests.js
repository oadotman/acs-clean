#!/usr/bin/env node

/**
 * Node.js E2E Test Runner for AdCopySurge
 * This script runs comprehensive end-to-end tests for all user paths
 */

// Mock DOM environment for React components (if needed)
import { JSDOM } from 'jsdom';

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost:3000',
  pretendToBeVisual: true,
  resources: 'usable'
});

global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;

// Set up environment variables for testing
process.env.REACT_APP_SUPABASE_URL = 'https://zbsuldhdwtqmvgqwmjno.supabase.co';
process.env.REACT_APP_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpic3VsZGhkd3RxbXZncXdtam5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY2NjM5OTUsImV4cCI6MjA3MjIzOTk5NX0.C84_GzoYs0abkW4CC5sB0eqQ4OxpIievtw54sT2HPZ4';

// Import the E2E tester after setting up environment
const E2EUserPathTester = (await import('./e2e-user-paths.js')).default;

async function runTests() {
  console.log('🚀 AdCopySurge E2E Testing Suite');
  console.log('=====================================\n');

  try {
    const tester = new E2EUserPathTester();
    await tester.runAllTests();
    
    console.log('\n🎉 All tests completed successfully!');
    process.exit(0);
    
  } catch (error) {
    console.error('\n💥 Test suite failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

// Run tests
runTests();
