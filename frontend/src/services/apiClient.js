// Simple API Client for making HTTP requests
// Handles authentication, error handling, and response formatting

class ApiClient {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
  }

  /**
   * Get authorization headers for API requests
   * @returns {Object} Headers object
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    // Add authorization token if available
    // First try custom authToken (for backwards compatibility)
    let token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');

    // If not found, try Supabase token
    if (!token) {
      try {
        const supabaseAuth = localStorage.getItem('adcopysurge-supabase-auth-token');
        if (supabaseAuth) {
          const authData = JSON.parse(supabaseAuth);
          token = authData.access_token;
        }
      } catch (e) {
        // Ignore parse errors
      }
    }

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Make a GET request
   * @param {string} url - API endpoint
   * @returns {Promise<Object>} Response data
   */
  async get(url) {
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Check if the response is actually JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        if (text.startsWith('<!DOCTYPE')) {
          throw new Error(`API endpoint returned HTML instead of JSON. Endpoint may not exist: ${url}`);
        }
        throw new Error(`API endpoint returned unexpected content type: ${contentType}`);
      }

      const data = await response.json();
      return { data, status: response.status };
    } catch (error) {
      // Only log detailed errors in development
      if (process.env.NODE_ENV === 'development') {
        console.warn(`API GET request failed for ${url}:`, error.message);
      }
      throw error;
    }
  }

  /**
   * Make a POST request
   * @param {string} url - API endpoint
   * @param {Object} data - Request body data
   * @returns {Promise<Object>} Response data
   */
  async post(url, data = {}) {
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      return { data: responseData, status: response.status };
    } catch (error) {
      console.error('API POST request failed:', error);
      throw error;
    }
  }

  /**
   * Make a PUT request
   * @param {string} url - API endpoint
   * @param {Object} data - Request body data
   * @returns {Promise<Object>} Response data
   */
  async put(url, data = {}) {
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      return { data: responseData, status: response.status };
    } catch (error) {
      console.error('API PUT request failed:', error);
      throw error;
    }
  }

  /**
   * Make a DELETE request
   * @param {string} url - API endpoint
   * @returns {Promise<Object>} Response data
   */
  async delete(url) {
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // DELETE requests might not return content
      let data = {};
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      }

      return { data, status: response.status };
    } catch (error) {
      console.error('API DELETE request failed:', error);
      throw error;
    }
  }
}

// Export singleton instance with backend URL from environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
// Ensure base URL ends with /api for all API routes
const baseWithApi = API_BASE_URL.endsWith('/api') ? API_BASE_URL : `${API_BASE_URL}/api`;
const apiClient = new ApiClient(baseWithApi);
export default apiClient;
