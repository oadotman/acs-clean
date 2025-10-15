import axios from 'axios';
import { supabase } from '../lib/supabaseClient';
import dataService from './dataService';

class ApiService {
  constructor() {
    // Debug environment variables
    console.log('🔧 Environment variables:', {
      REACT_APP_API_URL: process.env.REACT_APP_API_URL,
      REACT_APP_API_BASE_URL: process.env.REACT_APP_API_BASE_URL,
      NODE_ENV: process.env.NODE_ENV,
      all_env: Object.keys(process.env).filter(key => key.startsWith('REACT_APP'))
    });
    console.log('🚑 Raw REACT_APP_API_URL:', JSON.stringify(process.env.REACT_APP_API_URL));
    
    // API URL configuration for development and production
    let envApiUrl = process.env.REACT_APP_API_URL;
    const envBaseUrl = process.env.REACT_APP_API_BASE_URL;
    const isProduction = process.env.NODE_ENV === 'production';
    
    // Clean up environment variables to remove any malformed content
    if (envApiUrl && typeof envApiUrl === 'string') {
      // Remove any 'EOF' strings or other malformed content
      envApiUrl = envApiUrl.replace(/'EOF'/g, '').replace(/EOF/g, '').replace(/[^\w\d:\/\.-]/g, '');
      if (!envApiUrl.startsWith('http')) {
        envApiUrl = null;
      }
    }
    
    if (isProduction) {
      // In production (Datalix VPS), use relative URLs since frontend and backend are on same server
      this.baseURL = '/api';
      console.log('🏭 Production mode: Using relative API URL for same-server deployment');
    } else {
      // In development, ALWAYS use full localhost URL for proper authentication
      // Force localhost URL to avoid environment variable issues
      this.baseURL = 'http://localhost:8000/api';
      console.log('🔧 Development mode: Using hardcoded localhost URL to avoid env issues');
      console.log('🔗 Development baseURL:', this.baseURL);
    }
    
    // Clean up URL if it has double slashes or malformed content
    this.baseURL = this.baseURL.replace(/([^:])\/{2,}/g, '$1/').replace(/'EOF'/g, '').replace(/EOF/g, '');
    
    console.log('🚀 API Service initialized with baseURL:', this.baseURL);
    console.log('🚑 Final check - baseURL starts with http:', this.baseURL.startsWith('http'));
    
    // Validate the final URL
    try {
      new URL(this.baseURL + '/test');
      console.log('✅ URL validation passed');
    } catch (urlError) {
      console.error('❌ URL validation failed:', urlError);
      this.baseURL = 'http://localhost:8000/api'; // Fallback to safe default
      console.log('🔄 Using fallback baseURL:', this.baseURL);
    }
    // Create separate client for AI operations with longer timeout
    this.aiClient = axios.create({
      baseURL: this.baseURL,
      timeout: 120000, // 2 minutes for AI operations
      headers: {
        'Content-Type': 'application/json',
      }
    });

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // Regular timeout for non-AI operations
      headers: {
        'Content-Type': 'application/json',
      }
    });

    // Setup interceptors for both clients
    const setupInterceptors = (client, clientName) => {
      // Request interceptor to add Supabase auth token
      client.interceptors.request.use(
        async (config) => {
          try {
            // Get current session for authentication
            const { data: { session } } = await supabase.auth.getSession();
            if (session?.access_token) {
              config.headers['Authorization'] = `Bearer ${session.access_token}`;
              console.log(`🔐 Added auth token to ${clientName} request`);
            } else {
              console.log(`⚠️ Making unauthenticated ${clientName} request`);
            }
          } catch (authError) {
            console.warn(`⚠️ Could not get auth session for ${clientName}:`, authError.message);
          }
          
          console.log(`🔗 Making ${clientName} API request to:`, config.baseURL + config.url);
          return config;
        },
        (error) => Promise.reject(error)
      );

      // Response interceptor for error handling
      client.interceptors.response.use(
        (response) => response.data,
        (error) => {
          if (error.code === 'ECONNABORTED') {
            console.error(`⏰ ${clientName} request timed out:`, error.message);
          }
          if (error.response?.status === 401) {
            // Token expired or invalid - redirect to login
            supabase.auth.signOut();
            window.location.href = '/login';
          }
          return Promise.reject(error);
        }
      );
    };

    // Setup interceptors for both clients
    setupInterceptors(this.client, 'Standard');
    setupInterceptors(this.aiClient, 'AI');
  }

  // Integration endpoints
  async createIntegration(userId, integrationData) {
    const response = await fetch(`${this.baseURL}/integrations/user/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify(integrationData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create integration');
    }

    return response.json();
  }

  async getUserIntegrations(userId) {
    const response = await fetch(`${this.baseURL}/integrations/user/${userId}`, {
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch integrations');
    }

    return response.json();
  }

  async updateIntegration(integrationId, updateData) {
    const response = await fetch(`${this.baseURL}/integrations/${integrationId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify(updateData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update integration');
    }

    return response.json();
  }

  async deleteIntegration(integrationId) {
    const response = await fetch(`${this.baseURL}/integrations/${integrationId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete integration');
    }

    return response.json();
  }

  async testIntegration(integrationId) {
    const response = await fetch(`${this.baseURL}/integrations/${integrationId}/test`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to test integration');
    }

    return response.json();
  }

  async sendToIntegrations(userId, eventType, data) {
    const response = await fetch(`${this.baseURL}/integrations/send-to-integrations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify({
        user_id: userId,
        event_type: eventType,
        data: data
      })
    });

    if (!response.ok) {
      console.warn('Failed to send to integrations:', response.statusText);
    }

    return response.json();
  }

  getAuthToken() {
    // Get token from localStorage or auth service
    return localStorage.getItem('auth_token') || 'dummy_token_for_dev';
  }

  setAuthToken(token) {
    this.authToken = token;
  }

  clearAuthToken() {
    this.authToken = null;
  }
  
  // Helper method to check quota
  async checkQuota(userId) {
    return await dataService.checkUserQuota(userId);
  }

  // HTTP method shortcuts
  async get(url) {
    return this.client.get(url);
  }

  async post(url, data) {
    return this.client.post(url, data);
  }

  async put(url, data) {
    return this.client.put(url, data);
  }

  async delete(url) {
    return this.client.delete(url);
  }

  // Auth endpoints
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    return this.client.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async register(userData) {
    return this.client.post('/auth/register', userData);
  }

  async getCurrentUser() {
    return this.client.get('/auth/me');
  }

  // Comprehensive analysis with all 9 tools
  async comprehensiveAnalyze(adCopy, platform) {
    try {
      console.log('🎯 Starting comprehensive analysis...');
      
      // Use getSession instead of getUser to avoid 403 errors
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) {
        throw new Error('User not authenticated');
      }
      const user = session.user;

      // Quota check disabled for testing
      // const quota = await this.checkQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Analysis limit reached. ${quota.remaining || 0} analyses remaining.`);
      // }

      const response = await this.aiClient.post('/ads/comprehensive-analyze', {
        ad_copy: adCopy,
        platform: platform,
        user_id: user.id
      });
      
      return response;
    } catch (error) {
      console.error('Error in comprehensiveAnalyze:', error);
      throw error;
    }
  }

  // Ad analysis endpoints with integrated Supabase + AI processing
  /**
   * @deprecated Use sharedWorkflowService.startAdhocAnalysis() instead.
   * This method is maintained for backward compatibility only.
   * 
   * Legacy single-analysis method. Defaults to compliance-only analysis
   * if no enabledTools are specified.
   */
  async analyzeAd(adData, enabledTools = null) {
    try {
      console.log('🎯 ApiService: Starting ad analysis...', { adData });
      
      // SIMPLIFIED - Skip authentication and Supabase for now to isolate the issue
      console.log('⚠️ ApiService: Using simplified analysis (no auth/db for debugging)');
      
      // Send directly to backend AI service
      const aiRequest = {
        ad: adData.ad,
        competitor_ads: adData.competitor_ads || [],
        user_id: 'debug-user' // Temporary for testing
      };

      console.log('🤖 ApiService: Sending request to backend with extended timeout...', aiRequest);
      
      const aiResponse = await this.aiClient.post('/ads/analyze', aiRequest);
      
      console.log('✅ ApiService: AI analysis completed successfully', aiResponse);

      return {
        analysis_id: aiResponse.analysis_id || 'debug-analysis',
        scores: aiResponse.scores,
        alternatives: aiResponse.alternatives,
        feedback: aiResponse.feedback,
        quick_wins: aiResponse.quick_wins
      };
      
    } catch (error) {
      console.error('❌ ApiService: Error in analyzeAd:', error);
      console.error('❌ ApiService: Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        code: error.code
      });
      
      // Handle timeout specifically
      if (error.code === 'ECONNABORTED') {
        throw new Error('Analysis is taking longer than expected. Our AI is working hard on your request. Please try again.');
      }
      
      throw new Error(`Analysis failed: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getAnalysisHistory(limit = 10, offset = 0) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      return await dataService.getAnalysesHistory(user.id, limit, offset);
    } catch (error) {
      console.error('Error fetching analysis history:', error);
      throw error;
    }
  }

  async getAnalysisDetail(analysisId) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      return await dataService.getAnalysisDetail(analysisId, user.id);
    } catch (error) {
      console.error('Error fetching analysis detail:', error);
      throw error;
    }
  }

  async generateAlternatives(adData) {
    return this.client.post('/ads/generate-alternatives', adData);
  }

  async exportAnalyticsPDF(analysisIds) {
    return this.client.get('/analytics/export/pdf', {
      params: { analysis_ids: analysisIds }
    });
  }

  // Subscription endpoints
  async getSubscriptionPlans() {
    return this.client.get('/subscriptions/plans');
  }

  async getCurrentSubscription() {
    return this.client.get('/subscriptions/current');
  }

  async upgradeSubscription(subscriptionData) {
    return this.client.post('/subscriptions/upgrade', subscriptionData);
  }

  async cancelSubscription() {
    return this.client.post('/subscriptions/cancel');
  }

  // === NEW AI-POWERED TOOLS ===
  
  // 1. Platform Compliance Checker
  async checkCompliance(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Analysis limit reached. ${quota.remaining || 0} analyses remaining.`);
      // }
      
      return this.aiClient.post('/tools/compliance-checker', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in checkCompliance:', error);
      throw error;
    }
  }
  
  // 2. ROI-Driven Copy Generator
  async generateROICopy(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Generation limit reached. ${quota.remaining || 0} generations remaining.`);
      // }
      
      return this.aiClient.post('/tools/roi-generator', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in generateROICopy:', error);
      throw error;
    }
  }
  
  // 3. A/B Test Generator
  async generateABTests(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Generation limit reached. ${quota.remaining || 0} generations remaining.`);
      // }
      
      return this.aiClient.post('/tools/ab-test-generator', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in generateABTests:', error);
      throw error;
    }
  }
  
  // 4. Industry-Specific Optimizer
  async optimizeForIndustry(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Optimization limit reached. ${quota.remaining || 0} optimizations remaining.`);
      // }
      
      return this.aiClient.post('/tools/industry-optimizer', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in optimizeForIndustry:', error);
      throw error;
    }
  }
  
  // 5. Performance Forensics Tool
  async analyzePerformance(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Analysis limit reached. ${quota.remaining || 0} analyses remaining.`);
      // }
      
      return this.aiClient.post('/tools/performance-forensics', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in analyzePerformance:', error);
      throw error;
    }
  }
  
  // 6. Psychology Scorer
  async scorePsychology(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Analysis limit reached. ${quota.remaining || 0} analyses remaining.`);
      // }
      
      return this.aiClient.post('/tools/psychology-scorer', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in scorePsychology:', error);
      throw error;
    }
  }
  
  // 7. Brand Voice Engine
  async alignBrandVoice(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Analysis limit reached. ${quota.remaining || 0} analyses remaining.`);
      // }
      
      return this.aiClient.post('/tools/brand-voice-engine', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in alignBrandVoice:', error);
      throw error;
    }
  }
  
  // 8. Legal Risk Scanner
  async scanLegalRisks(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Analysis limit reached. ${quota.remaining || 0} analyses remaining.`);
      // }
      
      return this.aiClient.post('/tools/legal-risk-scanner', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in scanLegalRisks:', error);
      throw error;
    }
  }

  // === MULTI-INPUT SYSTEM METHODS ===
  
  // Parse pasted ad copy text
  async parsePastedCopy(text, platform = 'facebook') {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      return this.aiClient.post('/ads/parse', {
        text,
        platform,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in parsePastedCopy:', error);
      throw error;
    }
  }
  
  // Parse uploaded files
  async parseFile(formData, options = {}, userId = null) {
    try {
      // Get current user and add auth token (optional for testing)
      const { data: { session } } = await supabase.auth.getSession();
      const user = session?.user;
      
      if (userId) {
        formData.append('user_id', userId);
      }
      
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: options.timeout || 60000, // Default 60 second timeout
        ...options // Spread other options like onUploadProgress
      };
      
      // Add auth token if user is authenticated
      if (user && session) {
        config.headers['Authorization'] = `Bearer ${session.access_token}`;
        console.log('🔐 Adding auth token to file upload request');
      } else {
        console.log('⚠️ File upload without authentication - testing mode');
      }
      
      return this.client.post('/ads/parse-file', formData, config);
    } catch (error) {
      console.error('Error in parseFile:', error);
      if (error.code === 'ECONNABORTED') {
        throw new Error('File upload timed out. Please try with a smaller file.');
      }
      if (error.response?.status === 413) {
        throw new Error('File is too large. Please try with a smaller file.');
      }
      throw error;
    }
  }
  
  // Generate ad copy with AI
  async generateAdCopy(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await this.checkQuotaWithBypass(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Generation limit reached. ${quota.remaining || 0} generations remaining.`);
      // }
      
      return this.aiClient.post('/ads/generate', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in generateAdCopy:', error);
      throw error;
    }
  }
  
  // Analyze multiple ads in batch
  async analyzeAds(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Temporary: Skip quota check for testing
      console.log('⚠️ Skipping quota check for testing - analyzing ads');
      const adsCount = data.ads?.length || 1;
      
      // Use batch endpoint if multiple ads, otherwise single endpoint
      if (adsCount > 1) {
        return this.aiClient.post('/ads/analyze/batch', {
          ...data,
          user_id: user.id
        });
      } else {
        // Single ad - use existing analyzeAd method
        return this.analyzeAd({
          ad: data.ads[0],
          competitor_ads: data.competitor_ads || []
        });
      }
    } catch (error) {
      console.error('Error in analyzeAds:', error);
      throw error;
    }
  }
  
  // === VARIATION GENERATION METHODS ===
  
  // Generate variations for a single ad
  async generateAdVariations(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Generation limit reached. ${quota.remaining || 0} generations remaining.`);
      // }
      
      return this.aiClient.post('/ads/generate-variations', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in generateAdVariations:', error);
      throw error;
    }
  }
  
  // Generate variations for multiple ads
  async generateBatchVariations(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // const adsCount = data.ads?.length || 1;
      // 
      // if (!quota.canAnalyze || (quota.remaining && quota.remaining < adsCount)) {
      //   throw new Error(`Insufficient generation quota. Need ${adsCount} generations, ${quota.remaining || 0} remaining.`);
      // }
      
      return this.aiClient.post('/ads/generate-variations/batch', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in generateBatchVariations:', error);
      throw error;
    }
  }
  
  // Generate variations and auto-analyze with all tools
  async generateAndAnalyzeVariations(data) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('User not authenticated');
      const user = session.user;
      
      // Quota check disabled for testing
      // const quota = await dataService.checkUserQuota(user.id);
      // if (!quota.canAnalyze) {
      //   throw new Error(`Generation limit reached. ${quota.remaining || 0} generations remaining.`);
      // }
      
      return this.aiClient.post('/ads/generate-and-analyze', {
        ...data,
        user_id: user.id
      });
    } catch (error) {
      console.error('Error in generateAndAnalyzeVariations:', error);
      throw error;
    }
  }
}

const apiService = new ApiService();
export default apiService;
