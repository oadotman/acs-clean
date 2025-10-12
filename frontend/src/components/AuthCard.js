import React from 'react';
import { Box, Container, Paper, Slide } from '@mui/material';
import { createGradientBackground } from '../utils/gradients';

const AuthCard = ({ 
  children, 
  maxWidth = 420, 
  slideDirection = 'up',
  timeout = 800,
  gradientName = 'authBackground' 
}) => {
  return (
    <Box
      data-auth-page
      sx={{
        ...createGradientBackground(gradientName),
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Container component="main" maxWidth="sm">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 3,
            position: 'relative',
            zIndex: 1,
          }}
        >
          <Slide direction={slideDirection} in timeout={timeout}>
            <Paper 
              elevation={8}
              sx={{ 
                padding: { xs: 3, sm: 4 }, 
                width: '100%',
                maxWidth: maxWidth,
                borderRadius: 3,
                bgcolor: '#ffffff',
                border: '1px solid rgba(0, 0, 0, 0.08)',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1), 0 4px 10px rgba(0, 0, 0, 0.05)',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 15px 35px rgba(0, 0, 0, 0.15), 0 6px 15px rgba(0, 0, 0, 0.08)',
                },
              }}
            >
              {children}
            </Paper>
          </Slide>
        </Box>
      </Container>
    </Box>
  );
};

export default AuthCard;
