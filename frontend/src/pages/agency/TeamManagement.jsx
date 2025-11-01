import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Divider,
  useMediaQuery,
  useTheme,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Groups as TeamIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  PersonAdd as PersonAddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Email as EmailIcon,
  ContentCopy as CopyIcon,
  WhatsApp as WhatsAppIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

// Import services
import teamService from '../../services/teamService';
import { useAuth } from '../../services/authContext';
import { canInviteTeamMembers, getTeamMemberLimits } from '../../utils/creditSystem';
import { SUBSCRIPTION_TIERS } from '../../constants/plans';

// Roles configuration with proper capitalization
const ROLE_CONFIG = {
  admin: { label: 'Admin', description: 'Full access to all features and settings', color: 'error' },
  editor: { label: 'Editor', description: 'Can create and edit analyses, limited settings access', color: 'primary' },
  viewer: { label: 'Viewer', description: 'Read-only access to analyses and reports', color: 'default' },
  client: { label: 'Client', description: 'View-only access to specific projects (external client)', color: 'info' }
};

// Convert role config to array format for form selects
const roles = Object.entries(ROLE_CONFIG).map(([value, config]) => ({
  value,
  label: config.label,
  description: config.description
}));

const AgencyTeamManagement = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, isAuthenticated, loading: authLoading, subscription } = useAuth();
  
  // UI State
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedMember, setSelectedMember] = useState(null);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState('viewer');
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [selectedClients, setSelectedClients] = useState([]);
  const [isClientUser, setIsClientUser] = useState(false);
  const [invitationCode, setInvitationCode] = useState('');
  const [codeDialogOpen, setCodeDialogOpen] = useState(false);
  const [codeCopied, setCodeCopied] = useState(false);
  
  // Data State
  const [agency, setAgency] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [teamAnalytics, setTeamAnalytics] = useState(null);
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  
  // Team member limits based on subscription
  const [teamLimits, setTeamLimits] = useState(null);
  const [canInvite, setCanInvite] = useState(false);

  const handleMenuClick = (event, member) => {
    setAnchorEl(event.currentTarget);
    setSelectedMember(member);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedMember(null);
  };

  // Load agency data and team members
  useEffect(() => {
    if (!user || !isAuthenticated || authLoading) {
      console.log('⏳ Waiting for auth to complete', { user: !!user, isAuthenticated, authLoading });
      return;
    }
    
    // Prevent duplicate calls
    let cancelled = false;
    let timeoutId = null;
    
    const loadData = async () => {
      if (cancelled) return;
      
      console.log('🚀 Starting agency data load for user:', user?.id);
      
      try {
        await loadAgencyData();
      } catch (err) {
        console.error('❌ Error loading agency data:', err);
        if (!cancelled) {
          setError(err.message || 'Failed to load agency data');
          setLoading(false);
        }
      }
    };
    
    loadData();
    
    // Add timeout fallback to prevent infinite loading
    timeoutId = setTimeout(() => {
      if (loading && !cancelled) {
        console.warn('⚠️ Loading timeout - forcing completion');
        setError('Loading timeout. Please refresh the page.');
        setLoading(false);
      }
    }, 15000); // Increased to 15 seconds
    
    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [user?.id, isAuthenticated, authLoading]); // Added authLoading dependency

  const loadAgencyData = async () => {
    console.log('\n==================== LOAD AGENCY DATA START ====================');
    
    try {
      setLoading(true);
      setError(null);
      
      console.log('🏬 Loading agency data for user:', {
        userId: user?.id, 
        email: user?.email,
        isAuthenticated,
        hasUser: !!user
      });
      
      if (!user?.id) {
        console.error('❌ No user ID available');
        throw new Error('User session not found. Please refresh the page.');
      }
      
      // Get or create agency for the user with proper error handling
      console.log('🔍 Calling teamService.getOrCreateUserAgency...');
      const agencyData = await teamService.getOrCreateUserAgency(user.id).catch(err => {
        console.error('❌ teamService.getOrCreateUserAgency failed:', err);
        throw new Error(err.message || 'Unable to load agency data. Please try again.');
      });
      
      console.log('✅ Agency data received:', agencyData);
      
      // Validate agency data
      if (!agencyData || !agencyData.id) {
        console.error('❌ No valid agency data returned');
        throw new Error('Failed to load or create agency. Please try refreshing the page.');
      }
      
      setAgency(agencyData);
      
      // Load team members and analytics
      const [members, analytics, agencyProjects, agencyClients] = await Promise.all([
        teamService.getTeamMembers(agencyData.id),
        teamService.getTeamAnalytics(agencyData.id),
        teamService.getAgencyProjects(agencyData.id),
        teamService.getAgencyClients(agencyData.id)
      ]);
      
      setTeamMembers(members);
      setTeamAnalytics(analytics);
      setProjects(agencyProjects);
      setClients(agencyClients);
      
      // Check team member limits based on subscription
      // Read subscription_tier from the subscription object (user_profiles row)
      const userTier = subscription?.subscription_tier || subscription?.tier || agencyData?.subscription_tier || 'free';
      
      console.log('\n========== TEAM LIMITS DEBUG ==========');
      console.log('📊 Raw subscription object:', subscription);
      console.log('📊 Agency subscription_tier:', agencyData?.subscription_tier);
      console.log('📊 Subscription tier field:', subscription?.subscription_tier);
      console.log('📊 User tier field:', user?.subscription_tier);
      console.log('🔑 Final userTier determined:', userTier);
      console.log('👥 Current member count:', members.length);
      
      // Import PLAN_LIMITS to check
      console.log('📋 Available SUBSCRIPTION_TIERS:', SUBSCRIPTION_TIERS);
      
      const limits = getTeamMemberLimits(userTier);
      console.log('🚧 Limits returned from getTeamMemberLimits:', limits);
      
      const inviteCheck = canInviteTeamMembers(userTier, members.length);
      console.log('✅ Invite check result:', inviteCheck);
      console.log('========================================\n');
      
      setTeamLimits(limits);
      setCanInvite(inviteCheck.canInvite);
    } catch (err) {
      console.error('\n❌ ==================== ERROR IN LOAD AGENCY DATA ====================');
      console.error('Error object:', err);
      console.error('Error message:', err?.message);
      console.error('Error stack:', err?.stack);
      console.error('==================== END ERROR ====================\n');
      setError(err.message || 'Failed to load team data');
    } finally {
      console.log('🏁 loadAgencyData finally block - setting loading to false');
      setLoading(false);
      console.log('==================== LOAD AGENCY DATA END ====================\n');
    }
  };

  const handleInviteMember = async () => {
    if (!newMemberEmail || !agency) return;
    
    try {
      setActionLoading(true);
      
      const invitationData = {
        email: newMemberEmail,
        role: newMemberRole,
        projectAccess: selectedProjects,
        clientAccess: selectedClients
      };
      
      const response = await teamService.sendInvitation(agency.id, user.id, invitationData);
      
      // Refresh team members to show the pending invitation
      const updatedMembers = await teamService.getTeamMembers(agency.id);
      setTeamMembers(updatedMembers);
      
      // Show invitation code dialog if code is returned
      if (response?.invitation_code) {
        setInvitationCode(response.invitation_code);
        setCodeDialogOpen(true);
        setCodeCopied(false);
      }
      
      // Reset form
      setInviteDialogOpen(false);
      setNewMemberEmail('');
      setNewMemberRole('viewer');
      setSelectedProjects([]);
      setSelectedClients([]);
      setIsClientUser(false);
    } catch (err) {
      console.error('Error inviting member:', err);
      // Error already handled by service with toast
    } finally {
      setActionLoading(false);
    }
  };
  
  const handleCopyCode = () => {
    navigator.clipboard.writeText(invitationCode);
    setCodeCopied(true);
    setTimeout(() => setCodeCopied(false), 2000);
  };
  
  const handleShareWhatsApp = () => {
    const message = encodeURIComponent(`Join our team on AdCopySurge! Use this invitation code: ${invitationCode}`);
    window.open(`https://wa.me/?text=${message}`, '_blank');
  };
  
  const handleShareEmail = () => {
    const subject = encodeURIComponent('Team Invitation - AdCopySurge');
    const body = encodeURIComponent(`You've been invited to join our team on AdCopySurge!\n\nInvitation Code: ${invitationCode}\n\nPlease use this code to accept the invitation.`);
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
  };
  
  const handleUpdateMember = async (memberId, updates) => {
    try {
      setActionLoading(true);
      await teamService.updateTeamMember(memberId, updates);
      
      // Refresh team members
      const updatedMembers = await teamService.getTeamMembers(agency.id);
      setTeamMembers(updatedMembers);
      
      handleMenuClose();
    } catch (err) {
      console.error('Error updating member:', err);
    } finally {
      setActionLoading(false);
    }
  };
  
  const handleRemoveMember = async (memberId) => {
    try {
      setActionLoading(true);
      await teamService.removeTeamMember(memberId);
      
      // Refresh team members
      const updatedMembers = await teamService.getTeamMembers(agency.id);
      setTeamMembers(updatedMembers);
      
      handleMenuClose();
    } catch (err) {
      console.error('Error removing member:', err);
    } finally {
      setActionLoading(false);
    }
  };
  
  const handleResendInvite = async (memberId) => {
    try {
      setActionLoading(true);
      // For now, we'll treat this as resending based on member data
      // In a full implementation, you'd track invitation IDs
      await teamService.resendInvitation(memberId);
      handleMenuClose();
    } catch (err) {
      console.error('Error resending invitation:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'pending': return 'warning';
      case 'inactive': return 'error';
      default: return 'default';
    }
  };

  const getRoleColor = (role) => {
    return ROLE_CONFIG[role?.toLowerCase()]?.color || 'default';
  };
  
  // Show loading state during auth or data loading
  if (authLoading || loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={48} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Loading team data...
          </Typography>
        </Box>
      </Container>
    );
  }
  
  // Show error state
  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={loadAgencyData}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }
  
  // Ensure user is authenticated and has agency tier
  if (!isAuthenticated || !user) {
    console.log('🚫 Auth check failed:', { isAuthenticated, hasUser: !!user });
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="warning">
          Please sign in to access team management.
        </Alert>
      </Container>
    );
  }
  
  // Check if user has agency tier
  const userTier = subscription?.subscription_tier || subscription?.tier || 'free';
  if (!userTier.includes('agency') && userTier !== 'agency_unlimited') {
    console.log('🚫 User does not have agency tier:', userTier);
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="info" action={
          <Button color="inherit" size="small" href="/pricing">
            Upgrade
          </Button>
        }>
          Team management is available for Agency tier subscribers. Current tier: {userTier}
        </Alert>
      </Container>
    );
  }
  
  // If agency is null but we have user and not loading, this should not trigger a loop
  // Only show this if there's no error (error state is handled above)
  if (!agency && !loading && !error) {
    console.log('⚠️ No agency data but user is authenticated (no error yet)');
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert 
          severity="info"
          action={
            <Button color="inherit" size="small" onClick={loadAgencyData}>
              Retry
            </Button>
          }
        >
          Unable to load agency data. Please try again.
        </Alert>
      </Container>
    );
  }

  // Mobile card component for responsive design
  const TeamMemberCard = ({ member }) => (
    <Card 
      sx={{ 
        mb: 2,
        transition: 'all 0.15s ease-in-out',
        '&:hover': {
          transform: 'translateY(-1px)',
          boxShadow: theme.shadows[4]
        }
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar src={member.avatar} sx={{ width: 48, height: 48 }}>
            {member.name.charAt(0)}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.9375rem' }}>
              {member.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8125rem' }}>
              {member.email}
            </Typography>
          </Box>
          <IconButton
            size="small"
            onClick={(e) => handleMenuClick(e, member)}
            aria-label={`More actions for ${member.name}`}
          >
            <MoreVertIcon />
          </IconButton>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip 
            label={member.role} 
            size="small" 
            color={getRoleColor(member.role)}
            variant="outlined"
            aria-label={`Role: ${member.role}`}
          />
          <Chip 
            label={member.status} 
            size="small" 
            color={getStatusColor(member.status)}
            aria-label={`Status: ${member.status}`}
          />
          {member.creditsUsed > 100 && (
            <Chip label="High Usage" color="warning" size="small" />
          )}
          {member.isClient && (
            <Chip label="Client Access" color="info" size="small" />
          )}
        </Box>
        
        <Grid container spacing={2} sx={{ fontSize: '0.875rem' }}>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.6875rem' }}>
              Last Active
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
              {member.lastActive}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.6875rem' }}>
              Analyses
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
              {member.analysesThisMonth}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.6875rem' }}>
              Credits Used
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
              {member.creditsUsed}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.6875rem' }}>
              Access Scope
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
              {member.projectsAccess?.includes('all') ? 'Full Access' : member.projectsAccess?.length > 0 ? `${member.projectsAccess.length} Projects` : 'No Access'}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <TeamIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
            👥 Team Management
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
          Manage your agency team members, roles, and permissions. Control who has access to your analyses and reports.
        </Typography>
        {teamLimits && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Team Member Limit: {teamMembers.length}/{teamLimits.maxTeamMembers === 0 ? '0' : teamLimits.maxTeamMembers} members
            </Typography>
            {!teamLimits.canInviteTeamMembers && (
              <Alert severity="info" sx={{ mt: 1, maxWidth: 600 }}>
                Upgrade to Agency Standard or higher to invite team members.
              </Alert>
            )}
            {teamLimits.canInviteTeamMembers && !canInvite && (
              <Alert severity="warning" sx={{ mt: 1, maxWidth: 600 }}>
                You've reached your team member limit. Upgrade your plan to invite more members.
              </Alert>
            )}
          </Box>
        )}
      </Box>

      {/* Team Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                {teamAnalytics?.totalMembers || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Members
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'success.main' }}>
                {teamAnalytics?.activeMembers || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Members
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'warning.main' }}>
                {teamAnalytics?.pendingMembers || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pending Invites
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'info.main' }}>
                {teamAnalytics?.totalAnalyses || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Analyses This Month
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Team Members Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Team Members
            </Typography>
            <Button
              variant="contained"
              startIcon={<PersonAddIcon />}
              onClick={() => setInviteDialogOpen(true)}
              disabled={!canInvite}
            >
              {!teamLimits?.canInviteTeamMembers ? 'Upgrade to Invite' : !canInvite ? 'Limit Reached' : 'Invite Member'}
            </Button>
          </Box>

          {/* Responsive layout: Cards on mobile, Table on desktop */}
          {isMobile ? (
            <Box>
              {teamMembers.map((member) => (
                <TeamMemberCard key={member.id} member={member} />
              ))}
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Member</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Last Active</TableCell>
                    <TableCell>Analyses</TableCell>
                    <TableCell>Credits Used</TableCell>
                    <TableCell>Access</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {teamMembers.map((member) => (
                    <TableRow key={member.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar src={member.avatar} sx={{ width: 40, height: 40 }}>
                            {member.name.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              {member.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {member.email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={member.role}
                          size="small"
                          color={getRoleColor(member.role)}
                          variant="outlined"
                          aria-label={`Role: ${member.role}`}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={member.status}
                          size="small"
                          color={getStatusColor(member.status)}
                          aria-label={`Status: ${member.status}`}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {member.lastActive}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {member.analysesThisMonth}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2">
                            {member.creditsUsed}
                          </Typography>
                          {member.creditsUsed > 100 && (
                            <Chip label="High Usage" color="warning" size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Projects: {member.projectsAccess.includes('all') ? 'All' : member.projectsAccess.length}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Clients: {member.clientAccess.includes('all') ? 'All' : member.clientAccess.length}
                          </Typography>
                          {member.isClient && (
                            <Chip label="Client Access" color="info" size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuClick(e, member)}
                          aria-label={`More actions for ${member.name}`}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          // TODO: Implement edit role dialog
          console.log('Edit role for:', selectedMember);
          handleMenuClose();
        }} disabled={actionLoading}>
          <EditIcon sx={{ mr: 1, fontSize: 'small' }} />
          Edit Role
        </MenuItem>
        {selectedMember?.status === 'pending' && (
          <MenuItem onClick={() => handleResendInvite(selectedMember.id)} disabled={actionLoading}>
            <EmailIcon sx={{ mr: 1, fontSize: 'small' }} />
            Resend Invite
          </MenuItem>
        )}
        <Divider />
        <MenuItem 
          onClick={() => handleRemoveMember(selectedMember.id)} 
          sx={{ color: 'error.main' }}
          disabled={actionLoading}
        >
          <DeleteIcon sx={{ mr: 1, fontSize: 'small' }} />
          Remove Member
        </MenuItem>
      </Menu>

      {/* Invite Member Dialog */}
      <Dialog open={inviteDialogOpen} onClose={() => setInviteDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Invite Team Member</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Email Address"
              type="email"
              fullWidth
              value={newMemberEmail}
              onChange={(e) => setNewMemberEmail(e.target.value)}
              sx={{ mb: 3 }}
            />
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Role</InputLabel>
              <Select
                value={newMemberRole}
                label="Role"
                onChange={(e) => {
                  setNewMemberRole(e.target.value);
                  setIsClientUser(e.target.value === 'client');
                }}
              >
                {roles.map((role) => (
                  <MenuItem key={role.value} value={role.value}>
                    <Box>
                      <Typography variant="subtitle2">{role.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {role.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Project Access */}
            {(newMemberRole === 'editor' || newMemberRole === 'viewer' || newMemberRole === 'client') && (
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Project Access</InputLabel>
                <Select
                  multiple
                  value={selectedProjects}
                  label="Project Access"
                  onChange={(e) => setSelectedProjects(e.target.value)}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={projects.find(p => p.id === value)?.name} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {projects.map((project) => (
                    <MenuItem key={project.id} value={project.id}>
                      {project.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            {/* Client Access (for client users) */}
            {isClientUser && (
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Client Association</InputLabel>
                <Select
                  value={selectedClients[0] || ''}
                  label="Client Association"
                  onChange={(e) => setSelectedClients([e.target.value])}
                >
                  {clients.map((client) => (
                    <MenuItem key={client.id} value={client.id}>
                      {client.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            {/* Permissions Summary */}
            <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Permissions Summary:</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {newMemberRole === 'admin' && (
                  <Chip label="Full Access" color="error" size="small" />
                )}
                {newMemberRole === 'editor' && (
                  <>
                    <Chip label="Create" color="primary" size="small" />
                    <Chip label="Edit" color="primary" size="small" />
                    <Chip label="View" color="default" size="small" />
                  </>
                )}
                {(newMemberRole === 'viewer' || newMemberRole === 'client') && (
                  <Chip label="View Only" color="default" size="small" />
                )}
                {isClientUser && (
                  <Chip label="External Client" color="info" size="small" />
                )}
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInviteDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleInviteMember}
            disabled={!newMemberEmail || actionLoading}
            startIcon={actionLoading ? <CircularProgress size={16} /> : null}
          >
            {actionLoading ? 'Sending...' : 'Send Invite'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Invitation Code Dialog */}
      <Dialog 
        open={codeDialogOpen} 
        onClose={() => setCodeDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }
        }}
      >
        <DialogTitle sx={{ color: 'white', pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon />
            <Typography variant="h6" component="span">
              Invitation Created!
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Box sx={{ 
            bgcolor: 'rgba(255, 255, 255, 0.95)', 
            p: 3, 
            borderRadius: 2,
            textAlign: 'center'
          }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Share this code with your team member:
            </Typography>
            
            <Box sx={{ 
              bgcolor: '#f5f5f5', 
              p: 2, 
              borderRadius: 1, 
              mb: 3,
              border: '2px dashed #667eea'
            }}>
              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 700, 
                  letterSpacing: 4,
                  fontFamily: 'monospace',
                  color: '#667eea'
                }}
              >
                {invitationCode}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column' }}>
              <Button
                variant="contained"
                fullWidth
                startIcon={codeCopied ? <CheckCircleIcon /> : <CopyIcon />}
                onClick={handleCopyCode}
                sx={{ 
                  bgcolor: codeCopied ? '#4caf50' : '#667eea',
                  '&:hover': { bgcolor: codeCopied ? '#45a049' : '#5568d3' }
                }}
              >
                {codeCopied ? 'Copied!' : 'Copy Code'}
              </Button>
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<WhatsAppIcon />}
                  onClick={handleShareWhatsApp}
                  sx={{ 
                    borderColor: '#25D366',
                    color: '#25D366',
                    '&:hover': { 
                      borderColor: '#25D366',
                      bgcolor: 'rgba(37, 211, 102, 0.1)'
                    }
                  }}
                >
                  WhatsApp
                </Button>
                
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<EmailIcon />}
                  onClick={handleShareEmail}
                  sx={{ 
                    borderColor: '#667eea',
                    color: '#667eea',
                    '&:hover': { 
                      borderColor: '#667eea',
                      bgcolor: 'rgba(102, 126, 234, 0.1)'
                    }
                  }}
                >
                  Email
                </Button>
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button 
            onClick={() => setCodeDialogOpen(false)}
            sx={{ color: 'white' }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AgencyTeamManagement;
