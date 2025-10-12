import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  Box,
  CircularProgress,
  IconButton,
  LinearProgress,
  alpha,
  useTheme
} from '@mui/material';
import {
  Close as CloseIcon,
  AccessTime as ClockIcon
} from '@mui/icons-material';

const AnalysisLoadingModal = ({ 
  open, 
  onClose, 
  onComplete,
  adText = "" 
}) => {
  const theme = useTheme();
  const [progress, setProgress] = useState(0);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [currentStep, setCurrentStep] = useState('Initializing...');

  const steps = [
    'Analyzing compliance violations...',
    'Checking psychology triggers...',
    'Evaluating call-to-action strength...',
    'Scanning for legal risks...',
    'Assessing brand voice consistency...',
    'Optimizing for ROI potential...',
    'Generating A/B test variations...',
    'Running platform-specific checks...',
    'Finalizing recommendations...'
  ];

  useEffect(() => {
    if (!open) {
      setProgress(0);
      setTimeElapsed(0);
      setCurrentStep('Initializing...');
      return;
    }

    const startTime = Date.now();
    const totalDuration = 15000; // 15 seconds

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const newTimeElapsed = Math.floor(elapsed / 1000);
      const newProgress = Math.min((elapsed / totalDuration) * 100, 100);
      
      setTimeElapsed(newTimeElapsed);
      setProgress(newProgress);

      // Update current step based on progress
      const stepIndex = Math.min(
        Math.floor((elapsed / totalDuration) * steps.length), 
        steps.length - 1
      );
      setCurrentStep(steps[stepIndex]);

      // Complete analysis after 15 seconds
      if (elapsed >= totalDuration) {
        clearInterval(interval);
        setTimeout(() => {
          onComplete();
        }, 500);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [open, onComplete, steps]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          p: 2,
          backgroundImage: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
          border: `2px solid ${alpha(theme.palette.primary.main, 0.1)}`
        }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h5" fontWeight={700} color="text.primary">
            Analyzing your ad...
          </Typography>
          <IconButton 
            onClick={onClose}
            size="small"
            sx={{ 
              color: 'text.secondary',
              '&:hover': {
                backgroundColor: alpha(theme.palette.error.main, 0.1),
                color: 'error.main'
              }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ textAlign: 'center', py: 3 }}>
          {/* Clock Icon and Timer */}
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              mb: 3,
              gap: 1
            }}
          >
            <ClockIcon 
              sx={{ 
                fontSize: '2rem', 
                color: 'primary.main',
                animation: progress > 0 ? 'pulse 2s infinite' : 'none'
              }} 
            />
            <Typography variant="h6" fontWeight={600} color="text.secondary">
              {timeElapsed}s / 15s
            </Typography>
          </Box>

          {/* Progress Indicator */}
          <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
            <CircularProgress
              variant="determinate"
              value={progress}
              size={120}
              thickness={4}
              sx={{
                color: theme.palette.primary.main,
                '& .MuiCircularProgress-circle': {
                  strokeLinecap: 'round',
                }
              }}
            />
            <Box
              sx={{
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column'
              }}
            >
              <Typography 
                variant="h4" 
                component="div" 
                fontWeight={700}
                color="primary.main"
              >
                {Math.round(progress)}%
              </Typography>
            </Box>
          </Box>

          {/* Time Remaining */}
          <Typography 
            variant="body1" 
            color="text.secondary" 
            sx={{ mb: 2, fontWeight: 500 }}
          >
            Takes about 15 seconds
          </Typography>

          {/* Current Step */}
          <Typography 
            variant="h6" 
            fontWeight={600}
            color="text.primary"
            sx={{ mb: 3, minHeight: '1.5rem' }}
          >
            Running 9 intelligence tools...
          </Typography>

          {/* Current Processing Step */}
          <Box sx={{ mb: 3 }}>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ 
                mb: 1,
                fontStyle: 'italic',
                minHeight: '1.25rem'
              }}
            >
              {currentStep}
            </Typography>
            
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`
                }
              }}
            />
          </Box>

          {/* Ad Preview */}
          {adText && (
            <Box
              sx={{
                p: 2,
                backgroundColor: alpha(theme.palette.grey[100], 0.5),
                borderRadius: 2,
                border: `1px solid ${alpha(theme.palette.grey[300], 0.5)}`,
                maxHeight: 100,
                overflow: 'hidden'
              }}
            >
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ 
                  fontStyle: 'italic',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}
              >
                "{adText}"
              </Typography>
            </Box>
          )}
        </Box>
      </DialogContent>

      {/* CSS for pulse animation */}
      <style>
        {`
          @keyframes pulse {
            0% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
            100% {
              opacity: 1;
            }
          }
        `}
      </style>
    </Dialog>
  );
};

export default AnalysisLoadingModal;