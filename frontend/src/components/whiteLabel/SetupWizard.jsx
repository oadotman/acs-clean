import React, { useState, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Paper,
  Typography,
  TextField,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Stack,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Collapse,
  IconButton,
  InputAdornment
} from '@mui/material';
import {
  Business,
  Palette,
  Language,
  Visibility,
  CheckCircle,
  RadioButtonUnchecked,
  ExpandMore,
  ExpandLess,
  Upload,
  ContentCopy,
  Refresh,
  Launch,
  Warning,
  Info
} from '@mui/icons-material';
import { useWhiteLabel } from '../../contexts/WhiteLabelContext';
import { BrandingPreviewCard, BrandLogo } from './BrandingComponents';
import { FileUploadService } from '../../services/fileUploadService';
import { DomainService } from '../../services/domainService';
import toast from 'react-hot-toast';

const STEPS = [
  {
    id: 'branding',
    label: 'Company Branding',
    icon: Business,
    description: 'Set up your company name, logo, and brand colors'
  },
  {
    id: 'colors',
    label: 'Color Scheme',
    icon: Palette,
    description: 'Choose primary and secondary colors for your brand'
  },
  {
    id: 'domain',
    label: 'Custom Domain',
    icon: Language,
    description: 'Configure your custom domain (optional)'
  },
  {
    id: 'preview',
    label: 'Preview & Launch',
    icon: Visibility,
    description: 'Review your settings and launch your white-label platform'
  }
];

