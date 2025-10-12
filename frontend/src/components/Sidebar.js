import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Typography,
  Box,
  Avatar,
  Chip,
  IconButton,
  Divider,
  Tooltip,
  Collapse,
  useTheme,
  useMediaQuery,
  Badge
} from '@mui/material';
import BrandLogo from './BrandLogo';
import {
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  LibraryBooks as TemplateIcon,
  Assessment as ReportsIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  Payment as BillingIcon,
  Menu as MenuIcon,
  ChevronLeft,
  ChevronRight,
  ExpandLess,
  ExpandMore,
  Notifications,
  TrendingUp,
  Compare,
  Folder,
  Star,
  // New icons for expanded tools
  Policy as ComplianceIcon,
  AttachMoney as ROIIcon,
  Science as ABTestIcon,
  Business as IndustryIcon,
  SearchOff as ForensicsIcon,
  Psychology as PsychologyIcon,
  RecordVoiceOver as BrandVoiceIcon,
  Gavel as LegalIcon,
  // Shared workflow icons
  Folder as ProjectsIcon,
  // Agency icons
  Hub as IntegrationsIcon,
  Groups as TeamIcon,
  BarChart as AgencyReportsIcon,
  Label as WhiteLabelIcon
} from '@mui/icons-material';
import StartIcon from './icons/StartIcon';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/authContext';

const SIDEBAR_WIDTH = 280;
const SIDEBAR_COLLAPSED_WIDTH = 72;

const navigationSections = [
  {
    id: 'main',
    label: 'Navigation',
    items: [
      {
        id: 'projects',
        label: 'My Projects',
        path: '/projects',
        icon: ProjectsIcon,
        badge: null
      },
      {
        id: 'history',
        label: 'Analysis History',
        path: '/history',
        icon: HistoryIcon,
        badge: null
      }
    ]
  },
  {
    id: 'account',
    label: 'ACCOUNT',
    items: [
      {
        id: 'settings',
        label: 'Settings',
        path: '/settings',
        icon: SettingsIcon,
        badge: null
      },
      {
        id: 'billing',
        label: 'Billing & Credits',
        path: '/billing',
        icon: BillingIcon,
        badge: null
      },
      {
        id: 'agency',
        label: '[AGENCY]',
        path: null, // No direct path - this is a parent item
        icon: Star,
        badge: 'PRO',
        expandable: true,
        children: [
          {
            id: 'integrations',
            label: '🤝 Integrations',
            path: '/agency/integrations',
            icon: IntegrationsIcon
          },
          {
            id: 'team-management',
            label: '👥 Team Management',
            path: '/agency/team',
            icon: TeamIcon
          },
          {
            id: 'reports-branding',
            label: '📊 Reports & Branding',
            path: '/agency/reports',
            icon: AgencyReportsIcon
          },
          {
            id: 'white-label',
            label: '🏷️ White Label Settings',
            path: '/agency/white-label',
            icon: WhiteLabelIcon
          }
        ]
      }
    ]
  }
];

