-- ============================================================================
-- AdCopySurge Integrations System Migration
-- Creates tables for user integrations (webhooks, APIs, third-party services)
-- ============================================================================

-- ============================================================================
-- STEP 1: Create integrations table (available integrations catalog)
-- ============================================================================

CREATE TABLE IF NOT EXISTS integrations (
  id TEXT PRIMARY KEY, -- webhook, slack, zapier, api_access, etc.
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL, -- automation, communication, analytics, etc.
  icon_url TEXT,
  status TEXT NOT NULL DEFAULT 'available', -- available, coming_soon, deprecated
  setup_schema JSONB NOT NULL DEFAULT '{}', -- Form fields for setup
  features TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE integrations IS 'Catalog of available integrations';
COMMENT ON COLUMN integrations.setup_schema IS 'JSON schema defining setup form fields and validation';

-- ============================================================================
-- STEP 2: Create user_integrations table (user's configured integrations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  integration_type TEXT NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
  name TEXT NOT NULL, -- User-defined name for this integration
  
  -- Configuration and credentials
  config JSONB NOT NULL DEFAULT '{}', -- Integration-specific configuration
  credentials JSONB NOT NULL DEFAULT '{}', -- Encrypted API keys, tokens, etc.
  
  -- Status and metadata
  status TEXT NOT NULL DEFAULT 'active', -- active, inactive, error, pending
  last_used TIMESTAMPTZ,
  last_sync TIMESTAMPTZ,
  error_message TEXT,
  
  -- Settings
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  auto_sync BOOLEAN NOT NULL DEFAULT FALSE,
  sync_frequency INTEGER DEFAULT 3600, -- seconds between syncs
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT chk_user_integrations_status CHECK (status IN ('active', 'inactive', 'error', 'pending')),
  UNIQUE(user_id, integration_type, name) -- Allow multiple configs per integration type
);

COMMENT ON TABLE user_integrations IS 'User-configured integrations with credentials and settings';
COMMENT ON COLUMN user_integrations.config IS 'Integration-specific configuration (URLs, settings, etc.)';
COMMENT ON COLUMN user_integrations.credentials IS 'Encrypted credentials (API keys, tokens, etc.)';

-- ============================================================================
-- STEP 3: Create integration_logs table (activity and sync history)
-- ============================================================================

CREATE TABLE IF NOT EXISTS integration_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_integration_id UUID NOT NULL REFERENCES user_integrations(id) ON DELETE CASCADE,
  
  -- Log details
  action TEXT NOT NULL, -- sync, send, test, error, etc.
  status TEXT NOT NULL, -- success, error, pending
  message TEXT,
  error_details JSONB,
  
  -- Data transfer info
  records_processed INTEGER DEFAULT 0,
  data_sent JSONB,
  data_received JSONB,
  
  -- Timing
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE integration_logs IS 'Activity logs for integration syncs and operations';

-- ============================================================================
-- STEP 4: Create indexes for performance
-- ============================================================================

-- User integrations indexes
CREATE INDEX IF NOT EXISTS idx_user_integrations_user_id ON user_integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_integrations_type ON user_integrations(integration_type);
CREATE INDEX IF NOT EXISTS idx_user_integrations_status ON user_integrations(status);
CREATE INDEX IF NOT EXISTS idx_user_integrations_enabled ON user_integrations(enabled);
CREATE INDEX IF NOT EXISTS idx_user_integrations_created ON user_integrations(created_at DESC);

-- Integration logs indexes
CREATE INDEX IF NOT EXISTS idx_integration_logs_user_integration ON integration_logs(user_integration_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_action ON integration_logs(action);
CREATE INDEX IF NOT EXISTS idx_integration_logs_status ON integration_logs(status);
CREATE INDEX IF NOT EXISTS idx_integration_logs_created ON integration_logs(created_at DESC);

-- ============================================================================
-- STEP 5: Insert default integrations catalog
-- ============================================================================

INSERT INTO integrations (id, name, description, category, status, setup_schema, features) VALUES
  (
    'webhook',
    'Webhook',
    'Send analysis results to your custom webhook endpoint',
    'automation',
    'available',
    '{
      "fields": [
        {
          "name": "webhook_url",
          "label": "Webhook URL",
          "type": "url",
          "required": true,
          "placeholder": "https://your-app.com/webhook/adcopysurge"
        },
        {
          "name": "secret_token",
          "label": "Secret Token (Optional)",
          "type": "password",
          "required": false,
          "description": "Optional secret token for webhook validation"
        },
        {
          "name": "events",
          "label": "Events to Send",
          "type": "multiselect",
          "required": true,
          "options": ["analysis_completed", "project_created", "team_member_added"],
          "default": ["analysis_completed"]
        }
      ]
    }',
    ARRAY['Real-time notifications', 'Custom data processing', 'Automated workflows']
  ),
  
  (
    'slack',
    'Slack',
    'Get notifications and summaries in your Slack channels',
    'communication',
    'available',
    '{
      "fields": [
        {
          "name": "webhook_url",
          "label": "Slack Webhook URL",
          "type": "url",
          "required": true,
          "placeholder": "https://hooks.slack.com/services/...",
          "description": "Create an Incoming Webhook in your Slack workspace"
        },
        {
          "name": "channel",
          "label": "Channel",
          "type": "text",
          "required": false,
          "placeholder": "#marketing",
          "description": "Override default channel (optional)"
        },
        {
          "name": "mention_users",
          "label": "Mention Users",
          "type": "text",
          "required": false,
          "placeholder": "@john @marketing-team",
          "description": "Users/groups to mention in notifications"
        }
      ]
    }',
    ARRAY['Instant notifications', 'Team collaboration', 'Custom formatting']
  ),
  
  (
    'zapier',
    'Zapier',
    'Connect AdCopySurge to 5000+ apps with Zapier automation',
    'automation',
    'available',
    '{
      "fields": [
        {
          "name": "webhook_url",
          "label": "Zapier Webhook URL",
          "type": "url",
          "required": true,
          "placeholder": "https://hooks.zapier.com/hooks/catch/...",
          "description": "Copy the webhook URL from your Zapier trigger"
        },
        {
          "name": "data_format",
          "label": "Data Format",
          "type": "select",
          "required": true,
          "options": ["full", "summary", "scores_only"],
          "default": "summary",
          "description": "Amount of data to send to Zapier"
        }
      ]
    }',
    ARRAY['5000+ app integrations', 'Multi-step workflows', 'Data transformation']
  ),
  
  (
    'api_access',
    'API Access',
    'Generate API keys for custom integrations and development',
    'developer',
    'available',
    '{
      "fields": [
        {
          "name": "api_name",
          "label": "API Key Name",
          "type": "text",
          "required": true,
          "placeholder": "My Custom Integration",
          "description": "Descriptive name for this API key"
        },
        {
          "name": "permissions",
          "label": "Permissions",
          "type": "multiselect",
          "required": true,
          "options": ["read_analyses", "create_analyses", "read_projects", "create_projects"],
          "default": ["read_analyses"],
          "description": "What this API key can access"
        },
        {
          "name": "rate_limit",
          "label": "Rate Limit (requests/minute)",
          "type": "number",
          "required": true,
          "default": 60,
          "min": 1,
          "max": 1000
        }
      ]
    }',
    ARRAY['RESTful API access', 'Rate limiting', 'Detailed documentation']
  ),
  
  (
    'google_sheets',
    'Google Sheets',
    'Export analysis data directly to Google Sheets',
    'analytics',
    'coming_soon',
    '{
      "fields": [
        {
          "name": "sheet_url",
          "label": "Google Sheet URL",
          "type": "url",
          "required": true,
          "placeholder": "https://docs.google.com/spreadsheets/d/..."
        },
        {
          "name": "worksheet_name",
          "label": "Worksheet Name",
          "type": "text",
          "required": false,
          "default": "AdCopySurge Data"
        }
      ]
    }',
    ARRAY['Automatic data export', 'Real-time updates', 'Custom formatting']
  ),
  
  (
    'microsoft_teams',
    'Microsoft Teams',
    'Get notifications in your Microsoft Teams channels',
    'communication',
    'coming_soon',
    '{
      "fields": [
        {
          "name": "webhook_url",
          "label": "Teams Webhook URL",
          "type": "url",
          "required": true,
          "placeholder": "https://outlook.office.com/webhook/..."
        }
      ]
    }',
    ARRAY['Team notifications', 'Rich card formatting', 'Action buttons']
  )
  
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  category = EXCLUDED.category,
  status = EXCLUDED.status,
  setup_schema = EXCLUDED.setup_schema,
  features = EXCLUDED.features,
  updated_at = NOW();

