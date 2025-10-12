import React from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  Button,
  Stack,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Avatar,
  Chip,
  Divider,
  Alert
} from '@mui/material';
import {
  CheckCircle,
  Analytics,
  Speed,
  Security,
  TrendingUp,
  Lightbulb,
  Assignment,
  AutoAwesome,
  Rocket
} from '@mui/icons-material';
import StartIcon from '../../components/icons/StartIcon';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/authContext';

const GettingStarted = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const quickWins = [
    {
      title: "Run Your First Analysis",
      description: "Upload your existing ad copy and get instant insights",
      icon: <Analytics color="primary" />,
      time: "2 minutes",
      link: "/analyze"
    },
    {
      title: "Check Compliance",
      description: "Ensure your ads meet platform guidelines",
      icon: <Security color="primary" />,
      time: "1 minute",
      link: "/compliance-checker"
    },
    {
      title: "Generate A/B Tests",
      description: "Create 5-10 variations with different angles",
      icon: <Speed color="primary" />,
      time: "3 minutes",
      link: "/ab-test-generator"
    },
    {
      title: "Optimize for ROI",
      description: "Generate profit-focused copy variations",
      icon: <TrendingUp color="primary" />,
      time: "2 minutes",
      link: "/roi-generator"
    }
  ];

  const setupSteps = [
    {
      label: "Create Your Account",
      description: "Sign up for free and access all 9 tools immediately",
      content: [
        "No credit card required for free tier",
        "5 analyses per month per tool",
        "Access to all premium features for 30 days"
      ]
    },
    {
      label: "Complete Your Profile",
      description: "Set up your industry and preferences for better results",
      content: [
        "Select your primary industry (e-commerce, SaaS, etc.)",
        "Choose your main advertising platforms",
        "Set your brand voice preferences"
      ]
    },
    {
      label: "Run Your First Project",
      description: "Start with a simple ad copy analysis",
      content: [
        "Use the Quick Analysis for immediate results",
        "Try the Compliance Checker first - it's most impactful",
        "Review the detailed feedback and recommendations"
      ]
    },
    {
      label: "Explore All Tools",
      description: "Familiarize yourself with our 9 specialized tools",
      content: [
        "Each tool focuses on a specific aspect of ad optimization",
        "Use them individually or as part of a complete workflow",
        "Check the unified dashboard for project overview"
      ]
    }
  ];

  const toolOverview = [
    {
      name: "Ad Copy Analyzer",
      description: "Your starting point - comprehensive analysis with scoring",
      category: "Core"
    },
    {
      name: "Compliance Checker",
      description: "Avoid policy violations across all major platforms",
      category: "Essential"
    },
    {
      name: "ROI Copy Generator",
      description: "Generate profit-optimized copy for high-value customers",
      category: "Revenue"
    },
    {
      name: "A/B Test Generator",
      description: "Create multiple variations testing different angles",
      category: "Testing"
    },
    {
      name: "Industry Optimizer",
      description: "Adapt copy to industry-specific language and frameworks",
      category: "Targeting"
    },
    {
      name: "Performance Forensics",
      description: "Understand why ads perform well or poorly",
      category: "Analysis"
    },
    {
      name: "Psychology Scorer",
      description: "Score copy on 15+ psychological triggers",
      category: "Psychology"
    },
    {
      name: "Brand Voice Engine",
      description: "Ensure consistency across all generated copy",
      category: "Branding"
    },
    {
      name: "Legal Risk Scanner",
      description: "Identify problematic claims and get safer alternatives",
      category: "Compliance"
    }
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 6, md: 8 },
          mb: 4
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 800,
                  mb: 2,
                  fontSize: { xs: '2rem', md: '2.5rem' }
                }}
              >
                🚀 Getting Started with AdCopySurge
              </Typography>
              <Typography variant="h5" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
                Your complete guide to mastering ad copy optimization with our 9 intelligent tools
              </Typography>
              <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.8)', maxWidth: 600 }}>
                From compliance checking to ROI optimization, learn how to transform your marketing 
                campaigns and achieve 300%+ ROAS increases in just minutes.
              </Typography>
              
              {!isAuthenticated ? (
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/register')}
                    sx={{
                      background: 'linear-gradient(45deg, #FFD700 0%, #FFA000 100%)',
                      color: '#000',
                      fontWeight: 800,
                      '&:hover': {
                        background: 'linear-gradient(45deg, #FFC700 0%, #FF8F00 100%)',
                      }
                    }}
                  >
                    Start Free Account
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    sx={{
                      borderColor: 'rgba(255,255,255,0.5)',
                      color: 'white',
                      '&:hover': {
                        borderColor: 'white',
                        backgroundColor: 'rgba(255,255,255,0.1)'
                      }
                    }}
                    onClick={() => document.getElementById('quick-wins').scrollIntoView({ behavior: 'smooth' })}
                  >
                    View Quick Wins
                  </Button>
                </Stack>
              ) : (
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<StartIcon />}
                  onClick={() => navigate('/analysis/new')}
                  sx={{
                    background: 'linear-gradient(45deg, #FFD700 0%, #FFA000 100%)',
                    color: '#000',
                    fontWeight: 800,
                    '&:hover': {
                      background: 'linear-gradient(45deg, #FFC700 0%, #FF8F00 100%)',
                    }
                  }}
                >
                  Start Analysis
                </Button>
              )}
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper
                elevation={8}
                sx={{
                  p: 3,
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 3,
                  textAlign: 'center'
                }}
              >
                <Typography variant="h6" color="text.primary" sx={{ mb: 2 }}>
                  ⚡ Get Results In Minutes
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Join 500+ marketers already using AdCopySurge
                </Typography>
                <Stack direction="row" spacing={2} justifyContent="center">
                  <Chip label="Free Forever" color="success" size="small" />
                  <Chip label="9 Tools" color="primary" size="small" />
                  <Chip label="AI-Powered" color="secondary" size="small" />
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Quick Wins Section */}
        <Box id="quick-wins" sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            🎯 Quick Wins - Get Results in Under 10 Minutes
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            Start with these high-impact tasks to see immediate improvements
          </Typography>
          
          <Grid container spacing={3}>
            {quickWins.map((win, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card
                  elevation={3}
                  sx={{
                    height: '100%',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 8
                    }
                  }}
                  onClick={() => isAuthenticated ? navigate(win.link) : navigate('/register')}
                >
                  <CardContent sx={{ p: 3, textAlign: 'center' }}>
                    <Avatar
                      sx={{
                        bgcolor: 'primary.light',
                        width: 56,
                        height: 56,
                        mx: 'auto',
                        mb: 2
                      }}
                    >
                      {win.icon}
                    </Avatar>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                      {win.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {win.description}
                    </Typography>
                    <Chip
                      label={`${win.time} to complete`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Setup Steps */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            📋 Complete Setup Guide
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            Follow these steps to maximize your results with AdCopySurge
          </Typography>
          
          <Paper sx={{ p: 4 }}>
            <Stepper orientation="vertical">
              {setupSteps.map((step, index) => (
                <Step key={index} active={true}>
                  <StepLabel
                    StepIconComponent={() => (
                      <Avatar
                        sx={{
                          bgcolor: 'primary.main',
                          width: 32,
                          height: 32,
                          fontSize: '0.875rem',
                          fontWeight: 600
                        }}
                      >
                        {index + 1}
                      </Avatar>
                    )}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {step.label}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {step.description}
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <List>
                      {step.content.map((item, itemIndex) => (
                        <ListItem key={itemIndex} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CheckCircle color="success" sx={{ fontSize: 18 }} />
                          </ListItemIcon>
                          <ListItemText
                            primary={item}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                    {index === 0 && !isAuthenticated && (
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => navigate('/register')}
                        sx={{ mt: 1, mb: 2 }}
                      >
                        Create Free Account
                      </Button>
                    )}
                    {index === 2 && isAuthenticated && (
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => navigate('/analyze')}
                        sx={{ mt: 1, mb: 2 }}
                      >
                        Start First Analysis
                      </Button>
                    )}
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Paper>
        </Box>

        {/* Tool Overview */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
            🛠️ Tool Overview
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            Our 9 specialized tools work together to optimize every aspect of your ad copy
          </Typography>
          
          <Grid container spacing={2}>
            {toolOverview.map((tool, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card elevation={2} sx={{ p: 2 }}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Avatar
                      sx={{
                        bgcolor: 'primary.main',
                        width: 40,
                        height: 40,
                        fontSize: '1.2rem'
                      }}
                    >
                      {index + 1}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {tool.name}
                        </Typography>
                        <Chip 
                          label={tool.category} 
                          size="small" 
                          variant="outlined" 
                          color="primary" 
                        />
                      </Stack>
                      <Typography variant="body2" color="text.secondary">
                        {tool.description}
                      </Typography>
                    </Box>
                  </Stack>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Next Steps */}
        <Box sx={{ mb: 8 }}>
          <Paper
            sx={{
              p: 4,
              background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              textAlign: 'center'
            }}
          >
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
              🎉 Ready to Transform Your Ad Performance?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
              You now have everything you need to start optimizing your ad copy with AdCopySurge. 
              Join hundreds of marketers already seeing 300%+ ROAS increases.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              {!isAuthenticated ? (
                <>
                  <Button
                    component={Link}
                    to="/register"
                    variant="contained"
                    size="large"
                    startIcon={<Rocket />}
                  >
                    Start Your Free Account
                  </Button>
                  <Button
                    component={Link}
                    to="/resources/tutorials"
                    variant="outlined"
                    size="large"
                    startIcon={<Assignment />}
                  >
                    View Tutorials
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    component={Link}
                    to="/analyze"
                    variant="contained"
                    size="large"
                    startIcon={<AutoAwesome />}
                  >
                    Create Your First Analysis
                  </Button>
                  <Button
                    component={Link}
                    to="/resources/tutorials"
                    variant="outlined"
                    size="large"
                    startIcon={<Lightbulb />}
                  >
                    Learn Advanced Techniques
                  </Button>
                </>
              )}
            </Stack>
          </Paper>
        </Box>

        {/* Help Section */}
        <Box sx={{ mb: 4 }}>
          <Alert 
            severity="info" 
            icon={<Lightbulb />}
            sx={{ 
              borderRadius: 3,
              '& .MuiAlert-message': {
                width: '100%'
              }
            }}
          >
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Need Help Getting Started?
                </Typography>
                <Typography variant="body2">
                  Our support team is here to help you succeed. Get personalized guidance and tips.
                </Typography>
              </Box>
              <Button
                component={Link}
                to="/contact"
                variant="outlined"
                size="small"
              >
                Contact Support
              </Button>
            </Stack>
          </Alert>
        </Box>
      </Container>
    </Box>
  );
};

export default GettingStarted;
