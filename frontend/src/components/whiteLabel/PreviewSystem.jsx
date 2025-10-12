import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Button,
  Switch,
  FormControlLabel,
  useTheme,
  Divider,
  Chip,
  Stack,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Preview as PreviewIcon,
  Fullscreen,
  FullscreenExit,
  Smartphone,
  Tablet,
  Computer,
  Visibility,
  VisibilityOff,
  Settings,
  Dashboard,
  Assessment,
  People,
  Mail,
  Check,
  Star
} from '@mui/icons-material';
import { BrandLogo, CompanyName, PoweredByFooter, BrandingPreviewCard } from './BrandingComponents';
import { useWhiteLabel } from '../../contexts/WhiteLabelContext';

// Preview device sizes
const DEVICE_SIZES = {
  mobile: { width: 375, height: 667, label: 'Mobile', icon: Smartphone },
  tablet: { width: 768, height: 1024, label: 'Tablet', icon: Tablet },
  desktop: { width: 1200, height: 800, label: 'Desktop', icon: Computer }
};

// Mock screen templates for preview
const PreviewTemplates = {
  dashboard: ({ branding }) => (
    <Box sx={{ p: 3, bgcolor: 'background.default', minHeight: '100%' }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        mb: 3,
        pb: 2,
        borderBottom: 1,
        borderColor: 'divider'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <BrandLogo size="large" />
          <Box>
            <CompanyName variant="h5" sx={{ fontWeight: 700 }} />
            <Typography variant="body2" color="text.secondary">
              Ad Copy Analysis Platform
            </Typography>
          </Box>
        </Box>
        <Button variant="contained" size="small">
          Generate Copy
        </Button>
      </Box>

      {/* Stats Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 3 }}>
        {[
          { label: 'Active Campaigns', value: '24', color: branding.primaryColor },
          { label: 'Total Analyses', value: '1,247', color: branding.secondaryColor },
          { label: 'Avg. Score', value: '8.6', color: '#4caf50' },
          { label: 'Monthly Usage', value: '89%', color: '#ff9800' }
        ].map((stat, index) => (
          <Card key={index}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                {stat.label}
              </Typography>
              <Typography variant="h4" sx={{ color: stat.color, fontWeight: 700 }}>
                {stat.value}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Recent Activity */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Recent Activity
      </Typography>
      <List sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
        {[
          'New campaign "Summer Sale 2024" analyzed',
          'Report generated for Facebook ads',
          'Branding settings updated',
          'Team member invited'
        ].map((activity, index) => (
          <ListItem key={index}>
            <ListItemIcon>
              <Check sx={{ color: branding.primaryColor }} />
            </ListItemIcon>
            <ListItemText primary={activity} />
          </ListItem>
        ))}
      </List>
    </Box>
  ),

  analysis: ({ branding }) => (
    <Box sx={{ p: 3, bgcolor: 'background.default', minHeight: '100%' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <CompanyName variant="h4" sx={{ mb: 1, fontWeight: 700 }} />
        <Typography variant="h6" color="text.secondary">
          Ad Copy Analysis Results
        </Typography>
      </Box>

      {/* Analysis Score */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Box sx={{ 
            width: 120, 
            height: 120, 
            borderRadius: '50%', 
            bgcolor: branding.primaryColor,
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 2
          }}>
            <Typography variant="h2" fontWeight={700}>8.7</Typography>
          </Box>
          <Typography variant="h5" sx={{ mb: 1, color: branding.primaryColor }}>
            Excellent Score
          </Typography>
          <Typography color="text.secondary">
            Your ad copy has strong engagement potential
          </Typography>
        </CardContent>
      </Card>

      {/* Analysis Categories */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2 }}>
        {[
          { category: 'Emotional Appeal', score: 9.2, description: 'Strong emotional connection' },
          { category: 'Clarity', score: 8.5, description: 'Clear and concise messaging' },
          { category: 'Call to Action', score: 8.1, description: 'Compelling CTA' },
          { category: 'Brand Alignment', score: 8.9, description: 'Well-aligned with brand' }
        ].map((item, index) => (
          <Card key={index}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Star sx={{ color: branding.secondaryColor }} />
                <Typography variant="h6">{item.score}</Typography>
              </Box>
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                {item.category}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {item.description}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  ),

  reports: ({ branding }) => (
    <Box sx={{ p: 3, bgcolor: 'background.default', minHeight: '100%' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <CompanyName variant="h4" sx={{ mb: 1, fontWeight: 700 }} />
          <Typography variant="h6" color="text.secondary">
            Campaign Performance Report
          </Typography>
        </Box>
        <BrandLogo size="large" variant="icon" />
      </Box>

      {/* Report Summary */}
      <Box sx={{ 
        p: 3, 
        bgcolor: branding.primaryColor, 
        color: 'white', 
        borderRadius: 2, 
        mb: 3 
      }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Executive Summary
        </Typography>
        <Typography variant="body1">
          This report provides comprehensive analysis of your advertising campaigns 
          with detailed insights and recommendations for optimization.
        </Typography>
      </Box>

      {/* Key Metrics */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Key Performance Metrics
      </Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 3 }}>
        {[
          { metric: 'Click-through Rate', value: '3.2%', trend: '+0.8%' },
          { metric: 'Conversion Rate', value: '12.7%', trend: '+2.1%' },
          { metric: 'Cost per Click', value: '$1.23', trend: '-$0.15' },
          { metric: 'ROAS', value: '4.2x', trend: '+0.6x' }
        ].map((metric, index) => (
          <Box key={index} sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {metric.metric}
            </Typography>
            <Typography variant="h5" fontWeight={600}>
              {metric.value}
            </Typography>
            <Chip 
              label={metric.trend} 
              size="small" 
              color="success"
              sx={{ mt: 1 }} 
            />
          </Box>
        ))}
      </Box>

      {/* Recommendations */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Recommendations
      </Typography>
      <List sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
        {[
          'Increase budget allocation for high-performing keywords',
          'Test alternative ad copy variations',
          'Optimize landing page for mobile users',
          'Consider expanding to new audience segments'
        ].map((recommendation, index) => (
          <ListItem key={index}>
            <ListItemIcon>
              <Box sx={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                bgcolor: branding.primaryColor 
              }} />
            </ListItemIcon>
            <ListItemText primary={recommendation} />
          </ListItem>
        ))}
      </List>
    </Box>
  )
};

const PreviewControls = ({ device, onDeviceChange, isFullscreen, onFullscreenToggle }) => {
  const theme = useTheme();

  return (
    <Box sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      gap: 1,
      p: 1,
      bgcolor: 'background.paper',
      borderRadius: 1,
      border: 1,
      borderColor: 'divider'
    }}>
      {Object.entries(DEVICE_SIZES).map(([key, size]) => {
        const IconComponent = size.icon;
        return (
          <IconButton
            key={key}
            size="small"
            color={device === key ? 'primary' : 'default'}
            onClick={() => onDeviceChange(key)}
            title={size.label}
          >
            <IconComponent />
          </IconButton>
        );
      })}
      
      <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
      
      <IconButton
        size="small"
        onClick={onFullscreenToggle}
        title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
      >
        {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
      </IconButton>
    </Box>
  );
};

const PreviewFrame = ({ children, device, isFullscreen }) => {
  const theme = useTheme();
  const size = DEVICE_SIZES[device];

  const frameStyles = isFullscreen ? {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 1300,
    bgcolor: 'background.default'
  } : {
    width: size.width,
    height: size.height,
    maxWidth: '100%',
    margin: '0 auto',
    bgcolor: 'background.paper',
    border: 1,
    borderColor: 'divider',
    borderRadius: 2,
    overflow: 'hidden'
  };

  return (
    <Box sx={frameStyles}>
      <Box sx={{ 
        width: '100%', 
        height: '100%', 
        overflow: 'auto',
        bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50'
      }}>
        {children}
      </Box>
    </Box>
  );
};

export const WhiteLabelPreview = ({ sx = {}, ...props }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [device, setDevice] = useState('desktop');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [previewEnabled, setPreviewEnabled] = useState(true);
  
  const { settings, getEffectiveBranding, enablePreview, disablePreview } = useWhiteLabel();
  const branding = getEffectiveBranding();

  const templates = ['dashboard', 'analysis', 'reports'];
  
  useEffect(() => {
    if (previewEnabled) {
      enablePreview();
    } else {
      disablePreview();
    }
    
    return () => disablePreview();
  }, [previewEnabled, enablePreview, disablePreview]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleFullscreenToggle = () => {
    setIsFullscreen(!isFullscreen);
  };

  const renderPreview = () => {
    const templateKey = templates[activeTab];
    const TemplateComponent = PreviewTemplates[templateKey];
    
    return (
      <TemplateComponent branding={branding} />
    );
  };

  return (
    <Box sx={sx} {...props}>
      {/* Preview Controls */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        mb: 2,
        flexWrap: 'wrap',
        gap: 2
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PreviewIcon />
            White-Label Preview
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={previewEnabled}
                onChange={(e) => setPreviewEnabled(e.target.checked)}
                color="primary"
              />
            }
            label="Enable Preview"
          />
        </Box>
        
        <PreviewControls
          device={device}
          onDeviceChange={setDevice}
          isFullscreen={isFullscreen}
          onFullscreenToggle={handleFullscreenToggle}
        />
      </Box>

      {previewEnabled ? (
        <>
          {/* Preview Tabs */}
          <Paper sx={{ mb: 2 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="fullWidth"
              sx={{ minHeight: 48 }}
            >
              <Tab 
                icon={<Dashboard />} 
                label="Dashboard" 
                iconPosition="start"
                sx={{ minHeight: 48 }}
              />
              <Tab 
                icon={<Assessment />} 
                label="Analysis" 
                iconPosition="start"
                sx={{ minHeight: 48 }}
              />
              <Tab 
                icon={<Mail />} 
                label="Reports" 
                iconPosition="start"
                sx={{ minHeight: 48 }}
              />
            </Tabs>
          </Paper>

          {/* Preview Frame */}
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center',
            ...(isFullscreen && {
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 1300,
              bgcolor: 'background.default',
              p: 2
            })
          }}>
            <PreviewFrame
              device={device}
              isFullscreen={isFullscreen}
            >
              {renderPreview()}
              {/* Always show PoweredByFooter in preview */}
              <PoweredByFooter />
            </PreviewFrame>
          </Box>

          {/* Preview Info */}
          {!isFullscreen && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Preview shows how your white-label branding will appear to users.
                {' '}
                {settings.previewMode && (
                  <Chip 
                    label="Preview Mode Active" 
                    size="small" 
                    color="warning" 
                    sx={{ ml: 1 }}
                  />
                )}
              </Typography>
            </Box>
          )}
        </>
      ) : (
        <Box sx={{ 
          textAlign: 'center', 
          py: 6, 
          bgcolor: 'background.paper', 
          borderRadius: 2,
          border: 1,
          borderColor: 'divider'
        }}>
          <VisibilityOff sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
            Preview Disabled
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Enable the preview toggle to see how your white-label branding will look
          </Typography>
        </Box>
      )}

      {/* Branding Summary Card */}
      {previewEnabled && (
        <BrandingPreviewCard sx={{ mt: 3 }} />
      )}
    </Box>
  );
};

export default WhiteLabelPreview;