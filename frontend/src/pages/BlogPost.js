import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  Chip,
  Button,
  Stack,
  Divider,
  Avatar,
  IconButton,
  Card,
  CardContent,
  Breadcrumbs,
  LinearProgress,
  Skeleton,
  Fab,
  Collapse
} from '@mui/material';
import {
  Share as ShareIcon,
  Facebook as FacebookIcon,
  LinkedIn as LinkedInIcon,
  Twitter as TwitterIcon,
  Link as LinkIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Visibility as ViewIcon,
  ArrowUpward as ArrowUpIcon,
  Toc as TOCIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { toast } from 'react-hot-toast';
import { useBlog } from '../contexts/BlogContext';

// Custom useInView hook
const useInView = ({ threshold, triggerOnce, onChange }) => {
  const ref = useRef();
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        const isIntersecting = entry.isIntersecting;
        if (isIntersecting && triggerOnce) {
          onChange(true);
          observer.disconnect();
        } else {
          onChange(isIntersecting);
        }
      },
      { threshold }
    );
    
    if (ref.current) {
      observer.observe(ref.current);
    }
    
    return () => observer.disconnect();
  }, [threshold, triggerOnce, onChange]);
  
  return { ref };
};

const BlogPost = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const {
    getPost,
    trackPostView,
    trackPostShare,
    formatCategory,
    getPostUrl,
    getCategoryUrl
  } = useBlog();

  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [readingProgress, setReadingProgress] = useState(0);
  const [showTOC, setShowTOC] = useState(false);
  const [activeSection, setActiveSection] = useState('');
  const [showShareFab, setShowShareFab] = useState(false);

  const contentRef = useRef();
  const tocRef = useRef();

  // Track when post comes into view
  const { ref: postViewRef } = useInView({
    threshold: 0.5,
    triggerOnce: true,
    onChange: (inView) => {
      if (inView && post) {
        trackPostView(post.slug);
      }
    }
  });

  // Load post data
  useEffect(() => {
    const loadPost = async () => {
      try {
        setLoading(true);
        const postData = await getPost(slug);
        setPost(postData);
      } catch (err) {
        setError(err.message);
        if (err.response?.status === 404) {
          navigate('/blog', { replace: true });
        }
      } finally {
        setLoading(false);
      }
    };

    if (slug) {
      loadPost();
    }
  }, [slug, getPost, navigate]);

  // Reading progress and active section tracking
  useEffect(() => {
    const handleScroll = () => {
      if (!contentRef.current) return;

      const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
      const progress = (scrollTop / (scrollHeight - clientHeight)) * 100;
      setReadingProgress(Math.min(progress, 100));

      // Show share fab after 20% scroll
      setShowShareFab(progress > 20);

      // Update active section
      const headings = contentRef.current.querySelectorAll('h1, h2, h3, h4');
      let currentSection = '';

      headings.forEach((heading) => {
        const rect = heading.getBoundingClientRect();
        if (rect.top <= 100) {
          currentSection = heading.id;
        }
      });

      setActiveSection(currentSection);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [post]);

  // Share functions
  const shareUrl = `${window.location.origin}/blog/${slug}`;
  const shareTitle = post?.title || '';
  const shareText = post?.excerpt || '';

  const handleShare = async (platform) => {
    let url = '';
    
    switch (platform) {
      case 'facebook':
        url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
        break;
      case 'twitter':
        url = `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareTitle)}&via=AdCopySurge`;
        break;
      case 'linkedin':
        url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
        break;
      case 'copy':
        try {
          await navigator.clipboard.writeText(shareUrl);
          toast.success('Link copied to clipboard!');
          trackPostShare(slug, 'copy');
          return;
        } catch (err) {
          toast.error('Failed to copy link');
          return;
        }
      default:
        return;
    }

    if (url) {
      window.open(url, '_blank', 'width=600,height=400');
      trackPostShare(slug, platform);
    }
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
        <Container maxWidth="lg" sx={{ pt: 4 }}>
          <Grid container spacing={4}>
            <Grid item xs={12} md={8}>
              <Skeleton variant="text" height={60} sx={{ mb: 2 }} />
              <Skeleton variant="text" height={40} sx={{ mb: 4 }} />
              <Skeleton variant="rectangular" height={300} sx={{ mb: 4 }} />
              <Skeleton variant="text" height={20} />
              <Skeleton variant="text" height={20} />
              <Skeleton variant="text" height={20} />
            </Grid>
            <Grid item xs={12} md={4}>
              <Skeleton variant="rectangular" height={200} />
            </Grid>
          </Grid>
        </Container>
      </Box>
    );
  }

  if (error || !post) {
    return (
      <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', pt: 8 }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h4" color="error" sx={{ mb: 2 }}>
            Post Not Found
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            The blog post you're looking for doesn't exist or has been moved.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/blog')}>
            Back to Blog
          </Button>
        </Container>
      </Box>
    );
  }

  return (
    <>
      {/* Reading Progress Bar */}
      <LinearProgress
        variant="determinate"
        value={readingProgress}
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1300,
          height: 3,
          backgroundColor: 'transparent'
        }}
      />

      <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
        {/* Hero Image */}
        {post.hero_image && (
          <Box
            sx={{
              height: { xs: 300, md: 400 },
              backgroundImage: `linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url(${post.hero_image})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              display: 'flex',
              alignItems: 'flex-end',
              color: 'white'
            }}
          >
            <Container maxWidth="lg" sx={{ pb: 4 }}>
              <Typography variant="h2" sx={{ fontWeight: 800, mb: 1 }}>
                {post.title}
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9 }}>
                {post.excerpt}
              </Typography>
            </Container>
          </Box>
        )}

        <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
          {/* Breadcrumbs */}
          <Breadcrumbs sx={{ mb: 4 }}>
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
              Home
            </Link>
            <Link to="/blog" style={{ textDecoration: 'none', color: 'inherit' }}>
              Blog
            </Link>
            <Link 
              to={getCategoryUrl(post.category)} 
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              {formatCategory(post.category)}
            </Link>
            <Typography color="text.primary">{post.title}</Typography>
          </Breadcrumbs>

          <Grid container spacing={6}>
            {/* Main Content */}
            <Grid item xs={12} md={8}>
              <Box ref={postViewRef}>
                {/* Article Header (if no hero image) */}
                {!post.hero_image && (
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="h2" sx={{ fontWeight: 800, mb: 2 }}>
                      {post.title}
                    </Typography>
                    <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
                      {post.excerpt}
                    </Typography>
                  </Box>
                )}

                {/* Article Meta */}
                <Paper sx={{ p: 3, mb: 4, backgroundColor: 'grey.50' }}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item>
                      <Avatar sx={{ width: 56, height: 56 }}>
                        {post.author.name[0]}
                      </Avatar>
                    </Grid>
                    <Grid item xs>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {post.author.name}
                      </Typography>
                      <Stack direction="row" spacing={2} sx={{ mt: 0.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <ScheduleIcon fontSize="inherit" />
                          {format(new Date(post.published_at || post.created_at), 'MMM d, yyyy')}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <ScheduleIcon fontSize="inherit" />
                          {post.content_stats.read_time} min read
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <ViewIcon fontSize="inherit" />
                          {post.metadata.views} views
                        </Typography>
                      </Stack>
                    </Grid>
                    <Grid item>
                      <Stack direction="row" spacing={1}>
                        <Chip 
                          label={formatCategory(post.category)} 
                          color="primary" 
                          component={Link}
                          to={getCategoryUrl(post.category)}
                        />
                      </Stack>
                    </Grid>
                  </Grid>
                </Paper>

                {/* Article Content */}
                <Box 
                  ref={contentRef}
                  sx={{
                    '& .blog-paragraph': {
                      fontSize: '1.125rem',
                      lineHeight: 1.7,
                      mb: 3
                    },
                    '& .blog-heading': {
                      mt: 6,
                      mb: 3,
                      fontWeight: 700
                    },
                    '& .blog-image': {
                      width: '100%',
                      height: 'auto',
                      borderRadius: 2,
                      mb: 3
                    },
                    '& .blog-blockquote': {
                      borderLeft: '4px solid',
                      borderColor: 'primary.main',
                      pl: 3,
                      py: 2,
                      my: 4,
                      backgroundColor: 'grey.50',
                      fontStyle: 'italic',
                      fontSize: '1.125rem'
                    },
                    '& .blog-code-block': {
                      backgroundColor: 'grey.900',
                      color: 'white',
                      p: 3,
                      borderRadius: 2,
                      overflow: 'auto',
                      mb: 3
                    },
                    '& .blog-table-wrapper': {
                      overflow: 'auto',
                      mb: 3
                    },
                    '& .blog-table': {
                      width: '100%',
                      borderCollapse: 'collapse',
                      '& th, & td': {
                        border: '1px solid',
                        borderColor: 'divider',
                        p: 2
                      },
                      '& th': {
                        backgroundColor: 'grey.100',
                        fontWeight: 600
                      }
                    }
                  }}
                >
                  <div dangerouslySetInnerHTML={{ __html: post.content }} />
                </Box>

                {/* Tags */}
                {post.tags && post.tags.length > 0 && (
                  <Box sx={{ mt: 6, mb: 4 }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Tags
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      {post.tags.map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          variant="outlined"
                          clickable
                          onClick={() => navigate(`/blog/tag/${encodeURIComponent(tag)}`)}
                        />
                      ))}
                    </Stack>
                  </Box>
                )}

                {/* Share Buttons */}
                <Divider sx={{ my: 4 }} />
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Share this article
                  </Typography>
                  <Stack direction="row" spacing={2} justifyContent="center">
                    <Button
                      variant="contained"
                      sx={{ backgroundColor: '#1877f2' }}
                      startIcon={<FacebookIcon />}
                      onClick={() => handleShare('facebook')}
                    >
                      Facebook
                    </Button>
                    <Button
                      variant="contained"
                      sx={{ backgroundColor: '#1da1f2' }}
                      startIcon={<TwitterIcon />}
                      onClick={() => handleShare('twitter')}
                    >
                      Twitter
                    </Button>
                    <Button
                      variant="contained"
                      sx={{ backgroundColor: '#0077b5' }}
                      startIcon={<LinkedInIcon />}
                      onClick={() => handleShare('linkedin')}
                    >
                      LinkedIn
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<LinkIcon />}
                      onClick={() => handleShare('copy')}
                    >
                      Copy Link
                    </Button>
                  </Stack>
                </Box>

                {/* CTA Section */}
                <Paper sx={{ p: 4, mt: 6, textAlign: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                  <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>
                    Ready to optimize your ad copy?
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
                    Join thousands of marketers who use AdCopySurge to write better ads and increase their ROI.
                  </Typography>
                  <Button 
                    variant="contained" 
                    size="large"
                    sx={{ 
                      backgroundColor: 'white', 
                      color: 'primary.main',
                      '&:hover': {
                        backgroundColor: 'grey.100'
                      }
                    }}
                    component={Link}
                    to="/register"
                  >
                    Start Free Trial
                  </Button>
                </Paper>
              </Box>
            </Grid>

            {/* Sidebar */}
            <Grid item xs={12} md={4}>
              {/* Table of Contents */}
              {post.table_of_contents && post.table_of_contents.length > 0 && (
                <Paper sx={{ p: 3, mb: 4, position: 'sticky', top: 100 }}>
                  <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                    <Typography variant="h6">Table of Contents</Typography>
                    <IconButton 
                      size="small" 
                      onClick={() => setShowTOC(!showTOC)}
                      sx={{ display: { xs: 'block', md: 'none' } }}
                    >
                      {showTOC ? <CloseIcon /> : <TOCIcon />}
                    </IconButton>
                  </Stack>
                  
                  <Collapse in={showTOC} sx={{ display: { xs: 'block', md: 'block' } }}>
                    <Stack spacing={0.5}>
                      {post.table_of_contents.map((item, index) => (
                        <Button
                          key={index}
                          variant="text"
                          size="small"
                          onClick={() => scrollToSection(item.anchor)}
                          sx={{
                            justifyContent: 'flex-start',
                            pl: item.level * 2,
                            py: 0.5,
                            fontWeight: activeSection === item.anchor ? 600 : 400,
                            color: activeSection === item.anchor ? 'primary.main' : 'text.secondary',
                            '&:hover': {
                              backgroundColor: 'action.hover'
                            }
                          }}
                        >
                          {item.title}
                        </Button>
                      ))}
                    </Stack>
                  </Collapse>
                </Paper>
              )}

              {/* Related Posts */}
              {post.related_posts && post.related_posts.length > 0 && (
                <Paper sx={{ p: 3, mb: 4 }}>
                  <Typography variant="h6" sx={{ mb: 3 }}>
                    Related Articles
                  </Typography>
                  <Stack spacing={3}>
                    {post.related_posts.map((relatedPost) => (
                      <Card 
                        key={relatedPost.id}
                        elevation={1}
                        sx={{ 
                          cursor: 'pointer',
                          '&:hover': { boxShadow: 4 }
                        }}
                        onClick={() => navigate(getPostUrl(relatedPost.slug))}
                      >
                        <CardContent sx={{ p: 2 }}>
                          <Typography 
                            variant="subtitle2" 
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
                            {relatedPost.title}
                          </Typography>
                          <Typography 
                            variant="caption" 
                            color="text.secondary"
                            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                          >
                            <ScheduleIcon fontSize="inherit" />
                            {relatedPost.content_stats.read_time} min read
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </Stack>
                </Paper>
              )}
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Floating Action Buttons */}
      <Fab
        color="primary"
        size="medium"
        onClick={scrollToTop}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          opacity: readingProgress > 20 ? 1 : 0,
          transition: 'opacity 0.3s'
        }}
      >
        <ArrowUpIcon />
      </Fab>

      {showShareFab && (
        <Fab
          color="secondary"
          size="medium"
          onClick={() => handleShare('copy')}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 96,
            opacity: showShareFab ? 1 : 0,
            transition: 'opacity 0.3s'
          }}
        >
          <ShareIcon />
        </Fab>
      )}
    </>
  );
};

export default BlogPost;
