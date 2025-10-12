import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  ListItemText,
  Typography,
  Box,
  Alert,
  Chip,
  CircularProgress,
  IconButton,
  InputAdornment
} from '@mui/material';
import {
  Close,
  Visibility,
  VisibilityOff,
  Launch,
  ContentCopy
} from '@mui/icons-material';
import IntegrationService from '../../services/integrationService';
import toast from 'react-hot-toast';

const IntegrationSetupDialog = ({ 
  open, 
  onClose, 
  integration, 
  existingConfig = null, 
  onSuccess 
}) => {
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [showSecrets, setShowSecrets] = useState({});
  const [apiKey, setApiKey] = useState(null);

  // Initialize config with defaults or existing values
  useEffect(() => {
    if (integration) {
      const initialConfig = {};
      
      if (integration.setupFields) {
        integration.setupFields.forEach(field => {
          if (existingConfig && existingConfig[field.key] !== undefined) {
            initialConfig[field.key] = existingConfig[field.key];
          } else if (field.default !== undefined) {
            initialConfig[field.key] = field.default;
          } else {
            initialConfig[field.key] = field.type === 'multiselect' ? [] : '';
          }
        });
      }
      
      setConfig(initialConfig);
    }
  }, [integration, existingConfig]);

  const handleFieldChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field.key]: value
    }));
    
    // Clear test result when config changes
    if (testResult) {
      setTestResult(null);
    }
  };

  const handleTest = async () => {
    if (!integration) return;
    
    setTesting(true);
    try {
      const result = await IntegrationService.testIntegration(integration.id, config);
      setTestResult(result);
      
      if (result.success) {
        toast.success(result.message || 'Integration test passed!');
      } else {
        toast.error(result.error || 'Integration test failed');
      }
    } catch (error) {
      console.error('Test failed:', error);
      setTestResult({ success: false, error: error.message });
      toast.error('Failed to test integration');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!integration) return;
    
    setLoading(true);
    try {
      let result;
      
      // For API integration, generate an API key
      if (integration.id === 'api' && !existingConfig) {
        const generatedKey = IntegrationService.generateApiKey();
        setApiKey(generatedKey);
        const configWithKey = { ...config, api_key: generatedKey };
        result = await IntegrationService.connectIntegration(
          window.user?.id, // Would normally get from auth context
          integration.id,
          configWithKey
        );
      } else if (existingConfig) {
        // Update existing integration
        result = await IntegrationService.updateIntegration(
          existingConfig.id,
          config
        );
      } else {
        // Create new integration
        result = await IntegrationService.connectIntegration(
          window.user?.id, // Would normally get from auth context
          integration.id,
          config
        );
      }
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      // Don't close immediately for API integration so user can copy key
      if (integration.id !== 'api' || existingConfig) {
        onClose();
      }
    } catch (error) {
      console.error('Save failed:', error);
      // Error already shown by service
    } finally {
      setLoading(false);
    }
  };

  const handleCopyApiKey = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      toast.success('API key copied to clipboard!');
    }
  };

  const toggleShowSecret = (fieldKey) => {
    setShowSecrets(prev => ({
      ...prev,
      [fieldKey]: !prev[fieldKey]
    }));
  };

  const renderField = (field) => {
    switch (field.type) {
      case 'text':
      case 'url':
        return (
          <TextField
            key={field.key}
            fullWidth
            label={field.label}
            type={field.type === 'url' ? 'url' : 'text'}
            value={config[field.key] || ''}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
            error={field.required && !config[field.key]}
            helperText={field.required && !config[field.key] ? `${field.label} is required` : ''}
            sx={{ mb: 2 }}
          />
        );

      case 'password':
        return (
          <TextField
            key={field.key}
            fullWidth
            label={field.label}
            type={showSecrets[field.key] ? 'text' : 'password'}
            value={config[field.key] || ''}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
            error={field.required && !config[field.key]}
            helperText={field.required && !config[field.key] ? `${field.label} is required` : ''}
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => toggleShowSecret(field.key)}
                    edge="end"
                  >
                    {showSecrets[field.key] ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
        );

      case 'multiselect':
        return (
          <FormControl key={field.key} fullWidth sx={{ mb: 2 }}>
            <InputLabel>{field.label}</InputLabel>
            <Select
              multiple
              value={config[field.key] || []}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => {
                    const option = field.options.find(opt => opt.value === value);
                    return (
                      <Chip key={value} label={option?.label || value} size="small" />
                    );
                  })}
                </Box>
              )}
            >
              {field.options.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  <Checkbox checked={(config[field.key] || []).includes(option.value)} />
                  <ListItemText primary={option.label} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );

      default:
        return null;
    }
  };

  if (!integration) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        pb: 1
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ fontSize: '2rem' }}>{integration.icon}</Box>
          <Box>
            <Typography variant="h6">
              {existingConfig ? 'Update' : 'Connect'} {integration.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {integration.description}
            </Typography>
          </Box>
        </Box>
        <IconButton onClick={onClose}>
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        {/* External setup notice */}
        {integration.externalSetup && (
          <Alert severity="info" sx={{ mb: 2 }}>
            This integration requires setup on an external platform.{' '}
            <Button
              size="small"
              endIcon={<Launch />}
              href={integration.setupUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              Set up on {integration.name}
            </Button>
          </Alert>
        )}

        {/* Configuration fields */}
        {integration.configurable && integration.setupFields && (
          <Box sx={{ mt: 2 }}>
            {integration.setupFields.map(renderField)}
          </Box>
        )}

        {/* Test result */}
        {testResult && (
          <Alert 
            severity={testResult.success ? 'success' : 'error'}
            sx={{ mt: 2 }}
          >
            {testResult.message || testResult.error}
          </Alert>
        )}

        {/* API Key display */}
        {apiKey && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Your API Key (save this securely):
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              p: 1,
              bgcolor: 'rgba(0,0,0,0.1)',
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              wordBreak: 'break-all'
            }}>
              {apiKey}
              <IconButton size="small" onClick={handleCopyApiKey}>
                <ContentCopy fontSize="small" />
              </IconButton>
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              This API key will not be shown again. Store it securely.
            </Typography>
          </Alert>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2.5, pt: 1 }}>
        <Button onClick={onClose}>
          Cancel
        </Button>
        
        {/* Test button */}
        {integration.configurable && !apiKey && (
          <Button
            onClick={handleTest}
            disabled={testing || !Object.keys(config).length}
            startIcon={testing && <CircularProgress size={16} />}
          >
            {testing ? 'Testing...' : 'Test'}
          </Button>
        )}
        
        {/* Save/Connect button */}
        {apiKey ? (
          <Button onClick={onClose} variant="contained">
            Done
          </Button>
        ) : (
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={loading || (integration.configurable && testResult && !testResult.success)}
            startIcon={loading && <CircularProgress size={16} />}
          >
            {loading ? 'Saving...' : existingConfig ? 'Update' : 'Connect'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default IntegrationSetupDialog;