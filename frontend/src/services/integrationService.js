import { supabase } from '../lib/supabaseClientClean';
import toast from 'react-hot-toast';

export class IntegrationService {
  // Available integration types with real implementation details
  static AVAILABLE_INTEGRATIONS = {
    webhook: {
      id: 'webhook',
      name: 'Webhook Integration',
      description: 'Send analysis results to your custom endpoints in real-time',
      category: 'Developer Tools',
      icon: '🔗',
      features: ['Custom endpoints', 'Real-time data', 'JSON payloads', 'Retry logic'],
      status: 'available',
      configurable: true,
      setupFields: [
        {
          key: 'url',
          label: 'Webhook URL',
          type: 'url',
          required: true,
          placeholder: 'https://your-app.com/webhooks/adcopysurge'
        },
        {
          key: 'secret',
          label: 'Secret Key (Optional)',
          type: 'password',
          required: false,
          placeholder: 'For webhook signature verification'
        },
        {
          key: 'events',
          label: 'Events to Send',
          type: 'multiselect',
          required: true,
          options: [
            { value: 'analysis_completed', label: 'Analysis Completed' },
            { value: 'analysis_failed', label: 'Analysis Failed' },
            { value: 'report_generated', label: 'Report Generated' }
          ],
          default: ['analysis_completed']
        }
      ]
    },
    slack: {
      id: 'slack',
      name: 'Slack Notifications',
      description: 'Get analysis notifications and summaries in your Slack workspace',
      category: 'Communication',
      icon: '💬',
      features: ['Channel notifications', 'Direct messages', 'Daily summaries', 'Interactive buttons'],
      status: 'available',
      configurable: true,
      oauthUrl: process.env.REACT_APP_SLACK_OAUTH_URL,
      setupFields: [
        {
          key: 'channel',
          label: 'Default Channel',
          type: 'text',
          required: true,
          placeholder: '#general'
        },
        {
          key: 'notify_on',
          label: 'Notification Triggers',
          type: 'multiselect',
          required: true,
          options: [
            { value: 'low_score', label: 'Low Analysis Scores (< 6.0)' },
            { value: 'high_score', label: 'High Analysis Scores (> 8.0)' },
            { value: 'daily_summary', label: 'Daily Summary' },
            { value: 'all_analyses', label: 'All Analyses' }
          ],
          default: ['low_score', 'high_score', 'daily_summary']
        }
      ]
    },
    zapier: {
      id: 'zapier',
      name: 'Zapier',
      description: 'Connect AdCopySurge with 8,000+ apps through the world\'s leading automation platform. Build powerful multi-step workflows without code and streamline your entire ad analysis process with pre-built templates and enterprise-grade reliability.',
      category: 'Automation',
      icon: '⚡',
      features: ['8,000+ app integrations', 'No-code workflow builder', 'Pre-built templates', 'Multi-step automation', 'Enterprise reliability', 'Instant synchronization'],
      status: 'available',
      configurable: true,
      setupGuideUrl: '/docs/zapier-setup-guide.md',
      externalSetupUrl: 'https://zapier.com/app/editor',
      setupFields: [
        {
          key: 'webhook_url',
          label: 'Zapier Webhook URL',
          type: 'url',
          required: true,
          placeholder: 'https://hooks.zapier.com/hooks/catch/...',
          description: 'Copy this URL from your Zapier trigger setup'
        },
        {
          key: 'data_format',
          label: 'Data Format',
          type: 'select',
          required: true,
          options: [
            { value: 'summary', label: 'Summary (Recommended)' },
            { value: 'full', label: 'Full Analysis Data' },
            { value: 'scores_only', label: 'Scores Only' }
          ],
          default: 'summary',
          description: 'How much data to send to Zapier'
        }
      ]
    },
    n8n: {
      id: 'n8n',
      name: 'n8n',
      description: 'Open-source workflow automation platform that gives you complete control over your data and processes. Self-host for maximum privacy, customize with JavaScript, and connect to 400+ apps without vendor lock-in or recurring fees.',
      category: 'Automation',
      icon: '🔄',
      features: ['Open-source & self-hosted', '400+ native integrations', 'Visual workflow editor', 'Custom JavaScript code', 'Complete data privacy', 'No vendor lock-in'],
      status: 'available',
      configurable: true,
      setupGuideUrl: '/docs/n8n-setup-guide.md',
      externalSetupUrl: 'https://n8n.io/cloud',
      setupFields: [
        {
          key: 'webhook_url',
          label: 'n8n Webhook URL',
          type: 'url',
          required: true,
          placeholder: 'https://your-n8n-instance.com/webhook/...',
          description: 'Copy the webhook URL from your n8n workflow'
        },
        {
          key: 'data_format',
          label: 'Data Format',
          type: 'select',
          required: true,
          options: [
            { value: 'summary', label: 'Summary (Recommended)' },
            { value: 'full', label: 'Full Analysis Data' },
            { value: 'scores_only', label: 'Scores Only' }
          ],
          default: 'summary',
          description: 'Amount of data to send to your n8n workflow'
        }
      ]
    },
    api: {
      id: 'api',
      name: 'REST API Access',
      description: 'Direct API access with authentication tokens',
      category: 'Developer Tools',
      icon: '💻',
      features: ['REST endpoints', 'Authentication tokens', 'Rate limiting', 'Comprehensive docs'],
      status: 'available',
      configurable: true,
      setupFields: [
        {
          key: 'name',
          label: 'API Key Name',
          type: 'text',
          required: true,
          placeholder: 'My Integration'
        },
        {
          key: 'permissions',
          label: 'Permissions',
          type: 'multiselect',
          required: true,
          options: [
            { value: 'analyses.read', label: 'Read Analyses' },
            { value: 'analyses.write', label: 'Create Analyses' },
            { value: 'reports.read', label: 'Read Reports' },
            { value: 'reports.write', label: 'Generate Reports' }
          ],
          default: ['analyses.read']
        }
      ]
    }
  };

