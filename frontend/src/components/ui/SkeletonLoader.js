import React from 'react';
import { 
  Box, 
  Skeleton, 
  Grid, 
  Card, 
  CardContent, 
  Paper,
  Container 
} from '@mui/material';

const SkeletonLoader = ({ 
  variant = 'dashboard', // 'dashboard', 'analysis', 'profile', 'list', 'card', 'form'
  count = 1,
  maxWidth = 'lg',
  sx = {}
}) => {
  const renderDashboardSkeleton = () => (
    <Container maxWidth={maxWidth} sx={{ mt: 4, mb: 4, ...sx }}>
      <Grid container spacing={3}>
        {/* Header Skeleton */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Skeleton variant="text" width="50%" height={40} />
            <Skeleton variant="text" width="70%" height={20} />
          </Paper>
        </Grid>
        
        {/* Stats Cards Skeleton */}
        {[1, 2, 3].map((index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card>
              <CardContent>
                <Skeleton variant="text" width="60%" height={24} />
                <Skeleton variant="text" width="40%" height={48} />
                <Skeleton variant="text" width="80%" height={16} />
                <Skeleton variant="rectangular" width="100%" height={6} sx={{ mt: 2, borderRadius: 3 }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
        
        {/* Content Section Skeleton */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width="30%" height={24} />
            {[1, 2, 3].map((index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Skeleton variant="text" width="90%" height={20} />
                <Skeleton variant="text" width="60%" height={16} />
              </Box>
            ))}
          </Paper>
        </Grid>
        
        {/* Sidebar Skeleton */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width="50%" height={24} />
            {[1, 2, 3].map((index) => (
              <Skeleton key={index} variant="rectangular" width="100%" height={36} sx={{ mb: 2 }} />
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );

  const renderAnalysisSkeleton = () => (
    <Container maxWidth={maxWidth} sx={{ py: 4, ...sx }}>
      <Skeleton variant="text" width="40%" height={48} sx={{ mb: 3 }} />
      <Grid container spacing={3}>
        {/* Original Ad Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Skeleton variant="text" width="30%" height={32} />
            <Skeleton variant="text" width="15%" height={24} sx={{ mb: 2 }} />
            <Skeleton variant="text" width="90%" height={32} />
            <Skeleton variant="text" width="100%" height={64} sx={{ mb: 2 }} />
            <Skeleton variant="text" width="40%" height={32} />
          </Paper>
        </Grid>
        
        {/* Scores Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width="30%" height={24} />
            <Grid container spacing={3} sx={{ mt: 2 }}>
              {[1, 2, 3, 4].map((index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Skeleton variant="text" width="60%" height={20} />
                  <Skeleton variant="rectangular" width="100%" height={8} sx={{ mt: 1, borderRadius: 4 }} />
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );

  const renderProfileSkeleton = () => (
    <Container maxWidth={maxWidth} sx={{ py: 4, ...sx }}>
      <Skeleton variant="text" width="20%" height={48} sx={{ mb: 3 }} />
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width="60%" height={24} sx={{ mb: 2 }} />
            {[1, 2, 3, 4].map((index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Skeleton variant="text" width="30%" height={16} />
                <Skeleton variant="text" width="70%" height={20} />
              </Box>
            ))}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width="50%" height={24} sx={{ mb: 2 }} />
            <Skeleton variant="text" width="40%" height={20} sx={{ mb: 1 }} />
            <Skeleton variant="rectangular" width="100%" height={8} sx={{ mb: 2, borderRadius: 4 }} />
            <Skeleton variant="text" width="60%" height={16} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );

  const renderListSkeleton = () => (
    <Box sx={sx}>
      {Array.from({ length: count }).map((_, index) => (
        <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
          <Skeleton variant="text" width="80%" height={20} />
          <Skeleton variant="text" width="60%" height={16} />
          <Skeleton variant="text" width="40%" height={16} />
        </Box>
      ))}
    </Box>
  );

  const renderCardSkeleton = () => (
    <Grid container spacing={2} sx={sx}>
      {Array.from({ length: count }).map((_, index) => (
        <Grid item xs={12} sm={6} md={4} key={index}>
          <Card>
            <CardContent>
              <Skeleton variant="text" width="70%" height={24} />
              <Skeleton variant="text" width="100%" height={20} />
              <Skeleton variant="text" width="90%" height={20} />
              <Skeleton variant="rectangular" width="100%" height={36} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  const renderFormSkeleton = () => (
    <Box sx={sx}>
      {Array.from({ length: count }).map((_, index) => (
        <Box key={index} sx={{ mb: 3 }}>
          <Skeleton variant="text" width="25%" height={20} sx={{ mb: 1 }} />
          <Skeleton variant="rectangular" width="100%" height={56} sx={{ borderRadius: 1 }} />
        </Box>
      ))}
    </Box>
  );

  switch (variant) {
    case 'dashboard':
      return renderDashboardSkeleton();
    case 'analysis':
      return renderAnalysisSkeleton();
    case 'profile':
      return renderProfileSkeleton();
    case 'list':
      return renderListSkeleton();
    case 'card':
      return renderCardSkeleton();
    case 'form':
      return renderFormSkeleton();
    default:
      return renderDashboardSkeleton();
  }
};

export default SkeletonLoader;
