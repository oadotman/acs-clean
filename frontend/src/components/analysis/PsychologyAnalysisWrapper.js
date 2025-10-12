import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Alert
} from '@mui/material';
import { Psychology, Lock, TrendingUp } from '@mui/icons-material';
import { useAuth } from '../../services/authContext';
import { canPerformAction, getUserTier } from '../../utils/accessControl';
import UpgradeModal from '../shared/UpgradeModal';

const PsychologyAnalysisWrapper = ({ adText, analysisData, children }) => {
  const { user } = useAuth();
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  
  // Check if user can access psychology analysis
  const accessCheck = canPerformAction(user, 'usePsychologyAnalysis');
  const userTier = getUserTier(user);
  const hasAccess = accessCheck.canPerform;

  const handleUpgradeClick = () => {
    setShowUpgradeModal(true);
    
    // Log access denial for analytics
    console.log('Access denied', {
      userId: user?.id,
      feature: 'psychologyAnalysis',
      tier: userTier,
      reason: accessCheck.reason
    });
  };

  // If user doesn't have access, show upgrade prompt
  if (!hasAccess) {
    return (
      <>
        <Card sx={{
          background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(192, 132, 252, 0.05) 100%)',
          border: '2px solid rgba(168, 85, 247, 0.2)',
          borderRadius: 4,
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Blur overlay effect */}
          <Box sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(15, 11, 29, 0.8)',
            backdropFilter: 'blur(8px)',
            zIndex: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            p: 4,
            textAlign: 'center'
          }}>
            <Lock sx={{ 
              color: '#C084FC', 
              fontSize: 64, 
              mb: 2,
              opacity: 0.8 
            }} />
            
            <Typography variant="h4" sx={{
              color: '#F9FAFB',
              fontWeight: 700,
              mb: 2
            }}>
              🧠 15-Point Psychology Analysis
            </Typography>
            
            <Typography variant="body1" sx={{
              color: '#E5E7EB',
              mb: 3,
              maxWidth: '400px',
              lineHeight: 1.6
            }}>
              {accessCheck.reason || 'Unlock advanced psychological triggers analysis to understand what makes your ads persuasive.'}
            </Typography>

            <Chip
              label={`Available in ${accessCheck.upgradeRequired || 'Growth'} plan`}
              sx={{
                background: 'rgba(192, 132, 252, 0.2)',
                color: '#C084FC',
                fontWeight: 600,
                mb: 3
              }}
            />
            
            <Button
              variant="contained"
              size="large"
              onClick={handleUpgradeClick}
              startIcon={<TrendingUp />}
              sx={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%)',
                color: 'white',
                fontWeight: 700,
                px: 6,
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
              Unlock Psychology Analysis
            </Button>
          </Box>

          {/* Blurred preview content */}
          <CardContent sx={{ 
            p: 4,
            filter: 'blur(4px)',
            opacity: 0.3
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Psychology sx={{ color: '#C084FC', mr: 2, fontSize: 32 }} />
              <Typography variant="h5" sx={{ 
                color: '#F9FAFB', 
                fontWeight: 700 
              }}>
                Psychology Analysis
              </Typography>
            </Box>
            
            {/* Mock content to show what they're missing */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ color: '#E5E7EB', mb: 2 }}>
                Psychological Triggers Detected:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                {['Scarcity', 'Social Proof', 'Authority', 'Reciprocity', 'Loss Aversion'].map((trigger) => (
                  <Chip
                    key={trigger}
                    label={trigger}
                    size="small"
                    sx={{
                      background: 'rgba(16, 185, 129, 0.2)',
                      color: '#86EFAC',
                      fontWeight: 500
                    }}
                  />
                ))}
              </Box>
            </Box>

            <Alert 
              severity="info" 
              sx={{ 
                background: 'rgba(14, 165, 233, 0.1)',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                color: '#E5E7EB'
              }}
            >
              Based on 15-point analysis, this ad could be 23% more persuasive with optimized psychological triggers.
            </Alert>
          </CardContent>
        </Card>

        <UpgradeModal
          open={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
          reason={accessCheck.reason}
          recommendedTier={accessCheck.upgradeRequired}
          blockedAction="usePsychologyAnalysis"
        />
      </>
    );
  }

  // If user has access, render the actual component
  return (
    <Card sx={{
      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%)',
      border: '2px solid rgba(16, 185, 129, 0.2)',
      borderRadius: 4
    }}>
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Psychology sx={{ color: '#10b981', mr: 2, fontSize: 32 }} />
          <Typography variant="h5" sx={{ 
            color: '#F9FAFB', 
            fontWeight: 700 
          }}>
            Psychology Analysis
          </Typography>
          <Chip
            label="PREMIUM"
            size="small"
            sx={{
              ml: 2,
              background: 'rgba(16, 185, 129, 0.2)',
              color: '#86EFAC',
              fontWeight: 600,
              fontSize: '0.7rem'
            }}
          />
        </Box>
        
        {/* Render the actual psychology analysis component */}
        {children}
      </CardContent>
    </Card>
  );
};

export default PsychologyAnalysisWrapper;