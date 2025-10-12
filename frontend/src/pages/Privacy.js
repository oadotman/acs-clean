import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Divider,
  Alert
} from '@mui/material';
import { Security, Shield } from '@mui/icons-material';

const Privacy = () => {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Container maxWidth="md" sx={{ py: 8 }}>
        {/* Header */}
        <Box textAlign="center" sx={{ mb: 6 }}>
          <Shield sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h2" component="h1" sx={{ fontWeight: 800, mb: 2 }}>
            Privacy Policy
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Last updated: September 8, 2025
          </Typography>
        </Box>

        {/* Privacy Commitment Alert */}
        <Alert severity="info" sx={{ mb: 6 }}>
          <Typography variant="body1">
            <strong>Our Commitment:</strong> We are committed to protecting your privacy and maintaining the security of your data. 
            This policy explains how we collect, use, and safeguard your information.
          </Typography>
        </Alert>

        <Paper elevation={1} sx={{ p: 4 }}>
          {/* Introduction */}
          <Typography variant="body1" sx={{ mb: 4, fontSize: '1.1rem', lineHeight: 1.7 }}>
            This Privacy Policy describes how AdCopySurge Inc. ("we," "us," or "our") collects, uses, and shares 
            information about you when you use our AdCopySurge platform and services.
          </Typography>

          <Typography variant="body1" sx={{ mb: 4, fontSize: '1.1rem', lineHeight: 1.7 }}>
            We are committed to transparency about our data practices and your rights regarding your personal information. 
            This policy complies with applicable data protection laws, including GDPR and CCPA.
          </Typography>

          <Divider sx={{ my: 4 }} />

          {/* Section 1 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            1. Information We Collect
          </Typography>

          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Information You Provide
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 3 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Account information (name, email, password)</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Company information and marketing preferences</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Payment information (processed securely by third-party processors)</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Ad campaign data you upload for analysis</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Communications with our support team</Typography></li>
          </Box>

          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Information We Automatically Collect
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 4 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Usage data and platform interactions</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Device information (browser type, operating system)</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>IP address and general location information</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Cookies and similar tracking technologies</Typography></li>
          </Box>

          {/* Section 2 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            2. How We Use Your Information
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
            We use the information we collect to:
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 4 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Provide and improve our marketing intelligence services</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Analyze your ad campaigns and provide optimization recommendations</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Communicate with you about your account and our services</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Process payments and maintain billing records</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Improve our platform through usage analytics</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>Comply with legal obligations and protect our rights</Typography></li>
          </Box>

          {/* Section 3 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            3. Information Sharing and Disclosure
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
            We do not sell your personal information. We may share your information in the following circumstances:
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 4 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}>With service providers who help us operate our platform (hosting, payment processing, analytics)</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>When required by law or to protect our rights and safety</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>In connection with a business transfer or acquisition</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}>With your consent or at your direction</Typography></li>
          </Box>

          {/* Section 4 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            4. Data Security and Protection
          </Typography>
          <Box sx={{ mb: 4 }}>
            <Alert severity="success" sx={{ mb: 3 }}>
              <Security sx={{ mr: 1 }} />
              <strong>Enterprise-Grade Security:</strong> We implement industry-standard security measures including encryption, 
              secure data centers, and regular security audits.
            </Alert>
            <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
              We protect your information through:
            </Typography>
            <Box component="ul" sx={{ pl: 3 }}>
              <li><Typography variant="body1" sx={{ mb: 1 }}>SSL/TLS encryption for data in transit</Typography></li>
              <li><Typography variant="body1" sx={{ mb: 1 }}>AES-256 encryption for data at rest</Typography></li>
              <li><Typography variant="body1" sx={{ mb: 1 }}>Regular security assessments and penetration testing</Typography></li>
              <li><Typography variant="body1" sx={{ mb: 1 }}>Access controls and employee security training</Typography></li>
              <li><Typography variant="body1" sx={{ mb: 1 }}>SOC 2 Type II compliance (in progress)</Typography></li>
            </Box>
          </Box>

          {/* Section 5 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            5. Your Rights and Choices
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
            Depending on your location, you may have the following rights:
          </Typography>
          <Box component="ul" sx={{ pl: 3, mb: 4 }}>
            <li><Typography variant="body1" sx={{ mb: 1 }}><strong>Access:</strong> Request copies of your personal information</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}><strong>Correction:</strong> Request correction of inaccurate information</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}><strong>Deletion:</strong> Request deletion of your personal information</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}><strong>Portability:</strong> Request transfer of your data in a portable format</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}><strong>Opt-out:</strong> Unsubscribe from marketing communications</Typography></li>
            <li><Typography variant="body1" sx={{ mb: 1 }}><strong>Restrict processing:</strong> Request limitation of data processing</Typography></li>
          </Box>

          {/* Section 6 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            6. Cookies and Tracking Technologies
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            We use cookies and similar technologies to enhance your experience, analyze usage patterns, and provide personalized content. 
            You can control cookie preferences through your browser settings. Essential cookies required for platform functionality 
            cannot be disabled without affecting service performance.
          </Typography>

          {/* Section 7 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            7. Data Retention
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            We retain your personal information for as long as necessary to provide our services and comply with legal obligations. 
            Account data is typically retained for the duration of your subscription plus 30 days. Campaign data is retained for 
            up to 2 years to enable historical analysis and reporting. You can request deletion of your data at any time.
          </Typography>

          {/* Section 8 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            8. International Data Transfers
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            Our services are operated from servers located in secure data centers. If you are located outside of our primary 
            operating jurisdiction, your information may be transferred to and processed in countries with different data protection 
            laws. We ensure appropriate safeguards are in place for international transfers.
          </Typography>

          {/* Section 9 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            9. Children's Privacy
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            Our services are not intended for individuals under 18 years of age. We do not knowingly collect personal information 
            from children. If we become aware that we have collected information from a child, we will take steps to delete such information.
          </Typography>

          {/* Section 10 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            10. Changes to This Privacy Policy
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.7 }}>
            We may update this Privacy Policy from time to time to reflect changes in our practices or applicable law. 
            We will notify you of significant changes by email or through our platform. The updated policy will be effective 
            when posted with a new "last updated" date.
          </Typography>

          {/* Section 11 */}
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
            11. Contact Us
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
            If you have questions about this Privacy Policy or wish to exercise your rights, please contact us:
          </Typography>
          <Box sx={{ pl: 2, mb: 4 }}>
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>Email:</strong> privacy@adcopysurge.com
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>Address:</strong> AdCopySurge Inc.
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              123 Market Street, Suite 400, San Francisco, CA 94105, USA
            </Typography>
            <Typography variant="body1">
              <strong>Data Protection Officer:</strong> dpo@adcopysurge.com
            </Typography>
          </Box>

          <Divider sx={{ my: 4 }} />

          {/* Compliance Badges */}
          <Box textAlign="center" sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Compliance & Certifications
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>GDPR</Typography>
                <Typography variant="caption">Compliant</Typography>
              </Box>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>CCPA</Typography>
                <Typography variant="caption">Compliant</Typography>
              </Box>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>SOC 2</Typography>
                <Typography variant="caption">In Progress</Typography>
              </Box>
            </Box>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
            Your privacy is important to us. We are committed to protecting your personal information and being transparent about our data practices.
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default Privacy;
