/**
 * White-label API service for backend integration
 * Handles logo upload, domain validation, and email testing with real backend API
 */

import { supabase } from '../lib/supabaseClientClean';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class WhiteLabelApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Get auth headers with bearer token
  async getAuthHeaders() {
    try {
      // For development/testing, skip authentication for now
      // In production, use proper Supabase authentication
      return {
        'Content-Type': 'application/json'
      };
      
      // Commented out for testing - enable for production:
      /*
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      
      if (!token) {
        throw new Error('No authentication token available');
      }

      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      */
    } catch (error) {
      console.error('Error getting auth headers:', error);
      return {
        'Content-Type': 'application/json'
      };
    }
  }

  // Get auth headers for file upload (multipart/form-data)
  async getFileUploadHeaders() {
    try {
      // For development/testing, skip authentication for now
      return {}; // Let browser set Content-Type for file uploads
      
      // Commented out for testing - enable for production:
      /*
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      
      if (!token) {
        throw new Error('No authentication token available');
      }

      return {
        'Authorization': `Bearer ${token}`
        // Don't set Content-Type for file uploads - let browser set it
      };
      */
    } catch (error) {
      console.error('Error getting file upload headers:', error);
      return {};
    }
  }

  /**
   * Upload logo to backend
   */
  async uploadLogo(file) {
    try {
      console.log('🔄 Uploading logo to backend:', file.name);
      
      // Validate file client-side first
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        throw new Error('File size must be less than 5MB');
      }

      const allowedTypes = ['image/jpeg', 'image/png', 'image/svg+xml', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        throw new Error('Invalid file type. Please use JPEG, PNG, SVG, or WebP format');
      }

      // Prepare form data
      const formData = new FormData();
      formData.append('logo', file);
      formData.append('user_id', 'demo_user'); // For testing

      // Get auth headers
      const headers = await this.getFileUploadHeaders();

      // Make API request
      const response = await fetch(`${this.baseUrl}/whitelabel/upload-logo`, {
        method: 'POST',
        headers,
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        console.log('✅ Logo uploaded successfully:', result.logo_url);
        return {
          success: true,
          data: {
            url: result.logo_url,
            thumbnailUrl: result.thumbnail_url,
            fileSize: result.file_size,
            dimensions: result.dimensions
          }
        };
      } else {
        throw new Error(result.error || 'Upload failed');
      }

    } catch (error) {
      console.error('❌ Logo upload error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Delete logo from backend
   */
  async deleteLogo() {
    try {
      const headers = await this.getAuthHeaders();

      const response = await fetch(`${this.baseUrl}/whitelabel/logo`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Delete failed');
      }

      const result = await response.json();
      return result;

    } catch (error) {
      console.error('Error deleting logo:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Save white-label settings to backend
   */
  async saveSettings(settings) {
    try {
      console.log('🔄 Saving white-label settings to backend...');
      
      const headers = await this.getAuthHeaders();

      const response = await fetch(`${this.baseUrl}/whitelabel/settings?user_id=demo_user`, {
        method: 'POST',
        headers,
        body: JSON.stringify(settings)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Save failed');
      }

      const result = await response.json();
      console.log('✅ Settings saved successfully');
      return result;

    } catch (error) {
      console.error('❌ Error saving settings:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Load white-label settings from backend
   */
  async loadSettings() {
    try {
      const headers = await this.getAuthHeaders();

      const response = await fetch(`${this.baseUrl}/whitelabel/settings/demo_user`, {
        method: 'GET',
        headers
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Load failed');
      }

      const result = await response.json();
      return result;

    } catch (error) {
      console.error('Error loading settings:', error);
      return {
        success: false,
        error: error.message,
        settings: null
      };
    }
  }

  /**
   * Validate custom domain
   */
  async validateDomain(domain) {
    try {
      console.log('🔄 Validating domain:', domain);
      
      const headers = await this.getAuthHeaders();

      const response = await fetch(`${this.baseUrl}/whitelabel/validate-domain`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ domain })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Validation failed');
      }

      const result = await response.json();
      console.log('✅ Domain validation result:', result.valid ? 'Valid' : 'Invalid');
      return result;

    } catch (error) {
      console.error('❌ Domain validation error:', error);
      return {
        domain: domain,
        valid: false,
        available: false,
        error: error.message
      };
    }
  }

  /**
   * Test support email functionality
   */
  async testEmail(email) {
    try {
      console.log('🔄 Testing support email:', email);
      
      const headers = await this.getAuthHeaders();

      const response = await fetch(`${this.baseUrl}/whitelabel/test-email`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ email })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Email test failed');
      }

      const result = await response.json();
      console.log('✅ Test email sent successfully');
      return result;

    } catch (error) {
      console.error('❌ Email test error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Generate preview URL
   */
  async generatePreviewUrl() {
    try {
      console.log('🔄 Generating preview URL...');
      
      const headers = await this.getAuthHeaders();

      const response = await fetch(`${this.baseUrl}/whitelabel/generate-preview-url`, {
        method: 'POST',
        headers
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Preview generation failed');
      }

      const result = await response.json();
      console.log('✅ Preview URL generated:', result.preview_url);
      return result;

    } catch (error) {
      console.error('❌ Preview generation error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get preview settings (public endpoint)
   */
  async getPreviewSettings(token) {
    try {
      const response = await fetch(`${this.baseUrl}/whitelabel/preview/${token}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Preview not found');
      }

      const result = await response.json();
      return result;

    } catch (error) {
      console.error('Error loading preview settings:', error);
      return {
        success: false,
        error: error.message,
        settings: null
      };
    }
  }

  /**
   * Check if backend API is available
   */
  async checkApiHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/whitelabel/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      return {
        available: response.ok,
        status: response.status
      };

    } catch (error) {
      console.warn('Backend API not available, using localStorage fallback');
      return {
        available: false,
        error: error.message
      };
    }
  }
}

// Export singleton instance
export const whiteLabelApiService = new WhiteLabelApiService();
export default whiteLabelApiService;