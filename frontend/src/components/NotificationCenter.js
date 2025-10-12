import React, { useState, useEffect } from 'react';
import {
  IconButton,
  Badge,
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  Chip,
  useTheme,
  alpha
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Close as CloseIcon,
  MarkEmailRead as MarkEmailReadIcon
} from '@mui/icons-material';

const NotificationCenter = () => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'success',
      title: 'Analysis Complete',
      message: 'Your Facebook ad analysis is ready to view',
      timestamp: new Date(Date.now() - 1000 * 60 * 5), // 5 minutes ago
      read: false,
      actionText: 'View Results',
      actionLink: '/results/123'
    },
    {
      id: 2,
      type: 'info',
      title: 'New Template Available',
      message: 'Check out our latest SaaS ad templates',
      timestamp: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
      read: false,
      actionText: 'Browse Templates',
      actionLink: '/templates'
    },
    {
      id: 3,
      type: 'warning',
      title: 'Usage Limit Approaching',
      message: 'You\'ve used 8/10 of your monthly analyses',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
      read: true,
      actionText: 'Upgrade Plan',
      actionLink: '/pricing'
    }
  ]);

  const open = Boolean(anchorEl);
  const unreadCount = notifications.filter(n => !n.read).length;

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const markAsRead = (id) => {
    setNotifications(notifications.map(n => 
      n.id === id ? { ...n, read: true } : n
    ));
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const removeNotification = (id) => {
    setNotifications(notifications.filter(n => n.id !== id));
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon sx={{ color: 'success.main' }} />;
      case 'warning':
        return <WarningIcon sx={{ color: 'warning.main' }} />;
      case 'error':
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      default:
        return <InfoIcon sx={{ color: 'info.main' }} />;
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  return (
    <>
      <IconButton
        onClick={handleClick}
        sx={{
          position: 'relative',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
          }
        }}
      >
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            width: 380,
            maxHeight: 500,
            mt: 1,
            borderRadius: 3,
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider'
          }
        }}
      >
        <Box>
          {/* Header */}
          <Box
            sx={{
              p: 2,
              borderBottom: '1px solid',
              borderColor: 'divider',
              background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
            }}
          >
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" fontWeight="bold">
                Notifications
              </Typography>
              {unreadCount > 0 && (
                <Button
                  size="small"
                  startIcon={<MarkEmailReadIcon />}
                  onClick={markAllAsRead}
                  sx={{ fontSize: '0.75rem' }}
                >
                  Mark all read
                </Button>
              )}
            </Box>
            {unreadCount > 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
              </Typography>
            )}
          </Box>

          {/* Notifications List */}
          <Box sx={{ maxHeight: 350, overflow: 'auto' }}>
            {notifications.length > 0 ? (
              <List sx={{ p: 0 }}>
                {notifications.map((notification, index) => (
                  <React.Fragment key={notification.id}>
                    <ListItem
                      sx={{
                        py: 1.5,
                        px: 2,
                        bgcolor: notification.read ? 'transparent' : alpha(theme.palette.primary.main, 0.02),
                        borderLeft: notification.read ? 'none' : `3px solid ${theme.palette.primary.main}`,
                        '&:hover': {
                          bgcolor: alpha(theme.palette.primary.main, 0.05),
                        },
                        cursor: 'pointer'
                      }}
                      onClick={() => !notification.read && markAsRead(notification.id)}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        {getIcon(notification.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                            <Typography
                              variant="subtitle2"
                              fontWeight={notification.read ? 400 : 600}
                              sx={{ pr: 1 }}
                            >
                              {notification.title}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ whiteSpace: 'nowrap' }}
                              >
                                {formatTimeAgo(notification.timestamp)}
                              </Typography>
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  removeNotification(notification.id);
                                }}
                                sx={{ 
                                  opacity: 0.6,
                                  '&:hover': { opacity: 1 }
                                }}
                              >
                                <CloseIcon sx={{ fontSize: '0.9rem' }} />
                              </IconButton>
                            </Box>
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ mb: 1 }}
                            >
                              {notification.message}
                            </Typography>
                            {notification.actionText && (
                              <Button
                                size="small"
                                variant="outlined"
                                sx={{ 
                                  fontSize: '0.7rem',
                                  py: 0.5,
                                  px: 1.5
                                }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // Handle navigation here
                                  console.log('Navigate to:', notification.actionLink);
                                }}
                              >
                                {notification.actionText}
                              </Button>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < notifications.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                py={6}
                px={3}
              >
                <NotificationsIcon 
                  sx={{ 
                    fontSize: 48, 
                    color: 'text.disabled',
                    mb: 2
                  }} 
                />
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  No notifications yet
                </Typography>
              </Box>
            )}
          </Box>

          {/* Footer */}
          {notifications.length > 0 && (
            <Box
              sx={{
                p: 1.5,
                borderTop: '1px solid',
                borderColor: 'divider',
                textAlign: 'center'
              }}
            >
              <Button
                size="small"
                fullWidth
                onClick={() => {
                  // Handle view all notifications
                  console.log('View all notifications');
                  handleClose();
                }}
              >
                View All Notifications
              </Button>
            </Box>
          )}
        </Box>
      </Popover>
    </>
  );
};

export default NotificationCenter;
