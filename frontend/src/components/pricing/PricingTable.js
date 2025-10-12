import React, { useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  useMediaQuery,
  useTheme,
  Grid,
  Card,
  CardContent,
  CardActions,
  Tooltip,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import { CheckCircle, Clear, Info } from '@mui/icons-material';
import { formatLimit, isUnlimited, EVERY_PLAN_FEATURES } from '../../constants/plans';

const PricingTable = ({ plans, onPlanSelect, isYearly, setIsYearly }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const getPlanPrice = (plan) => {
    if (plan.price === 0) return 0;
    if (isYearly) {
      return Math.floor(plan.price * 12 * 0.8); // 20% discount
    }
    return plan.price;
  };

  const getPlanPeriod = (plan) => {
    if (plan.price === 0) return 'forever';
    return isYearly ? 'year' : 'month';
  };

  const getOriginalPrice = (plan) => {
    if (plan.price === 0 || !isYearly) return null;
    return plan.price * 12;
  };

  const formatSupportLevel = (support) => {
    const supportMap = {
      'community': 'Community',
      'email': 'Email',
      'priority': 'Priority',
      'dedicated': 'Dedicated'
    };
    return supportMap[support] || support;
  };

  const renderFeatureValue = (value, type = 'default') => {
    if (type === 'boolean') {
      return value ? (
        <CheckCircle sx={{ color: '#86EFAC', fontSize: 20 }} />
      ) : (
        <Clear sx={{ color: '#9CA3AF', fontSize: 20 }} />
      );
    }
    
    if (type === 'support') {
      return formatSupportLevel(value);
    }
    
    return formatLimit(value);
  };

  // Reusable tooltip content for "What's included"
  const renderFeaturesTooltip = () => (
    <Box sx={{ p: 2, maxWidth: 400 }}>
      <Typography variant="h6" sx={{ 
        color: '#F9FAFB',
        fontWeight: 700,
        mb: 2
      }}>
        ✅ Every Plan Includes:
      </Typography>
      <List dense sx={{ p: 0 }}>
        {EVERY_PLAN_FEATURES.map((feature, index) => (
          <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
            <ListItemIcon sx={{ minWidth: 20 }}>
              <CheckCircle sx={{ 
                color: '#86EFAC', 
                fontSize: 16 
              }} />
            </ListItemIcon>
            <ListItemText
              primary={feature}
              primaryTypographyProps={{
                sx: {
                  color: '#F9FAFB',
                  fontSize: '0.85rem',
                  lineHeight: 1.4
                }
              }}
            />
          </ListItem>
        ))}
      </List>
      <Typography variant="body2" sx={{ 
        color: '#E5E7EB',
        mt: 2,
        fontSize: '0.8rem',
        fontStyle: 'italic'
      }}>
        💡 All plans include access to our 9 proprietary AdCopySurge tools
      </Typography>
    </Box>
  );

  // Mobile card view
  if (isMobile) {
    return (
      <Box sx={{ mt: 4 }}>
        {/* Pricing Toggle */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          mb: 6,
          gap: 2
        }}>
          <ToggleButtonGroup
            value={isYearly ? 'yearly' : 'monthly'}
            exclusive
            onChange={(event, newValue) => {
              if (newValue !== null) {
                setIsYearly(newValue === 'yearly');
              }
            }}
            sx={{
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              border: '2px solid rgba(192, 132, 252, 0.3)',
              borderRadius: 3,
              backdropFilter: 'blur(10px)',
              '& .MuiToggleButton-root': {
                border: 'none',
                color: '#E5E7EB',
                fontWeight: 600,
                fontSize: '1rem',
                px: 4,
                py: 1.5,
                '&.Mui-selected': {
                  backgroundColor: 'rgba(192, 132, 252, 0.8)',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'rgba(192, 132, 252, 0.9)',
                  }
                },
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                }
              }
            }}
          >
            <ToggleButton value="monthly">
              Monthly
            </ToggleButton>
            <ToggleButton value="yearly">
              Yearly
              <Chip
                label="Save 20%"
                size="small"
                sx={{
                  ml: 1,
                  backgroundColor: '#10b981',
                  color: 'white',
                  fontWeight: 700,
                  fontSize: '0.7rem',
                  height: '20px',
                  '& .MuiChip-label': {
                    px: 1
                  }
                }}
              />
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <Grid container spacing={3}>
          {plans.map((plan, index) => {
            const price = getPlanPrice(plan);
            const period = getPlanPeriod(plan);
            const originalPrice = getOriginalPrice(plan);

            return (
              <Grid item xs={12} sm={6} key={plan.id}>
                <Card 
                  sx={{
                    background: plan.popular 
                      ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(192, 132, 252, 0.05) 100%)'
                      : 'rgba(255, 255, 255, 0.05)',
                    backdropFilter: 'blur(10px)',
                    border: plan.popular 
                      ? '2px solid #C084FC' 
                      : '1px solid rgba(192, 132, 252, 0.2)',
                    borderRadius: 4,
                    position: 'relative',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transform: plan.popular ? 'scale(1.02)' : 'scale(1)',
                    transition: 'all 0.3s ease'
                  }}
                >
                  {plan.popular && (
                    <Chip
                      label="✨ Most Popular"
                      sx={{
                        position: 'absolute',
                        top: -12,
                        left: '50%',
                        transform: 'translateX(-50%)',
                        background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                        color: 'white',
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        boxShadow: '0 4px 15px rgba(251, 191, 36, 0.3)'
                      }}
                    />
                  )}

                  <CardContent sx={{ flexGrow: 1, p: 3 }}>
                    <Box sx={{ textAlign: 'center', mb: 2 }}>
                      <Typography variant="h5" sx={{ 
                        fontWeight: 700, 
                        color: '#F9FAFB',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 1
                      }}>
                        {plan.name}
                        <Tooltip
                          title={renderFeaturesTooltip()}
                          arrow
                          placement="top"
                          PopperProps={{
                            sx: {
                              '& .MuiTooltip-tooltip': {
                                background: 'linear-gradient(135deg, #1f2937 0%, #374151 100%)',
                                border: '1px solid rgba(192, 132, 252, 0.3)',
                                borderRadius: 2,
                                boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
                              },
                              '& .MuiTooltip-arrow': {
                                color: '#1f2937'
                              }
                            }
                          }}
                        >
                          <IconButton 
                            size="small" 
                            sx={{ 
                              color: '#C084FC',
                              '&:hover': { color: '#E5E7EB' }
                            }}
                          >
                            <Info fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Typography>
                    </Box>

                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                      {originalPrice && (
                        <Typography variant="body2" sx={{ 
                          color: '#9CA3AF',
                          textDecoration: 'line-through',
                          fontSize: '1.1rem',
                          mb: 0.5
                        }}>
                          ${originalPrice}/{period}
                        </Typography>
                      )}
                      <Typography variant="h2" sx={{ 
                        fontWeight: 800, 
                        color: plan.popular ? '#F9FAFB' : '#C084FC',
                        fontSize: '2.5rem',
                        lineHeight: 1
                      }}>
                        ${price}
                      </Typography>
                      <Typography variant="body1" sx={{ 
                        color: '#E5E7EB',
                        fontWeight: 600,
                        fontSize: '1.1rem'
                      }}>
                        /{period}
                        {isYearly && plan.price > 0 && (
                          <Chip
                            label="20% OFF"
                            size="small"
                            sx={{
                              ml: 1,
                              backgroundColor: '#10b981',
                              color: 'white',
                              fontWeight: 700,
                              fontSize: '0.65rem',
                              height: '18px'
                            }}
                          />
                        )}
                      </Typography>
                    </Box>

                    <Typography variant="body2" sx={{ 
                      color: '#E5E7EB',
                      textAlign: 'center',
                      mb: 3,
                      minHeight: '3rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      {plan.description}
                    </Typography>

                    {/* Plan Features */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" sx={{ color: '#F9FAFB', mb: 2, fontSize: '1rem' }}>
                        Plan Features:
                      </Typography>
                      
                      <Box sx={{ 
                        display: 'grid', 
                        gridTemplateColumns: '1fr 1fr',
                        gap: 2,
                        fontSize: '0.85rem'
                      }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography sx={{ color: '#E5E7EB' }}>Ad Analyses</Typography>
                          <Typography sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                            {formatLimit(plan.limits.adAnalyses)}
                          </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography sx={{ color: '#E5E7EB' }}>Team Members</Typography>
                          <Typography sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                            {formatLimit(plan.limits.teamMembers)}
                          </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography sx={{ color: '#E5E7EB' }}>Psychology</Typography>
                          {renderFeatureValue(plan.limits.psychologyAnalysis, 'boolean')}
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography sx={{ color: '#E5E7EB' }}>Reports</Typography>
                          <Typography sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                            {formatLimit(plan.limits.reports)}
                          </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography sx={{ color: '#E5E7EB' }}>White-label</Typography>
                          {renderFeatureValue(plan.limits.whiteLabel, 'boolean')}
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography sx={{ color: '#E5E7EB' }}>Integrations</Typography>
                          {renderFeatureValue(plan.limits.integrations, 'boolean')}
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography sx={{ color: '#E5E7EB' }}>API Access</Typography>
                          {renderFeatureValue(plan.limits.apiAccess, 'boolean')}
                        </Box>
                      </Box>
                      
                      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                        <Typography sx={{ color: '#E5E7EB', fontSize: '0.85rem' }}>
                          Support: <span style={{ color: '#F9FAFB', fontWeight: 600 }}>
                            {formatSupportLevel(plan.limits.support)}
                          </span>
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>

                  <CardActions sx={{ p: 3, pt: 0 }}>
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={() => onPlanSelect(plan)}
                      sx={{
                        background: plan.popular 
                          ? 'linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.3) 100%)' 
                          : 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%)',
                        color: 'white',
                        fontWeight: 700,
                        py: 2,
                        fontSize: '1rem',
                        textTransform: 'none',
                        borderRadius: 3,
                        boxShadow: plan.popular 
                          ? '0 8px 25px rgba(255,255,255,0.2)' 
                          : '0 8px 25px rgba(168, 85, 247, 0.3)',
                        border: plan.popular ? '2px solid rgba(255,255,255,0.3)' : 'none',
                        '&:hover': {
                          background: plan.popular 
                            ? 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.4) 100%)' 
                            : 'linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #a855f7 100%)',
                          transform: 'translateY(-2px)',
                          boxShadow: plan.popular 
                            ? '0 12px 35px rgba(255,255,255,0.3)' 
                            : '0 12px 35px rgba(168, 85, 247, 0.4)'
                        },
                        transition: 'all 0.3s ease'
                      }}
                    >
                      {plan.cta}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    );
  }

  // Desktop table view
  return (
    <Box sx={{ mt: 4 }}>
      {/* Pricing Toggle */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        mb: 6,
        gap: 2
      }}>
        <ToggleButtonGroup
          value={isYearly ? 'yearly' : 'monthly'}
          exclusive
          onChange={(event, newValue) => {
            if (newValue !== null) {
              setIsYearly(newValue === 'yearly');
            }
          }}
          sx={{
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            border: '2px solid rgba(192, 132, 252, 0.3)',
            borderRadius: 3,
            backdropFilter: 'blur(10px)',
            '& .MuiToggleButton-root': {
              border: 'none',
              color: '#E5E7EB',
              fontWeight: 600,
              fontSize: '1rem',
              px: 4,
              py: 1.5,
              '&.Mui-selected': {
                backgroundColor: 'rgba(192, 132, 252, 0.8)',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(192, 132, 252, 0.9)',
                }
              },
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }
          }}
        >
          <ToggleButton value="monthly">
            Monthly
          </ToggleButton>
          <ToggleButton value="yearly">
            Yearly
            <Chip
              label="Save 20%"
              size="small"
              sx={{
                ml: 1,
                backgroundColor: '#10b981',
                color: 'white',
                fontWeight: 700,
                fontSize: '0.7rem',
                height: '20px',
                '& .MuiChip-label': {
                  px: 1
                }
              }}
            />
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <TableContainer 
        component={Paper}
        sx={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          borderRadius: 4,
          border: '1px solid rgba(192, 132, 252, 0.2)',
          boxShadow: '0 10px 40px rgba(168, 85, 247, 0.1)',
          overflow: 'hidden'
        }}
      >
        <Table>
          <TableHead>
            <TableRow sx={{ 
              background: 'rgba(124, 58, 237, 0.2)',
              '& .MuiTableCell-root': {
                borderBottom: '2px solid rgba(192, 132, 252, 0.3)',
                color: '#F9FAFB',
                fontWeight: 700,
                fontSize: '1.1rem',
                py: 3
              }
            }}>
              <TableCell sx={{ color: '#F9FAFB !important', width: '200px' }}>
                Features
              </TableCell>
              {plans.map((plan) => {
                const price = getPlanPrice(plan);
                const period = getPlanPeriod(plan);
                const originalPrice = getOriginalPrice(plan);
                
                return (
                  <TableCell 
                    key={plan.id} 
                    align="center"
                    sx={{ 
                      color: '#F9FAFB !important',
                      position: 'relative',
                      backgroundColor: plan.popular ? 'rgba(192, 132, 252, 0.1)' : 'transparent'
                    }}
                  >
                    {plan.popular && (
                      <Chip
                        label="Most Popular"
                        size="small"
                        sx={{
                          position: 'absolute',
                          top: 8,
                          left: '50%',
                          transform: 'translateX(-50%)',
                          background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                          color: 'white',
                          fontWeight: 700,
                          fontSize: '0.65rem',
                          height: '20px'
                        }}
                      />
                    )}
                    <Box sx={{ mt: plan.popular ? 3 : 0 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 800 }}>
                          {plan.name}
                        </Typography>
                        <Tooltip
                          title={renderFeaturesTooltip()}
                          arrow
                          placement="top"
                          PopperProps={{
                            sx: {
                              '& .MuiTooltip-tooltip': {
                                background: 'linear-gradient(135deg, #1f2937 0%, #374151 100%)',
                                border: '1px solid rgba(192, 132, 252, 0.3)',
                                borderRadius: 2,
                                boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
                              },
                              '& .MuiTooltip-arrow': {
                                color: '#1f2937'
                              }
                            }
                          }}
                        >
                          <IconButton 
                            size="small" 
                            sx={{ 
                              color: '#C084FC',
                              '&:hover': { color: '#E5E7EB' },
                              p: 0.5
                            }}
                          >
                            <Info fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      {originalPrice && (
                        <Typography variant="body2" sx={{ 
                          color: '#9CA3AF',
                          textDecoration: 'line-through',
                          fontSize: '0.9rem'
                        }}>
                          ${originalPrice}/{period}
                        </Typography>
                      )}
                      <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
                        ${price}
                      </Typography>
                      <Typography variant="body2">
                        /{period}
                        {isYearly && plan.price > 0 && (
                          <Chip
                            label="20% OFF"
                            size="small"
                            sx={{
                              ml: 1,
                              backgroundColor: '#10b981',
                              color: 'white',
                              fontWeight: 700,
                              fontSize: '0.6rem',
                              height: '16px'
                            }}
                          />
                        )}
                      </Typography>
                    </Box>
                  </TableCell>
                );
              })}
            </TableRow>
          </TableHead>
          <TableBody>
            {/* Ad Analyses Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: '1px solid rgba(255, 255, 255, 0.1)', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                Ad Analyses / Month
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center" sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                  {formatLimit(plan.limits.adAnalyses)}
                </TableCell>
              ))}
            </TableRow>

            {/* Team Members Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: '1px solid rgba(255, 255, 255, 0.1)', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                Team Members
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center" sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                  {formatLimit(plan.limits.teamMembers)}
                </TableCell>
              ))}
            </TableRow>

            {/* Psychology Analysis Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: '1px solid rgba(255, 255, 255, 0.1)', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                15-Point Psychology Analysis
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center">
                  {renderFeatureValue(plan.limits.psychologyAnalysis, 'boolean')}
                </TableCell>
              ))}
            </TableRow>

            {/* Reports Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: '1px solid rgba(255, 255, 255, 0.1)', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                Reports / Month
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center" sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                  {formatLimit(plan.limits.reports)}
                </TableCell>
              ))}
            </TableRow>

            {/* White-Label Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: '1px solid rgba(255, 255, 255, 0.1)', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                White-Label Branding
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center">
                  {renderFeatureValue(plan.limits.whiteLabel, 'boolean')}
                </TableCell>
              ))}
            </TableRow>

            {/* Integrations Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: '1px solid rgba(255, 255, 255, 0.1)', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                Integrations (5000+ tools)
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center">
                  {renderFeatureValue(plan.limits.integrations, 'boolean')}
                </TableCell>
              ))}
            </TableRow>

            {/* Support Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: '1px solid rgba(255, 255, 255, 0.1)', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                Support Level
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center" sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                  {renderFeatureValue(plan.limits.support, 'support')}
                </TableCell>
              ))}
            </TableRow>

            {/* API Access Row */}
            <TableRow sx={{ '& .MuiTableCell-root': { borderBottom: 'none', py: 2 } }}>
              <TableCell sx={{ color: '#F9FAFB', fontWeight: 600 }}>
                API Access
              </TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center">
                  {renderFeatureValue(plan.limits.apiAccess, 'boolean')}
                </TableCell>
              ))}
            </TableRow>

            {/* CTA Row */}
            <TableRow sx={{ 
              background: 'rgba(124, 58, 237, 0.1)',
              '& .MuiTableCell-root': { 
                borderBottom: 'none', 
                py: 3,
                borderTop: '2px solid rgba(192, 132, 252, 0.3)'
              } 
            }}>
              <TableCell></TableCell>
              {plans.map((plan) => (
                <TableCell key={plan.id} align="center">
                  <Button
                    variant="contained"
                    onClick={() => onPlanSelect(plan)}
                    sx={{
                      background: plan.popular 
                        ? 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.9) 100%)' 
                        : 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%)',
                      color: plan.popular ? '#7c3aed' : 'white',
                      fontWeight: 700,
                      py: 1.5,
                      px: 3,
                      fontSize: '0.9rem',
                      textTransform: 'none',
                      borderRadius: 3,
                      minWidth: '140px',
                      boxShadow: plan.popular 
                        ? '0 8px 25px rgba(255,255,255,0.2)' 
                        : '0 8px 25px rgba(168, 85, 247, 0.3)',
                      border: plan.popular ? '2px solid rgba(124, 58, 237, 0.2)' : 'none',
                      '&:hover': {
                        background: plan.popular 
                          ? 'linear-gradient(135deg, rgba(250,247,255,0.9) 0%, rgba(243,232,255,0.9) 100%)' 
                          : 'linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #a855f7 100%)',
                        transform: 'translateY(-2px)',
                        boxShadow: plan.popular 
                          ? '0 12px 35px rgba(124, 58, 237, 0.2)' 
                          : '0 12px 35px rgba(168, 85, 247, 0.4)',
                        color: plan.popular ? '#6d28d9' : 'white'
                      },
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {plan.cta}
                  </Button>
                </TableCell>
              ))}
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PricingTable;