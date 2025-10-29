import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  IconButton,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Alert,
  Fab,
  Slide,
  Fade
} from '@mui/material';
import {
  Close as CloseIcon,
  HelpOutline as HelpIcon,
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import axios from 'axios';

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const FAQ_ITEMS = [
  {
    question: 'How do credits work?',
    answer: 'Each ad analysis consumes credits based on the complexity. Basic analyses use 1 credit, while advanced analyses with multiple platforms may use 2-3 credits. Credits refresh monthly based on your plan.'
  },
  {
    question: 'How to upgrade my plan?',
    answer: 'Navigate to Billing in the sidebar, select your desired plan, and complete the checkout process. Your new credits will be available immediately, and you\'ll be billed on your next cycle.'
  },
  {
    question: 'Payment issues?',
    answer: 'If you\'re experiencing payment issues, please ensure your card is valid and has sufficient funds. For billing questions, contact your payment provider or submit a support ticket with "Billing Issue" selected.'
  },
  {
    question: 'How to cancel subscription?',
    answer: 'Go to Billing > Manage Subscription > Cancel. Your access will continue until the end of your billing period. You can reactivate anytime before the period ends.'
  }
];

const SUBJECT_OPTIONS = [
  'Bug Report',
  'Feature Request',
  'Billing Issue',
  'General Question',
  'Technical Support',
  'Account Issue'
];

const SupportWidget = () => {
  const { user, isAuthenticated } = useAuth();
  const [open, setOpen] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedFaq, setExpandedFaq] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: 'General Question',
    priority: 'normal',
    message: ''
  });

  // Pre-fill form if user is authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      setFormData(prev => ({
        ...prev,
        name: user.user_metadata?.full_name || user.email?.split('@')[0] || '',
        email: user.email || ''
      }));
    }
  }, [isAuthenticated, user]);

  const handleOpen = () => {
    setOpen(true);
    setError('');
    setShowSuccess(false);
  };

  const handleClose = () => {
    setOpen(false);
    setShowSuccess(false);
    setError('');
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const handleFaqChange = (panel) => (event, isExpanded) => {
    setExpandedFaq(isExpanded ? panel : false);
  };

  const validateForm = () => {
    if (!formData.name.trim() || formData.name.length < 2) {
      setError('Please enter your name (at least 2 characters)');
      return false;
    }
    if (!formData.email.trim() || !formData.email.includes('@')) {
      setError('Please enter a valid email address');
      return false;
    }
    if (!formData.message.trim() || formData.message.length < 20) {
      setError('Please enter a message (at least 20 characters)');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      
      const payload = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        subject: formData.subject,
        priority: formData.priority,
        message: formData.message.trim(),
        user_id: user?.id || null
      };

      const response = await axios.post(`${API_URL}/api/support/send`, payload);

      if (response.data.success) {
        setShowSuccess(true);
        // Reset form after 2 seconds
        setTimeout(() => {
          setFormData({
            name: user?.user_metadata?.full_name || user?.email?.split('@')[0] || '',
            email: user?.email || '',
            subject: 'General Question',
            priority: 'normal',
            message: ''
          });
          setTimeout(() => handleClose(), 1500);
        }, 2000);
      }
    } catch (err) {
      console.error('Support ticket error:', err);
      
      if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please wait before submitting another ticket. Maximum 3 tickets per hour.');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to submit support ticket. Please try again or email us directly.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <Fade in={!open}>
        <Fab
          color="primary"
          aria-label="support"
          onClick={handleOpen}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            width: 64,
            height: 64,
            background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
            boxShadow: '0 8px 32px rgba(124, 58, 237, 0.4)',
            animation: 'pulse 2s infinite',
            '@keyframes pulse': {
              '0%': {
                boxShadow: '0 8px 32px rgba(124, 58, 237, 0.4)'
              },
              '50%': {
                boxShadow: '0 8px 48px rgba(192, 132, 252, 0.6)'
              },
              '100%': {
                boxShadow: '0 8px 32px rgba(124, 58, 237, 0.4)'
              }
            },
            '&:hover': {
              background: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 50%, #A855F7 100%)',
              transform: 'scale(1.05)',
              boxShadow: '0 12px 48px rgba(192, 132, 252, 0.6)'
            },
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            zIndex: 1300
          }}
        >
          <HelpIcon sx={{ fontSize: 32 }} />
        </Fab>
      </Fade>

      {/* Support Dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        TransitionComponent={Transition}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            background: 'linear-gradient(135deg, #1A0F2E 0%, #0F0B1D 100%)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            boxShadow: '0 20px 60px rgba(124, 58, 237, 0.3)'
          }
        }}
      >
        <DialogTitle
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid rgba(168, 85, 247, 0.2)',
            pb: 2
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <HelpIcon sx={{ color: '#A855F7' }} />
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#F9FAFB' }}>
              Get Support
            </Typography>
          </Box>
          <IconButton onClick={handleClose} sx={{ color: '#E5E7EB' }}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ mt: 2 }}>
          {showSuccess ? (
            <Box
              sx={{
                textAlign: 'center',
                py: 6,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2
              }}
            >
              <CheckCircleIcon sx={{ fontSize: 80, color: '#10b981' }} />
              <Typography variant="h5" sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                Message Sent Successfully!
              </Typography>
              <Typography sx={{ color: '#E5E7EB' }}>
                We'll respond within 24 hours
              </Typography>
            </Box>
          ) : (
            <>
              {/* FAQ Section */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, color: '#F9FAFB', fontWeight: 600 }}>
                  Common Questions
                </Typography>
                {FAQ_ITEMS.map((item, index) => (
                  <Accordion
                    key={index}
                    expanded={expandedFaq === `panel${index}`}
                    onChange={handleFaqChange(`panel${index}`)}
                    sx={{
                      background: 'rgba(26, 15, 46, 0.5)',
                      border: '1px solid rgba(168, 85, 247, 0.2)',
                      borderRadius: '8px !important',
                      mb: 1,
                      '&:before': { display: 'none' },
                      '&.Mui-expanded': {
                        margin: '0 0 8px 0'
                      }
                    }}
                  >
                    <AccordionSummary
                      expandIcon={<ExpandMoreIcon sx={{ color: '#A855F7' }} />}
                      sx={{ color: '#F9FAFB' }}
                    >
                      <Typography sx={{ fontWeight: 500 }}>{item.question}</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography sx={{ color: '#E5E7EB' }}>{item.answer}</Typography>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>

              <Typography variant="h6" sx={{ mb: 2, color: '#F9FAFB', fontWeight: 600 }}>
                Still Need Help?
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Name"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  required
                  sx={{ mb: 2 }}
                  disabled={loading}
                />

                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  required
                  sx={{ mb: 2 }}
                  disabled={loading}
                />

                <TextField
                  fullWidth
                  select
                  label="Subject"
                  value={formData.subject}
                  onChange={(e) => handleChange('subject', e.target.value)}
                  sx={{ mb: 2 }}
                  disabled={loading}
                >
                  {SUBJECT_OPTIONS.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </TextField>

                <FormControl component="fieldset" sx={{ mb: 2, width: '100%' }}>
                  <FormLabel
                    component="legend"
                    sx={{ color: '#E5E7EB', mb: 1, fontWeight: 500 }}
                  >
                    Priority
                  </FormLabel>
                  <RadioGroup
                    row
                    value={formData.priority}
                    onChange={(e) => handleChange('priority', e.target.value)}
                  >
                    <FormControlLabel
                      value="normal"
                      control={<Radio />}
                      label="Normal"
                      disabled={loading}
                      sx={{
                        color: '#E5E7EB',
                        '& .MuiFormControlLabel-label': { color: '#E5E7EB' }
                      }}
                    />
                    <FormControlLabel
                      value="urgent"
                      control={<Radio />}
                      label="Urgent"
                      disabled={loading}
                      sx={{
                        color: '#E5E7EB',
                        '& .MuiFormControlLabel-label': { color: '#E5E7EB' }
                      }}
                    />
                  </RadioGroup>
                </FormControl>

                <TextField
                  fullWidth
                  label="Message"
                  multiline
                  rows={4}
                  value={formData.message}
                  onChange={(e) => handleChange('message', e.target.value)}
                  required
                  placeholder="Please describe your issue or question in detail (minimum 20 characters)"
                  helperText={`${formData.message.length} / 20 minimum characters`}
                  sx={{ mb: 2 }}
                  disabled={loading}
                />
              </Box>
            </>
          )}
        </DialogContent>

        {!showSuccess && (
          <DialogActions sx={{ p: 3, borderTop: '1px solid rgba(168, 85, 247, 0.2)' }}>
            <Button
              onClick={handleClose}
              disabled={loading}
              sx={{ color: '#E5E7EB' }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              variant="contained"
              disabled={loading || formData.message.length < 20}
              startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              sx={{
                background: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 50%, #A855F7 100%)'
                }
              }}
            >
              {loading ? 'Sending...' : 'Send Message'}
            </Button>
          </DialogActions>
        )}
      </Dialog>
    </>
  );
};

export default SupportWidget;
