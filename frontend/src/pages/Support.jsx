import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Stack,
  Link,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Email as EmailIcon,
  ContentCopy as CopyIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import toast from 'react-hot-toast';

const Support = () => {
  const [copied, setCopied] = useState(false);
  const supportEmail = 'support@adcopysurge.com';

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(supportEmail);
    setCopied(true);
    toast.success('Email address copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleEmailClick = () => {
    window.location.href = `mailto:${supportEmail}`;
  };

  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
          Get Support
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Need help? We're here for you.
        </Typography>
      </Box>

      <Card elevation={3}>
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={4} alignItems="center">
            {/* Email Icon */}
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                bgcolor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2
              }}
            >
              <EmailIcon sx={{ fontSize: 40, color: 'white' }} />
            </Box>

            {/* Contact Information */}
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Email Support
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Send us an email and we'll get back to you as soon as possible
              </Typography>

              {/* Email Address with Copy Button */}
              <Box
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 1,
                  bgcolor: 'action.hover',
                  px: 3,
                  py: 1.5,
                  borderRadius: 2,
                  mb: 3
                }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    fontFamily: 'monospace',
                    fontWeight: 600,
                    color: 'primary.main'
                  }}
                >
                  {supportEmail}
                </Typography>
                <Tooltip title={copied ? 'Copied!' : 'Copy email address'}>
                  <IconButton
                    size="small"
                    onClick={handleCopyEmail}
                    color={copied ? 'success' : 'default'}
                  >
                    {copied ? <CheckIcon /> : <CopyIcon />}
                  </IconButton>
                </Tooltip>
              </Box>

              {/* Open Email Client Button */}
              <Button
                variant="contained"
                size="large"
                startIcon={<EmailIcon />}
                onClick={handleEmailClick}
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600
                }}
              >
                Open Email Client
              </Button>
            </Box>

            {/* Additional Information */}
            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Typography variant="body2" color="text.secondary">
                Typical response time: Within 24 hours
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                For urgent issues, please include "URGENT" in your subject line
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* Additional Resources */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Before contacting support, you might want to check our{' '}
          <Link href="/docs" color="primary" sx={{ fontWeight: 600 }}>
            documentation
          </Link>
          {' '}or{' '}
          <Link href="/faq" color="primary" sx={{ fontWeight: 600 }}>
            FAQ
          </Link>
        </Typography>
      </Box>
    </Container>
  );
};

export default Support;
