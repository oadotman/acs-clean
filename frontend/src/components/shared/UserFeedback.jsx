import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Collapse,
  Stack,
  Tooltip,
  Divider,
  Alert,
  Fade
} from '@mui/material';
import {
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Feedback as FeedbackIcon,
  Close as CloseIcon,
  Send as SendIcon,
  CheckCircle as CheckIcon,
  ExpandMore as ExpandIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Feedback categories and options
const FEEDBACK_CATEGORIES = {
  tone: {
    label: 'Tone Issues',
    icon: '🎭',
    options: [
      { value: 'too_formal', label: 'Too formal for my audience' },
      { value: 'too_casual', label: 'Too casual/unprofessional' },
      { value: 'wrong_emotion', label: 'Wrong emotional tone' },
      { value: 'inconsistent_tone', label: 'Inconsistent brand voice' }
    ]
  },
  length: {
    label: 'Length Issues',
    icon: '📏',
    options: [
      { value: 'too_long', label: 'Too long/wordy' },
      { value: 'too_short', label: 'Too short/lacks detail' },
      { value: 'poor_structure', label: 'Poor structure/flow' }
    ]
  },
  content: {
    label: 'Content Issues',
    icon: '📝',
    options: [
      { value: 'missing_key_points', label: 'Missing key selling points' },
      { value: 'incorrect_facts', label: 'Incorrect or irrelevant information' },
      { value: 'weak_cta', label: 'Weak or unclear call-to-action' },
      { value: 'generic_content', label: 'Too generic/not specific enough' }
    ]
  },
  creativity: {
    label: 'Creativity Issues',
    icon: '🎨',
    options: [
      { value: 'too_creative', label: 'Too creative/risky for my brand' },
      { value: 'not_creative', label: 'Not creative enough/boring' },
      { value: 'off_brand', label: 'Doesn\'t match my brand personality' },
      { value: 'cliche_heavy', label: 'Too many clichés or overused phrases' }
    ]
  },
  targeting: {
    label: 'Audience Targeting',
    icon: '🎯',
    options: [
      { value: 'wrong_audience', label: 'Doesn\'t speak to my target audience' },
      { value: 'too_broad', label: 'Too broad/not specific enough' },
      { value: 'wrong_platform', label: 'Doesn\'t fit this platform well' }
    ]
  }
};

const UserFeedback = ({
  generatedCopy,
  analysisId,
  onFeedbackSubmit,
  platform = 'facebook',
  compact = false,
  variant = 'card' // 'card', 'inline', 'floating'
}) => {
  const [feedback, setFeedback] = useState(null); // 'positive' or 'negative'
  const [showDetailedFeedback, setShowDetailedFeedback] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedIssues, setSelectedIssues] = useState([]);
  const [customFeedback, setCustomFeedback] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showThankYou, setShowThankYou] = useState(false);

  // Handle thumbs up/down click
  const handleFeedbackClick = useCallback((type) => {
    setFeedback(type);
    
    if (type === 'positive') {
      // For positive feedback, submit immediately
      submitFeedback({
        type: 'positive',
        rating: 5,
        category: null,
        issues: [],
        comment: 'User liked the generated copy'
      });
    } else {
      // For negative feedback, show detailed form
      setShowDetailedFeedback(true);
    }
  }, []);

  // Handle issue selection
  const handleIssueToggle = (issue) => {
    setSelectedIssues(prev => 
      prev.includes(issue) 
        ? prev.filter(i => i !== issue)
        : [...prev, issue]
    );
  };

  // Submit feedback to parent/service
  const submitFeedback = async (feedbackData) => {
    setIsSubmitting(true);
    
    try {
      const fullFeedbackData = {
        ...feedbackData,
        analysisId,
        platform,
        generatedCopy,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        sessionId: sessionStorage.getItem('sessionId') || 'unknown'
      };

      // Call parent callback if provided
      if (onFeedbackSubmit) {
        await onFeedbackSubmit(fullFeedbackData);
      }

      setIsSubmitted(true);
      setShowThankYou(true);
      
      // Hide thank you message after 3 seconds
      setTimeout(() => {
        setShowThankYou(false);
      }, 3000);
      
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle detailed feedback submission
  const handleDetailedSubmit = () => {
    const feedbackData = {
      type: 'negative',
      rating: selectedIssues.length > 2 ? 1 : 2,
      category: selectedCategory,
      issues: selectedIssues,
      comment: customFeedback.trim(),
      platform,
      analysisId
    };

    submitFeedback(feedbackData);
    setShowDetailedFeedback(false);
  };

  // Reset feedback state
  const resetFeedback = () => {
    setFeedback(null);
    setShowDetailedFeedback(false);
    setSelectedCategory('');
    setSelectedIssues([]);
    setCustomFeedback('');
    setIsSubmitted(false);
  };

  if (compact) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {!isSubmitted ? (
          <>
            <Tooltip title="This result was helpful">
              <IconButton
                size="small"
                color={feedback === 'positive' ? 'success' : 'default'}
                onClick={() => handleFeedbackClick('positive')}
                disabled={isSubmitting}
              >
                <ThumbUpIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="This result needs improvement">
              <IconButton
                size="small"
                color={feedback === 'negative' ? 'error' : 'default'}
                onClick={() => handleFeedbackClick('negative')}
                disabled={isSubmitting}
              >
                <ThumbDownIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </>
        ) : (
          <Fade in={showThankYou}>
            <Chip
              icon={<CheckIcon />}
              label="Thanks!"
              color="success"
              size="small"
              sx={{ animation: showThankYou ? 'pulse 1s ease-in-out' : 'none' }}
            />
          </Fade>
        )}
      </Box>
    );
  }

  if (variant === 'floating') {
    return (
      <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          zIndex: 1000
        }}
      >
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ duration: 0.3, type: 'spring' }}
        >
          <Card
            elevation={8}
            sx={{
              minWidth: 200,
              border: '2px solid',
              borderColor: 'primary.main'
            }}
          >
            <CardContent sx={{ py: 2 }}>
              <Typography variant="body2" fontWeight={600} gutterBottom>
                How was this result?
              </Typography>
              <Stack direction="row" spacing={1} justifyContent="center">
                <Button
                  startIcon={<ThumbUpIcon />}
                  onClick={() => handleFeedbackClick('positive')}
                  color="success"
                  variant={feedback === 'positive' ? 'contained' : 'outlined'}
                  size="small"
                  disabled={isSubmitting}
                >
                  Good
                </Button>
                <Button
                  startIcon={<ThumbDownIcon />}
                  onClick={() => handleFeedbackClick('negative')}
                  color="error"
                  variant={feedback === 'negative' ? 'contained' : 'outlined'}
                  size="small"
                  disabled={isSubmitting}
                >
                  Needs Work
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    );
  }

  // Default card variant
  return (
    <>
      <Card 
        variant="outlined" 
        sx={{ 
          mb: 2,
          backgroundColor: isSubmitted ? 'rgba(76, 175, 80, 0.05)' : 'background.paper'
        }}
      >
        <CardContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FeedbackIcon color="primary" />
              <Typography variant="subtitle2" fontWeight={600}>
                {isSubmitted ? 'Thank you for your feedback!' : 'How was this result?'}
              </Typography>
            </Box>
            
            {!isSubmitted ? (
              <Stack direction="row" spacing={1}>
                <Button
                  startIcon={<ThumbUpIcon />}
                  onClick={() => handleFeedbackClick('positive')}
                  color="success"
                  variant={feedback === 'positive' ? 'contained' : 'outlined'}
                  size="small"
                  disabled={isSubmitting}
                  sx={{ textTransform: 'none' }}
                >
                  Helpful
                </Button>
                <Button
                  startIcon={<ThumbDownIcon />}
                  onClick={() => handleFeedbackClick('negative')}
                  color="error"
                  variant={feedback === 'negative' ? 'contained' : 'outlined'}
                  size="small"
                  disabled={isSubmitting}
                  sx={{ textTransform: 'none' }}
                >
                  Needs Improvement
                </Button>
              </Stack>
            ) : (
              <Chip
                icon={<CheckIcon />}
                label="Feedback submitted"
                color="success"
                size="small"
              />
            )}
          </Box>
          
          {isSubmitted && (
            <Box sx={{ mt: 2 }}>
              <Alert severity="success" variant="outlined">
                Your feedback helps us improve the AI system. Thank you for taking the time to share your thoughts!
              </Alert>
              <Button
                size="small"
                variant="text"
                onClick={resetFeedback}
                sx={{ mt: 1, textTransform: 'none' }}
              >
                Submit different feedback
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Detailed Feedback Dialog */}
      <Dialog
        open={showDetailedFeedback}
        onClose={() => setShowDetailedFeedback(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FeedbackIcon color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Help Us Improve
            </Typography>
          </Box>
          <IconButton onClick={() => setShowDetailedFeedback(false)}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            What could be better about this generated copy? Your feedback helps train our AI to create better results.
          </Typography>

          {/* Feedback Categories */}
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            What type of issue did you encounter?
          </Typography>
          
          <RadioGroup
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            sx={{ mb: 3 }}
          >
            {Object.entries(FEEDBACK_CATEGORIES).map(([key, category]) => (
              <FormControlLabel
                key={key}
                value={key}
                control={<Radio />}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span>{category.icon}</span>
                    <span>{category.label}</span>
                  </Box>
                }
              />
            ))}
          </RadioGroup>

          {/* Specific Issues */}
          {selectedCategory && (
            <Collapse in={Boolean(selectedCategory)} timeout="auto" unmountOnExit>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Specific issues (select all that apply):
              </Typography>
              
              <Stack spacing={1} sx={{ mb: 3 }}>
                {FEEDBACK_CATEGORIES[selectedCategory].options.map((option) => (
                  <Chip
                    key={option.value}
                    label={option.label}
                    variant={selectedIssues.includes(option.value) ? 'filled' : 'outlined'}
                    color={selectedIssues.includes(option.value) ? 'primary' : 'default'}
                    onClick={() => handleIssueToggle(option.value)}
                    sx={{ 
                      justifyContent: 'flex-start',
                      '& .MuiChip-label': { textAlign: 'left' }
                    }}
                  />
                ))}
              </Stack>
            </Collapse>
          )}

          {/* Additional Comments */}
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Additional comments (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            placeholder="Tell us more about what you'd like to see improved..."
            value={customFeedback}
            onChange={(e) => setCustomFeedback(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          <Typography variant="caption" color="text.secondary">
            Your feedback is anonymous and helps improve the system for everyone.
          </Typography>
        </DialogContent>
        
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button 
            onClick={() => setShowDetailedFeedback(false)}
            color="inherit"
            sx={{ textTransform: 'none' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDetailedSubmit}
            variant="contained"
            startIcon={<SendIcon />}
            disabled={!selectedCategory || isSubmitting}
            sx={{ textTransform: 'none' }}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default UserFeedback;