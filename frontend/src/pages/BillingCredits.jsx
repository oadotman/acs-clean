import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  AccountBalanceWallet,
  CreditCard,
  History,
  TrendingUp,
  Add,
  Download,
  Info,
  CheckCircle,
  AccessTime,
  Receipt,
  Settings,
  Star
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import useCredits from '../hooks/useCredits';
import useFeatureAccess from '../hooks/useFeatureAccess';
import { CREDIT_COSTS, getCreditHistory, formatCredits } from '../utils/creditSystem';
import { PRICING_PLANS } from '../constants/plans';
import toast from 'react-hot-toast';

const BillingCredits = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [creditHistory, setCreditHistory] = useState([]);
  const [buyCreditsDialog, setBuyCreditsDialog] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const { 
    credits, 
    monthlyAllowance, 
    totalUsed,
    bonusCredits,
    loading: creditsLoading,
    error: creditsError,
    getFormattedCredits,
    getCreditStatusColor,
    getCreditPercentage,
    getDaysUntilReset,
    refreshCredits
  } = useCredits();

  const { userTier, subscription } = useFeatureAccess();

  // Check URL params for initial tab
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tab = params.get('tab');
    
    if (tab === 'credits') {
      setActiveTab(0);
    } else if (tab === 'billing') {
      setActiveTab(1);
    } else if (tab === 'history') {
      setActiveTab(2);
    }
  }, [location.search]);

  // Load credit history
  useEffect(() => {
    const loadHistory = async () => {
      if (activeTab === 2) {
        setLoadingHistory(true);
        try {
          const history = await getCreditHistory();
          setCreditHistory(history);
        } catch (error) {
          console.error('Error loading credit history:', error);
          toast.error('Failed to load credit history');
        } finally {
          setLoadingHistory(false);
        }
      }
    };
    loadHistory();
  }, [activeTab]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    
    // Update URL
    const params = new URLSearchParams();
    if (newValue === 0) params.set('tab', 'credits');
    else if (newValue === 1) params.set('tab', 'billing');
    else if (newValue === 2) params.set('tab', 'history');
    
    navigate(`/billing?${params.toString()}`, { replace: true });
  };

  const handleBuyCredits = (amount, price) => {
    // This would integrate with your payment processor
    toast.success(`Would purchase ${amount} credits for $${price}`);
    setBuyCreditsDialog(false);
  };

  const handleUpgradePlan = () => {
    navigate('/pricing');
  };

  const creditPackages = [
    { credits: 50, price: 9.99, popular: false },
    { credits: 150, price: 24.99, popular: true, bonus: 25 },
    { credits: 300, price: 44.99, popular: false, bonus: 75 },
    { credits: 750, price: 99.99, popular: false, bonus: 250 }
  ];

  const currentPlan = PRICING_PLANS.find(plan => plan.tier === userTier);
  // Check if user has unlimited tier - use both tier check and credit value
  const isUnlimited = userTier === 'agency_unlimited' || 
                     subscription?.subscription_tier === 'agency_unlimited' ||
                     credits === 'unlimited' || 
                     credits >= 999999 ||
                     monthlyAllowance >= 999999;
  
  console.log('📊 BillingCredits - isUnlimited check:', {
    userTier,
    subscriptionTier: subscription?.subscription_tier,
    credits,
    monthlyAllowance,
    isUnlimited
  });
  
  const creditColor = getCreditStatusColor();
  const percentage = getCreditPercentage();

  const renderCreditsTab = () => (
    <Grid container spacing={3}>
      {/* Current Credits Card - Hidden for unlimited users */}
      {!isUnlimited && (
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="between" mb={3}>
              <Box>
                <Typography variant="h5" fontWeight="bold" gutterBottom>
                  Credit Balance
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Track your available credits and usage
                </Typography>
              </Box>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Box textAlign="center" p={2} 
                  sx={{ 
                    border: '2px solid',
                    borderColor: `${creditColor}.main`,
                    borderRadius: 2,
                    backgroundColor: `${creditColor}.50`
                  }}
                >
                  <AccountBalanceWallet sx={{ 
                    fontSize: 48, 
                    color: `${creditColor}.main`, 
                    mb: 1 
                  }} />
                  <Typography variant="h4" fontWeight="bold" color={`${creditColor}.main`}>
                    {getFormattedCredits()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Available Credits
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Box p={2}>
                  <Typography variant="h6" gutterBottom>
                    Monthly Allowance
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" gutterBottom>
                    {formatCredits(monthlyAllowance)}
                  </Typography>
                  
                  {!isUnlimited && monthlyAllowance > 0 && (
                    <>
                      <LinearProgress
                        variant="determinate"
                        value={100 - percentage}
                        color={creditColor}
                        sx={{ height: 8, borderRadius: 4, mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {(100 - percentage).toFixed(0)}% remaining • Resets in {getDaysUntilReset()} days
                      </Typography>
                    </>
                  )}
                  
                  {isUnlimited && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      <Typography variant="body2" fontWeight="bold">
                        ✨ Unlimited Plan Active
                      </Typography>
                      <Typography variant="caption">
                        You have unlimited credits - analyze as much as you want!
                      </Typography>
                    </Alert>
                  )}
                </Box>
              </Grid>
            </Grid>

            {bonusCredits > 0 && (
              <Alert severity="success" sx={{ mt: 2 }}>
                <strong>Bonus Credits:</strong> You have {formatCredits(bonusCredits)} bonus credits from upgrades and promotions!
              </Alert>
            )}
          </CardContent>
        </Card>
      </Grid>
      )}

      {/* Unlimited Plan Message */}
      {isUnlimited && (
        <Grid item xs={12}>
          <Card>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Star sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold" gutterBottom color="success.main">
                ✨ Unlimited Credits Active
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                You're on the Agency Unlimited plan with unlimited credits.
                <br />
                Analyze as many ads as you want - no limits, no restrictions!
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Your plan renews automatically each month.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      )}

      {/* Credit Costs Reference */}
      <Grid item xs={12} md={isUnlimited ? 12 : 4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Credit Costs
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              How many credits each operation uses
            </Typography>
            
            <List dense>
              {Object.entries(CREDIT_COSTS).map(([operation, cost]) => (
                <ListItem key={operation} sx={{ py: 0.5, px: 0 }}>
                  <ListItemText 
                    primary={operation.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                  <Chip 
                    label={`${cost} credit${cost !== 1 ? 's' : ''}`} 
                    size="small" 
                    variant="outlined"
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Buy Credits Section */}
      {!isUnlimited && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Buy Additional Credits
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Purchase extra credits to supplement your monthly allowance
              </Typography>

              <Grid container spacing={2}>
                {creditPackages.map((pkg, index) => (
                  <Grid item xs={12} sm={6} md={3} key={index}>
                    <Card 
                      variant="outlined" 
                      sx={{ 
                        position: 'relative',
                        ...(pkg.popular && {
                          border: '2px solid',
                          borderColor: 'primary.main',
                          transform: 'scale(1.02)'
                        })
                      }}
                    >
                      {pkg.popular && (
                        <Chip
                          label="Popular"
                          color="primary"
                          size="small"
                          sx={{
                            position: 'absolute',
                            top: -8,
                            left: '50%',
                            transform: 'translateX(-50%)'
                          }}
                        />
                      )}
                      <CardContent sx={{ textAlign: 'center', py: 3 }}>
                        <Typography variant="h4" fontWeight="bold" color="primary">
                          {pkg.credits}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Credits
                        </Typography>
                        {pkg.bonus && (
                          <Typography variant="body2" color="success.main" sx={{ mb: 1 }}>
                            + {pkg.bonus} bonus credits
                          </Typography>
                        )}
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                          ${pkg.price}
                        </Typography>
                        <Button
                          variant={pkg.popular ? "contained" : "outlined"}
                          fullWidth
                          onClick={() => handleBuyCredits(pkg.credits + (pkg.bonus || 0), pkg.price)}
                        >
                          Purchase
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );

  const renderBillingTab = () => (
    <Grid container spacing={3}>
      {/* Current Plan */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Plan
            </Typography>
            
            <Box display="flex" alignItems="center" gap={2} mb={3}>
              <Star sx={{ color: 'primary.main', fontSize: 32 }} />
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  {currentPlan?.name || 'Free Plan'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {currentPlan?.description || 'Basic features included'}
                </Typography>
              </Box>
            </Box>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Monthly Credits
                </Typography>
                <Typography variant="h6" fontWeight="bold">
                  {formatCredits(monthlyAllowance)}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Monthly Price
                </Typography>
                <Typography variant="h6" fontWeight="bold">
                  ${currentPlan?.price || 0}
                </Typography>
              </Grid>
            </Grid>

            <Button 
              variant="contained" 
              onClick={handleUpgradePlan}
              startIcon={<TrendingUp />}
            >
              {currentPlan?.tier === 'free' ? 'Upgrade Plan' : 'Change Plan'}
            </Button>
          </CardContent>
        </Card>
      </Grid>

      {/* Billing History */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Billing History
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Recent transactions and invoices
            </Typography>

            <Alert severity="info">
              <Typography variant="body2">
                No billing history available. Upgrade to a paid plan to see invoices and payment history.
              </Typography>
            </Alert>

            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Receipt />}
                disabled
              >
                Download Invoices
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderHistoryTab = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Credit Transaction History
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Track all your credit usage and additions
        </Typography>

        {loadingHistory ? (
          <Box display="flex" justifyContent="center" p={4}>
            <div>Loading transaction history...</div>
          </Box>
        ) : creditHistory.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Operation</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Description</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {creditHistory.map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell>
                      {format(new Date(transaction.created_at), 'MMM dd, yyyy HH:mm')}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={transaction.operation.replace(/_/g, ' ')}
                        size="small"
                        color={transaction.amount > 0 ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography
                        color={transaction.amount > 0 ? 'success.main' : 'text.secondary'}
                        fontWeight="bold"
                      >
                        {transaction.amount > 0 ? '+' : ''}{transaction.amount}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {transaction.description}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Alert severity="info">
            <Typography variant="body2">
              No credit transactions yet. Start using the platform to see your usage history here.
            </Typography>
          </Alert>
        )}
      </CardContent>
    </Card>
  );

  // Handle credit loading and error states
  const handleRetryCredits = async () => {
    console.log('🔄 Retrying credit fetch...');
    await refreshCredits();
  };

  if (creditsLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={2} py={8}>
          <Typography variant="h5" gutterBottom>
            Loading your credit information...
          </Typography>
          <LinearProgress sx={{ width: '50%' }} />
        </Box>
      </Container>
    );
  }

  if (creditsError) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={handleRetryCredits}>
              Retry
            </Button>
          }
          sx={{ mb: 3 }}
        >
          <Typography variant="body1" fontWeight="bold">
            Failed to load credit information
          </Typography>
          <Typography variant="body2">
            {creditsError}
          </Typography>
        </Alert>
        
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Unable to display billing information
            </Typography>
            <Button 
              variant="contained" 
              onClick={handleRetryCredits}
              sx={{ mt: 2 }}
            >
              Reload Credits
            </Button>
          </CardContent>
        </Card>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Billing & Credits
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage your credits, billing, and subscription
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab 
            icon={<AccountBalanceWallet />} 
            label="Credits" 
            iconPosition="start"
          />
          <Tab 
            icon={<CreditCard />} 
            label="Billing" 
            iconPosition="start"
          />
          <Tab 
            icon={<History />} 
            label="History" 
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      <Box sx={{ py: 3 }}>
        {activeTab === 0 && renderCreditsTab()}
        {activeTab === 1 && renderBillingTab()}
        {activeTab === 2 && renderHistoryTab()}
      </Box>
    </Container>
  );
};

export default BillingCredits;