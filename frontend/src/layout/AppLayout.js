import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  IconButton,
  useMediaQuery,
  useTheme,
  alpha,
  Tooltip
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon
} from '@mui/icons-material';
import { Link, useLocation, Outlet } from 'react-router-dom';

// Components
import BrandLogo from '../components/BrandLogo';
import TopBar from '../components/TopBar';
import CreditsWidget from '../components/CreditsWidget';

// Navigation data
import { NAV_SECTIONS, getFilteredNavItems, canAccessNavItem } from '../constants/navigation';

// Auth context
import { useAuth } from '../services/authContext';

const DRAWER_WIDTH = 200;
const DRAWER_COLLAPSED_WIDTH = 56;

const AppLayout = () => {
  const theme = useTheme();
  const location = useLocation();
  const { user, subscription } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  // Removed expandedSections state - always show all items for cleaner UI

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleCollapseToggle = () => {
    setCollapsed(!collapsed);
  };

  // Removed handleSectionToggle - sections always visible for simplicity

  const isActive = (path) => {
    return location.pathname === path;
  };

  const NavigationList = ({ sections, isCollapsed = false }) => {
    return (
      <>
        {sections.map((section, sectionIndex) => {
          const filteredItems = getFilteredNavItems(section.items, user, subscription);
          
          if (filteredItems.length === 0) return null;

          return (
            <Box key={section.id}>
              {section.divider && <Divider sx={{ my: 1 }} />}
              
              {/* Section Header - Minimal */}
              {!isCollapsed && sectionIndex > 0 && (
                <Box
                  sx={{
                    px: 2,
                    pt: 2,
                    pb: 0.5,
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      color: alpha(theme.palette.text.secondary, 0.6),
                      letterSpacing: '0.08em',
                      textTransform: 'uppercase',
                    }}
                  >
                    {section.title}
                  </Typography>
                </Box>
              )}

              {/* Navigation Items */}
              <List disablePadding sx={{ px: isCollapsed ? 0.75 : 1.5, pb: 1 }}>
                  {filteredItems.map((item) => {
                    const active = isActive(item.path);
                    const IconComponent = item.icon;
                    const accessible = canAccessNavItem(item, user, subscription);

                    if (isCollapsed) {
                      return (
                        <Tooltip
                          key={item.id}
                          title={`${item.label}${!accessible ? ' (Pro/Agency only)' : ''}`}
                          placement="right"
                          arrow
                        >
                          <ListItemButton
                            component={Link}
                            to={item.path}
                            disabled={!accessible}
                            onClick={() => isMobile && setMobileOpen(false)}
                            sx={{
                              minHeight: 40,
                              justifyContent: 'center',
                              px: 0.5,
                              py: 0.75,
                              mb: 0.25,
                              borderRadius: 1.5,
                              backgroundColor: active 
                                ? alpha(theme.palette.primary.main, 0.1)
                                : 'transparent',
                              color: active 
                                ? theme.palette.primary.main 
                                : accessible ? 'text.primary' : 'text.disabled',
                              transition: 'all 0.15s ease-in-out',
                              '&:hover': {
                                backgroundColor: active 
                                  ? alpha(theme.palette.primary.main, 0.14)
                                  : alpha(theme.palette.action.hover, 0.06),
                                transform: 'translateX(2px)'
                              },
                              '&.Mui-disabled': {
                                opacity: 0.4
                              }
                            }}
                          >
                            <ListItemIcon
                              sx={{
                                minWidth: 'auto',
                                color: 'inherit',
                                '& .MuiSvgIcon-root': {
                                  fontSize: '1.125rem'
                                }
                              }}
                            >
                              <IconComponent />
                            </ListItemIcon>
                          </ListItemButton>
                        </Tooltip>
                      );
                    }

                    return (
                      <ListItemButton
                        key={item.id}
                        component={Link}
                        to={item.path}
                        disabled={!accessible}
                        onClick={() => isMobile && setMobileOpen(false)}
                        sx={{
                          minHeight: 36,
                          px: 1.5,
                          py: 0.75,
                          mb: 0.25,
                          borderRadius: 1.5,
                          backgroundColor: active 
                            ? alpha(theme.palette.primary.main, 0.1)
                            : 'transparent',
                          color: active 
                            ? theme.palette.primary.main 
                            : accessible ? 'text.primary' : 'text.disabled',
                          transition: 'all 0.15s ease-in-out',
                          '&:hover': {
                            backgroundColor: active 
                              ? alpha(theme.palette.primary.main, 0.14)
                              : alpha(theme.palette.action.hover, 0.06),
                            transform: 'translateX(2px)',
                          },
                          '&.Mui-disabled': {
                            opacity: 0.4,
                            '& .MuiListItemText-primary': {
                              color: 'text.disabled'
                            }
                          }
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            minWidth: 32,
                            color: 'inherit',
                            '& .MuiSvgIcon-root': {
                              fontSize: '1.125rem'
                            }
                          }}
                        >
                          <IconComponent />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography 
                              variant="body2" 
                              sx={{
                                fontSize: '0.8125rem',
                                fontWeight: active ? 600 : 500,
                                lineHeight: 1.4
                              }}
                            >
                              {item.label}
                              {!accessible && (
                                <Typography
                                  component="span"
                                  variant="caption"
                                  sx={{
                                    ml: 0.75,
                                    px: 0.75,
                                    py: 0.125,
                                    borderRadius: 0.75,
                                    backgroundColor: alpha(theme.palette.warning.main, 0.15),
                                    color: theme.palette.warning.dark,
                                    fontSize: '0.625rem',
                                    fontWeight: 700,
                                    letterSpacing: '0.02em'
                                  }}
                                >
                                  {item.requiresTeam ? 'AGENCY' : 'PRO'}
                                </Typography>
                              )}
                            </Typography>
                          }
                        />
                      </ListItemButton>
                    );
                  })}
                </List>
            </Box>
          );
        })}
      </>
    );
  };

  const drawer = (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.paper'
      }}
    >
      {/* Header - Clean & Minimal */}
      <Box
        sx={{
          px: 1.5,
          py: 1.5,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.6)}`,
          minHeight: 56,
          backgroundColor: 'background.paper'
        }}
      >
        {!collapsed ? (
          <BrandLogo variant="full" size="small" />
        ) : (
          <BrandLogo variant="icon" size="small" />
        )}
        
        {!isMobile && (
          <IconButton
            onClick={handleCollapseToggle}
            size="small"
            sx={{
              width: 28,
              height: 28,
              backgroundColor: alpha(theme.palette.action.hover, 0.05),
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main
              },
              transition: 'all 0.2s ease-in-out'
            }}
          >
            {collapsed ? <MenuIcon sx={{ fontSize: '1rem' }} /> : <ChevronLeftIcon sx={{ fontSize: '1rem' }} />}
          </IconButton>
        )}
      </Box>

      {/* Navigation - Generous Whitespace */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          py: 1,
          '&::-webkit-scrollbar': {
            width: '3px'
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'transparent'
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: alpha(theme.palette.grey[400], 0.4),
            borderRadius: '1.5px',
            '&:hover': {
              backgroundColor: alpha(theme.palette.grey[400], 0.6)
            }
          }
        }}
      >
        <NavigationList sections={NAV_SECTIONS} isCollapsed={collapsed} />
      </Box>

      {/* Credits Widget - Always visible in sidebar */}
      <CreditsWidget collapsed={collapsed} />
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Mobile drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              border: 'none',
              boxShadow: theme.shadows[8]
            },
          }}
        >
          {drawer}
        </Drawer>
      )}

      {/* Desktop drawer */}
      {!isMobile && (
        <Drawer
          variant="permanent"
          sx={{
            width: collapsed ? DRAWER_COLLAPSED_WIDTH : DRAWER_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: collapsed ? DRAWER_COLLAPSED_WIDTH : DRAWER_WIDTH,
              boxSizing: 'border-box',
              border: 'none',
              borderRight: 1,
              borderColor: 'divider',
              transition: theme.transitions.create(['width'], {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      )}

      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          backgroundColor: 'background.default',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Top Bar with User Profile and Theme Toggle */}
        <TopBar 
          onMenuClick={handleDrawerToggle}
          showMenuButton={isMobile}
        />

        {/* Mobile legacy fallback (if needed) */}
        {false && isMobile && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              p: 2,
              borderBottom: 1,
              borderColor: 'divider',
              backgroundColor: 'background.paper',
              minHeight: 64
            }}
          >
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <BrandLogo variant="full" size="small" />
          </Box>
        )}

        {/* Page content */}
        <Box sx={{ flex: 1, p: { xs: 2, sm: 3, md: 4 }, overflow: 'auto' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default AppLayout;