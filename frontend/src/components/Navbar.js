import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Chip,
  Breadcrumbs,
  InputBase,
  Badge,
  Divider,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import BrandLogo from './BrandLogo';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  ExitToApp as LogoutIcon,
  CreditCard as BillingIcon,
  Help as HelpIcon,
  Clear as ClearIcon,
  KeyboardArrowDown as ArrowDownIcon,
  Description as DocsIcon,
  School as TutorialsIcon,
  Business as CaseStudiesIcon,
  Code as ApiIcon,
  VideoLibrary as VideoIcon,
  Article as BlogIcon
} from '@mui/icons-material';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../services/authContext';
import { useDebounce } from '../hooks/useDebounce'; // We'll create this

const Navbar = ({ onSidebarToggle, showSidebarToggle = false }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, subscription, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [resourcesAnchorEl, setResourcesAnchorEl] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleResourcesMenuOpen = (event) => {
    setResourcesAnchorEl(event.currentTarget);
  };

  const handleResourcesMenuClose = () => {
    setResourcesAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
    handleMenuClose();
  };

  // Search handlers
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/history?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
  };

  // Effect for debounced search
  useEffect(() => {
    if (debouncedSearchQuery && debouncedSearchQuery.length >= 2) {
      // Could trigger live search suggestions here
      console.log('Searching for:', debouncedSearchQuery);
    }
  }, [debouncedSearchQuery]);

  // Resources dropdown items
  const resourcesMenuItems = [
    {
      label: 'API Documentation',
      description: 'Complete API reference and integration guides',
      icon: <ApiIcon sx={{ fontSize: '1.2rem' }} />,
      to: '/resources/api'
    },
    {
      label: 'Getting Started',
      description: 'Quick start guides and setup tutorials',
      icon: <DocsIcon sx={{ fontSize: '1.2rem' }} />,
      to: '/resources/getting-started'
    },
    {
      label: 'Tutorials & Guides',
      description: 'Step-by-step tutorials and best practices',
      icon: <TutorialsIcon sx={{ fontSize: '1.2rem' }} />,
      to: '/resources/tutorials'
    },
    {
      label: 'Case Studies',
      description: 'Real-world success stories and results',
      icon: <CaseStudiesIcon sx={{ fontSize: '1.2rem' }} />,
      to: '/resources/case-studies'
    },
    {
      label: 'Video Library',
      description: 'Video tutorials and product demos',
      icon: <VideoIcon sx={{ fontSize: '1.2rem' }} />,
      to: '/resources/videos'
    },
    {
      label: 'Blog',
      description: 'Marketing insights and product updates',
      icon: <BlogIcon sx={{ fontSize: '1.2rem' }} />,
      to: '/blog'
    }
  ];

  const getSubscriptionColor = (tier) => {
    switch (tier) {
      case 'growth':
        return 'primary';
      case 'agency_standard':
        return 'secondary';
      case 'agency_premium':
        return 'success';
      case 'agency_unlimited':
        return 'info';
      // Legacy support
      case 'basic':
        return 'primary';
      case 'pro':
        return 'info';
      case 'free':
      default:
        return 'default';
    }
  };

  const getBreadcrumbs = () => {
    const path = location.pathname;
    const segments = path.split('/').filter(Boolean);
    
    const breadcrumbMap = {
      'dashboard': 'Dashboard',
      'analyze': 'New Analysis',
      'history': 'Analysis History',
      'templates': 'Templates Library',
      'reports': 'Reports & Insights',
      'profile': 'Settings & Profile',
      'help': 'Help & Support',
      'pricing': 'Billing',
      'results': 'Analysis Results'
    };

    const breadcrumbs = [{ name: 'Home', path: '/dashboard' }];
    
    segments.forEach((segment, index) => {
      const path = '/' + segments.slice(0, index + 1).join('/');
      const name = breadcrumbMap[segment] || segment;
      breadcrumbs.push({ name, path });
    });

    return breadcrumbs.slice(0, -1); // Remove current page from breadcrumbs
  };

  const isAuthPage = ['/login', '/register'].includes(location.pathname);

  return (
    <AppBar 
      position="sticky" 
      elevation={0}
      sx={{ 
        bgcolor: 'background.paper',
        borderBottom: '2px solid',
        borderColor: 'primary.main',
        color: 'text.primary',
        '&::before': {
          content: '""',
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: 'linear-gradient(90deg, #2563eb 0%, #f59e0b 50%, #7c3aed 100%)',
        }
      }}
    >
      <Toolbar sx={{ minHeight: { xs: 72, md: 80 }, py: 1 }}>
        {/* Mobile Sidebar Toggle */}
        {showSidebarToggle && (
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={onSidebarToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}

        {/* Logo for auth pages or when sidebar is hidden */}
        {(isAuthPage || !isAuthenticated) && (
          <Box 
            component={Link} 
            to="/" 
            sx={{ 
              flexGrow: 1,
              textDecoration: 'none',
              display: 'flex'
            }}
          >
            <BrandLogo variant="compact" size="medium" />
          </Box>
        )}

        {/* Breadcrumbs for authenticated pages */}
        {isAuthenticated && !isAuthPage && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexGrow: 1 }}>
            <Breadcrumbs 
              separator={<NavigateNextIcon fontSize="small" />}
              sx={{ display: { xs: 'none', lg: 'flex' } }}
            >
              {getBreadcrumbs().map((crumb, index) => (
                <Typography
                  key={crumb.path}
                  component={Link}
                  to={crumb.path}
                  sx={{
                    color: index === getBreadcrumbs().length - 1 ? 'text.primary' : 'text.secondary',
                    textDecoration: 'none',
                    fontSize: '0.9rem',
                    '&:hover': { textDecoration: 'underline' }
                  }}
                >
                  {crumb.name === 'Home' ? <HomeIcon sx={{ fontSize: '1.2rem' }} /> : crumb.name}
                </Typography>
              ))}
            </Breadcrumbs>
            
            {/* Search Bar */}
            <Box 
              component="form" 
              onSubmit={handleSearchSubmit}
              sx={{ 
                display: { xs: 'none', md: 'flex' }, 
                alignItems: 'center',
                bgcolor: 'background.paper',
                borderRadius: 3,
                border: '2px solid',
                borderColor: searchFocused ? 'primary.main' : 'divider',
                px: 2,
                py: 0.75, // Smaller padding
                minWidth: 260,
                maxWidth: 360,
                transition: 'all 0.2s ease-in-out',
                boxShadow: searchFocused ? '0 4px 12px rgba(37, 99, 235, 0.15)' : '0 1px 3px rgba(0,0,0,0.1)',
                '&:hover': {
                  borderColor: 'primary.light',
                  boxShadow: '0 2px 8px rgba(37, 99, 235, 0.1)'
                }
              }}
            >
              <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
              <InputBase
                placeholder="Search analyses..."
                value={searchQuery}
                onChange={handleSearchChange}
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setSearchFocused(false)}
                sx={{
                  flex: 1,
                  fontSize: '0.875rem',
                  '& ::placeholder': {
                    color: 'text.secondary',
                    opacity: 0.7
                  }
                }}
              />
              {searchQuery && (
                <IconButton
                  size="small"
                  onClick={handleClearSearch}
                  sx={{ p: 0.5, color: 'text.secondary' }}
                >
                  <ClearIcon sx={{ fontSize: '1rem' }} />
                </IconButton>
              )}
            </Box>
          </Box>
        )}

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {!isAuthenticated ? (
            <>
              {/* Resources Dropdown for non-authenticated users */}
              <Box sx={{ display: { xs: 'none', md: 'block' } }}>
                <Button
                  color="primary"
                  onClick={handleResourcesMenuOpen}
                  endIcon={<ArrowDownIcon />}
                  sx={{
                    '& .MuiSvgIcon-root': {
                      transition: 'transform 0.2s',
                      transform: Boolean(resourcesAnchorEl) ? 'rotate(180deg)' : 'none'
                    }
                  }}
                >
                  Resources
                </Button>
                <Menu
                  anchorEl={resourcesAnchorEl}
                  open={Boolean(resourcesAnchorEl)}
                  onClose={handleResourcesMenuClose}
                  transformOrigin={{ horizontal: 'left', vertical: 'top' }}
                  anchorOrigin={{ horizontal: 'left', vertical: 'bottom' }}
                  PaperProps={{
                    sx: {
                      mt: 1,
                      minWidth: 320,
                      borderRadius: 3,
                      boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
                      border: '1px solid',
                      borderColor: 'divider'
                    }
                  }}
                >
                  <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="subtitle2" fontWeight={600} color="primary.main">
                      Resources & Documentation
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Everything you need to get started and succeed
                    </Typography>
                  </Box>
                  {resourcesMenuItems.map((item) => (
                    <MenuItem
                      key={item.to}
                      onClick={() => {
                        navigate(item.to);
                        handleResourcesMenuClose();
                      }}
                      sx={{ py: 1.5, px: 2 }}
                    >
                      <Box sx={{ mr: 2, color: 'primary.main' }}>
                        {item.icon}
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" fontWeight={600}>
                          {item.label}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {item.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ px: 2, py: 1.5, textAlign: 'center' }}>
                    <Button
                      component={Link}
                      to="/resources"
                      variant="outlined"
                      size="small"
                      fullWidth
                      onClick={handleResourcesMenuClose}
                    >
                      View All Resources
                    </Button>
                  </Box>
                </Menu>
              </Box>
              <Button
                color="primary"
                component={Link}
                to="/pricing"
                sx={{ display: { xs: 'none', md: 'inline-flex' } }}
              >
                Pricing
              </Button>
              <Button
                color="primary"
                component={Link}
                to="/login"
              >
                Login
              </Button>
              <Button
                variant="contained"
                component={Link}
                to="/register"
                sx={{ ml: 1 }}
              >
                Sign Up
              </Button>
            </>
          ) : (
            <>
              {/* Notifications */}
              <IconButton
                color="inherit"
                sx={{ 
                  color: 'text.secondary',
                  '&:hover': { 
                    bgcolor: 'action.hover',
                    color: 'primary.main'
                  }
                }}
              >
                <Badge 
                  badgeContent={3} 
                  color="error"
                  sx={{
                    '& .MuiBadge-badge': {
                      fontSize: '0.625rem', // 10px font
                      height: '16px',
                      minWidth: '16px'
                    }
                  }}
                >
                  <NotificationsIcon />
                </Badge>
              </IconButton>

              {/* Subscription Tier Chip */}
              <Box sx={{ display: { xs: 'none', lg: 'flex' }, alignItems: 'center', gap: 1 }}>
                {subscription && (
                  <Chip
                    label={subscription.subscription_tier?.toUpperCase()}
                    color={getSubscriptionColor(subscription.subscription_tier)}
                    size="small"
                    variant="outlined"
                  />
                )}
              </Box>

              {/* User Menu */}
              <IconButton
                onClick={handleMenuOpen}
                color="inherit"
                sx={{ 
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  width: 40,
                  height: 40,
                  '&:hover': { 
                    bgcolor: 'primary.dark',
                    transform: 'scale(1.05)'
                  },
                  transition: 'all 0.2s ease-in-out'
                }}
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'transparent' }}>
                  {user?.email?.charAt(0)?.toUpperCase()}
                </Avatar>
              </IconButton>

              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                PaperProps={{
                  sx: { 
                    mt: 1.5, 
                    minWidth: 240,
                    borderRadius: 3,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
                    border: '1px solid',
                    borderColor: 'divider'
                  }
                }}
              >
                {/* User Info Header */}
                <Box sx={{ px: 3, py: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="subtitle2" fontWeight={600}>
                    {subscription?.full_name || user?.email?.split('@')[0] || 'User'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {user?.email}
                  </Typography>
                  <Chip
                    label={subscription?.subscription_tier?.toUpperCase() || 'FREE'}
                    size="small"
                    color={getSubscriptionColor(subscription?.subscription_tier)}
                    sx={{ mt: 1, height: 20, fontSize: '0.65rem' }}
                  />
                </Box>
                
                {/* Account Section */}
                <MenuItem 
                  onClick={() => { navigate('/profile'); handleMenuClose(); }}
                  sx={{ py: 1.5, px: 3 }}
                >
                  <ListItemIcon>
                    <PersonIcon sx={{ fontSize: '1.2rem' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Profile Settings" 
                    primaryTypographyProps={{ fontSize: '0.875rem' }}
                  />
                </MenuItem>
                
                <MenuItem 
                  onClick={() => { navigate('/pricing'); handleMenuClose(); }}
                  sx={{ py: 1.5, px: 3 }}
                >
                  <ListItemIcon>
                    <BillingIcon sx={{ fontSize: '1.2rem' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Billing & Subscription" 
                    primaryTypographyProps={{ fontSize: '0.875rem' }}
                  />
                </MenuItem>
                
                <Divider sx={{ my: 1 }} />
                
                {/* Help Section */}
                <MenuItem 
                  onClick={() => { window.open('/help', '_blank'); handleMenuClose(); }}
                  sx={{ py: 1.5, px: 3 }}
                >
                  <ListItemIcon>
                    <HelpIcon sx={{ fontSize: '1.2rem' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Help & Support" 
                    primaryTypographyProps={{ fontSize: '0.875rem' }}
                  />
                </MenuItem>
                
                <Divider sx={{ my: 1 }} />
                
                {/* Logout */}
                <MenuItem 
                  onClick={handleLogout}
                  sx={{ 
                    py: 1.5, 
                    px: 3,
                    color: 'error.main',
                    '&:hover': { bgcolor: 'error.light', color: 'error.contrastText' }
                  }}
                >
                  <ListItemIcon>
                    <LogoutIcon sx={{ fontSize: '1.2rem', color: 'inherit' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Logout" 
                    primaryTypographyProps={{ fontSize: '0.875rem', color: 'inherit' }}
                  />
                </MenuItem>
              </Menu>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
