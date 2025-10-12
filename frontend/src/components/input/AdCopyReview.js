import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Divider,
} from '@mui/material';
import { ExpandMore, Delete, Add, Analytics } from '@mui/icons-material';
import EditableAdForm from './EditableAdForm';

const AdCopyReview = ({ 
  adCopies, 
  onUpdateAdCopy, 
  onRemoveAdCopy, 
  onAddAdCopy, 
  onAnalyzeAll,
  competitorAds,
  onUpdateCompetitorAd,
  onAddCompetitorAd,
  onRemoveCompetitorAd,
  loading = false 
}) => {
  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography variant="h6" gutterBottom>
            📝 Review & Edit Ad Copies
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Review and edit your {adCopies.length} ad cop{adCopies.length === 1 ? 'y' : 'ies'} before analysis
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip 
            label={`${adCopies.length} Ad${adCopies.length !== 1 ? 's' : ''}`} 
            color="primary" 
            variant="outlined" 
          />
          <Button
            variant="outlined"
            startIcon={<Add />}
            onClick={onAddAdCopy}
            size="small"
          >
            Add More
          </Button>
        </Box>
      </Box>

      {/* Ad Copies List */}
      <Grid container spacing={3}>
        {adCopies.map((adCopy, index) => (
          <Grid item xs={12} key={adCopy.id || index}>
            <Paper 
              variant="outlined" 
              sx={{ 
                overflow: 'hidden',
                border: '2px solid',
                borderColor: 'primary.light',
                backgroundColor: 'rgba(124, 58, 237, 0.02)'
              }}
            >
              <Box sx={{ 
                px: 3, 
                py: 2, 
                backgroundColor: 'primary.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <Typography variant="subtitle1" sx={{ color: 'primary.contrastText', fontWeight: 600 }}>
                  Ad Copy #{index + 1}
                  {adCopy.headline && `: ${adCopy.headline.substring(0, 50)}${adCopy.headline.length > 50 ? '...' : ''}`}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <Chip 
                    label={adCopy.platform || 'facebook'} 
                    size="small" 
                    sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'primary.contrastText' }}
                  />
                  <IconButton
                    size="small"
                    onClick={() => onRemoveAdCopy(adCopy.id || index)}
                    disabled={adCopies.length === 1}
                    sx={{ color: 'primary.contrastText' }}
                  >
                    <Delete fontSize="small" />
                  </IconButton>
                </Box>
              </Box>
              
              <Box sx={{ p: 3 }}>
                <EditableAdForm
                  initialValues={adCopy}
                  onUpdate={(updatedData) => onUpdateAdCopy(adCopy.id || index, updatedData)}
                  showPlatform={true}
                  showIndustry={true}
                  showTargetAudience={true}
                />
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Competitor Ads Section */}
      <Box sx={{ mt: 4 }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              🏆 Competitor Ads (Optional) - {competitorAds?.length || 0} added
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Add competitor ads to benchmark your performance against the competition
              </Typography>
              
              {competitorAds && competitorAds.length > 0 ? (
                <Grid container spacing={2}>
                  {competitorAds.map((competitor, index) => (
                    <Grid item xs={12} key={competitor.id || index}>
                      <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                          <Typography variant="subtitle2">
                            Competitor #{index + 1}
                          </Typography>
                          <Button 
                            color="error" 
                            size="small"
                            onClick={() => onRemoveCompetitorAd(competitor.id || index)}
                          >
                            Remove
                          </Button>
                        </Box>
                        <EditableAdForm
                          initialValues={competitor}
                          onUpdate={(updatedData) => onUpdateCompetitorAd(competitor.id || index, updatedData)}
                          showPlatform={true}
                          showIndustry={false}
                          showTargetAudience={false}
                        />
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Box sx={{ textAlign: 'center', py: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    No competitor ads added yet
                  </Typography>
                </Box>
              )}
              
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Button variant="outlined" onClick={onAddCompetitorAd} size="small">
                  Add Competitor Ad
                </Button>
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* Analysis Actions */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center',
        alignItems: 'center',
        gap: 2,
        py: 3,
        backgroundColor: 'rgba(0, 0, 0, 0.02)',
        borderRadius: 2,
        mx: -2,
        px: 4
      }}>
        <Box sx={{ textAlign: 'center', flexGrow: 1 }}>
          <Typography variant="h6" gutterBottom>
            🚀 Ready to Analyze?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {adCopies.length === 1 
              ? 'Analyze your ad copy with our AI-powered tools'
              : `Run comprehensive analysis on all ${adCopies.length} ad copies`
            }
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={loading ? null : <Analytics />}
            onClick={onAnalyzeAll}
            disabled={loading || adCopies.length === 0}
            sx={{ 
              minWidth: 280,
              py: 2,
              px: 4,
              fontSize: '1.1rem',
              fontWeight: 700,
              borderRadius: 3,
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              boxShadow: '0 8px 32px rgba(245, 158, 11, 0.3)',
              '&:hover': {
                background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 12px 40px rgba(245, 158, 11, 0.4)',
              },
              '&:disabled': {
                background: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                transform: 'none',
                boxShadow: 'none'
              }
            }}
          >
            {loading 
              ? `🧑‍💻 Analyzing ${adCopies.length} Ad${adCopies.length !== 1 ? 's' : ''}...`
              : `🚀 Analyze ${adCopies.length === 1 ? 'Ad Copy' : `All ${adCopies.length} Ads`}`
            }
          </Button>
          
          {adCopies.length > 1 && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              Each ad will be analyzed separately with individual results
            </Typography>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default AdCopyReview;
