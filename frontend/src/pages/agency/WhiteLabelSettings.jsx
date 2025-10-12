import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Paper,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Label as LabelIcon,
  CheckCircle,
  PlayArrow,
  Settings as SettingsIcon,
  Visibility as PreviewIcon,
  Business,
  Palette,
  Language,
  Launch,
  RadioButtonUnchecked
} from '@mui/icons-material';
import { WhiteLabelSetupWizard } from '../../components/whiteLabel/SetupWizard';
import { WhiteLabelPreview } from '../../components/whiteLabel/PreviewSystem';
import { useWhiteLabel } from '../../contexts/WhiteLabelContext';

const AgencyWhiteLabelSettings = () => {
  const [currentView, setCurrentView] = useState('overview'); // 'overview', 'wizard', 'preview'
  const { settings, getEffectiveBranding } = useWhiteLabel();
  const branding = getEffectiveBranding();
  
  const isSetupComplete = settings.setupCompleted;
  const hasBasicConfig = settings.companyName && settings.primaryColor;
  
  const handleStartWizard = () => {
    setCurrentView('wizard');
  };
  
  const handleWizardComplete = () => {
    setCurrentView('overview');
    // Optionally redirect or show success message
  };
  
  const handleShowPreview = () => {
    setCurrentView('preview');
  };
  
  const handleBackToOverview = () => {
    setCurrentView('overview');
  };

  // Render different views based on current state
  if (currentView === 'wizard') {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Button
            variant="outlined"
            onClick={handleBackToOverview}
            sx={{ mb: 2 }}
          >
            ← Back to Overview
          </Button>
        </Box>
        <WhiteLabelSetupWizard onComplete={handleWizardComplete} />
      </Container>
    );
  }
  
  if (currentView === 'preview') {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Button
            variant="outlined"
            onClick={handleBackToOverview}
            sx={{ mb: 2 }}
          >
            ← Back to Overview
          </Button>
        </Box>
        <WhiteLabelPreview />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <LabelIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
            🏷️ White Label Branding
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
          Transform AdCopySurge into your own branded platform with custom logos, colors, and domains.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Main Action Card */}
        <Grid item xs={12} lg={8}>
          {!isSetupComplete ? (
            /* Setup Required Card */
            <Card 
              sx={{ 
                mb: 3, 
                border: 2,
                borderColor: 'primary.main',
                boxShadow: 3
              }}
            >
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <Box sx={{ 
                    display: 'inline-flex',
                    p: 2,
                    borderRadius: '50%',
                    bgcolor: 'primary.light',
                    mb: 2
                  }}>
                    <SettingsIcon sx={{ fontSize: 48, color: 'primary.main' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                    Set Up Your White-Label Platform
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500, mx: 'auto' }}>
                    Transform AdCopySurge into your own branded platform in just a few simple steps. 
                    Our setup wizard will guide you through the entire process.
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleStartWizard}
                    startIcon={<PlayArrow />}
                    sx={{ 
                      py: 1.5,
                      px: 4,
                      fontSize: '1.1rem'
                    }}
                  >
                    Start Setup Wizard
                  </Button>
                  {hasBasicConfig && (
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={handleShowPreview}
                      startIcon={<PreviewIcon />}
                      sx={{ py: 1.5, px: 4 }}
                    >
                      Preview Changes
                    </Button>
                  )}
                </Box>
                
                {hasBasicConfig && (
                  <Alert severity="info" sx={{ mt: 3 }}>
                    You have partial configuration saved. Complete the setup wizard to finish your white-label platform.
                  </Alert>
                )}
              </CardContent>
            </Card>
          ) : (
            /* Setup Complete Card */
            <Card sx={{ mb: 3, border: 1, borderColor: 'success.main' }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <Box sx={{ 
                    display: 'inline-flex',
                    p: 2,
                    borderRadius: '50%',
                    bgcolor: 'success.light',
                    mb: 2
                  }}>
                    <CheckCircle sx={{ fontSize: 48, color: 'success.main' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, color: 'success.main' }}>
                    White-Label Platform Active!
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Your branded platform is live and ready for your clients.
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleShowPreview}
                    startIcon={<PreviewIcon />}
                    sx={{ py: 1.5, px: 4 }}
                  >
                    View Live Platform
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={handleStartWizard}
                    startIcon={<SettingsIcon />}
                    sx={{ py: 1.5, px: 4 }}
                  >
                    Modify Settings
                  </Button>
                  {branding.customDomain && (
                    <Button
                      variant="text"
                      size="large"
                      href={`https://${branding.customDomain}`}
                      target="_blank"
                      startIcon={<Launch />}
                      sx={{ py: 1.5, px: 4 }}
                    >
                      Open Custom Domain
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          )}
          
          {/* Current Configuration */}
          {isSetupComplete && (
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  Current Configuration
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Company Name
                      </Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {branding.companyName || 'Not set'}
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Custom Domain
                      </Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {branding.customDomain || 'Not configured'}
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Primary Color
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 24,
                            height: 24,
                            borderRadius: 1,
                            bgcolor: branding.primaryColor,
                            border: 1,
                            borderColor: 'divider'
                          }}
                        />
                        <Typography variant="body1" fontWeight={600}>
                          {branding.primaryColor}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Logo Status
                      </Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {branding.logo ? 'Uploaded' : 'Not uploaded'}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}
        </Grid>
        
        {/* Status Overview */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Setup Progress
              </Typography>
              
              <List disablePadding>
                <ListItem disablePadding sx={{ mb: 2 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {branding.companyName ? (
                      <CheckCircle color="success" />
                    ) : (
                      <RadioButtonUnchecked color="disabled" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="Company Branding"
                    secondary="Company name and basic info"
                    primaryTypographyProps={{ variant: 'subtitle2', fontWeight: 600 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
                
                <ListItem disablePadding sx={{ mb: 2 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {branding.logo ? (
                      <CheckCircle color="success" />
                    ) : (
                      <RadioButtonUnchecked color="disabled" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="Logo Upload"
                    secondary="Custom logo and branding assets"
                    primaryTypographyProps={{ variant: 'subtitle2', fontWeight: 600 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
                
                <ListItem disablePadding sx={{ mb: 2 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {branding.primaryColor ? (
                      <CheckCircle color="success" />
                    ) : (
                      <RadioButtonUnchecked color="disabled" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="Brand Colors"
                    secondary="Custom color scheme"
                    primaryTypographyProps={{ variant: 'subtitle2', fontWeight: 600 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
                
                <ListItem disablePadding sx={{ mb: 2 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {branding.customDomain ? (
                      <CheckCircle color="success" />
                    ) : (
                      <RadioButtonUnchecked color="disabled" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="Custom Domain"
                    secondary="Your own domain setup (optional)"
                    primaryTypographyProps={{ variant: 'subtitle2', fontWeight: 600 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
              </List>
              
              <Divider sx={{ my: 3 }} />
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                  {isSetupComplete ? 'Platform is live and ready!' : 'Complete setup to go live'}
                </Typography>
                <Chip
                  label={isSetupComplete ? 'Active' : 'Setup Required'}
                  color={isSetupComplete ? 'success' : 'warning'}
                  variant={isSetupComplete ? 'filled' : 'outlined'}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AgencyWhiteLabelSettings;