const Sidebar = ({ open, onClose, variant = 'permanent' }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const navigate = useNavigate();
  const { user, subscription, logout } = useAuth();
  
  const [collapsed, setCollapsed] = useState(false);
  const [expandedItems, setExpandedItems] = useState({});
  const [collapsedSections, setCollapsedSections] = useState({
    'ai-tools': true, // Start with AI tools collapsed
  });

  const handleToggleCollapse = () => {
    setCollapsed(!collapsed);
  };

  const handleExpandItem = (itemId) => {
    setExpandedItems(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }));
  };

  const handleToggleSection = (sectionId) => {
    setCollapsedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  const isActive = (path) => location.pathname === path;

  const filteredNavSections = navigationSections;

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const sidebarContent = (
    <Box
      sx={{
        width: collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        borderRight: 1,
        borderColor: 'divider',
        transition: theme.transitions.create(['width'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      }}
    >
      {/* Header */}
      <Box 
        sx={{ 
          p: 2.5, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          borderBottom: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'rgba(37, 99, 235, 0.02)'
        }}
      >
        {!collapsed ? (
          <BrandLogo variant="full" size="medium" />
        ) : (
          <BrandLogo variant="icon" size="small" />
        )}
        <IconButton
          onClick={handleToggleCollapse}
          size="small"
          sx={{
            ml: collapsed ? 'auto' : 1,
            transition: 'all 0.2s ease-in-out',
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            '&:hover': { 
              transform: 'scale(1.1)',
              backgroundColor: 'rgba(37, 99, 235, 0.12)'
            }
          }}
        >
          {collapsed ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      </Box>

      <Divider />


      {/* Navigation Items with Sections */}
      <Box sx={{ flex: 1, py: 1, overflow: 'auto' }}>
        {filteredNavSections.map((section, sectionIndex) => (
          <Box key={section.id}>
            {/* Section Label (only if not collapsed) */}
            {!collapsed && (
              <Box 
                sx={{ 
                  px: 2, 
                  py: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: section.collapsible ? 'pointer' : 'default'
                }}
                onClick={section.collapsible ? () => handleToggleSection(section.id) : undefined}
              >
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: 'text.secondary',
                    fontWeight: 600,
                    fontSize: '0.65rem',
                    lineHeight: 1.2,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}
                >
                  {section.label}
                </Typography>
                {section.collapsible && (
                  <IconButton
                    size="small"
                    sx={{ p: 0.25, color: 'text.secondary' }}
                  >
                    {collapsedSections[section.id] ? <ExpandMore fontSize="small" /> : <ExpandLess fontSize="small" />}
                  </IconButton>
                )}
              </Box>
            )}
            
            {/* Section Items */}
            <Collapse in={!section.collapsible || !collapsedSections[section.id]} timeout="auto">
              <List sx={{ px: 1, pb: 0 }}>
                {section.items.map((item) => (
                  <Box key={item.id}>
                    <ListItem disablePadding sx={{ mb: 0.5 }}>
                      <Tooltip title={collapsed ? item.label : ''} placement="right">
                        <ListItemButton
                          onClick={() => {
                            if (item.expandable) {
                              handleExpandItem(item.id);
                            } else if (item.path) {
                              handleNavigation(item.path);
                            }
                          }}
                          sx={{
                            borderRadius: 2,
                            minHeight: 40,
                            py: 0.5,
                            bgcolor: isActive(item.path) ? 'primary.main' : 'transparent',
                            color: isActive(item.path) ? 'primary.contrastText' : 'text.primary',
                            boxShadow: isActive(item.path) ? '0 2px 8px rgba(37, 99, 235, 0.3)' : 'none',
                            '&:hover': {
                              bgcolor: isActive(item.path) ? 'primary.dark' : 'rgba(37, 99, 235, 0.08)',
                              transform: 'translateX(2px)',
                            },
                            transition: 'all 0.2s ease-in-out',
                          }}
                        >
                          <ListItemIcon
                            sx={{
                              minWidth: 0,
                              mr: collapsed ? 0 : 1,
                              justifyContent: 'center',
                              color: 'inherit',
                            }}
                          >
                            <Badge
                              color="error"
                              variant="dot"
                              invisible={!item.badge}
                              sx={{ '& .MuiBadge-badge': { right: -2, top: -2 } }}
                            >
                              <item.icon />
                            </Badge>
                          </ListItemIcon>
                          {!collapsed && (
                            <>
                              <ListItemText
                                primary={item.label}
                                primaryTypographyProps={{
                                  fontWeight: isActive(item.path) ? 600 : 500,
                                  fontSize: '0.8125rem', // 13px
                                  lineHeight: 1.2,
                                }}
                              />
                              {item.badge && (
                                <Chip
                                  label={item.badge}
                                  size="small"
                                  color="secondary"
                                  sx={{ height: 18, fontSize: '0.65rem', mr: 0.5 }}
                                />
                              )}
                              {item.expandable && (
                                <IconButton
                                  size="small"
                                  sx={{ p: 0.25, color: 'inherit' }}
                                >
                                  {expandedItems[item.id] ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
                                </IconButton>
                              )}
                            </>
                          )}
                        </ListItemButton>
                      </Tooltip>
                    </ListItem>
                    
                    {/* Child Items (Agency Submenu) */}
                    {item.expandable && item.children && (
                      <Collapse in={expandedItems[item.id]} timeout="auto">
                        <List sx={{ pl: 2 }}>
                          {item.children.map((child) => (
                            <ListItem key={child.id} disablePadding sx={{ mb: 0.25 }}>
                              <Tooltip title={collapsed ? child.label : ''} placement="right">
                                <ListItemButton
                                  onClick={() => handleNavigation(child.path)}
                                  sx={{
                                    borderRadius: 1.5,
                                    minHeight: 36,
                                    py: 0.25,
                                    pl: 1,
                                    bgcolor: isActive(child.path) ? 'primary.main' : 'transparent',
                                    color: isActive(child.path) ? 'primary.contrastText' : 'text.secondary',
                                    '&:hover': {
                                      bgcolor: isActive(child.path) ? 'primary.dark' : 'rgba(37, 99, 235, 0.06)',
                                      transform: 'translateX(2px)',
                                    },
                                    transition: 'all 0.2s ease-in-out',
                                  }}
                                >
                                  {!collapsed && (
                                    <ListItemText
                                      primary={child.label}
                                      primaryTypographyProps={{
                                        fontWeight: isActive(child.path) ? 600 : 400,
                                        fontSize: '0.75rem', // 12px - smaller for children
                                        lineHeight: 1.2,
                                      }}
                                    />
                                  )}
                                </ListItemButton>
                              </Tooltip>
                            </ListItem>
                          ))}
                        </List>
                      </Collapse>
                    )}
                  </Box>
                ))}
              </List>
            </Collapse>
            
            {/* Section Divider */}
            {sectionIndex < filteredNavSections.length - 1 && (
              <Divider 
                sx={{ 
                  mx: 2, 
                  my: 1,
                  borderColor: 'rgba(37, 99, 235, 0.1)'
                }} 
              />
            )}
          </Box>
        ))}
      </Box>

    </Box>
  );

  if (isMobile) {
    return (
      <Drawer
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          '& .MuiDrawer-paper': {
            width: SIDEBAR_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        {sidebarContent}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
          boxSizing: 'border-box',
          transition: theme.transitions.create(['width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        },
      }}
      open
    >
      {sidebarContent}
    </Drawer>
  );
};

export default Sidebar;