const StepBranding = ({ data, onChange, errors }) => {
  const [logoFile, setLogoFile] = useState(null);
  const [logoUploading, setLogoUploading] = useState(false);
  const [logoPreview, setLogoPreview] = useState(data.logo);

  const handleLogoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLogoUploading(true);
    try {
      const result = await FileUploadService.uploadLogo(file);
      
      if (result.success) {
        setLogoFile(result.data.file);
        setLogoPreview(result.data.base64);
        onChange('logo', result.data.base64);
        toast.success('Logo uploaded successfully!');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      console.error('Logo upload error:', error);
      toast.error('Failed to upload logo');
    } finally {
      setLogoUploading(false);
    }
  };

  const removeLogo = () => {
    setLogoFile(null);
    setLogoPreview(null);
    onChange('logo', null);
    if (logoPreview && logoPreview.startsWith('blob:')) {
      FileUploadService.cleanupPreviewUrl(logoPreview);
    }
  };

  useEffect(() => {
    return () => {
      if (logoPreview && logoPreview.startsWith('blob:')) {
        FileUploadService.cleanupPreviewUrl(logoPreview);
      }
    };
  }, [logoPreview]);

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Company Information
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Company Name"
            value={data.companyName || ''}
            onChange={(e) => onChange('companyName', e.target.value)}
            error={!!errors.companyName}
            helperText={errors.companyName || 'This will appear throughout your platform'}
            required
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Support Email"
            type="email"
            value={data.customSupportEmail || ''}
            onChange={(e) => onChange('customSupportEmail', e.target.value)}
            helperText="Custom support email for your users"
          />
        </Grid>
        
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom>
            Company Logo
          </Typography>
          
          {logoPreview ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <img
                src={logoPreview}
                alt="Logo preview"
                style={{
                  maxWidth: 120,
                  maxHeight: 80,
                  objectFit: 'contain',
                  border: '1px solid #ddd',
                  borderRadius: 4,
                  padding: 8
                }}
              />
              <Button
                variant="outlined"
                color="error"
                size="small"
                onClick={removeLogo}
              >
                Remove
              </Button>
            </Box>
          ) : (
            <Box sx={{
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 1,
              p: 3,
              textAlign: 'center',
              mb: 2
            }}>
              <Upload sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Upload your company logo
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Recommended: 200x80px, PNG or SVG format
              </Typography>
            </Box>
          )}
          
          <Button
            component="label"
            variant="contained"
            startIcon={logoUploading ? <CircularProgress size={16} /> : <Upload />}
            disabled={logoUploading}
            sx={{ mb: 1 }}
          >
            {logoUploading ? 'Uploading...' : logoPreview ? 'Change Logo' : 'Upload Logo'}
            <input
              type="file"
              hidden
              accept="image/*"
              onChange={handleLogoUpload}
            />
          </Button>
          
          {errors.logo && (
            <Typography variant="caption" color="error" display="block">
              {errors.logo}
            </Typography>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

const StepColors = ({ data, onChange, errors }) => {
  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Brand Colors
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Choose colors that represent your brand. These will be used throughout the platform.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Primary Color"
            type="color"
            value={data.primaryColor || '#2563eb'}
            onChange={(e) => onChange('primaryColor', e.target.value)}
            helperText="Used for buttons, links, and main accents"
            InputProps={{
              startAdornment: (
                <Box
                  sx={{
                    width: 24,
                    height: 24,
                    borderRadius: 1,
                    bgcolor: data.primaryColor || '#2563eb',
                    mr: 1,
                    border: 1,
                    borderColor: 'divider'
                  }}
                />
              )
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Secondary Color"
            type="color"
            value={data.secondaryColor || '#7c3aed'}
            onChange={(e) => onChange('secondaryColor', e.target.value)}
            helperText="Used for secondary elements and highlights"
            InputProps={{
              startAdornment: (
                <Box
                  sx={{
                    width: 24,
                    height: 24,
                    borderRadius: 1,
                    bgcolor: data.secondaryColor || '#7c3aed',
                    mr: 1,
                    border: 1,
                    borderColor: 'divider'
                  }}
                />
              )
            }}
          />
        </Grid>
        
        <Grid item xs={12}>
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                Color Preview
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Box sx={{
                  width: 60,
                  height: 40,
                  bgcolor: data.primaryColor,
                  borderRadius: 1,
                  border: 1,
                  borderColor: 'divider'
                }} />
                <Box sx={{
                  width: 60,
                  height: 40,
                  bgcolor: data.secondaryColor,
                  borderRadius: 1,
                  border: 1,
                  borderColor: 'divider'
                }} />
              </Box>
              <Typography variant="caption" color="text.secondary">
                These colors will be applied to buttons, navigation, and other UI elements
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

const StepDomain = ({ data, onChange, errors }) => {
  const [domainStatus, setDomainStatus] = useState('idle'); // idle, checking, verified, failed
  const [dnsRecords, setDnsRecords] = useState(null);
  const [verificationDetails, setVerificationDetails] = useState(null);
  const [showInstructions, setShowInstructions] = useState(false);

  const checkDomain = async () => {
    if (!data.customDomain) {
      toast.error('Please enter a domain first');
      return;
    }

    const validation = DomainService.validateDomain(data.customDomain);
    if (!validation.isValid) {
      toast.error(validation.errors[0]);
      return;
    }

    setDomainStatus('checking');
    
    try {
      // Generate DNS records
      const records = DomainService.generateDNSRecords(validation.cleanDomain);
      setDnsRecords(records);
      
      // Verify domain setup
      const result = await DomainService.verifyDomainSetup(
        validation.cleanDomain,
        records.verification.value
      );
      
      setVerificationDetails(result);
      setDomainStatus(result.success ? 'verified' : 'failed');
      
      if (result.success) {
        toast.success('Domain verified successfully!');
        onChange('domainVerified', true);
      } else {
        toast.error(result.message || 'Domain verification failed');
      }
    } catch (error) {
      console.error('Domain verification error:', error);
      setDomainStatus('failed');
      toast.error('Failed to verify domain');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Custom Domain Setup
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Connect your own domain to create a fully branded experience. This step is optional.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Custom Domain"
            placeholder="app.yourcompany.com"
            value={data.customDomain || ''}
            onChange={(e) => onChange('customDomain', e.target.value)}
            error={!!errors.customDomain}
            helperText={errors.customDomain || 'Enter your custom domain (e.g., app.yourcompany.com)'}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <Button
                    variant="contained"
                    size="small"
                    onClick={checkDomain}
                    disabled={domainStatus === 'checking' || !data.customDomain}
                    startIcon={domainStatus === 'checking' ? <CircularProgress size={16} /> : <Refresh />}
                  >
                    {domainStatus === 'checking' ? 'Checking...' : 'Verify'}
                  </Button>
                </InputAdornment>
              )
            }}
          />
        </Grid>
        
        {dnsRecords && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="subtitle2">
                    DNS Configuration Required
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => setShowInstructions(!showInstructions)}
                  >
                    {showInstructions ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>
                
                <Collapse in={showInstructions}>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Add these DNS records to your domain provider to complete setup.
                  </Alert>
                  
                  <Stack spacing={2}>
                    {Object.entries(dnsRecords).map(([key, record]) => {
                      if (!record) return null;
                      
                      return (
                        <Box key={key} sx={{ 
                          p: 2, 
                          bgcolor: 'background.paper', 
                          border: 1, 
                          borderColor: 'divider',
                          borderRadius: 1 
                        }}>
                          <Typography variant="subtitle2" gutterBottom>
                            {record.type} Record
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', flex: 1 }}>
                              {record.name}
                            </Typography>
                            <IconButton
                              size="small"
                              onClick={() => copyToClipboard(record.name)}
                              title="Copy name"
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', flex: 1 }}>
                              {record.value}
                            </Typography>
                            <IconButton
                              size="small"
                              onClick={() => copyToClipboard(record.value)}
                              title="Copy value"
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {record.description}
                          </Typography>
                        </Box>
                      );
                    })}
                  </Stack>
                </Collapse>
              </CardContent>
            </Card>
          </Grid>
        )}
        
        {verificationDetails && (
          <Grid item xs={12}>
            <Alert 
              severity={verificationDetails.success ? 'success' : 'warning'}
              sx={{ mb: 2 }}
            >
              {verificationDetails.message}
            </Alert>
            
            {verificationDetails.details && (
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Verification Status
                  </Typography>
                  <List dense>
                    {Object.entries(verificationDetails.details).map(([key, detail]) => (
                      <ListItem key={key}>
                        <ListItemIcon>
                          {detail.configured ? (
                            <CheckCircle color="success" />
                          ) : (
                            <RadioButtonUnchecked color="error" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={key.toUpperCase()}
                          secondary={detail.error || (detail.configured ? 'Configured' : 'Not configured')}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            )}
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

const StepPreview = ({ data, onComplete }) => {
  const [launching, setLaunching] = useState(false);

  const handleLaunch = async () => {
    setLaunching(true);
    
    try {
      // Simulate launch process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('White-label platform launched successfully!');
      onComplete();
    } catch (error) {
      console.error('Launch error:', error);
      toast.error('Failed to launch platform');
    } finally {
      setLaunching(false);
    }
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Review & Launch
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Review your white-label configuration and launch your branded platform.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <BrandingPreviewCard />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuration Summary
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    {data.companyName ? <CheckCircle color="success" /> : <RadioButtonUnchecked />}
                  </ListItemIcon>
                  <ListItemText
                    primary="Company Name"
                    secondary={data.companyName || 'Not set'}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    {data.logo ? <CheckCircle color="success" /> : <RadioButtonUnchecked />}
                  </ListItemIcon>
                  <ListItemText
                    primary="Logo"
                    secondary={data.logo ? 'Uploaded' : 'Not uploaded'}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <CheckCircle color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Brand Colors"
                    secondary="Configured"
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    {data.customDomain && data.domainVerified ? (
                      <CheckCircle color="success" />
                    ) : data.customDomain ? (
                      <Warning color="warning" />
                    ) : (
                      <Info color="info" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="Custom Domain"
                    secondary={
                      data.customDomain
                        ? data.domainVerified
                          ? 'Verified'
                          : 'Pending verification'
                        : 'Not configured (optional)'
                    }
                  />
                </ListItem>
              </List>
              
              <Divider sx={{ my: 2 }} />
              
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleLaunch}
                disabled={launching || !data.companyName}
                startIcon={launching ? <CircularProgress size={20} /> : <Launch />}
              >
                {launching ? 'Launching...' : 'Launch Platform'}
              </Button>
              
              {!data.companyName && (
                <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
                  Company name is required to launch
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export const WhiteLabelSetupWizard = ({ onComplete, sx = {}, ...props }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [errors, setErrors] = useState({});
  const { settings, updateSettings, saveSettings } = useWhiteLabel();

  // Local state for wizard data
  const [wizardData, setWizardData] = useState({
    companyName: settings.companyName || '',
    logo: settings.logo || null,
    primaryColor: settings.primaryColor || '#2563eb',
    secondaryColor: settings.secondaryColor || '#7c3aed',
    customDomain: settings.customDomain || '',
    domainVerified: settings.domainVerified || false,
    customSupportEmail: settings.customSupportEmail || ''
  });

  const handleDataChange = (field, value) => {
    setWizardData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear field error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateStep = (stepIndex) => {
    const stepErrors = {};
    
    switch (stepIndex) {
      case 0: // Branding
        if (!wizardData.companyName?.trim()) {
          stepErrors.companyName = 'Company name is required';
        }
        break;
        
      case 1: // Colors
        // Colors have default values, so no validation needed
        break;
        
      case 2: // Domain
        if (wizardData.customDomain) {
          const validation = DomainService.validateDomain(wizardData.customDomain);
          if (!validation.isValid) {
            stepErrors.customDomain = validation.errors[0];
          }
        }
        break;
        
      case 3: // Preview
        if (!wizardData.companyName?.trim()) {
          stepErrors.companyName = 'Company name is required to launch';
        }
        break;
    }
    
    setErrors(stepErrors);
    return Object.keys(stepErrors).length === 0;
  };

  const handleNext = async () => {
    if (!validateStep(activeStep)) {
      return;
    }
    
    // Save current step data to context
    await updateSettings(wizardData);
    
    if (activeStep === STEPS.length - 1) {
      // Final step - complete wizard
      await handleWizardComplete();
    } else {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleWizardComplete = async () => {
    try {
      // Save all settings
      await updateSettings({
        ...wizardData,
        setupCompleted: true,
        setupCompletedAt: new Date().toISOString()
      });
      
      await saveSettings();
      
      toast.success('White-label setup completed successfully!');
      onComplete?.();
    } catch (error) {
      console.error('Wizard completion error:', error);
      toast.error('Failed to complete setup');
    }
  };

  const renderStepContent = (stepIndex) => {
    const props = {
      data: wizardData,
      onChange: handleDataChange,
      errors
    };
    
    switch (stepIndex) {
      case 0:
        return <StepBranding {...props} />;
      case 1:
        return <StepColors {...props} />;
      case 2:
        return <StepDomain {...props} />;
      case 3:
        return <StepPreview {...props} onComplete={onComplete} />;
      default:
        return null;
    }
  };

  return (
    <Box sx={sx} {...props}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          White-Label Setup Wizard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Let's configure your branded platform in a few simple steps.
        </Typography>
        
        <Stepper activeStep={activeStep} orientation="vertical">
          {STEPS.map((step, index) => {
            const IconComponent = step.icon;
            
            return (
              <Step key={step.id}>
                <StepLabel
                  icon={<IconComponent />}
                  optional={
                    step.id === 'domain' && (
                      <Typography variant="caption">Optional</Typography>
                    )
                  }
                >
                  <Typography variant="h6">{step.label}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {step.description}
                  </Typography>
                </StepLabel>
                <StepContent>
                  {renderStepContent(index)}
                  
                  <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                    <Button
                      disabled={activeStep === 0}
                      onClick={handleBack}
                    >
                      Back
                    </Button>
                    <Button
                      variant="contained"
                      onClick={handleNext}
                    >
                      {activeStep === STEPS.length - 1 ? 'Complete Setup' : 'Next'}
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            );
          })}
        </Stepper>
        
        {activeStep === STEPS.length && (
          <Paper sx={{ p: 3, mt: 3, textAlign: 'center' }}>
            <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Setup Complete!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Your white-label platform is now ready to use.
            </Typography>
          </Paper>
        )}
      </Paper>
    </Box>
  );
};

export default WhiteLabelSetupWizard;