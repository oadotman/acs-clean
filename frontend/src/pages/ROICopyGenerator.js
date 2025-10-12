import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
  TextField,
  Slider,
  Chip,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { ErrorMessage } from '../components/ui';
import CopyInputForm from '../components/shared/CopyInputForm';

const ROICopyGenerator = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  const { control, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      headline: '',
      body_text: '',
      cta: '',
      platform: 'facebook',
      industry: '',
      target_audience: '',
      product_price: '',
      cost_per_unit: '',
      target_margin: 50,
      customer_lifetime_value: '',
      conversion_goal: 'sales'
    }
  });

  const targetMargin = watch('target_margin');
  const productPrice = watch('product_price');
  const costPerUnit = watch('cost_per_unit');

  const calculatedProfit = productPrice && costPerUnit 
    ? (productPrice - costPerUnit) 
    : 0;

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await apiService.generateROICopy(data);
      setResults(response);
      toast.success('ROI-optimized copy generated! 💰');
    } catch (error) {
      console.error('ROI copy generation failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Copy generation failed';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      {/* Header Section */}
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          mb: 3,
          background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
          color: 'white',
          textAlign: 'center'
        }}
      >
        <Typography 
          variant="h3" 
          gutterBottom 
          sx={{ 
            fontWeight: 800,
            mb: 2,
            letterSpacing: '-0.02em'
          }}
        >
          💰 ROI-Driven Copy Generator
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            opacity: 0.9,
            fontWeight: 400,
            maxWidth: 600,
            mx: 'auto'
          }}
        >
          Generate ad copy optimized for profit margins and conversions. 
          Target high-value customers with premium positioning.
        </Typography>
      </Paper>

      {/* Form Section */}
      <Paper sx={{ p: 4, mb: results ? 3 : 0 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={4}>
            {/* Financial Settings */}
            <Grid item xs={12}>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 3, 
                  backgroundColor: 'rgba(245, 158, 11, 0.05)',
                  border: '1px solid rgba(245, 158, 11, 0.2)'
                }}
              >
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 600,
                    color: 'warning.main',
                    mb: 3,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}
                >
                  💵 Financial Parameters
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="product_price"
                      control={control}
                      rules={{ required: 'Product price is required' }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          label="Product Price ($)"
                          fullWidth
                          required
                          type="number"
                          inputProps={{ min: 0, step: 0.01 }}
                          error={!!errors.product_price}
                          helperText={errors.product_price?.message}
                          placeholder="99.99"
                        />
                      )}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="cost_per_unit"
                      control={control}
                      rules={{ required: 'Cost per unit is required' }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          label="Cost per Unit ($)"
                          fullWidth
                          required
                          type="number"
                          inputProps={{ min: 0, step: 0.01 }}
                          error={!!errors.cost_per_unit}
                          helperText={errors.cost_per_unit?.message}
                          placeholder="29.99"
                        />
                      )}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="customer_lifetime_value"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          label="Customer Lifetime Value ($)"
                          fullWidth
                          type="number"
                          inputProps={{ min: 0, step: 0.01 }}
                          placeholder="500"
                          helperText="Expected total revenue per customer"
                        />
                      )}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box>
                      <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
                        Target Profit Margin: {targetMargin}%
                      </Typography>
                      <Controller
                        name="target_margin"
                        control={control}
                        render={({ field }) => (
                          <Slider
                            {...field}
                            min={10}
                            max={80}
                            step={5}
                            valueLabelDisplay="auto"
                            valueLabelFormat={(value) => `${value}%`}
                            sx={{ color: 'warning.main' }}
                          />
                        )}
                      />
                    </Box>
                  </Grid>
                </Grid>
                
                {/* Profit Calculation Display */}
                {calculatedProfit > 0 && (
                  <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(16, 185, 129, 0.1)', borderRadius: 2 }}>
                    <Typography variant="h6" sx={{ color: 'success.main', fontWeight: 600 }}>
                      💎 Calculated Profit: ${calculatedProfit.toFixed(2)} per sale
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Profit Margin: {productPrice ? ((calculatedProfit / productPrice) * 100).toFixed(1) : 0}%
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>

            {/* Ad Content Input */}
            <Grid item xs={12}>
              <CopyInputForm
                control={control}
                errors={errors}
                title="📝 Base Copy (Optional)"
                subtitle="Provide existing copy to optimize, or leave blank for new generation"
              />
            </Grid>

            {/* Submit Button */}
            <Grid item xs={12}>
              <Box display="flex" justifyContent="center" mt={2}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ 
                    minWidth: 280,
                    py: 2,
                    px: 4,
                    fontSize: '1.1rem',
                    fontWeight: 700,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
                      transform: 'translateY(-2px)',
                    }
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 2, color: 'white' }} />
                      💰 Generating ROI Copy...
                    </>
                  ) : (
                    <>
                      🚀 Generate ROI-Optimized Copy
                    </>
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {/* Results Section */}
      {results && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
            💎 ROI-Optimized Copy Variations
          </Typography>
          
          {results.variations && results.variations.map((variation, index) => (
            <Card key={index} sx={{ mb: 3, border: '2px solid', borderColor: 'warning.light' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {variation.strategy_type}
                  </Typography>
                  <Chip 
                    label={`ROI Score: ${variation.roi_score}/100`} 
                    color="warning"
                    variant="filled"
                  />
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, mb: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        HEADLINE
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {variation.headline}
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, mb: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        BODY TEXT
                      </Typography>
                      <Typography variant="body1">
                        {variation.body_text}
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        CALL-TO-ACTION
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {variation.cta}
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ p: 2, bgcolor: 'rgba(245, 158, 11, 0.1)', borderRadius: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        PRICING STRATEGY
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600, color: 'warning.main' }}>
                        {variation.pricing_angle}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="body2" color="textSecondary">
                  <strong>Why this works:</strong> {variation.roi_explanation}
                </Typography>
              </CardContent>
            </Card>
          ))}
          
          {/* ROI Insights */}
          {results.roi_insights && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                💡 ROI Optimization Insights
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'rgba(245, 158, 11, 0.05)' }}>
                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                  {results.roi_insights.map((insight, index) => (
                    <li key={index}>
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        {insight}
                      </Typography>
                    </li>
                  ))}
                </ul>
              </Paper>
            </Box>
          )}
        </Paper>
      )}
      
      {/* Error Display */}
      {error && (
        <Box sx={{ mt: 2 }}>
          <ErrorMessage
            variant="inline"
            title="ROI Copy Generation Failed"
            message={error.message}
            error={error}
            onRetry={() => setError(null)}
            showActions={false}
          />
        </Box>
      )}
    </Container>
  );
};

export default ROICopyGenerator;
