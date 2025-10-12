// Domain verification and DNS setup service
export class DomainService {
  // Validate domain format
  static validateDomain(domain) {
    if (!domain) {
      return { isValid: false, errors: ['Domain is required'] };
    }

    const errors = [];
    
    // Remove protocol if present
    const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/\/$/, '');
    
    // Basic domain regex (allows subdomains)
    const domainRegex = /^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
    
    if (!domainRegex.test(cleanDomain)) {
      errors.push('Please enter a valid domain name (e.g., app.yourcompany.com)');
    }

    // Check for localhost or IP addresses
    if (cleanDomain.includes('localhost') || /^\d+\.\d+\.\d+\.\d+/.test(cleanDomain)) {
      errors.push('Please use a public domain name, not localhost or IP address');
    }

    // Length validation
    if (cleanDomain.length > 253) {
      errors.push('Domain name is too long');
    }

    // Check for valid TLD
    const parts = cleanDomain.split('.');
    if (parts.length < 2) {
      errors.push('Domain must have at least one dot (e.g., example.com)');
    }

    return {
      isValid: errors.length === 0,
      errors,
      cleanDomain: cleanDomain.toLowerCase()
    };
  }

  // Generate DNS records for domain setup
  static generateDNSRecords(domain, config = {}) {
    const {
      appId = 'adcopysurge-app',
      verificationToken = this.generateVerificationToken(),
      sslEnabled = true
    } = config;

    const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/\/$/, '');

    return {
      cname: {
        type: 'CNAME',
        name: cleanDomain,
        value: `${appId}.adcopysurge.com`,
        ttl: 300,
        description: 'Points your domain to AdCopySurge servers'
      },
      verification: {
        type: 'TXT',
        name: `_adcopysurge-verification.${cleanDomain}`,
        value: verificationToken,
        ttl: 300,
        description: 'Verifies domain ownership'
      },
      ssl: sslEnabled ? {
        type: 'CAA',
        name: cleanDomain,
        value: '0 issue "letsencrypt.org"',
        ttl: 300,
        description: 'Allows SSL certificate generation'
      } : null
    };
  }

  // Generate unique verification token
  static generateVerificationToken() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = 'adcopysurge-verify-';
    for (let i = 0; i < 32; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  // DNS verification with real-world considerations
  static async verifyDomainSetup(domain, verificationToken) {
    try {
      console.log(`🔍 Verifying DNS setup for ${domain} with token: ${verificationToken}`);
      
      // Simulate DNS lookup delay (real DNS lookups take time)
      await new Promise(resolve => setTimeout(resolve, 2000));

      const results = {
        cname: { configured: false, error: null, value: null },
        verification: { configured: false, error: null, token: null },
        ssl: { configured: false, error: null, certificate: null }
      };

      // Try to verify CNAME record
      try {
        // In production, this would use a DNS lookup service
        // For now, we simulate based on domain characteristics
        const isValidDomain = this.validateDomain(domain).isValid;
        
        if (isValidDomain) {
          // Simulate CNAME check - in production, use DNS over HTTPS or backend DNS query
          results.cname = {
            configured: true,
            value: 'adcopysurge-app.adcopysurge.com',
            checkedAt: new Date().toISOString()
          };
        } else {
          results.cname = {
            configured: false,
            error: 'Invalid domain format',
            checkedAt: new Date().toISOString()
          };
        }
      } catch (error) {
        results.cname = {
          configured: false,
          error: 'DNS lookup failed',
          details: error.message
        };
      }

      // Try to verify TXT record
      try {
        // In production, this would query for the specific TXT record
        // For demo purposes, we'll assume it's configured if CNAME is working
        if (results.cname.configured) {
          results.verification = {
            configured: true,
            token: verificationToken,
            checkedAt: new Date().toISOString()
          };
        } else {
          results.verification = {
            configured: false,
            error: 'TXT record not found or CNAME not configured',
            expectedToken: verificationToken
          };
        }
      } catch (error) {
        results.verification = {
          configured: false,
          error: 'TXT record verification failed',
          details: error.message
        };
      }

      // Check SSL availability
      try {
        if (results.cname.configured && results.verification.configured) {
          results.ssl = {
            configured: true,
            certificate: 'pending_generation',
            issuer: "Let's Encrypt",
            estimatedTime: '5-15 minutes'
          };
        } else {
          results.ssl = {
            configured: false,
            error: 'SSL requires both CNAME and verification records to be configured'
          };
        }
      } catch (error) {
        results.ssl = {
          configured: false,
          error: 'SSL check failed',
          details: error.message
        };
      }

      // Determine overall success
      const allConfigured = results.cname.configured && results.verification.configured;
      const errors = [];
      
      if (!results.cname.configured) {
        errors.push(`CNAME record issue: ${results.cname.error}`);
      }
      if (!results.verification.configured) {
        errors.push(`TXT record issue: ${results.verification.error}`);
      }
      if (!results.ssl.configured && allConfigured) {
        errors.push(`SSL issue: ${results.ssl.error}`);
      }

      const response = {
        success: allConfigured,
        status: allConfigured ? 'verified' : (results.cname.configured ? 'partial' : 'failed'),
        message: allConfigured 
          ? 'Domain successfully verified and configured' 
          : 'Domain verification incomplete',
        details: results,
        errors: errors.length > 0 ? errors : undefined,
        verifiedAt: new Date().toISOString(),
        nextSteps: allConfigured ? [
          'DNS propagation may take up to 48 hours worldwide',
          'SSL certificate will be generated automatically',
          'You can start using your custom domain once propagation completes'
        ] : [
          'Please add the required DNS records to your domain provider',
          'Allow 5-30 minutes for DNS changes to take effect',
          'Run verification again after making DNS changes'
        ]
      };

      console.log('🔍 DNS verification results:', response);
      return response;
      
    } catch (error) {
      console.error('Domain verification error:', error);
      return {
        success: false,
        status: 'error',
        message: 'Failed to verify domain setup due to technical error',
        error: error.message,
        details: {
          cname: { configured: false, error: 'Verification failed' },
          verification: { configured: false, error: 'Verification failed' },
          ssl: { configured: false, error: 'Verification failed' }
        }
      };
    }
  }

  // Get domain setup instructions
  static getDomainInstructions(domain, dnsRecords) {
    return {
      overview: `To use ${domain} as your white-label domain, you need to configure DNS records with your domain provider.`,
      steps: [
        {
          step: 1,
          title: 'Access your domain DNS settings',
          description: 'Log in to your domain registrar or DNS provider (e.g., GoDaddy, Namecheap, Cloudflare).',
          details: 'Look for "DNS Management", "DNS Records", or "Zone Editor" in your control panel.'
        },
        {
          step: 2,
          title: 'Add CNAME record',
          description: 'Create a CNAME record to point your domain to our servers.',
          details: {
            type: 'CNAME',
            name: domain,
            value: dnsRecords.cname.value,
            ttl: '5 minutes (300 seconds)'
          }
        },
        {
          step: 3,
          title: 'Add verification TXT record',
          description: 'Add a TXT record to verify domain ownership.',
          details: {
            type: 'TXT',
            name: dnsRecords.verification.name,
            value: dnsRecords.verification.value,
            ttl: '5 minutes (300 seconds)'
          }
        },
        {
          step: 4,
          title: 'Optional: Add CAA record for SSL',
          description: 'Add a CAA record to allow automatic SSL certificate generation.',
          details: dnsRecords.ssl ? {
            type: 'CAA',
            name: domain,
            value: dnsRecords.ssl.value,
            ttl: '5 minutes (300 seconds)'
          } : null
        },
        {
          step: 5,
          title: 'Wait for DNS propagation',
          description: 'DNS changes can take 5 minutes to 48 hours to propagate worldwide.',
          details: 'You can use tools like DNS Checker to monitor propagation status.'
        }
      ],
      troubleshooting: [
        {
          issue: 'DNS changes not taking effect',
          solution: 'DNS propagation can take up to 48 hours. Try clearing your DNS cache or checking from a different network.'
        },
        {
          issue: 'CNAME conflicts with existing records',
          solution: 'Remove any existing A or AAAA records for the same subdomain before adding the CNAME record.'
        },
        {
          issue: 'Verification failing',
          solution: 'Double-check that the TXT record name and value are exactly as shown, including any underscores or hyphens.'
        }
      ],
      estimatedTime: '5-30 minutes (plus DNS propagation time)',
      supportContact: 'support@adcopysurge.com'
    };
  }

  // Check DNS propagation status
  static async checkPropagationStatus(domain) {
    try {
      // Mock propagation check
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const regions = ['US East', 'US West', 'Europe', 'Asia', 'Australia'];
      const results = regions.map(region => ({
        region,
        status: Math.random() > 0.3 ? 'propagated' : 'pending',
        lastCheck: new Date().toISOString()
      }));

      const propagatedCount = results.filter(r => r.status === 'propagated').length;
      const totalRegions = results.length;

      return {
        domain,
        overall: propagatedCount === totalRegions ? 'complete' : 'partial',
        percentage: Math.round((propagatedCount / totalRegions) * 100),
        regions: results,
        checkedAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('Propagation check error:', error);
      return {
        domain,
        overall: 'error',
        error: error.message,
        checkedAt: new Date().toISOString()
      };
    }
  }

  // Generate SSL certificate (mock)
  static async generateSSLCertificate(domain) {
    try {
      // Simulate SSL certificate generation
      await new Promise(resolve => setTimeout(resolve, 3000));

      return {
        success: true,
        domain,
        certificate: {
          issued: new Date().toISOString(),
          expires: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(), // 90 days
          issuer: "Let's Encrypt",
          status: 'active'
        },
        message: 'SSL certificate successfully generated and installed'
      };
    } catch (error) {
      console.error('SSL generation error:', error);
      return {
        success: false,
        error: error.message,
        message: 'Failed to generate SSL certificate'
      };
    }
  }

  // Validate subdomain availability
  static async checkSubdomainAvailability(subdomain) {
    try {
      // Mock availability check
      await new Promise(resolve => setTimeout(resolve, 500));

      // Simulate some taken subdomains
      const takenSubdomains = ['app', 'www', 'admin', 'api', 'mail', 'test'];
      const isAvailable = !takenSubdomains.includes(subdomain.toLowerCase());

      return {
        subdomain,
        available: isAvailable,
        suggestions: isAvailable ? [] : [
          `${subdomain}app`,
          `${subdomain}portal`,
          `my${subdomain}`,
          `${subdomain}2024`
        ],
        checkedAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('Subdomain check error:', error);
      return {
        subdomain,
        available: false,
        error: error.message
      };
    }
  }
}

// Utility functions
export const extractDomainParts = (domain) => {
  const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/\/$/, '');
  const parts = cleanDomain.split('.');
  
  if (parts.length < 2) return null;
  
  return {
    subdomain: parts.length > 2 ? parts.slice(0, -2).join('.') : null,
    domain: parts.slice(-2).join('.'),
    tld: parts[parts.length - 1],
    full: cleanDomain
  };
};

export const formatDomainForDisplay = (domain) => {
  return domain.replace(/^https?:\/\//, '').replace(/\/$/, '');
};

export const isDomainValid = (domain) => {
  const validation = DomainService.validateDomain(domain);
  return validation.isValid;
};

export default DomainService;