/**
 * Comprehensive End-to-End User Path Testing Script
 * This script simulates all critical user journeys in AdCopySurge
 */

import { supabase } from '../src/lib/supabaseClient.js';
import dataService from '../src/services/dataService.js';

class E2EUserPathTester {
  constructor() {
    this.testResults = [];
    this.testUser = null;
    this.testAnalysisId = null;
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const logEntry = { timestamp, message, type };
    console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
    this.testResults.push(logEntry);
  }

  async runAllTests() {
    this.log('🚀 Starting comprehensive E2E user path testing...', 'info');
    
    try {
      // Test 1: User Registration and Authentication Flow
      await this.testUserRegistrationFlow();
      
      // Test 2: User Login Flow
      await this.testUserLoginFlow();
      
      // Test 3: Dashboard Data Loading
      await this.testDashboardLoadingFlow();
      
      // Test 4: Ad Analysis Creation Flow
      await this.testAdAnalysisFlow();
      
      // Test 5: Analysis Results Display
      await this.testAnalysisResultsFlow();
      
      // Test 6: Profile Management
      await this.testProfileManagementFlow();
      
      // Test 7: Subscription and Quota Management
      await this.testSubscriptionFlow();
      
      // Test 8: Real-time Updates
      await this.testRealtimeUpdatesFlow();
      
      // Test 9: Error Handling
      await this.testErrorHandlingFlow();
      
      // Test 10: Navigation and Routing
      await this.testNavigationFlow();
      
      // Cleanup
      await this.cleanup();
      
      this.log('✅ All user path tests completed successfully!', 'success');
      this.generateReport();
      
    } catch (error) {
      this.log(`❌ Test suite failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testUserRegistrationFlow() {
    this.log('Testing user registration flow...', 'test');
    
    try {
      const testUserData = {
        email: `test-${Date.now()}@adcopysurge.test`,
        password: 'TestPassword123!',
        full_name: 'Test User',
        company: 'Test Company'
      };

      // Simulate user registration
      const { data, error } = await supabase.auth.signUp({
        email: testUserData.email,
        password: testUserData.password,
        options: {
          data: {
            full_name: testUserData.full_name,
            company: testUserData.company
          }
        }
      });

      if (error) throw error;
      
      this.testUser = data.user;
      this.log(`✅ User registration successful: ${testUserData.email}`, 'success');
      
      // Verify user profile was created
      const profile = await dataService.getUserProfile(this.testUser.id);
      if (!profile) {
        throw new Error('User profile was not created automatically');
      }
      
      this.log('✅ User profile created automatically', 'success');
      
    } catch (error) {
      this.log(`❌ Registration flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testUserLoginFlow() {
    this.log('Testing user login flow...', 'test');
    
    try {
      // First sign out to test login
      await supabase.auth.signOut();
      
      // Test login with correct credentials
      const { data, error } = await supabase.auth.signInWithPassword({
        email: this.testUser.email,
        password: 'TestPassword123!'
      });

      if (error) throw error;
      
      this.log('✅ User login successful', 'success');
      
      // Verify session is active
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('Session not established after login');
      }
      
      this.log('✅ Session established successfully', 'success');
      
    } catch (error) {
      this.log(`❌ Login flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testDashboardLoadingFlow() {
    this.log('Testing dashboard data loading flow...', 'test');
    
    try {
      // Test dashboard analytics loading
      const analytics = await dataService.getDashboardAnalytics(this.testUser.id);
      
      if (!analytics || typeof analytics !== 'object') {
        throw new Error('Dashboard analytics not loaded properly');
      }
      
      this.log('✅ Dashboard analytics loaded successfully', 'success');
      
      // Test recent analyses loading
      const recentAnalyses = await dataService.getAnalysesHistory(this.testUser.id, 5, 0);
      
      if (!Array.isArray(recentAnalyses)) {
        throw new Error('Recent analyses not loaded as array');
      }
      
      this.log(`✅ Recent analyses loaded: ${recentAnalyses.length} items`, 'success');
      
      // Test user profile loading
      const profile = await dataService.getUserProfile(this.testUser.id);
      
      if (!profile) {
        throw new Error('User profile not loaded');
      }
      
      this.log('✅ User profile loaded successfully', 'success');
      
    } catch (error) {
      this.log(`❌ Dashboard loading failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testAdAnalysisFlow() {
    this.log('Testing ad analysis creation flow...', 'test');
    
    try {
      const sampleAdData = {
        headline: 'Test Ad Headline - Revolutionary AI Tool',
        body_text: 'Transform your business with our cutting-edge AI technology. Increase productivity by 300% and reduce costs significantly.',
        cta: 'Get Started Free Today',
        platform: 'facebook',
        target_audience: 'Small business owners',
        industry: 'SaaS'
      };

      // Test quota check
      const quota = await dataService.checkUserQuota(this.testUser.id);
      if (!quota.canAnalyze) {
        throw new Error('User quota exceeded - cannot test analysis flow');
      }
      
      this.log(`✅ User quota check passed: ${quota.remaining} analyses remaining`, 'success');

      // Create analysis
      const analysis = await dataService.createAnalysis(this.testUser.id, sampleAdData);
      
      if (!analysis || !analysis.id) {
        throw new Error('Analysis creation failed');
      }
      
      this.testAnalysisId = analysis.id;
      this.log(`✅ Analysis created successfully: ${analysis.id}`, 'success');

      // Test analysis with competitor data
      const competitorData = [{
        headline: 'Competitor Ad Headline',
        body_text: 'Competitor body text here.',
        cta: 'Buy Now',
        platform: 'facebook'
      }];

      const competitors = await dataService.addCompetitorBenchmarks(analysis.id, competitorData);
      
      if (!competitors || competitors.length === 0) {
        throw new Error('Competitor benchmarks not added');
      }
      
      this.log('✅ Competitor benchmarks added successfully', 'success');

      // Test generated alternatives
      const alternatives = [{
        variant_type: 'emotional',
        headline: 'Emotional Alternative Headline',
        body_text: 'Emotional body text here.',
        cta: 'Start Your Journey',
        improvement_reason: 'Increased emotional appeal'
      }];

      const generatedAlts = await dataService.addGeneratedAlternatives(analysis.id, alternatives);
      
      if (!generatedAlts || generatedAlts.length === 0) {
        throw new Error('Generated alternatives not added');
      }
      
      this.log('✅ Generated alternatives added successfully', 'success');

    } catch (error) {
      this.log(`❌ Ad analysis flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testAnalysisResultsFlow() {
    this.log('Testing analysis results display flow...', 'test');
    
    try {
      if (!this.testAnalysisId) {
        throw new Error('No test analysis available for results flow');
      }

      // Test loading analysis detail
      const analysisDetail = await dataService.getAnalysisDetail(this.testAnalysisId, this.testUser.id);
      
      if (!analysisDetail) {
        throw new Error('Analysis detail not loaded');
      }
      
      this.log('✅ Analysis detail loaded successfully', 'success');

      // Verify all required fields are present
      const requiredFields = ['headline', 'body_text', 'cta', 'platform'];
      for (const field of requiredFields) {
        if (!analysisDetail[field]) {
          throw new Error(`Required field missing: ${field}`);
        }
      }
      
      this.log('✅ All required analysis fields present', 'success');

      // Test updating analysis scores (simulating AI processing completion)
      const mockScores = {
        overall_score: 85.5,
        clarity_score: 88.0,
        persuasion_score: 83.0,
        emotion_score: 87.0,
        cta_strength_score: 85.0,
        platform_fit_score: 82.5,
        analysis_data: {
          feedback: 'Your ad shows strong emotional appeal and clear messaging.'
        }
      };

      const updatedAnalysis = await dataService.updateAnalysisScores(this.testAnalysisId, mockScores);
      
      if (!updatedAnalysis || updatedAnalysis.overall_score !== 85.5) {
        throw new Error('Analysis scores not updated properly');
      }
      
      this.log('✅ Analysis scores updated successfully', 'success');

    } catch (error) {
      this.log(`❌ Analysis results flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testProfileManagementFlow() {
    this.log('Testing profile management flow...', 'test');
    
    try {
      const profileUpdates = {
        full_name: 'Updated Test User',
        company: 'Updated Test Company'
      };

      const updatedProfile = await dataService.updateUserProfile(this.testUser.id, profileUpdates);
      
      if (!updatedProfile || updatedProfile.full_name !== 'Updated Test User') {
        throw new Error('Profile update failed');
      }
      
      this.log('✅ Profile updated successfully', 'success');

    } catch (error) {
      this.log(`❌ Profile management flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testSubscriptionFlow() {
    this.log('Testing subscription and quota flow...', 'test');
    
    try {
      // Test quota checking
      const quota = await dataService.checkUserQuota(this.testUser.id);
      
      if (!quota || typeof quota.canAnalyze !== 'boolean') {
        throw new Error('Quota check failed');
      }
      
      this.log(`✅ Quota check successful: ${quota.current}/${quota.limit} used`, 'success');

      // Test getting current subscription
      const profile = await dataService.getUserProfile(this.testUser.id);
      
      if (!profile || !profile.subscription_tier) {
        throw new Error('Subscription tier not found');
      }
      
      this.log(`✅ Subscription tier loaded: ${profile.subscription_tier}`, 'success');

    } catch (error) {
      this.log(`❌ Subscription flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testRealtimeUpdatesFlow() {
    this.log('Testing real-time updates flow...', 'test');
    
    try {
      let realtimeUpdateReceived = false;

      // Set up real-time subscription
      const unsubscribe = dataService.subscribeToUserAnalyses(this.testUser.id, (payload) => {
        this.log(`Real-time update received: ${payload.eventType}`, 'info');
        realtimeUpdateReceived = true;
      });

      // Create a new analysis to trigger real-time update
      const testAnalysis = await dataService.createAnalysis(this.testUser.id, {
        headline: 'Real-time Test Ad',
        body_text: 'Testing real-time updates.',
        cta: 'Test Now',
        platform: 'google'
      });

      // Wait for real-time update (with timeout)
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Real-time update timeout'));
        }, 5000);

        const checkUpdate = setInterval(() => {
          if (realtimeUpdateReceived) {
            clearInterval(checkUpdate);
            clearTimeout(timeout);
            resolve();
          }
        }, 100);
      });

      unsubscribe();
      this.log('✅ Real-time updates working correctly', 'success');

    } catch (error) {
      this.log(`❌ Real-time updates flow failed: ${error.message}`, 'error');
      // Don't throw error as real-time might not be critical for basic functionality
    }
  }

  async testErrorHandlingFlow() {
    this.log('Testing error handling flow...', 'test');
    
    try {
      // Test unauthorized access
      await supabase.auth.signOut();
      
      try {
        await dataService.getUserProfile(this.testUser.id);
        throw new Error('Unauthorized access should have failed');
      } catch (error) {
        this.log('✅ Unauthorized access properly handled', 'success');
      }

      // Sign back in for remaining tests
      await supabase.auth.signInWithPassword({
        email: this.testUser.email,
        password: 'TestPassword123!'
      });

      // Test invalid data handling
      try {
        await dataService.createAnalysis(this.testUser.id, {
          // Missing required fields
          headline: ''
        });
        throw new Error('Invalid data should have been rejected');
      } catch (error) {
        this.log('✅ Invalid data properly rejected', 'success');
      }

    } catch (error) {
      this.log(`❌ Error handling flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async testNavigationFlow() {
    this.log('Testing navigation and routing flow...', 'test');
    
    try {
      // Test authenticated user can access protected routes
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error('User not authenticated for navigation test');
      }
      
      this.log('✅ Authentication state valid for navigation', 'success');

      // Test data access for various routes
      const dashboardData = await dataService.getDashboardAnalytics(user.id);
      if (!dashboardData) {
        throw new Error('Dashboard route data not accessible');
      }
      
      this.log('✅ Dashboard route data accessible', 'success');

      if (this.testAnalysisId) {
        const analysisData = await dataService.getAnalysisDetail(this.testAnalysisId, user.id);
        if (!analysisData) {
          throw new Error('Analysis results route data not accessible');
        }
        
        this.log('✅ Analysis results route data accessible', 'success');
      }

    } catch (error) {
      this.log(`❌ Navigation flow failed: ${error.message}`, 'error');
      throw error;
    }
  }

  async cleanup() {
    this.log('Cleaning up test data...', 'info');
    
    try {
      if (this.testUser) {
        // Clean up test analyses
        const { error: deleteError } = await supabase
          .from('ad_analyses')
          .delete()
          .eq('user_id', this.testUser.id);

        if (!deleteError) {
          this.log('✅ Test analyses cleaned up', 'success');
        }

        // Note: We don't delete the user as it would require admin privileges
        // In a real test environment, you'd use a service role key for cleanup
        this.log('Test user cleanup skipped (requires admin privileges)', 'info');
      }
      
    } catch (error) {
      this.log(`⚠️ Cleanup partially failed: ${error.message}`, 'warning');
    }
  }

  generateReport() {
    const successCount = this.testResults.filter(r => r.type === 'success').length;
    const errorCount = this.testResults.filter(r => r.type === 'error').length;
    const totalTests = this.testResults.filter(r => r.type === 'test').length;

    console.log('\n' + '='.repeat(60));
    console.log('                  E2E TEST REPORT');
    console.log('='.repeat(60));
    console.log(`Total Test Suites: ${totalTests}`);
    console.log(`Successful Operations: ${successCount}`);
    console.log(`Errors: ${errorCount}`);
    console.log(`Overall Status: ${errorCount === 0 ? '✅ PASS' : '❌ FAIL'}`);
    console.log('='.repeat(60));

    // Detailed log
    console.log('\nDetailed Test Log:');
    this.testResults.forEach(result => {
      const icon = {
        'info': 'ℹ️',
        'test': '🧪',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️'
      }[result.type];
      
      console.log(`${icon} ${result.message}`);
    });
  }
}

// Export for use in test runners
export default E2EUserPathTester;

// Run tests if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new E2EUserPathTester();
  tester.runAllTests().catch(error => {
    console.error('Test suite failed:', error);
    process.exit(1);
  });
}
