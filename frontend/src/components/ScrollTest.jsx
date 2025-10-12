import React, { useRef } from 'react';
import { Box, Button, Typography, Paper } from '@mui/material';

const ScrollTest = () => {
  const targetRef = useRef(null);

  const handleScroll = () => {
    console.log('Scroll button clicked');
    console.log('targetRef.current:', targetRef.current);

    if (targetRef.current) {
      console.log('Attempting to scroll...');
      
      // Method 1: scrollIntoView
      try {
        targetRef.current.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
          inline: 'nearest'
        });
        console.log('scrollIntoView executed successfully');
      } catch (error) {
        console.error('scrollIntoView failed:', error);
        
        // Method 2: window.scrollTo fallback
        try {
          const rect = targetRef.current.getBoundingClientRect();
          const scrollTop = window.pageYOffset + rect.top - 100;
          window.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
          });
          console.log('window.scrollTo fallback executed');
        } catch (fallbackError) {
          console.error('window.scrollTo fallback also failed:', fallbackError);
        }
      }
    } else {
      console.error('targetRef.current is null');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Scroll Functionality Test
      </Typography>
      
      <Button 
        variant="contained" 
        onClick={handleScroll}
        sx={{ mb: 4 }}
      >
        Click to Scroll to Target
      </Button>

      {/* Spacer content */}
      <Box sx={{ height: '150vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Scroll down to see the target...
        </Typography>
      </Box>

      {/* Target element */}
      <Paper 
        ref={targetRef}
        sx={{ 
          p: 4, 
          bgcolor: 'primary.light', 
          border: '3px solid',
          borderColor: 'primary.main',
          textAlign: 'center'
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.dark' }}>
          🎯 TARGET ELEMENT
        </Typography>
        <Typography variant="body1" sx={{ mt: 2 }}>
          If auto-scroll works, you should have smoothly scrolled to this element.
        </Typography>
      </Paper>

      {/* More spacer content */}
      <Box sx={{ height: '50vh' }}>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 4 }}>
          End of test page
        </Typography>
      </Box>
    </Box>
  );
};

export default ScrollTest;