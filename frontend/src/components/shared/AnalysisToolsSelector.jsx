import React from 'react';
import { 
  Card, 
  CardContent, 
  Chip, 
  Typography, 
  Grid, 
  Box, 
  Switch, 
  FormControlLabel, 
  Tooltip, 
  Collapse,
  Fade 
} from '@mui/material';
import { AVAILABLE_TOOLS } from '../../constants/analysisTools';
import { useSettings } from '../../contexts/SettingsContext';

/**
 * AnalysisToolsSelector
 * Reusable selector for choosing which analysis tools to run.
 * Now uses global settings context for advanced settings toggle
 * Expects react-hook-form props: control, watch, setValue
 */
const AnalysisToolsSelector = ({ 
  watch, 
  setValue, 
  // Legacy props for backward compatibility (deprecated)
  showAdvancedSettings: legacyShowAdvancedSettings, 
  setShowAdvancedSettings: legacySetShowAdvancedSettings, 
  title = 'Analysis Tools', 
  subtitle 
}) => {
  const selectedTools = watch('enabledTools') || [];
  const { showAdvancedSettings, toggleAdvancedSettings } = useSettings();
  
  // Use settings context, but fallback to legacy props if provided for backward compatibility
  const isAdvancedVisible = legacyShowAdvancedSettings !== undefined 
    ? legacyShowAdvancedSettings 
    : showAdvancedSettings;
    
  const handleAdvancedToggle = (checked) => {
    if (legacySetShowAdvancedSettings) {
      // Use legacy prop if provided
      legacySetShowAdvancedSettings(checked);
    } else {
      // Use settings context
      toggleAdvancedSettings();
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          🔧 {title}
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={isAdvancedVisible}
              onChange={(e) => handleAdvancedToggle(e.target.checked)}
              color="primary"
            />
          }
          label="Advanced Settings"
          sx={{
            '& .MuiFormControlLabel-label': {
              fontSize: '0.875rem',
              fontWeight: 500
            }
          }}
        />
      </Box>

      {subtitle && (
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          {subtitle}
        </Typography>
      )}

      <Collapse in={isAdvancedVisible} timeout={300}>
        <Fade in={isAdvancedVisible} timeout={isAdvancedVisible ? 400 : 0}>
          <Grid container spacing={2}>
            {AVAILABLE_TOOLS.map((tool) => {
              const isSelected = selectedTools.includes(tool.id);
              return (
                <Grid item xs={12} sm={6} md={4} key={tool.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      height: 140, // Fixed height for consistency
                      display: 'flex',
                      flexDirection: 'column',
                      border: isSelected ? '2px solid' : '1px solid',
                      borderColor: isSelected ? 'primary.main' : 'divider',
                      bgcolor: isSelected ? 'rgba(25, 118, 210, 0.08)' : 'background.paper',
                      boxShadow: isSelected ? 2 : 1,
                      '&:hover': {
                        borderColor: 'primary.main',
                        transform: 'translateY(-2px)',
                        boxShadow: isSelected ? 4 : 3
                      },
                      transition: 'all 0.2s ease-in-out',
                      position: 'relative'
                    }}
                    onClick={() => {
                      const currentTools = watch('enabledTools') || [];
                      if (isSelected) {
                        setValue('enabledTools', currentTools.filter(t => t !== tool.id));
                      } else {
                        setValue('enabledTools', [...currentTools, tool.id]);
                      }
                    }}
                  >
                    <CardContent sx={{ 
                      p: 2, 
                      flex: 1, 
                      display: 'flex', 
                      flexDirection: 'column',
                      justifyContent: 'space-between'
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                        <Typography variant="h5" component="span" sx={{ fontSize: '1.5rem' }}>
                          {tool.icon}
                        </Typography>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography 
                            variant="subtitle2" 
                            sx={{ 
                              fontWeight: 600,
                              color: isSelected ? 'primary.main' : 'text.primary',
                              lineHeight: 1.2,
                              mb: 0.5
                            }}
                          >
                            {tool.name}
                          </Typography>
                          {tool.description && (
                            <Typography 
                              variant="caption" 
                              color="text.secondary"
                              sx={{ 
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                                fontSize: '0.75rem',
                                lineHeight: 1.3
                              }}
                            >
                              {tool.description}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                      
                      {/* Selected indicator */}
                      {isSelected && (
                        <Box sx={{ 
                          position: 'absolute', 
                          top: 8, 
                          right: 8,
                          zIndex: 1
                        }}>
                          <Chip 
                            label="✓" 
                            size="small" 
                            color="primary" 
                            sx={{ 
                              minWidth: 24,
                              height: 24,
                              '& .MuiChip-label': {
                                px: 0.5,
                                fontSize: '0.75rem',
                                fontWeight: 'bold'
                              }
                            }}
                          />
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </Fade>
      </Collapse>
      
      {/* Show a message when advanced settings are hidden */}
      {!isAdvancedVisible && (
        <Box sx={{ 
          p: 3, 
          textAlign: 'center',
          bgcolor: 'rgba(0, 0, 0, 0.02)',
          borderRadius: 2,
          border: '1px dashed',
          borderColor: 'divider'
        }}>
          <Typography variant="body2" color="text.secondary">
            Toggle "Advanced Settings" to select specific analysis tools. Default tools will be used.
          </Typography>
        </Box>
      )}

      <Collapse in={isAdvancedVisible} timeout={300}>
        <Fade in={isAdvancedVisible} timeout={isAdvancedVisible ? 400 : 0}>
          <Box sx={{ 
            mt: 3, 
            pt: 3, 
            borderTop: 1, 
            borderColor: 'divider',
            bgcolor: 'rgba(37, 99, 235, 0.02)',
            borderRadius: 2,
            p: 2
          }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: 'primary.main' }}>
              ⚙️ Advanced Settings
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Tooltip title="Automatically run analysis after saving your project">
                <FormControlLabel
                  control={
                    <Switch
                      checked={!!watch('autoAnalyze')}
                      onChange={(e) => setValue('autoAnalyze', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Auto-run analysis when saving"
                  sx={{
                    '& .MuiFormControlLabel-label': {
                      fontSize: '0.875rem'
                    }
                  }}
                />
              </Tooltip>
              
              {/* Additional future settings can go here */}
              <Typography variant="caption" color="text.secondary" sx={{ ml: 4 }}>
                More advanced options will be available here in future updates.
              </Typography>
            </Box>
          </Box>
        </Fade>
      </Collapse>
    </Box>
  );
};

export default AnalysisToolsSelector;

