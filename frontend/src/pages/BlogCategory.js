import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Stack,
  Skeleton,
  Breadcrumbs,
  Button
} from '@mui/material';
import {
  Schedule as ScheduleIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { useBlog } from '../contexts/BlogContext';

// Custom useInView hook
const useInView = ({ threshold, rootMargin }) => {
  const ref = React.useRef();
  const [inView, setInView] = React.useState(false);
  
  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setInView(entry.isIntersecting);
      },
      { threshold, rootMargin }
    );
    
    if (ref.current) {
      observer.observe(ref.current);
    }
    
    return () => observer.disconnect();
  }, [threshold, rootMargin]);
  
  return { ref, inView };
};

const BlogCategory = () => {
  const { category } = useParams();
  const navigate = useNavigate();
  const { 
    getPostsByCategory,
    loading,
    formatCategory,
    getPostUrl,
    getCategoryUrl
  } = useBlog();

  const [posts, setPosts] = useState([]);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 20,
    offset: 0,
    hasMore: false
  });

  // Infinite scroll
  const { ref: loadMoreRef, inView } = useInView({
    threshold: 0,
    rootMargin: '100px'
  });

  // Load posts for category
  useEffect(() => {
    const loadCategoryPosts = async () => {
      try {
        const data = await getPostsByCategory(category, { limit: 20, offset: 0 });
        setPosts(data.posts);
        setPagination({
          total: data.total,
          limit: data.limit,
          offset: data.offset,
          hasMore: data.has_more
        });
      } catch (err) {
        console.error('Error loading category posts:', err);
        if (err.response?.status === 404) {
          navigate('/blog', { replace: true });
        }
      }
    };

    if (category) {
      loadCategoryPosts();
    }
  }, [category, getPostsByCategory, navigate]);

  // Load more posts
  const loadMorePosts = async () => {
    if (!pagination.hasMore || loading) return;

    try {
      const nextOffset = pagination.offset + pagination.limit;
      const data = await getPostsByCategory(category, { 
        limit: pagination.limit, 
        offset: nextOffset 
      });
      
      setPosts(prevPosts => [...prevPosts, ...data.posts]);
      setPagination({
        total: data.total,
        limit: data.limit,
        offset: data.offset,
        hasMore: data.has_more
      });
    } catch (err) {
      console.error('Error loading more posts:', err);
    }
  };

  // Load more on scroll
  useEffect(() => {
    if (inView && pagination.hasMore && !loading) {
      loadMorePosts();
    }
  }, [inView, pagination.hasMore, loading]);

  const categoryTitle = formatCategory(category);

  const getCategoryDescription = (cat) => {
    switch (cat) {
      case 'educational':
        return 'Learn proven strategies and frameworks to write better ad copy and optimize your marketing campaigns.';
      case 'case_study':
        return 'Real success stories showing how businesses achieved remarkable results using ad copy optimization.';
      case 'tool_focused':
        return 'Deep dives into AdCopySurge features and how to leverage our tools for maximum impact.';
      case 'industry_insights':
        return 'Latest trends, data, and insights from the digital marketing and advertising industry.';
      default:
        return 'Expert insights and actionable tips for ad copy optimization and digital marketing success.';
    }
  };

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
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <ScheduleIcon fontSize="inherit" />
            {post.content_stats.read_time} min read
          </Typography>
        </Stack>

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

        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <PersonIcon fontSize="inherit" />
            {post.author.name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {format(new Date(post.published_at || post.created_at), 'MMM d, yyyy')}
          </Typography>
        </Stack>

        {post.tags && post.tags.length > 0 && (
          <Stack direction="row" spacing={0.5} sx={{ mt: 1, flexWrap: 'wrap' }}>
            {post.tags.slice(0, 2).map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.65rem', height: 20 }}
              />
            ))}
          </Stack>
        )}
      </CardContent>
    </Card>
  );

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
            py: 6,
            mb: 6
          }}
        >
          <Container maxWidth="lg">
            <Typography
              variant="h2"
              sx={{
                fontWeight: 800,
                mb: 2,
                fontSize: { xs: '2rem', md: '2.5rem' }
              }}
            >
              {categoryTitle}
            </Typography>
            <Typography variant="h6" sx={{ mb: 3, color: 'rgba(255,255,255,0.9)' }}>
              {getCategoryDescription(category)}
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              {pagination.total} articles in this category
            </Typography>
          </Container>
        </Box>

        <Container maxWidth="lg">
          {/* Breadcrumbs */}
          <Breadcrumbs sx={{ mb: 4 }}>
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
              Home
            </Link>
            <Link to="/blog" style={{ textDecoration: 'none', color: 'inherit' }}>
              Blog
            </Link>
            <Typography color="text.primary">{categoryTitle}</Typography>
          </Breadcrumbs>

          {/* Posts Grid */}
          <Grid container spacing={4}>
            {posts.map((post) => (
              <Grid item xs={12} sm={6} md={4} key={post.id}>
                <PostCard post={post} />
              </Grid>
            ))}
            
            {/* Loading skeletons */}
            {loading && (
              <>
                {[...Array(6)].map((_, index) => (
                  <Grid item xs={12} sm={6} md={4} key={`skeleton-${index}`}>
                    <PostSkeleton />
                  </Grid>
                ))}
              </>
            )}
          </Grid>

          {/* Load more trigger */}
          {pagination.hasMore && (
            <Box ref={loadMoreRef} sx={{ py: 4, textAlign: 'center' }}>
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
          {!loading && posts.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                No articles found in this category
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Check back later for new content in {categoryTitle}.
              </Typography>
              <Button 
                variant="contained" 
                component={Link}
                to="/blog"
              >
                Browse All Articles
              </Button>
            </Box>
          )}
        </Container>
      </Box>
  );
};

export default BlogCategory;
