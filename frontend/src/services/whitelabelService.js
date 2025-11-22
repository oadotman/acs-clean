/**
 * Whitelabel API Service
 * Handles all white-label configuration API calls
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Get authorization headers
 */
const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
  };

  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
};

/**
 * Get headers for multipart/form-data (file uploads)
 */
const getMultipartHeaders = () => {
  const headers = {};

  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  // Don't set Content-Type for multipart - browser will set it with boundary
  return headers;
};

/**
 * Create a new agency
 */
export const createAgency = async (name, description = null) => {
  try {
    const response = await fetch(`${API_BASE}/api/whitelabel/agency`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, description })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create agency');
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating agency:', error);
    throw error;
  }
};

/**
 * Get white-label settings for an agency
 */
export const getWhitelabelSettings = async (agencyId) => {
  try {
    const response = await fetch(
      `${API_BASE}/api/whitelabel/settings?agency_id=${agencyId}`,
      {
        method: 'GET',
        headers: getHeaders()
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch settings');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching whitelabel settings:', error);
    throw error;
  }
};

/**
 * Update white-label settings for an agency
 */
export const updateWhitelabelSettings = async (agencyId, settings) => {
  try {
    const response = await fetch(
      `${API_BASE}/api/whitelabel/settings?agency_id=${agencyId}`,
      {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(settings)
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update settings');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating whitelabel settings:', error);
    throw error;
  }
};

/**
 * Upload a logo to Supabase Storage
 */
export const uploadLogo = async (agencyId, file) => {
  try {
    const formData = new FormData();
    formData.append('agency_id', agencyId);
    formData.append('logo', file);

    const response = await fetch(`${API_BASE}/api/whitelabel/logo/upload`, {
      method: 'POST',
      headers: getMultipartHeaders(),
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload logo');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading logo:', error);
    throw error;
  }
};

/**
 * Verify custom domain
 */
export const verifyDomain = async (agencyId, domain, verificationToken = null) => {
  try {
    const response = await fetch(
      `${API_BASE}/api/whitelabel/domain/verify?agency_id=${agencyId}`,
      {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          domain,
          verification_token: verificationToken
        })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to verify domain');
    }

    return await response.json();
  } catch (error) {
    console.error('Error verifying domain:', error);
    throw error;
  }
};

export default {
  createAgency,
  getWhitelabelSettings,
  updateWhitelabelSettings,
  uploadLogo,
  verifyDomain
};