  // Get user's integrations from database
  static async getUserIntegrations(userId) {
    try {
      const { data, error } = await supabase
        .from('user_integrations')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Failed to fetch user integrations:', error);
        
        // If table doesn't exist (404), return empty array gracefully
        if (error.code === 'PGRST116' || error.message?.includes('does not exist') || error.code === '42P01') {
          console.log('⚠️ user_integrations table not found - returning empty integrations list');
          return [];
        }
        
        throw error;
      }

      return data || [];
    } catch (error) {
      console.error('Error getting user integrations:', error);
      
      // Check if it's a network error or table doesn't exist
      if (error.message?.includes('404') || error.message?.includes('does not exist')) {
        console.log('⚠️ Integrations feature not yet set up - showing available integrations only');
        return [];
      }
      
      // Only show error toast for actual errors, not missing tables
      toast.error('Failed to load integrations');
      return [];
    }
  }

  // Connect a new integration
  static async connectIntegration(userId, integrationType, config = {}) {
    try {
      const integration = this.AVAILABLE_INTEGRATIONS[integrationType];
      if (!integration) {
        throw new Error('Invalid integration type');
      }

      // Validate configuration
      if (integration.configurable && integration.setupFields) {
        this.validateConfig(integration.setupFields, config);
      }

      // Test the integration before saving
      const testResult = await this.testIntegration(integrationType, config);
      if (!testResult.success) {
        throw new Error(testResult.error || 'Integration test failed');
      }

      const { data, error } = await supabase
        .from('user_integrations')
        .insert([
          {
            user_id: userId,
            integration_type: integrationType,
            config: config,
            status: 'active',
            last_used: new Date().toISOString()
          }
        ])
        .select()
        .single();

      if (error) {
        console.error('Failed to save integration:', error);
        throw error;
      }

      toast.success(`${integration.name} connected successfully!`);
      return data;
    } catch (error) {
      console.error('Error connecting integration:', error);
      toast.error(error.message || 'Failed to connect integration');
      throw error;
    }
  }

  // Update an existing integration
  static async updateIntegration(integrationId, config) {
    try {
      const { data, error } = await supabase
        .from('user_integrations')
        .update({
          config: config,
          updated_at: new Date().toISOString()
        })
        .eq('id', integrationId)
        .select()
        .single();

      if (error) {
        console.error('Failed to update integration:', error);
        throw error;
      }

      toast.success('Integration updated successfully!');
      return data;
    } catch (error) {
      console.error('Error updating integration:', error);
      toast.error(error.message || 'Failed to update integration');
      throw error;
    }
  }

  // Disconnect an integration
  static async disconnectIntegration(integrationId) {
    try {
      const { error } = await supabase
        .from('user_integrations')
        .delete()
        .eq('id', integrationId);

      if (error) {
        console.error('Failed to disconnect integration:', error);
        throw error;
      }

      toast.success('Integration disconnected successfully!');
    } catch (error) {
      console.error('Error disconnecting integration:', error);
      toast.error(error.message || 'Failed to disconnect integration');
      throw error;
    }
  }

  // Toggle integration active status
  static async toggleIntegration(integrationId, active) {
    try {
      const { data, error } = await supabase
        .from('user_integrations')
        .update({
          status: active ? 'active' : 'inactive',
          updated_at: new Date().toISOString()
        })
        .eq('id', integrationId)
        .select()
        .single();

      if (error) {
        console.error('Failed to toggle integration:', error);
        throw error;
      }

      toast.success(`Integration ${active ? 'enabled' : 'disabled'}`);
      return data;
    } catch (error) {
      console.error('Error toggling integration:', error);
      toast.error(error.message || 'Failed to update integration');
      throw error;
    }
  }

  // Test integration connectivity
  static async testIntegration(integrationType, config) {
    try {
      switch (integrationType) {
        case 'webhook':
          return await this.testWebhook(config);
        case 'slack':
          return await this.testSlack(config);
        case 'zapier':
          return await this.testZapier(config);
        case 'n8n':
          return await this.testN8n(config);
        case 'api':
          return await this.testApi(config);
        default:
          return { success: true, message: 'Integration available' };
      }
    } catch (error) {
      console.error('Integration test failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Test webhook endpoint
  static async testWebhook(config) {
    try {
      const testPayload = {
        test: true,
        timestamp: new Date().toISOString(),
        event: 'connection_test',
        data: {
          message: 'This is a test webhook from AdCopySurge'
        }
      };

      const response = await fetch(config.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(config.secret && { 'X-AdCopySurge-Secret': config.secret })
        },
        body: JSON.stringify(testPayload)
      });

      if (!response.ok) {
        throw new Error(`Webhook test failed: ${response.status} ${response.statusText}`);
      }

      return { success: true, message: 'Webhook endpoint is reachable' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Test Slack configuration (simplified)
  static async testSlack(config) {
    // In a real implementation, this would verify the Slack token
    // For now, just validate the channel format
    if (!config.channel || !config.channel.startsWith('#')) {
      return { success: false, error: 'Channel must start with #' };
    }
    return { success: true, message: 'Slack configuration valid' };
  }

  // Test Zapier webhook
  static async testZapier(config) {
    try {
      if (!config.webhook_url) {
        return { success: false, error: 'Zapier webhook URL is required' };
      }

      const testPayload = {
        test: true,
        timestamp: new Date().toISOString(),
        event: 'connection_test',
        data: {
          message: 'Test connection from AdCopySurge',
          platform: 'test',
          score: 8.5
        }
      };

      const response = await fetch(config.webhook_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testPayload)
      });

      if (!response.ok) {
        throw new Error(`Zapier webhook test failed: ${response.status} ${response.statusText}`);
      }

      return { success: true, message: 'Zapier webhook connected successfully' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Test n8n webhook
  static async testN8n(config) {
    try {
      if (!config.webhook_url) {
        return { success: false, error: 'n8n webhook URL is required' };
      }

      const testPayload = {
        test: true,
        timestamp: new Date().toISOString(),
        event: 'connection_test',
        data: {
          message: 'Test connection from AdCopySurge',
          platform: 'test',
          score: 8.5
        }
      };

      const response = await fetch(config.webhook_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testPayload)
      });

      if (!response.ok) {
        throw new Error(`n8n webhook test failed: ${response.status} ${response.statusText}`);
      }

      return { success: true, message: 'n8n webhook connected successfully' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Test API configuration
  static async testApi(config) {
    // Validate permissions
    if (!config.permissions || config.permissions.length === 0) {
      return { success: false, error: 'At least one permission is required' };
    }
    return { success: true, message: 'API configuration valid' };
  }

  // Generate API key for API integration
  static generateApiKey() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const prefix = 'acs_';
    let key = prefix;
    for (let i = 0; i < 32; i++) {
      key += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return key;
  }

  // Validate integration configuration
  static validateConfig(fields, config) {
    for (const field of fields) {
      if (field.required && (!config[field.key] || config[field.key].length === 0)) {
        throw new Error(`${field.label} is required`);
      }

      if (field.type === 'url' && config[field.key]) {
        try {
          new URL(config[field.key]);
        } catch {
          throw new Error(`${field.label} must be a valid URL`);
        }
      }
    }
  }

  // Send data to connected integrations
  static async sendToIntegrations(userId, eventType, data) {
    try {
      const integrations = await this.getUserIntegrations(userId);
      const activeIntegrations = integrations.filter(i => i.status === 'active');

      const promises = activeIntegrations.map(integration => 
        this.sendToIntegration(integration, eventType, data)
      );

      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Error sending to integrations:', error);
    }
  }

  // Send data to a specific integration
  static async sendToIntegration(integration, eventType, data) {
    try {
      switch (integration.integration_type) {
        case 'webhook':
          await this.sendWebhook(integration.config, eventType, data);
          break;
        case 'slack':
          await this.sendSlackNotification(integration.config, eventType, data);
          break;
        case 'zapier':
          await this.sendZapier(integration.config, eventType, data);
          break;
        case 'n8n':
          await this.sendN8n(integration.config, eventType, data);
          break;
        default:
          console.log(`Integration type ${integration.integration_type} not implemented for sending`);
      }

      // Update last used timestamp
      await supabase
        .from('user_integrations')
        .update({ last_used: new Date().toISOString() })
        .eq('id', integration.id);

    } catch (error) {
      console.error(`Error sending to ${integration.integration_type}:`, error);
    }
  }

  // Send webhook
  static async sendWebhook(config, eventType, data) {
    if (!config.events || !config.events.includes(eventType)) {
      return; // Event not subscribed
    }

    const payload = {
      event: eventType,
      timestamp: new Date().toISOString(),
      data: data
    };

    await fetch(config.url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(config.secret && { 'X-AdCopySurge-Secret': config.secret })
      },
      body: JSON.stringify(payload)
    });
  }

  // Send Slack notification (simplified - would use Slack API in production)
  static async sendSlackNotification(config, eventType, data) {
    if (!config.notify_on || !config.notify_on.includes(eventType)) {
      return; // Event not subscribed
    }

    // In production, this would use the Slack Web API
    console.log(`Would send Slack notification to ${config.channel}:`, {
      eventType,
      data
    });
  }

  // Send data to Zapier
  static async sendZapier(config, eventType, data) {
    if (!config.webhook_url) {
      console.error('Zapier webhook URL not configured');
      return;
    }

    // Format data based on config
    let payload_data;
    const data_format = config.data_format || 'summary';

    if (data_format === 'scores_only') {
      payload_data = {
        score: data.score,
        platform: data.platform,
        improvement: data.improvement
      };
    } else if (data_format === 'full') {
      payload_data = data;
    } else {
      payload_data = {
        score: data.score,
        platform: data.platform,
        improvement: data.improvement,
        top_insights: data.insights?.slice(0, 3) || []
      };
    }

    const payload = {
      event: eventType,
      timestamp: new Date().toISOString(),
      data: payload_data
    };

    await fetch(config.webhook_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
  }

  // Send data to n8n
  static async sendN8n(config, eventType, data) {
    if (!config.webhook_url) {
      console.error('n8n webhook URL not configured');
      return;
    }

    // Format data based on config
    let payload_data;
    const data_format = config.data_format || 'summary';

    if (data_format === 'scores_only') {
      payload_data = {
        score: data.score,
        platform: data.platform,
        improvement: data.improvement
      };
    } else if (data_format === 'full') {
      payload_data = data;
    } else {
      payload_data = {
        score: data.score,
        platform: data.platform,
        improvement: data.improvement,
        top_insights: data.insights?.slice(0, 3) || []
      };
    }

    const payload = {
      event: eventType,
      timestamp: new Date().toISOString(),
      data: payload_data
    };

    await fetch(config.webhook_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
  }
}

export default IntegrationService;