-- ============================================================================
-- STEP 6: Create updated_at triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables
CREATE TRIGGER update_integrations_updated_at
  BEFORE UPDATE ON integrations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_integrations_updated_at
  BEFORE UPDATE ON user_integrations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- STEP 7: Grant permissions
-- ============================================================================

-- Grant permissions to authenticated users (Supabase pattern)
GRANT ALL ON TABLE integrations TO authenticated;
GRANT ALL ON TABLE user_integrations TO authenticated;
GRANT ALL ON TABLE integration_logs TO authenticated;

-- Grant permissions to service role
GRANT ALL ON TABLE integrations TO service_role;
GRANT ALL ON TABLE user_integrations TO service_role;
GRANT ALL ON TABLE integration_logs TO service_role;

-- ============================================================================
-- STEP 8: Row Level Security (RLS) - Optional, currently disabled for simplicity
-- ============================================================================

-- Disable RLS for now to match existing pattern
ALTER TABLE integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE integration_logs DISABLE ROW LEVEL SECURITY;

-- If you want to enable RLS later, use these policies:
/*
-- Enable RLS
ALTER TABLE user_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_logs ENABLE ROW LEVEL SECURITY;

-- RLS policies for user_integrations
CREATE POLICY "Users can view own integrations" ON user_integrations
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own integrations" ON user_integrations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own integrations" ON user_integrations
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own integrations" ON user_integrations
  FOR DELETE USING (auth.uid() = user_id);

-- RLS policies for integration_logs
CREATE POLICY "Users can view own integration logs" ON integration_logs
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM user_integrations ui 
      WHERE ui.id = user_integration_id AND ui.user_id = auth.uid()
    )
  );
*/

-- ============================================================================
-- VERIFICATION QUERIES (Optional - for testing)
-- ============================================================================

-- Verify tables were created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%integration%';

-- Verify integrations were inserted
-- SELECT id, name, status FROM integrations ORDER BY name;