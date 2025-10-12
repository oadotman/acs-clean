import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
  ListItemText,
  Chip,
  Tooltip,
  useTheme,
  alpha
} from '@mui/material';
import {
  LightMode,
  DarkMode,
  AccountCircle,
  Settings,
  Logout,
  Menu as MenuIcon,
  CreditCard
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import { useThemeMode } from '../contexts/ThemeContext';

const TopBar = ({ onMenuClick, showMenuButton = false }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user, logout, subscription } = useAuth();
  const { mode, toggleTheme } = useThemeMode();
  
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    handleMenuClose();
    navigate('/profile');
  };

  const handleBilling = () => {
    handleMenuClose();
    navigate('/billing');
  };

  const handleSettings = () => {
    handleMenuClose();
    navigate('/settings');
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
    navigate('/login');
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user) return 'U';
    const email = user.email || '';
    return email.charAt(0).toUpperCase();
  };

  // Get subscription badge
  const getSubscriptionBadge = () => {
    const tier = subscription?.subscription_tier || subscription || 'free';
    
    switch (tier) {
      case 'growth':
        return { label: 'Growth', color: 'primary' };
      case 'agency_standard':
        return { label: 'Standard', color: 'secondary' };
      case 'agency_premium':
        return { label: 'Premium', color: 'success' };
      case 'agency_unlimited':
        return { label: 'Unlimited', color: 'info' };
      // Legacy support
      case 'basic':
        return { label: 'Growth', color: 'primary' };
      case 'pro':
        return { label: 'Unlimited', color: 'info' };
      case 'agency':
        return { label: 'Agency', color: 'success' };
      case 'free':
      default:
        return { label: 'Free', color: 'default' };
    }
  };

  const badge = getSubscriptionBadge();

  return (
    <AppBar 
      position="sticky" 
      elevation={0}
      sx={{
        backgroundColor: alpha(theme.palette.background.paper, 0.9),
        backdropFilter: 'blur(20px)',
        borderBottom: `1px solid ${theme.palette.divider}`,
        color: theme.palette.text.primary
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, sm: 3 }, minHeight: { xs: 56, sm: 64 } }}>
        {/* Left Side - Mobile Menu Button */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {showMenuButton && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={onMenuClick}
              sx={{ display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
          )}
        </Box>

        {/* Right Side - Theme Toggle, User Profile */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 } }}>
          {/* Theme Toggle Button */}
          <Tooltip title={mode === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'} arrow>
            <IconButton
              onClick={toggleTheme}
              color="inherit"
              size="medium"
              sx={{
                backgroundColor: alpha(theme.palette.action.hover, 0.05),
                '&:hover': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  color: theme.palette.primary.main,
                },
                transition: 'all 0.2s ease-in-out'
              }}
            >
              {mode === 'light' ? <DarkMode fontSize="small" /> : <LightMode fontSize="small" />}
            </IconButton>
          </Tooltip>

          {/* User Profile Menu */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              px: 1.5,
              py: 0.75,
              borderRadius: 2,
              backgroundColor: alpha(theme.palette.action.hover, 0.05),
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.08),
              }
            }}
            onClick={handleMenuOpen}
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                fontSize: '0.875rem',
                fontWeight: 600,
                bgcolor: theme.palette.primary.main,
                color: '#FFFFFF'
              }}
            >
              {getUserInitials()}
            </Avatar>
            
            <Box sx={{ display: { xs: 'none', md: 'flex' }, flexDirection: 'column', alignItems: 'flex-start' }}>
              <Typography variant="body2" fontWeight={600} sx={{ lineHeight: 1.2 }}>
                {user?.email?.split('@')[0] || 'User'}
              </Typography>
              <Chip 
                label={badge.label} 
                size="small" 
                color={badge.color}
                sx={{ 
                  height: 16, 
                  fontSize: '0.625rem',
                  fontWeight: 700,
                  '& .MuiChip-label': {
                    px: 0.75,
                    py: 0
                  }
                }} 
              />
            </Box>
          </Box>

          {/* Dropdown Menu */}
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            onClick={handleMenuClose}
            PaperProps={{
              elevation: 8,
              sx: {
                mt: 1.5,
                minWidth: 220,
                borderRadius: 2,
                overflow: 'visible',
                filter: 'drop-shadow(0px 4px 20px rgba(0,0,0,0.1))',
                '&:before': {
                  content: '""',
                  display: 'block',
                  position: 'absolute',
                  top: 0,
                  right: 14,
                  width: 10,
                  height: 10,
                  bgcolor: 'background.paper',
                  transform: 'translateY(-50%) rotate(45deg)',
                  zIndex: 0,
                },
              },
            }}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            {/* User Info Header */}
            <Box sx={{ px: 2, py: 1.5, pb: 1 }}>
              <Typography variant="body2" fontWeight={600} color="text.primary">
                {user?.email || 'user@example.com'}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                <Chip 
                  label={badge.label} 
                  size="small" 
                  color={badge.color}
                  sx={{ 
                    height: 20, 
                    fontSize: '0.6875rem',
                    fontWeight: 700
                  }} 
                />
              </Box>
            </Box>
            
            <Divider />

            {/* Menu Items */}
            <MenuItem onClick={handleProfile} sx={{ py: 1.25 }}>
              <ListItemIcon>
                <AccountCircle fontSize="small" />
              </ListItemIcon>
              <ListItemText>Profile</ListItemText>
            </MenuItem>

            <MenuItem onClick={handleBilling} sx={{ py: 1.25 }}>
              <ListItemIcon>
                <CreditCard fontSize="small" />
              </ListItemIcon>
              <ListItemText>Billing & Credits</ListItemText>
            </MenuItem>

            <MenuItem onClick={handleSettings} sx={{ py: 1.25 }}>
              <ListItemIcon>
                <Settings fontSize="small" />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>

            <Divider />

            <MenuItem onClick={handleLogout} sx={{ py: 1.25, color: 'error.main' }}>
              <ListItemIcon>
                <Logout fontSize="small" color="error" />
              </ListItemIcon>
              <ListItemText>Sign Out</ListItemText>
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
