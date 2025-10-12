import React, { useState, useCallback } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Chip,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack
} from '@mui/material';
import {
  Search,
  FilterList,
  ContentCopy,
  Favorite,
  FavoriteBorder,
  Visibility,
  Star,
  TrendingUp,
  Business,
  SportsEsports,
  Health,
  ShoppingCart,
  School
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import { EmptyState } from '../components/ui';
import toast from 'react-hot-toast';

// Mock templates data - in production, this would come from an API
const mockTemplates = [
  {
    id: 1,
    title: 'High-Converting SaaS Landing Page',
    description: 'Proven template for B2B software companies looking to increase sign-ups',
    category: 'saas',
    platform: 'facebook',
    industry: 'Technology',
    headline: 'Transform Your Business Process in 30 Days or Less',
    body_text: 'Join 10,000+ companies using our platform to streamline operations, reduce costs by 40%, and boost productivity. Get started with our free 14-day trial - no credit card required.',
    cta: 'Start Free Trial',
    score: 92,
    usage_count: 1247,
    is_premium: false,
    tags: ['B2B', 'SaaS', 'Conversion', 'Free Trial']
  },
  {
    id: 2,
    title: 'E-commerce Flash Sale',
    description: 'Create urgency and drive immediate purchases with this time-sensitive offer template',
    category: 'ecommerce',
    platform: 'instagram',
    industry: 'Retail',
    headline: '⚡ FLASH SALE: 50% Off Everything - 24 Hours Only!',
    body_text: 'Don\'t miss out! Our biggest sale of the year ends in 24 hours. Premium quality products at unbeatable prices. Free shipping on orders over $50. Limited stock available!',
    cta: 'Shop Now',
    score: 89,
    usage_count: 2103,
    is_premium: false,
    tags: ['E-commerce', 'Sale', 'Urgency', 'Limited Time']
  },
  {
    id: 3,
    title: 'Premium Fitness Challenge',
    description: 'Motivational template for fitness and health programs',
    category: 'fitness',
    platform: 'google',
    industry: 'Health & Fitness',
    headline: 'Transform Your Body in 90 Days - Guaranteed Results',
    body_text: 'Ready to make a real change? Our scientifically-backed 90-day transformation program has helped 50,000+ people achieve their dream body. Personal trainer included.',
    cta: 'Join Challenge',
    score: 87,
    usage_count: 856,
    is_premium: true,
    tags: ['Fitness', 'Transformation', 'Challenge', 'Results']
  },
  {
    id: 4,
    title: 'Professional Course Launch',
    description: 'Educational content template for online courses and coaching',
    category: 'education',
    platform: 'linkedin',
    industry: 'Education',
    headline: 'Master Digital Marketing in 6 Weeks - Live Cohort',
    body_text: 'Learn from industry experts with 15+ years of experience. Small class sizes, personalized feedback, and real client projects. 95% of graduates land jobs or promotions.',
    cta: 'Enroll Today',
    score: 94,
    usage_count: 672,
    is_premium: true,
    tags: ['Education', 'Course', 'Professional', 'Career']
  }
];

const categories = [
  { value: 'all', label: 'All Categories' },
  { value: 'saas', label: 'SaaS & Technology', icon: Business },
  { value: 'ecommerce', label: 'E-commerce', icon: ShoppingCart },
  { value: 'fitness', label: 'Health & Fitness', icon: Health },
  { value: 'education', label: 'Education', icon: School },
  { value: 'gaming', label: 'Gaming', icon: SportsEsports }
];

const platforms = [
  { value: 'all', label: 'All Platforms' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'google', label: 'Google Ads' },
  { value: 'linkedin', label: 'LinkedIn' }
];

const TemplatesLibrary = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [templates] = useState(mockTemplates);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  // Filter templates based on search and filters
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesPlatform = selectedPlatform === 'all' || template.platform === selectedPlatform;
    
    return matchesSearch && matchesCategory && matchesPlatform;
  });

  const handlePreview = (template) => {
    setSelectedTemplate(template);
    setPreviewOpen(true);
  };

  const handleUseTemplate = (template) => {
    // Copy template data to analyze page
    const templateData = {
      headline: template.headline,
      body_text: template.body_text,
      cta: template.cta,
      platform: template.platform
    };
    
    // Store in sessionStorage to pre-fill the analyze form
    sessionStorage.setItem('templateData', JSON.stringify(templateData));
    
    toast.success('Template loaded! Redirecting to analysis page...');
    navigate('/analyze');
  };

  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 80) return 'primary';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getCategoryIcon = (category) => {
    const categoryData = categories.find(cat => cat.value === category);
    const IconComponent = categoryData?.icon || Business;
    return <IconComponent />;
  };

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <EmptyState
          title="Sign in required"
          description="Please sign in to access the templates library"
          actionText="Go to Login"
          onAction={() => navigate('/login')}
        />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          Templates Library
          <Chip label="New" color="secondary" size="small" sx={{ ml: 1 }} />
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
          Choose from our collection of high-performing ad copy templates, proven to drive results across different industries and platforms
        </Typography>
      </Box>

      {/* Search and Filters */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                label="Category"
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth>
              <InputLabel>Platform</InputLabel>
              <Select
                value={selectedPlatform}
                label="Platform"
                onChange={(e) => setSelectedPlatform(e.target.value)}
              >
                {platforms.map((platform) => (
                  <MenuItem key={platform.value} value={platform.value}>
                    {platform.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <EmptyState
          variant="templates"
          title="No templates found"
          description="Try adjusting your search criteria or browse all templates"
          actionText="Clear Filters"
          onAction={() => {
            setSearchQuery('');
            setSelectedCategory('all');
            setSelectedPlatform('all');
          }}
        />
      ) : (
        <Grid container spacing={3}>
          {filteredTemplates.map((template) => (
            <Grid item xs={12} md={6} lg={4} key={template.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.2s ease-in-out',
                  position: 'relative',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 6,
                  },
                }}
              >
                {template.is_premium && (
                  <Chip
                    label="PRO"
                    color="warning"
                    size="small"
                    sx={{
                      position: 'absolute',
                      top: 12,
                      right: 12,
                      zIndex: 1,
                      fontWeight: 'bold'
                    }}
                  />
                )}
                
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Header */}
                  <Box sx={{ mb: 2 }}>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      {getCategoryIcon(template.category)}
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                        {template.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {template.description}
                    </Typography>
                  </Box>

                  {/* Platform and Score */}
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Chip
                      label={template.platform?.toUpperCase()}
                      variant="outlined"
                      size="small"
                    />
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <Star sx={{ color: 'warning.main', fontSize: '1rem' }} />
                      <Typography variant="body2" fontWeight="bold">
                        {template.score}%
                      </Typography>
                    </Box>
                  </Box>

                  {/* Preview Text */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                      {template.headline}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {template.body_text}
                    </Typography>
                  </Box>

                  {/* Tags */}
                  <Box sx={{ mb: 2 }}>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {template.tags.slice(0, 3).map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.7rem', height: 24 }}
                        />
                      ))}
                    </Stack>
                  </Box>

                  {/* Usage Stats */}
                  <Box display="flex" alignItems="center" gap={0.5} mb={2}>
                    <TrendingUp sx={{ fontSize: '0.875rem', color: 'text.secondary' }} />
                    <Typography variant="caption" color="text.secondary">
                      Used {template.usage_count.toLocaleString()} times
                    </Typography>
                  </Box>
                </CardContent>

                {/* Actions */}
                <Box sx={{ p: 2, pt: 0 }}>
                  <Box display="flex" gap={1}>
                    <Button
                      variant="contained"
                      onClick={() => handleUseTemplate(template)}
                      sx={{ flex: 1 }}
                    >
                      Use Template
                    </Button>
                    <Tooltip title="Preview">
                      <IconButton onClick={() => handlePreview(template)}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedTemplate && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center" gap={1}>
                {getCategoryIcon(selectedTemplate.category)}
                {selectedTemplate.title}
                {selectedTemplate.is_premium && (
                  <Chip label="PRO" color="warning" size="small" />
                )}
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Headline
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body1" sx={{ flex: 1 }}>
                        {selectedTemplate.headline}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleCopyToClipboard(selectedTemplate.headline)}
                      >
                        <ContentCopy />
                      </IconButton>
                    </Box>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Body Text
                    </Typography>
                    <Box display="flex" alignItems="flex-start" gap={1}>
                      <Typography variant="body1" sx={{ flex: 1 }}>
                        {selectedTemplate.body_text}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleCopyToClipboard(selectedTemplate.body_text)}
                      >
                        <ContentCopy />
                      </IconButton>
                    </Box>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Call-to-Action
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Button variant="outlined" disabled>
                        {selectedTemplate.cta}
                      </Button>
                      <IconButton
                        size="small"
                        onClick={() => handleCopyToClipboard(selectedTemplate.cta)}
                      >
                        <ContentCopy />
                      </IconButton>
                    </Box>
                  </Box>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Performance Score
                    </Typography>
                    <Chip
                      label={`${selectedTemplate.score}%`}
                      color={getScoreColor(selectedTemplate.score)}
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Platform
                    </Typography>
                    <Chip label={selectedTemplate.platform?.toUpperCase()} variant="outlined" />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Industry
                    </Typography>
                    <Typography variant="body2">
                      {selectedTemplate.industry}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Tags
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 1 }}>
                      {selectedTemplate.tags.map((tag, index) => (
                        <Chip key={index} label={tag} size="small" variant="outlined" />
                      ))}
                    </Stack>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setPreviewOpen(false)}>
                Close
              </Button>
              <Button
                variant="contained"
                onClick={() => {
                  handleUseTemplate(selectedTemplate);
                  setPreviewOpen(false);
                }}
              >
                Use This Template
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default TemplatesLibrary;
