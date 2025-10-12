import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  IconButton,
  Switch,
  FormControlLabel,
  Divider,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Hub as IntegrationsIcon,
  Settings as SettingsIcon,
  Check as CheckIcon,
  Add as AddIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  Delete as DeleteIcon,
  Launch as LaunchIcon
} from '@mui/icons-material';
import { useAuth } from '../../services/authContext';
import IntegrationService from '../../services/integrationService';
import IntegrationSetupDialog from '../../components/integrations/IntegrationSetupDialog';
import toast from 'react-hot-toast';

const AgencyIntegrations = () => {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [userIntegrations, setUserIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [setupDialogOpen, setSetupDialogOpen] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [existingConfig, setExistingConfig] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [integrationToDelete, setIntegrationToDelete] = useState(null);
  const [searchInputRef, setSearchInputRef] = useState(null);

  // Get available integrations from service
  const availableIntegrations = Object.values(IntegrationService.AVAILABLE_INTEGRATIONS);

  // Available categories
  const categories = useMemo(() => {
    const cats = ['all', ...new Set(availableIntegrations.map(i => i.category))];
    return cats;
  }, []);

  // Combine available integrations with user's connected integrations
  const integrationsWithStatus = useMemo(() => {
    return availableIntegrations.map(integration => {
      const userIntegration = userIntegrations.find(ui => ui.integration_type === integration.id);
      return {
        ...integration,
        connected: !!userIntegration,
        userIntegration,
        lastSync: userIntegration?.last_used ? new Date(userIntegration.last_used).toLocaleString() : null,
        status: userIntegration?.status || integration.status
      };
    });
  }, [availableIntegrations, userIntegrations]);

  // Filter integrations based on search and category
  const filteredIntegrations = useMemo(() => {
    return integrationsWithStatus.filter(integration => {
      const matchesSearch = 
        integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        integration.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        integration.features?.some(feature => 
          feature.toLowerCase().includes(searchQuery.toLowerCase())
        );
      
      const matchesCategory = 
        selectedCategory === 'all' || integration.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }, [integrationsWithStatus, searchQuery, selectedCategory]);

  // Load user integrations on mount
  useEffect(() => {
    if (user) {
      loadUserIntegrations();
    }
  }, [user]);

  const loadUserIntegrations = async () => {
    try {
      setLoading(true);
      const integrations = await IntegrationService.getUserIntegrations(user.id);
      setUserIntegrations(integrations);
    } catch (error) {
      console.error('Failed to load integrations:', error);
      toast.error('Failed to load integrations. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  };

  // Keyboard shortcut for search (Ctrl/Cmd + K)
  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        searchInputRef?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [searchInputRef]);

  const handleClearSearch = () => {
    setSearchQuery('');
    searchInputRef?.focus();
  };

  const handleConnect = (integration) => {
    setSelectedIntegration(integration);
    setExistingConfig(null);
    setSetupDialogOpen(true);
  };

  const handleSettings = (integration) => {
    setSelectedIntegration(integration);
    setExistingConfig(integration.userIntegration);
    setSetupDialogOpen(true);
  };

  const handleToggle = async (integration, enabled) => {
    try {
      await IntegrationService.toggleIntegration(integration.userIntegration.id, enabled);
      await loadUserIntegrations();
      toast.success(`${integration.name} ${enabled ? 'enabled' : 'disabled'} successfully`);
    } catch (error) {
      console.error('Failed to toggle integration:', error);
      toast.error(`Failed to ${enabled ? 'enable' : 'disable'} ${integration.name}`);
    }
  };

  const handleDisconnect = (integration) => {
    setIntegrationToDelete(integration);
    setDeleteDialogOpen(true);
  };

  const confirmDisconnect = async () => {
    if (integrationToDelete) {
      try {
        await IntegrationService.disconnectIntegration(integrationToDelete.userIntegration.id);
        await loadUserIntegrations();
        setDeleteDialogOpen(false);
        setIntegrationToDelete(null);
        toast.success(`${integrationToDelete.name} disconnected successfully`);
      } catch (error) {
        console.error('Failed to disconnect integration:', error);
        toast.error(`Failed to disconnect ${integrationToDelete.name}`);
      }
    }
  };

  const handleSetupSuccess = async () => {
    setSetupDialogOpen(false);
    setSelectedIntegration(null);
    setExistingConfig(null);
    await loadUserIntegrations();
    toast.success('Integration configured successfully!');
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <IntegrationsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
            🤝 Integrations
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
          Connect AdCopySurge with your favorite tools and platforms to streamline your workflow and automate your ad analysis process.
        </Typography>
      </Box>

      {/* Search and Filter Controls */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <TextField
          placeholder="Search integrations... (Ctrl+K)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          inputRef={(ref) => setSearchInputRef(ref)}
          sx={{ minWidth: 280, flex: 1, maxWidth: 400 }}
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary', fontSize: '1.125rem' }} />
              </InputAdornment>
            ),
            endAdornment: searchQuery && (
              <InputAdornment position="end">
                <IconButton
                  size="small"
                  onClick={handleClearSearch}
                  aria-label="Clear search"
                >
                  <ClearIcon sx={{ fontSize: '1rem' }} />
                </IconButton>
              </InputAdornment>
            ),
            'aria-label': 'Search integrations by name, description, or features'
          }}
        />
        
        <FormControl sx={{ minWidth: 160 }} size="small">
          <InputLabel id="category-select-label">Category</InputLabel>
          <Select
            labelId="category-select-label"
            value={selectedCategory}
            label="Category"
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(cat => (
              <MenuItem key={cat} value={cat}>
                {cat === 'all' ? 'All Categories' : cat}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

      </Box>

      {/* Results Summary */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {loading ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={16} />
            <Typography variant="body2" color="text.secondary">
              Loading integrations...
            </Typography>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            {`${filteredIntegrations.length} of ${availableIntegrations.length} integrations`}
          </Typography>
        )}
        {(searchQuery || selectedCategory !== 'all') && (
          <Button
            variant="text"
            size="small"
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('all');
            }}
          >
            Clear filters
          </Button>
        )}
      </Box>

      {/* Integration Cards Grid */}
      {filteredIntegrations.length === 0 ? (
        <Box 
          sx={{ 
            textAlign: 'center', 
            py: 8, 
            px: 3,
            bgcolor: 'background.paper',
            borderRadius: 2,
            border: '1px dashed',
            borderColor: 'divider'
          }}
        >
          <IntegrationsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
            No integrations found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {searchQuery 
              ? `No integrations match "${searchQuery}"` 
              : 'No integrations match your selected filters'
            }
          </Typography>
          <Button 
            variant="outlined" 
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('all');
            }}
          >
            Clear all filters
          </Button>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredIntegrations.map((integration) => (
          <Grid item xs={12} md={6} lg={4} key={integration.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.15s ease-in-out',
                borderRadius: 1.5,
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: theme => theme.shadows[4]
                }
              }}
            >
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box
                    sx={{
                      fontSize: '2rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {integration.icon}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {integration.name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {integration.connected ? (
                        <Chip
                          label="Connected"
                          size="small"
                          color="success"
                          icon={<CheckIcon />}
                          aria-label="Integration is connected and active"
                        />
                      ) : integration.status === 'coming-soon' ? (
                        <Chip
                          label="Coming Soon"
                          size="small"
                          color="warning"
                          aria-label="Integration not yet available"
                        />
                      ) : (
                        <Chip
                          label="Available"
                          size="small"
                          variant="outlined"
                          aria-label="Integration available for connection"
                        />
                      )}
                    </Box>
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {integration.description}
                </Typography>
                
                {integration.features && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                      Features:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                      {integration.features.map((feature, index) => (
                        <Chip key={index} label={feature} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Box>
                )}
                
                {integration.connected && integration.lastSync && (
                  <Typography variant="caption" color="success.main" sx={{ mb: 2, display: 'block' }}>
                    ✓ Last sync: {integration.lastSync}
                  </Typography>
                )}

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {integration.connected ? (
                    <>
                      <FormControlLabel
                        control={<Switch 
                          checked={integration.userIntegration?.status === 'active'}
                          onChange={(e) => handleToggle(integration, e.target.checked)}
                          size="small" 
                        />}
                        label="Enabled"
                        sx={{ flex: 1 }}
                      />
                      <IconButton size="small" onClick={() => handleSettings(integration)}>
                        <SettingsIcon fontSize="small" />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDisconnect(integration)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </>
                  ) : integration.status === 'available' ? (
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      size="small"
                      fullWidth
                      onClick={() => handleConnect(integration)}
                    >
                      Connect
                    </Button>
                  ) : (
                    <Button
                      variant="outlined"
                      size="small"
                      fullWidth
                      disabled
                    >
                      Coming Soon
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          ))}
        </Grid>
      )}

      <Divider sx={{ my: 4 }} />

      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Need a Custom Integration?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 500, mx: 'auto' }}>
          Contact our team to discuss custom integrations for your agency's specific needs.
        </Typography>
        <Button variant="outlined" size="large">
          Contact Support
        </Button>
      </Box>

      {/* Integration Setup Dialog */}
      <IntegrationSetupDialog
        open={setupDialogOpen}
        onClose={() => setSetupDialogOpen(false)}
        integration={selectedIntegration}
        existingConfig={existingConfig}
        onSuccess={handleSetupSuccess}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Disconnect {integrationToDelete?.name}?
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to disconnect this integration? This will remove all associated configuration and stop data synchronization.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={confirmDisconnect} 
            color="error" 
            variant="contained"
          >
            Disconnect
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AgencyIntegrations;
