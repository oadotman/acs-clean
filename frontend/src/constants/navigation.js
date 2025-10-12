import {
  Dashboard,
  AddCircle,
  Analytics,
  Folder,
  Groups,
  Settings,
  Hub,
  CreditCard,
  Home,
  Assessment,
  BarChart,
  TrendingUp,
  Engineering,
  AccountCircle,
  Star,
  Business,
  Label
} from '@mui/icons-material';

// Primary navigation items for the left sidebar
export const MAIN_NAV_ITEMS = [
  {
    id: 'new-analysis',
    label: 'New Analysis',
    icon: AddCircle,
    path: '/analysis/new',
    description: 'Start a new ad analysis',
    default: true // This is the default landing page
  },
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Home,
    path: '/dashboard',
    description: 'Main dashboard overview'
  },
  {
    id: 'analyses',
    label: 'Analyses',
    icon: Analytics,
    path: '/history',
    description: 'View analysis history'
  },
  {
    id: 'projects',
    label: 'Projects',
    icon: Folder,
    path: '/projects',
    description: 'Manage your projects'
  },
  {
    id: 'team',
    label: 'Team',
    icon: Groups,
    path: '/team',
    description: 'Team management',
    requiresTeam: true // Show only for team/agency plans
  }
];

// Account & Settings navigation items
export const ACCOUNT_NAV_ITEMS = [
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    path: '/profile',
    description: 'Account settings and preferences'
  },
  {
    id: 'billing',
    label: 'Billing & Credits',
    icon: CreditCard,
    path: '/billing',
    description: 'Billing information and credits'
  }
];

// Agency-specific navigation items
export const AGENCY_NAV_ITEMS = [
  {
    id: 'agency-integrations',
    label: '🤝 Integrations',
    icon: Hub,
    path: '/agency/integrations',
    description: 'Agency integrations and API connections'
    // requiresTeam: true // Temporarily removed to show for all users
  },
  {
    id: 'team-management',
    label: '👥 Team Management',
    icon: Groups,
    path: '/agency/team',
    description: 'Manage team members and permissions'
    // requiresTeam: true // Temporarily removed to show for all users
  },
  {
    id: 'reports-branding',
    label: '📊 Reports & Branding',
    icon: Business,
    path: '/agency/reports',
    description: 'Custom reports and branding options'
    // requiresTeam: true // Temporarily removed to show for all users
  },
  {
    id: 'white-label',
    label: '🏷️ White Label Settings',
    icon: Label,
    path: '/agency/white-label',
    description: 'White label configuration and branding'
    // requiresTeam: true // Temporarily removed to show for all users
  }
];

// All navigation items combined
export const ALL_NAV_ITEMS = [...MAIN_NAV_ITEMS, ...ACCOUNT_NAV_ITEMS, ...AGENCY_NAV_ITEMS];

// Navigation sections for the sidebar
export const NAV_SECTIONS = [
  {
    id: 'main',
    title: 'Main',
    items: MAIN_NAV_ITEMS
  },
  {
    id: 'account',
    title: 'ACCOUNT',
    items: ACCOUNT_NAV_ITEMS,
    divider: true // Show divider before this section
  },
  {
    id: 'agency',
    title: 'Agency',
    items: AGENCY_NAV_ITEMS,
    divider: false // No divider since it's part of account section
  }
];

// Helper functions to check user permissions for navigation items
export const canAccessNavItem = (item, user, subscription) => {
  // If no special requirements, item is accessible
  if (!item.requiresPro && !item.requiresTeam) {
    return true;
  }

  // Check Pro/Agency plan requirement
  if (item.requiresPro) {
    return subscription?.tier === 'pro' || subscription?.tier === 'agency';
  }

  // Check Team/Agency plan requirement
  if (item.requiresTeam) {
    return subscription?.tier === 'agency';
  }

  return false;
};

// Get filtered navigation items based on user permissions
export const getFilteredNavItems = (items, user, subscription) => {
  return items.filter(item => canAccessNavItem(item, user, subscription));
};

// Navigation paths that require authentication
export const PROTECTED_PATHS = ALL_NAV_ITEMS.map(item => item.path);

// Quick access to paths
export const PATHS = {
  DASHBOARD: '/dashboard',
  NEW_ANALYSIS: '/analysis/new',
  ANALYSES: '/history',
  PROJECTS: '/projects',
  TEAM: '/team',
  SETTINGS: '/profile',
  BILLING: '/billing',
  // Agency paths
  AGENCY_INTEGRATIONS: '/agency/integrations',
  AGENCY_TEAM: '/agency/team',
  AGENCY_REPORTS: '/agency/reports',
  AGENCY_WHITE_LABEL: '/agency/white-label'
};
