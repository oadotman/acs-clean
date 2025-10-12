import React, { useState } from 'react';
import {
  Box,
  Avatar,
  Typography,
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  alpha,
  useTheme,
  Tooltip
} from '@mui/material';
import {
  AccountCircle as ProfileIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  KeyboardArrowUp as ArrowUpIcon,
  KeyboardArrowDown as ArrowDownIcon
} from '@mui/icons-material';
import { useAuth } from '../services/authContext';
import { useNavigate } from 'react-router-dom';

const UserProfileMenu = ({ collapsed = false }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  const handleLogout = async () => {
    handleClose();
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Generate user initials for avatar
  const getUserInitials = (user) => {
    if (!user) return 'U';
    
    const email = user.email || '';
    const name = user.name || user.full_name || '';
    
    if (name) {
      const nameParts = name.split(' ');
      return nameParts.length > 1 
        ? `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase()
        : nameParts[0][0].toUpperCase();
    }
    
    return email[0]?.toUpperCase() || 'U';
  };

  // Get display name
  const getDisplayName = (user) => {
    if (!user) return 'User';
    return user.name || user.full_name || user.email?.split('@')[0] || 'User';
  };

  if (!user) {
    return null;
  }

  const userInitials = getUserInitials(user);
  const displayName = getDisplayName(user);
  const userEmail = user.email || 'No email';

  if (collapsed) {
    return (
      <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider' }}>
        <Tooltip title={`${displayName} (${userEmail})`} placement="right">
          <IconButton
            onClick={handleClick}
            size="small"
            sx={{
              width: '100%',
              height: 48,
              backgroundColor: alpha(theme.palette.primary.main, 0.08),
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.12),
              }
            }}
          >
            <Avatar 
              sx={{ 
                width: 32, 
                height: 32,
                bgcolor: theme.palette.primary.main,
                fontSize: '0.875rem',
                fontWeight: 600
              }}
            >
              {userInitials}
            </Avatar>
          </IconButton>
        </Tooltip>
        
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          sx={{
            '& .MuiPaper-root': {
              minWidth: 200,
              mt: -1
            }
          }}
        >
          <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" fontWeight={600}>
              {displayName}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {userEmail}
            </Typography>
          </Box>
          
          <MenuItem onClick={handleProfile}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </MenuItem>
          
          <Divider />
          
          <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" color="error" />
            </ListItemIcon>
            <ListItemText primary="Sign Out" />
          </MenuItem>
        </Menu>
      </Box>
    );
  }

  return (
    <Box 
      sx={{ 
        px: 2, 
        py: 1.5, 
        borderTop: `1px solid ${alpha(theme.palette.divider, 0.6)}`,
        backgroundColor: 'background.paper'
      }}
    >
      <Button
        onClick={handleClick}
        fullWidth
        sx={{
          justifyContent: 'flex-start',
          textAlign: 'left',
          textTransform: 'none',
          p: 1,
          borderRadius: 1.5,
          backgroundColor: 'transparent',
          minHeight: 48,
          transition: 'all 0.15s ease-in-out',
          '&:hover': {
            backgroundColor: alpha(theme.palette.action.hover, 0.04),
          }
        }}
      >
        <Avatar 
          sx={{ 
            width: 32, 
            height: 32, 
            mr: 1.25,
            bgcolor: theme.palette.primary.main,
            fontSize: '0.875rem',
            fontWeight: 600
          }}
        >
          {userInitials}
        </Avatar>
        
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Typography 
            variant="body2" 
            sx={{
              fontSize: '0.8125rem',
              fontWeight: 600,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {displayName}
          </Typography>
          <Typography 
            variant="caption" 
            sx={{ 
              fontSize: '0.6875rem',
              color: alpha(theme.palette.text.secondary, 0.8),
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              display: 'block'
            }}
          >
            {userEmail}
          </Typography>
        </Box>
        
        {open ? (
          <ArrowUpIcon sx={{ ml: 0.5, fontSize: '1rem', color: 'text.secondary' }} />
        ) : (
          <ArrowDownIcon sx={{ ml: 0.5, fontSize: '1rem', color: 'text.secondary' }} />
        )}
      </Button>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        sx={{
          '& .MuiPaper-root': {
            width: anchorEl?.offsetWidth || 240,
            mt: -1
          }
        }}
      >
        <MenuItem onClick={handleProfile}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText 
            primary="Settings" 
            secondary="Account settings and preferences"
          />
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText 
            primary="Sign Out"
            secondary="Log out of your account"
          />
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default UserProfileMenu;