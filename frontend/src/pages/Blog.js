import React, { useState, useEffect, useMemo } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia,
  Chip, 
  Button, 
  TextField,
  InputAdornment,
  Paper,
  Stack,
  Skeleton,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  IconButton,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  TrendingUp as TrendingIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useInView } from '../hooks/useInView';
import { useBlog } from '../contexts/BlogContext';
import { format } from 'date-fns';

const Blog = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { 
    posts, 
    categories, 
    popularPosts, 
    trendingPosts,
    loading, 
    searchResults, 
    pagination,
    fetchPosts, 
    searchPosts, 
    clearSearch, 
    loadMorePosts,
    formatCategory,
    getPostUrl,
    getCategoryUrl
  } = useBlog();

  // Local state
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '');
  const [sortBy, setSortBy] = useState(searchParams.get('sort') || 'published_at');
  const [showFilters, setShowFilters] = useState(false);

  // Infinite scroll
  const { ref: loadMoreRef, inView } = useInView({
    threshold: 0,
    rootMargin: '100px'
  });

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if (selectedCategory) params.set('category', selectedCategory);
    if (sortBy !== 'published_at') params.set('sort', sortBy);
    
    setSearchParams(params, { replace: true });
  }, [searchQuery, selectedCategory, sortBy, setSearchParams]);

  // Load initial posts
  useEffect(() => {
    const loadInitialPosts = async () => {
      if (searchQuery) {
        await searchPosts(searchQuery, {
          category: selectedCategory || undefined,
          sortBy,
          sortOrder: 'desc'
        });
      } else {
        await fetchPosts({
          category: selectedCategory || undefined,
          sortBy,
          sortOrder: 'desc'
        });
      }
    };

    loadInitialPosts();
  }, [searchQuery, selectedCategory, sortBy, fetchPosts, searchPosts]);

  // Load more on scroll
  useEffect(() => {
    if (inView && pagination.hasMore && !loading) {
      loadMorePosts();
    }
  }, [inView, pagination.hasMore, loading, loadMorePosts]);

  // Handle search
  const handleSearch = (event) => {
    event.preventDefault();
    if (searchQuery.trim()) {
      searchPosts(searchQuery.trim(), {
        category: selectedCategory || undefined,
        sortBy,
        sortOrder: 'desc'
      });
    } else {
      clearSearch();
      fetchPosts({
        category: selectedCategory || undefined,
        sortBy,
        sortOrder: 'desc'
      });
    }
  };

  // Clear all filters
  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSortBy('published_at');
    clearSearch();
    fetchPosts();
  };

  // Get current posts to display
  const currentPosts = searchResults ? searchResults.posts : posts;
  const currentPagination = searchResults ? {
    total: searchResults.total,
    hasMore: searchResults.has_more
  } : pagination;

  // Post card component
  const PostCard = ({ post }) => (
    <Card 
      elevation={2}
      sx={{
        height: '100%',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 8
        }
      }}
      onClick={() => navigate(getPostUrl(post.slug))}
    >
      {post.featured_image && (
        <CardMedia
          component="img"
          height="200"
          image={post.featured_image}
          alt={post.title}
          loading="lazy"
        />
      )}
      <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Category and reading time */}
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <Chip 
            label={formatCategory(post.category)} 
            color="primary" 
            size="small"
            component={Link}
            to={getCategoryUrl(post.category)}
            onClick={(e) => e.stopPropagation()}
          />
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <ScheduleIcon fontSize="inherit" />
            {post.content_stats.read_time} min read
          </Typography>
        </Stack>

        {/* Title */}
        <Typography 
          variant="h6" 
          sx={{ 
            fontWeight: 600, 
            mb: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical'
          }}
        >
          {post.title}
        </Typography>

        {/* Excerpt */}
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            mb: 2, 
            flexGrow: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical'
          }}
        >
          {post.excerpt}
        </Typography>

        {/* Author and date */}
        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <PersonIcon fontSize="inherit" />
            {post.author.name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {format(new Date(post.published_at || post.created_at), 'MMM d, yyyy')}
          </Typography>
        </Stack>

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <Stack direction="row" spacing={0.5} sx={{ mt: 1, flexWrap: 'wrap' }}>
            {post.tags.slice(0, 3).map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.65rem', height: 20 }}
              />
            ))}
            {post.tags.length > 3 && (
              <Typography variant="caption" color="text.secondary">
                +{post.tags.length - 3} more
              </Typography>
            )}
          </Stack>
        )}
      </CardContent>
    </Card>
  );

  // Loading skeleton
  const PostSkeleton = () => (
    <Card elevation={2}>
      <Skeleton variant="rectangular" height={200} />
      <CardContent>
        <Skeleton variant="text" width="60%" height={24} />
        <Skeleton variant="text" height={20} />
        <Skeleton variant="text" height={20} />
        <Skeleton variant="text" width="40%" height={20} />
      </CardContent>
    </Card>
  );

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
                  AdCopySurge Blog
                </Typography>
                <Typography variant="h5" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
                  Expert insights on ad copy optimization and digital marketing success
                </Typography>
                <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.8)' }}>
                  Discover proven strategies, real case studies, and actionable tips to maximize your marketing ROI.
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                {/* Search */}
                <Paper
                  component="form"
                  onSubmit={handleSearch}
                  sx={{
                    p: 1,
                    display: 'flex',
                    alignItems: 'center',
                    backgroundColor: 'rgba(255,255,255,0.95)',
                    backdropFilter: 'blur(10px)'
                  }}
                >
                  <TextField
                    fullWidth
                    placeholder="Search articles..."
                    variant="outlined"
                    size="small"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon sx={{ color: 'text.secondary' }} />
                        </InputAdornment>
                      ),
                      sx: { border: 'none' }
                    }}
                  />
                  {searchQuery && (
                    <IconButton onClick={() => setSearchQuery('')}>
                      <ClearIcon />
                    </IconButton>
                  )}
                </Paper>
              </Grid>
            </Grid>
          </Container>
        </Box>

        <Container maxWidth="lg">
          <Grid container spacing={4}>
            {/* Main Content */}
            <Grid item xs={12} md={8}>
              {/* Filters */}
              <Paper sx={{ p: 2, mb: 4 }}>
                <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                  <Button
                    startIcon={<FilterIcon />}
                    onClick={() => setShowFilters(!showFilters)}
                    sx={{ mb: { xs: 1, sm: 0 } }}
                  >
                    Filters
                  </Button>
                  
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={selectedCategory}
                      label="Category"
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      <MenuItem value="">All Categories</MenuItem>
                      {categories.map((category) => (
                        <MenuItem key={category} value={category}>
                          {formatCategory(category)}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Sort By</InputLabel>
                    <Select
                      value={sortBy}
                      label="Sort By"
                      onChange={(e) => setSortBy(e.target.value)}
                    >
                      <MenuItem value="published_at">Latest</MenuItem>
                      <MenuItem value="views">Most Popular</MenuItem>
                      <MenuItem value="title">Title A-Z</MenuItem>
                    </Select>
                  </FormControl>

                  {(searchQuery || selectedCategory || sortBy !== 'published_at') && (
                    <Button
                      onClick={handleClearFilters}
                      size="small"
                      sx={{ ml: 'auto' }}
                    >
                      Clear All
                    </Button>
                  )}
                </Stack>

                {/* Results info */}
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  {searchResults ? (
                    `Found ${currentPagination.total} articles for "${searchQuery}"`
                  ) : (
                    `Showing ${currentPosts.length} of ${currentPagination.total} articles`
                  )}
                </Typography>
              </Paper>

              {/* Posts Grid */}
              <Grid container spacing={4}>
                {currentPosts.map((post) => (
                  <Grid item xs={12} sm={6} key={post.id}>
                    <PostCard post={post} />
                  </Grid>
                ))}
                
                {/* Loading skeletons */}
                {loading && (
                  <>
                    {[...Array(4)].map((_, index) => (
                      <Grid item xs={12} sm={6} key={`skeleton-${index}`}>
                        <PostSkeleton />
                      </Grid>
                    ))}
                  </>
                )}
              </Grid>

              {/* Load more trigger */}
              {currentPagination.hasMore && (
                <Box ref={loadMoreRef} sx={{ py: 2, textAlign: 'center' }}>
                  {loading ? (
                    <Typography variant="body2" color="text.secondary">
                      Loading more articles...
                    </Typography>
                  ) : (
                    <Button onClick={loadMorePosts} variant="outlined">
                      Load More Articles
                    </Button>
                  )}
                </Box>
              )}

              {/* No results */}
              {!loading && currentPosts.length === 0 && (
                <Paper sx={{ p: 6, textAlign: 'center' }}>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    No articles found
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    {searchQuery 
                      ? `No articles match your search for "${searchQuery}"`
                      : 'No articles available with the selected filters'
                    }
                  </Typography>
                  <Button onClick={handleClearFilters} variant="contained">
                    Show All Articles
                  </Button>
                </Paper>
              )}
            </Grid>

            {/* Sidebar */}
            <Grid item xs={12} md={4}>
              {/* Popular Posts */}
              <Paper sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingIcon color="primary" />
                  Popular Articles
                </Typography>
                <Stack spacing={2}>
                  {popularPosts.map((post, index) => (
                    <Box key={post.id}>
                      <Link 
                        to={getPostUrl(post.slug)} 
                        style={{ textDecoration: 'none', color: 'inherit' }}
                      >
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontWeight: 500,
                            '&:hover': { color: 'primary.main' },
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical'
                          }}
                        >
                          {post.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {post.metadata.views} views
                        </Typography>
                      </Link>
                      {index < popularPosts.length - 1 && <Divider sx={{ mt: 2 }} />}
                    </Box>
                  ))}
                </Stack>
              </Paper>

              {/* Categories */}
              <Paper sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Categories
                </Typography>
                <Stack spacing={1}>
                  {categories.map((category) => (
                    <Button
                      key={category}
                      component={Link}
                      to={getCategoryUrl(category)}
                      variant={selectedCategory === category ? 'contained' : 'text'}
                      size="small"
                      sx={{ justifyContent: 'flex-start' }}
                    >
                      {formatCategory(category)}
                    </Button>
                  ))}
                </Stack>
              </Paper>

              {/* Newsletter CTA */}
              <Paper 
                sx={{ 
                  p: 3, 
                  background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                  textAlign: 'center' 
                }}
              >
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Get Marketing Tips Weekly
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Join 10,000+ marketers getting actionable insights delivered to their inbox.
                </Typography>
                <Button 
                  variant="contained" 
                  color="primary"
                  fullWidth
                  component={Link}
                  to="/newsletter"
                >
                  Subscribe Now
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
  );
};

export default Blog;
