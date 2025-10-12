import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Stack,
  Paper,
  Avatar,
  Divider
} from '@mui/material';
import {
  Email,
  Phone,
  LocationOn,
  Schedule,
  Send,
  CheckCircle,
  BusinessCenter,
  Support,
  School
} from '@mui/icons-material';

const ContactUs = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // TODO: Integrate with actual form submission service
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSubmitted(true);
      setFormData({ name: '', email: '', company: '', subject: '', message: '' });
    } catch (error) {
      console.error('Form submission failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const contactInfo = [
    {
      icon: <Email />,
      title: 'Email Us',
      details: 'support@adcopysurge.com',
      description: 'Get in touch for general inquiries'
    },
    {
      icon: <Phone />,
      title: 'Call Us',
      details: '+1 (555) 123-4567',
      description: 'Mon-Fri 9AM-6PM PST'
    },
    {
      icon: <LocationOn />,
      title: 'Visit Us',
      details: 'San Francisco, CA',
      description: 'Schedule an in-person meeting'
    },
    {
      icon: <Schedule />,
      title: 'Response Time',
      details: '< 24 hours',
      description: 'We respond to all inquiries quickly'
    }
  ];

  const contactReasons = [
    {
      icon: <BusinessCenter />,
      title: 'Sales & Partnerships',
      email: 'sales@adcopysurge.com',
      description: 'Enterprise sales, partnerships, and custom solutions'
    },
    {
      icon: <Support />,
      title: 'Technical Support',
      email: 'support@adcopysurge.com',
      description: 'Account issues, bug reports, and technical assistance'
    },
    {
      icon: <School />,
      title: 'Training & Education',
      email: 'training@adcopysurge.com',
      description: 'Onboarding, workshops, and certification programs'
    }
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: 8,
          mb: 6
        }}
      >
        <Container maxWidth="lg">
          <Box textAlign="center">
            <Typography
              variant="h2"
              sx={{
                fontWeight: 800,
                mb: 2,
                fontSize: { xs: '2rem', md: '2.5rem' }
              }}
            >
              Get in Touch
            </Typography>
            <Typography variant="h5" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
              We're here to help you succeed with your marketing campaigns
            </Typography>
            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', maxWidth: 600, mx: 'auto' }}>
              Whether you need technical support, want to explore enterprise solutions, 
              or just have questions about our platform, our team is ready to assist.
            </Typography>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="lg">
        <Grid container spacing={6}>
          {/* Contact Form */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
              <Typography variant="h4" sx={{ fontWeight: 600, mb: 3 }}>
                Send us a Message
              </Typography>
              
              {submitted ? (
                <Box textAlign="center" sx={{ py: 4 }}>
                  <CheckCircle color="success" sx={{ fontSize: 64, mb: 2 }} />
                  <Typography variant="h5" color="success.main" sx={{ mb: 2 }}>
                    Message Sent Successfully!
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Thank you for contacting us. We'll get back to you within 24 hours.
                  </Typography>
                  <Button
                    variant="outlined"
                    onClick={() => setSubmitted(false)}
                    sx={{ mt: 3 }}
                  >
                    Send Another Message
                  </Button>
                </Box>
              ) : (
                <Box component="form" onSubmit={handleSubmit}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        required
                        label="Full Name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        required
                        type="email"
                        label="Email Address"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Company (Optional)"
                        name="company"
                        value={formData.company}
                        onChange={handleChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        required
                        label="Subject"
                        name="subject"
                        value={formData.subject}
                        onChange={handleChange}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        required
                        multiline
                        rows={6}
                        label="Message"
                        name="message"
                        value={formData.message}
                        onChange={handleChange}
                        placeholder="Tell us about your needs, questions, or how we can help you..."
                      />
                    </Grid>
                  </Grid>
                  
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={loading}
                    startIcon={loading ? null : <Send />}
                    sx={{ mt: 3, px: 4 }}
                  >
                    {loading ? 'Sending...' : 'Send Message'}
                  </Button>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Contact Information */}
          <Grid item xs={12} md={4}>
            <Stack spacing={3}>
              <Card elevation={2}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
                    Contact Information
                  </Typography>
                  <Stack spacing={3}>
                    {contactInfo.map((info, index) => (
                      <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                        <Avatar
                          sx={{
                            bgcolor: 'primary.main',
                            width: 40,
                            height: 40
                          }}
                        >
                          {info.icon}
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle1" fontWeight={600}>
                            {info.title}
                          </Typography>
                          <Typography variant="body2" color="primary.main" sx={{ mb: 0.5 }}>
                            {info.details}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {info.description}
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>

              <Card elevation={2}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                    Specialized Support
                  </Typography>
                  <Stack spacing={2} divider={<Divider />}>
                    {contactReasons.map((reason, index) => (
                      <Box key={index}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          {reason.icon}
                          <Typography variant="subtitle2" fontWeight={600}>
                            {reason.title}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {reason.description}
                        </Typography>
                        <Typography variant="caption" color="primary.main">
                          {reason.email}
                        </Typography>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>

              <Paper
                sx={{
                  p: 3,
                  background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                  textAlign: 'center'
                }}
              >
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  Need Immediate Help?
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Check out our knowledge base and community forum for instant answers.
                </Typography>
                <Stack direction="column" spacing={1}>
                  <Button
                    variant="outlined"
                    size="small"
                    href="/resources"
                    fullWidth
                  >
                    Visit Help Center
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    href="/community"
                    fullWidth
                  >
                    Community Forum
                  </Button>
                </Stack>
              </Paper>
            </Stack>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default ContactUs;
