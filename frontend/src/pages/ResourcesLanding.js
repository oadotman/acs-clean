import React from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Stack,
  Chip,
  Avatar,
  Paper,
  InputBase,
  IconButton
} from '@mui/material';
import {
  Code as ApiIcon,
  Description as DocsIcon,
  School as TutorialsIcon,
  Business as CaseStudiesIcon,
  VideoLibrary as VideoIcon,
  Article as BlogIcon,
  Event as WebinarIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  ArrowForward,
  Star,
  TrendingUp,
  People
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';

const ResourcesLanding = () => {
  const navigate = useNavigate();

  const resourceCategories = [
    {
      title: 'API Documentation',
      description: 'Complete API reference, authentication guides, and integration examples for developers.',
      icon: <ApiIcon sx={{ fontSize: 40 }} />,
      color: 'primary.main',
      bgColor: 'primary.light',
      link: '/resources/api',
      badge: 'Technical',
      items: ['REST API Reference', 'Authentication', 'SDKs & Libraries', 'Webhooks']
    },
    {
      title: 'Getting Started',
      description: 'Quick start guides to help you set up and launch your first campaign in minutes.',
      icon: <DocsIcon sx={{ fontSize: 40 }} />,
      color: 'success.main',
      bgColor: 'success.light',
      link: '/resources/getting-started',
      badge: 'Beginner',
      items: ['Account Setup', 'First Analysis', 'Tool Overview', 'Quick Wins']
    },
    {
      title: 'Tutorials & Guides',
      description: 'Step-by-step tutorials covering advanced features and marketing strategies.',
      icon: <TutorialsIcon sx={{ fontSize: 40 }} />,
      color: 'secondary.main',
      bgColor: 'secondary.light',
      link: '/resources/tutorials',
      badge: 'Popular',
      items: ['Advanced Features', 'Workflow Guides', 'Best Practices', 'Tips & Tricks']
    },
    {
      title: 'Case Studies',
      description: 'Real-world success stories showing how businesses achieved 300%+ ROAS increases.',
      icon: <CaseStudiesIcon sx={{ fontSize: 40 }} />,
      color: 'warning.main',
      bgColor: 'warning.light',
      link: '/resources/case-studies',
      badge: 'Results',
      items: ['E-commerce Success', 'SaaS Growth', 'Agency Case Studies', 'ROI Analysis']
    },
    {
      title: 'Video Library',
      description: 'Product demos, feature walkthroughs, and marketing masterclasses.',
      icon: <VideoIcon sx={{ fontSize: 40 }} />,
      color: 'error.main',
      bgColor: 'error.light',
      link: '/resources/videos',
      badge: 'Visual',
      items: ['Product Demos', 'Feature Tutorials', 'Webinar Recordings', 'Expert Interviews']
    },
    {
      title: 'Blog & Insights',
      description: 'Latest marketing trends, product updates, and industry insights from our experts.',
      icon: <BlogIcon sx={{ fontSize: 40 }} />,
      color: 'info.main',
      bgColor: 'info.light',
      link: '/blog',
      badge: 'Fresh',
      items: ['Marketing Trends', 'Product Updates', 'Industry Reports', 'Expert Opinions']
    }
  ];

  const featuredResources = [
    {
      title: 'Complete Ad Copy Analysis Guide',
      description: 'Learn how to analyze and optimize ad copy using all 9 tools in our platform.',
      type: 'Guide',
      readTime: '15 min read',
      link: '/resources/tutorials/complete-analysis-guide',
      featured: true
    },
    {
      title: 'API Integration in 10 Minutes',
      description: 'Quick start guide to integrate AdCopySurge API into your existing workflow.',
      type: 'Tutorial',
      readTime: '10 min read',
      link: '/resources/api/quick-start',
      featured: true
    },
    {
      title: 'E-commerce Success Story: 450% ROAS Increase',
      description: 'How TechGadgets increased their ROAS by 450% using our compliance checker and ROI generator.',
      type: 'Case Study',
      readTime: '8 min read',
      link: '/resources/case-studies/techgadgets-success',
      featured: true
    }
  ];

  const stats = [
    { icon: <Star />, number: '500+', label: 'Resources Available' },
    { icon: <TrendingUp />, number: '50k+', label: 'Monthly Readers' },
    { icon: <People />, number: '10k+', label: 'Community Members' }
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
                Resources & Documentation
              </Typography>
              <Typography variant="h5" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
                Everything you need to master ad copy optimization and maximize your marketing ROI
              </Typography>
              <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.8)' }}>
                From API documentation to marketing masterclasses, find guides, tutorials, 
                and case studies to help you succeed with AdCopySurge.
              </Typography>
              
              {/* Search Bar */}
              <Paper
                sx={{
                  p: 1,
                  display: 'flex',
                  alignItems: 'center',
                  maxWidth: 500,
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  backdropFilter: 'blur(10px)'
                }}
              >
                <SearchIcon sx={{ color: 'text.secondary', mr: 1, ml: 1 }} />
                <InputBase
                  sx={{ ml: 1, flex: 1 }}
                  placeholder="Search resources, tutorials, guides..."
                />
                <IconButton type="button" sx={{ p: 1, color: 'primary.main' }}>
                  <SearchIcon />
                </IconButton>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              {/* Stats */}
              <Paper
                elevation={8}
                sx={{
                  p: 3,
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 3
                }}
              >
                <Typography variant="h6" color="text.primary" sx={{ mb: 2, textAlign: 'center' }}>
                  Resource Hub Stats
                </Typography>
                <Grid container spacing={2}>
                  {stats.map((stat, index) => (
                    <Grid item xs={4} key={index}>
                      <Box textAlign="center">
                        <Avatar
                          sx={{
                            bgcolor: 'primary.main',
                            width: 32,
                            height: 32,
                            mx: 'auto',
                            mb: 1
                          }}
                        >
                          {stat.icon}
                        </Avatar>
                        <Typography variant="h6" color="primary.main" fontWeight={700}>
                          {stat.number}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {stat.label}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Featured Resources */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
            Featured Resources
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
            Handpicked content to help you get the most out of AdCopySurge
          </Typography>
          
          <Grid container spacing={3}>
            {featuredResources.map((resource, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card
                  elevation={3}
                  sx={{
                    height: '100%',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 6
                    }
                  }}
                  onClick={() => navigate(resource.link)}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                      <Chip
                        label={resource.type}
                        color="primary"
                        size="small"
                        variant="outlined"
                      />
                      {resource.featured && (
                        <Chip
                          label="Featured"
                          color="warning"
                          size="small"
                        />
                      )}
                    </Stack>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                      {resource.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {resource.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {resource.readTime}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Resource Categories */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
            Browse by Category
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
            Find exactly what you're looking for with our organized resource library
          </Typography>
          
          <Grid container spacing={4}>
            {resourceCategories.map((category, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card
                  elevation={2}
                  sx={{
                    height: '100%',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    position: 'relative',
                    overflow: 'visible',
                    '&:hover': {
                      transform: 'translateY(-6px)',
                      boxShadow: 8
                    }
                  }}
                  onClick={() => navigate(category.link)}
                >
                  <Chip
                    label={category.badge}
                    color="primary"
                    size="small"
                    sx={{
                      position: 'absolute',
                      top: -8,
                      right: 16,
                      fontWeight: 600,
                      zIndex: 1
                    }}
                  />
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar
                        sx={{
                          bgcolor: category.bgColor,
                          color: category.color,
                          width: 60,
                          height: 60,
                          mr: 2
                        }}
                      >
                        {category.icon}
                      </Avatar>
                      <Box>
                        <Typography variant="h5" sx={{ fontWeight: 600, mb: 0.5 }}>
                          {category.title}
                        </Typography>
                      </Box>
                    </Box>
                    
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                      {category.description}
                    </Typography>
                    
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                      What you'll find:
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      {category.items.map((item, itemIndex) => (
                        <Chip
                          key={itemIndex}
                          label={item}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.7rem' }}
                        />
                      ))}
                    </Stack>
                    
                    <Button
                      component={Link}
                      to={category.link}
                      variant="contained"
                      endIcon={<ArrowForward />}
                      sx={{ mt: 3 }}
                    >
                      Explore {category.title}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Quick Links */}
        <Box sx={{ mb: 8 }}>
          <Paper
            sx={{
              p: 4,
              background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              textAlign: 'center'
            }}
          >
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
              Need Help Getting Started?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
              Our support team is here to help you succeed. Get personalized assistance, 
              join our community, or schedule a demo.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              <Button
                component={Link}
                to="/contact"
                variant="contained"
                size="large"
                startIcon={<People />}
              >
                Contact Support
              </Button>
              <Button
                component={Link}
                to="/community"
                variant="outlined"
                size="large"
                startIcon={<People />}
              >
                Join Community
              </Button>
              <Button
                component={Link}
                to="/demo"
                variant="outlined"
                size="large"
                startIcon={<VideoIcon />}
              >
                Schedule Demo
              </Button>
            </Stack>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
};

export default ResourcesLanding;
