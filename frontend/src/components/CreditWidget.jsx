import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  Button,
  Card,
  CardContent,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  AccountBalanceWallet,
  Add,
  Info,
  TrendingUp,
  AccessTime
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import useCredits from '../hooks/useCredits';
import { formatCredits } from '../utils/creditSystem';

const CreditWidget = ({ compact = false }) => {
  const navigate = useNavigate();
  const { 
    credits, 
    monthlyAllowance, 
    loading, 
    getFormattedCredits, 
    getCreditStatusColor, 
    getCreditPercentage,
    getDaysUntilReset 
  } = useCredits();

  const handleViewBilling = () => {
    navigate('/billing');
  };

  const handleBuyCredits = () => {
    navigate('/billing?tab=credits');
  };

  if (loading) {
    return (
      <Card elevation={0} sx={{ backgroundColor: 'rgba(124, 58, 237, 0.05)' }}>
        <CardContent sx={{ p: 2 }}>
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <AccountBalanceWallet sx={{ fontSize: 20, color: 'primary.main' }} />
            <Typography variant="body2" fontWeight="600">
              Credits
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Loading...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const creditColor = getCreditStatusColor();
  const percentage = getCreditPercentage();
  const isUnlimited = credits === 'unlimited' || credits >= 999999;

  if (compact) {
    return (
      <Box
        onClick={handleViewBilling}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1,
          borderRadius: 1,
          cursor: 'pointer',
          '&:hover': {
            backgroundColor: 'rgba(124, 58, 237, 0.05)'
          }
        }}
      >
        <AccountBalanceWallet sx={{ fontSize: 18, color: `${creditColor}.main` }} />
        <Box flex={1}>
          <Typography variant="caption" fontWeight="600">
            {getFormattedCredits()}
          </Typography>
          {!isUnlimited && (
            <Typography variant="caption" color="text.secondary" display="block">
              / {formatCredits(monthlyAllowance)}
            </Typography>
          )}
        </Box>
      </Box>
    );
  }

  return (
    <Card 
      elevation={0} 
      sx={{ 
        backgroundColor: isUnlimited ? 
          'rgba(16, 185, 129, 0.05)' : 
          percentage > 80 ? 
            'rgba(239, 68, 68, 0.05)' : 
            'rgba(124, 58, 237, 0.05)',
        border: '1px solid',
        borderColor: isUnlimited ? 
          'rgba(16, 185, 129, 0.2)' : 
          percentage > 80 ? 
            'rgba(239, 68, 68, 0.2)' : 
            'rgba(124, 58, 237, 0.2)'
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        {/* Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <AccountBalanceWallet sx={{ fontSize: 20, color: `${creditColor}.main` }} />
            <Typography variant="subtitle2" fontWeight="700">
              Credits
            </Typography>
          </Box>
          <Tooltip title="View billing details">
            <IconButton 
              size="small" 
              onClick={handleViewBilling}
              sx={{ color: 'text.secondary' }}
            >
              <Info sx={{ fontSize: 16 }} />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Credit Display */}
        <Box mb={2}>
          <Box display="flex" alignItems="baseline" gap={1} mb={1}>
            <Typography variant="h6" fontWeight="800" color={`${creditColor}.main`}>
              {getFormattedCredits()}
            </Typography>
            {!isUnlimited && (
              <Typography variant="body2" color="text.secondary">
                / {formatCredits(monthlyAllowance)}
              </Typography>
            )}
          </Box>
          
          {!isUnlimited && monthlyAllowance > 0 && (
            <Box>
              <LinearProgress
                variant="determinate"
                value={100 - percentage}
                color={creditColor}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: 'rgba(0,0,0,0.1)',
                  mb: 1
                }}
              />
              <Typography variant="caption" color="text.secondary">
                {(100 - percentage).toFixed(0)}% remaining
              </Typography>
            </Box>
          )}
        </Box>

        {/* Status Chip */}
        <Box mb={2}>
          {isUnlimited ? (
            <Chip
              icon={<TrendingUp />}
              label="Unlimited Plan"
              color="success"
              size="small"
              variant="outlined"
            />
          ) : percentage > 80 ? (
            <Chip
              label="Low Credits"
              color="error"
              size="small"
              variant="outlined"
            />
          ) : percentage > 50 ? (
            <Chip
              label="Running Low"
              color="warning"
              size="small"
              variant="outlined"
            />
          ) : (
            <Chip
              icon={<AccessTime />}
              label={`${getDaysUntilReset()} days to reset`}
              color="primary"
              size="small"
              variant="outlined"
            />
          )}
        </Box>

        {/* Action Buttons */}
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            size="small"
            fullWidth
            onClick={handleViewBilling}
            sx={{ textTransform: 'none', fontSize: '0.75rem' }}
          >
            View Details
          </Button>
          {!isUnlimited && (
            <Button
              variant="contained"
              size="small"
              startIcon={<Add sx={{ fontSize: '14px !important' }} />}
              onClick={handleBuyCredits}
              sx={{ 
                textTransform: 'none', 
                fontSize: '0.75rem',
                minWidth: 'fit-content',
                px: 1.5
              }}
            >
              Buy
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default CreditWidget;