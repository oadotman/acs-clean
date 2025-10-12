import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Divider
} from '@mui/material';
import { 
  CheckCircle, 
  Close, 
  TrendingUp, 
  Security, 
  Speed,
  Analytics
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { PRICING_PLANS, SUBSCRIPTION_TIERS, formatLimit } from '../../constants/plans';

const UpgradeModal = ({ 
  open, 
  onClose, 
  reason, 
  recommendedTier = SUBSCRIPTION_TIERS.GROWTH,
  currentUsage = {},
  blockedAction
}) => {
  const navigate = useNavigate();
  
  // Find the recommended plan
  const recommendedPlan = PRICING_PLANS.find(plan => plan.tier === recommendedTier) || PRICING_PLANS[1];
  
  const handleUpgrade = () => {
    onClose();
    navigate('/pricing');
  };

  const getFeatureIcon = (feature) => {
    const icons = {
      'adAnalyses': <Analytics sx={{ color: '#C084FC' }} />,
      'psychologyAnalysis': <Speed sx={{ color: '#10b981' }} />,
      'reports': <TrendingUp sx={{ color: '#f59e0b' }} />,
      'whiteLabel': <Security sx={{ color: '#ef4444' }} />,
      'integrations': <CheckCircle sx={{ color: '#8b5cf6' }} />,
      'apiAccess': <Security sx={{ color: '#06b6d4' }} />
    };
    return icons[feature] || <CheckCircle sx={{ color: '#10b981' }} />;
  };

  const getActionTitle = (action) => {
    const titles = {
      'analyzeAd': 'Analyze More Ads',
      'usePsychologyAnalysis': 'Psychology Analysis',
      'generateReport': 'Generate Reports',
      'useWhiteLabel': 'White-Label Branding',
      'useIntegrations': 'Integrations',
      'useAPI': 'API Access'
    };
    return titles[action] || 'Premium Feature';
  };

  const benefits = [
    `${formatLimit(recommendedPlan.limits.adAnalyses)} ad analyses per month`,
    recommendedPlan.limits.psychologyAnalysis ? '15-Point Psychology Analysis' : null,
    recommendedPlan.limits.reports > 0 ? `${formatLimit(recommendedPlan.limits.reports)} reports per month` : null,
    recommendedPlan.limits.whiteLabel ? 'White-label branding' : null,
    recommendedPlan.limits.integrations ? '5000+ integrations' : null,
    recommendedPlan.limits.apiAccess ? 'API access' : null,
    `${recommendedPlan.limits.support} support`
  ].filter(Boolean);

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          background: 'linear-gradient(135deg, #0f0b1d 0%, #1a1333 50%, #2d1b5e 100%)',
          border: '2px solid rgba(192, 132, 252, 0.2)',
          borderRadius: 4,
          color: '#F9FAFB'
        }
      }}
    >
      <DialogTitle sx={{ 
        textAlign: 'center', 
        pb: 2,
        position: 'relative'
      }}>
        <Button
          onClick={onClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            minWidth: 'auto',
            p: 1,
            color: '#9CA3AF'
          }}
        >
          <Close />
        </Button>
        
        <Box sx={{ mb: 2 }}>
          {getFeatureIcon(blockedAction)}
        </Box>
        
        <Typography variant="h4" sx={{ 
          fontWeight: 800, 
          color: '#F9FAFB',
          mb: 1
        }}>
          Unlock {getActionTitle(blockedAction)}
        </Typography>
        
        <Typography variant="body1" sx={{ 
          color: '#E5E7EB',
          opacity: 0.9
        }}>
          {reason || 'Upgrade to access this premium feature'}
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ px: 3, py: 2 }}>
        {/* Current vs Recommended Comparison */}
        <Box sx={{ 
          background: 'rgba(168, 85, 247, 0.1)',
          borderRadius: 3,
          p: 3,
          mb: 4,
          border: '1px solid rgba(168, 85, 247, 0.2)'
        }}>
          <Typography variant="h6" sx={{ 
            color: '#C084FC', 
            fontWeight: 700, 
            mb: 3,
            textAlign: 'center'
          }}>
            Upgrade to {recommendedPlan.name}
          </Typography>
          
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            mb: 3
          }}>
            <Typography variant="h2" sx={{ 
              fontWeight: 800, 
              color: '#F9FAFB',
              mr: 1
            }}>
              ${recommendedPlan.price}
            </Typography>
            <Typography variant="body1" sx={{ 
              color: '#E5E7EB',
              fontWeight: 600
            }}>
              /{recommendedPlan.period}
            </Typography>
          </Box>

          <Typography variant="body2" sx={{ 
            color: '#E5E7EB',
            textAlign: 'center',
            mb: 3
          }}>
            {recommendedPlan.description}
          </Typography>

          <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', my: 3 }} />

          <Typography variant="h6" sx={{ 
            color: '#F9FAFB', 
            fontWeight: 600, 
            mb: 2
          }}>
            What you'll get:
          </Typography>

          <List dense sx={{ py: 0 }}>
            {benefits.map((benefit, index) => (
              <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <CheckCircle sx={{ 
                    color: '#86EFAC', 
                    fontSize: 20
                  }} />
                </ListItemIcon>
                <ListItemText 
                  primary={benefit}
                  primaryTypographyProps={{
                    variant: 'body2',
                    sx: {
                      color: '#F9FAFB',
                      fontWeight: 500
                    }
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>

        {/* Social Proof */}
        <Box sx={{ 
          textAlign: 'center',
          background: 'rgba(16, 185, 129, 0.1)',
          borderRadius: 3,
          p: 3,
          border: '1px solid rgba(16, 185, 129, 0.2)'
        }}>
          <Typography variant="body1" sx={{ 
            color: '#86EFAC',
            fontWeight: 600,
            mb: 1
          }}>
            🚀 Join 500+ agencies already using {recommendedPlan.name}
          </Typography>
          <Typography variant="body2" sx={{ 
            color: '#E5E7EB',
            opacity: 0.9
          }}>
            Average increase of 300% ROAS within 90 days
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ 
        px: 3, 
        pb: 3, 
        pt: 0,
        flexDirection: 'column',
        gap: 2
      }}>
        <Button
          onClick={handleUpgrade}
          variant="contained"
          fullWidth
          size="large"
          sx={{
            background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%)',
            color: 'white',
            fontWeight: 700,
            py: 2,
            fontSize: '1.1rem',
            textTransform: 'none',
            borderRadius: 3,
            boxShadow: '0 8px 25px rgba(168, 85, 247, 0.3)',
            '&:hover': {
              background: 'linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #a855f7 100%)',
              transform: 'translateY(-2px)',
              boxShadow: '0 12px 35px rgba(168, 85, 247, 0.4)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          Upgrade to {recommendedPlan.name} →
        </Button>

        <Button
          onClick={onClose}
          sx={{
            color: '#9CA3AF',
            fontWeight: 500,
            textTransform: 'none',
            '&:hover': {
              color: '#E5E7EB'
            }
          }}
        >
          Maybe later
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UpgradeModal;