import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Divider
} from '@mui/material';
import { Gavel } from '@mui/icons-material';

const Terms = () => {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Container maxWidth="md" sx={{ py: 8 }}>
        {/* Header */}
        <Box textAlign="center" sx={{ mb: 6 }}>
          <Gavel sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h2" component="h1" sx={{ fontWeight: 800, mb: 2 }}>
            Terms of Service
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Last updated: September 8, 2025
          </Typography>
        </Box>

        <Paper elevation={1} sx={{ p: 4 }}>
          {/* Introduction */}
          <Typography variant="body1" sx={{ mb: 4, fontSize: '1.1rem', lineHeight: 1.7 }}>
            Welcome to AdCopySurge. These Terms of Service ("Terms") govern your use of our marketing intelligence platform 
            and services provided by AdCopySurge Inc. ("Company", "we", "us", or "our").
          </Typography>

          <Typography variant="body1" sx={{ mb: 4, fontSize: '1.1rem', lineHeight: 1.7 }}>
            By accessing or using AdCopySurge, you agree to be bound by these Terms. If you disagree with any part of these terms, 
            then you may not access the service.
          </Typography>

          <Divider sx={{ my: 4 }} />

          {/* Section 1 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            1. Acceptance of Terms
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            By creating an account or using our services, you confirm that you are at least 18 years old and have the legal capacity 
            to enter into this agreement. If you are using our services on behalf of a company or organization, you represent and 
            warrant that you have the authority to bind that entity to these Terms.
          </Typography>

          {/* Section 2 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            2. Description of Service
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
            AdCopySurge provides a marketing intelligence platform that includes:
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 4 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Ad copy analysis and scoring tools</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Compliance checking for multiple advertising platforms</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>ROI optimization and copy generation tools</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>A/B testing and psychology scoring capabilities</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Performance analytics and reporting features</Typography></li>
          </Box>

          {/* Section 3 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            3. User Accounts and Responsibilities
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
            To access certain features of our service, you must create an account. You agree to:
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 4 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Provide accurate and complete information when creating your account</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Maintain the security of your login credentials</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Notify us immediately of any unauthorized use of your account</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Use the service only for lawful purposes and in compliance with applicable laws</Typography></li>
          </Box>

          {/* Section 4 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            4. Subscription and Payment Terms
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            Our service offers both free and paid subscription tiers. Paid subscriptions are billed monthly or annually as selected. 
            All fees are non-refundable except as required by law or as explicitly stated in our refund policy. We reserve the right 
            to change our pricing with 30 days' notice to existing subscribers.
          </Typography>

          {/* Section 5 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            5. Intellectual Property Rights
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            The AdCopySurge platform, including all content, features, and functionality, is owned by AdCopySurge Inc. 
            and is protected by copyright, trademark, and other intellectual property laws. You retain ownership of your campaign data 
            and content, but grant us a limited license to process and analyze it to provide our services.
          </Typography>

          {/* Section 6 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            6. Data Privacy and Security
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            We take data privacy seriously and are committed to protecting your information. Our data practices are governed by our 
            Privacy Policy, which is incorporated into these Terms by reference. We implement industry-standard security measures 
            to protect your data and comply with applicable data protection regulations including GDPR and CCPA.
          </Typography>

          {/* Section 7 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            7. Prohibited Uses
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
            You may not use our service to:
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 4 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Create, promote, or distribute illegal, harmful, or offensive content</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Violate any applicable laws or regulations</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Attempt to gain unauthorized access to our systems or user accounts</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Use automated means to access the service without permission</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Interfere with or disrupt the service or servers</Typography></li>
          </Box>

          {/* Section 8 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            8. Service Availability and Modifications
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            We strive to maintain high service availability but cannot guarantee uninterrupted access. We may modify, suspend, 
            or discontinue any part of our service at any time with reasonable notice. We will make reasonable efforts to provide 
            advance notice of significant changes that may affect your use of the service.
          </Typography>

          {/* Section 9 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            9. Limitation of Liability
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, ADCOPYSURGE INC. SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, 
            SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, 
            OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES RESULTING FROM YOUR USE OF THE SERVICE.
          </Typography>

          {/* Section 10 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            10. Termination
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            Either party may terminate this agreement at any time. Upon termination, your access to the service will cease, 
            and we may delete your account and data in accordance with our data retention policies. Sections of these Terms 
            that by their nature should survive termination will remain in effect.
          </Typography>

          {/* Section 11 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            11. Changes to Terms
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            We may update these Terms from time to time. We will notify users of significant changes by email or through the service. 
            Your continued use of the service after such modifications constitutes acceptance of the updated Terms.
          </Typography>

          {/* Section 12 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            12. Governing Law
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            These Terms are governed by and construed in accordance with the laws of the State of California, USA, without regard to its 
            conflict of law principles. Any disputes arising from these Terms or your use of the service will be resolved 
            through binding arbitration or in the courts of California, USA.
          </Typography>

          {/* Contact */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            13. Contact Information
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            If you have questions about these Terms, please contact us at:
          </Typography>
          <Box sx={{ pl: 2, mb: 4 }}>
            <Typography variant="body1" sx={{ mb: 1 }}>
              Email: legal@adcopysurge.com
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              Address: AdCopySurge Inc.
            </Typography>
            <Typography variant="body1">
              123 Market Street, Suite 400, San Francisco, CA 94105, USA
            </Typography>
          </Box>

          <Divider sx={{ my: 4 }} />

          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
            By using AdCopySurge, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default Terms;
