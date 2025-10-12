import React from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  alpha,
  useTheme
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  AddCircleOutline,
  CloudUpload,
  History,
  TrendingUp
} from '@mui/icons-material';

const ActionButton = ({ 
  title, 
  description, 
  icon: Icon, 
  onClick, 
  variant = 'contained',
  color = 'primary',
  disabled = false 
}) => {
  const theme = useTheme();
  
  return (
    <motion.div
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
    >
      <Button
        variant={variant}
        onClick={onClick}
        disabled={disabled}
        startIcon={<Icon />}
        sx={{
          height: '100%',
          minHeight: 80,
          p: 3,
          borderRadius: 3,
          justifyContent: 'flex-start',
          textAlign: 'left',
          flexDirection: 'column',
          alignItems: 'flex-start',
          gap: 1,
          border: variant === 'outlined' ? `2px solid ${theme.palette.divider}` : 'none',
          boxShadow: variant === 'contained' ? 3 : 'none',
          '&:hover': {
            boxShadow: variant === 'contained' ? 6 : 2,
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
          <Icon sx={{ fontSize: 24 }} />
          <Typography variant="h6" fontWeight={600} sx={{ flex: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography 
          variant="body2" 
          sx={{ 
            color: variant === 'contained' ? 'inherit' : 'text.secondary',
            opacity: variant === 'contained' ? 0.9 : 1
          }}
        >
          {description}
        </Typography>
      </Button>
    </motion.div>
  );
};

const QuickActions = ({ 
  onAnalyzeClick, 
  onUploadClick, 
  onHistoryClick,
  onTrendsClick,
  platformSelected = false,
  disabled = false 
}) => {
  const theme = useTheme();
  
  return (
    <Paper 
      elevation={1}
      sx={{ 
        p: 3,
        borderRadius: 3,
        border: `1px solid ${theme.palette.divider}`,
        backgroundColor: 'background.paper'
      }}
    >
      <Box sx={{ mb: 3 }}>
        <Typography 
          variant="h6" 
          fontWeight={700}
          color="text.primary"
          gutterBottom
        >
          Quick Actions
        </Typography>
        <Typography 
          variant="body2" 
          color="text.secondary"
        >
          {platformSelected 
            ? 'Choose an action to get started' 
            : 'Select a platform above to enable actions'}
        </Typography>
      </Box>
      
      <Box 
        sx={{ 
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
          gap: 2
        }}
      >
        <ActionButton
          title="Analyze Ad"
          description="Paste or type your ad copy"
          icon={AddCircleOutline}
          onClick={() => {
            console.log('🔄 QuickActions: Analyze button clicked');
            console.log('📝 QuickActions: platformSelected:', platformSelected);
            console.log('📝 QuickActions: disabled:', disabled);
            console.log('📝 QuickActions: onAnalyzeClick function:', typeof onAnalyzeClick);
            if (onAnalyzeClick) {
              console.log('✅ QuickActions: Calling onAnalyzeClick');
              onAnalyzeClick();
            } else {
              console.log('❌ QuickActions: onAnalyzeClick is null/undefined');
            }
          }}
          variant="contained"
          color="primary"
          disabled={!platformSelected || disabled}
        />
        
        <ActionButton
          title="Upload CSV"
          description="Batch analyze multiple ads"
          icon={CloudUpload}
          onClick={onUploadClick}
          variant="outlined"
          disabled={!platformSelected || disabled}
        />
        
        <ActionButton
          title="View History"
          description="See your recent analyses"
          icon={History}
          onClick={onHistoryClick}
          variant="outlined"
          disabled={disabled}
        />
        
        <ActionButton
          title="View Trends"
          description="Check performance metrics"
          icon={TrendingUp}
          onClick={onTrendsClick}
          variant="outlined"
          disabled={disabled}
        />
      </Box>
      
      {!platformSelected && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Box 
            sx={{ 
              mt: 3, 
              p: 2, 
              borderRadius: 2,
              backgroundColor: alpha(theme.palette.warning.main, 0.05),
              border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`
            }}
          >
            <Typography 
              variant="body2" 
              color="warning.dark"
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1,
                fontWeight: 500
              }}
            >
              ⓘ Please select a platform above to start analyzing ads
            </Typography>
          </Box>
        </motion.div>
      )}
    </Paper>
  );
};

export default QuickActions;