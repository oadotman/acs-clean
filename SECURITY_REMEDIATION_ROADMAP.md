# AdCopySurge Security Remediation Roadmap
*Created: October 2025*

## Immediate Action Items (CRITICAL - Execute This Week)

### 1. Secret Rotation & Management (HIGH PRIORITY)

#### 🚨 IMMEDIATE ACTIONS (Next 24-48 Hours)

**Step 1: Rotate Exposed Supabase Keys**
```bash
# Access Supabase Dashboard
# 1. Go to https://app.supabase.com/project/{your-project}
# 2. Settings > API
# 3. Reset service_role key 
# 4. Reset JWT secret (requires database reset - plan carefully)

# Document current keys before rotation:
# - SUPABASE_SERVICE_ROLE_KEY (exposed in docker-compose.datalix.yml)
# - SUPABASE_JWT_SECRET (exposed in docker-compose.datalix.yml)
# - SUPABASE_ANON_KEY (exposed in .env.local)
```

**Step 2: Remove Secrets from Version Control**
```bash
# Remove exposed files from git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch docker-compose.datalix.yml .env.local' \
  --prune-empty --tag-name-filter cat -- --all

# Add to .gitignore immediately:
echo "docker-compose.datalix.yml" >> .gitignore
echo ".env.production" >> .gitignore
echo ".env.local" >> .gitignore

# Force push to remote (COORDINATE WITH TEAM FIRST)
git push origin --force --all
```

**Step 3: Implement Environment-Based Secret Management**
```bash
# Create secure environment variables on your VPS
sudo mkdir -p /etc/adcopysurge
sudo touch /etc/adcopysurge/production.env
sudo chmod 600 /etc/adcopysurge/production.env
sudo chown www-data:www-data /etc/adcopysurge/production.env

# Add to systemd service file
# Edit /etc/systemd/system/adcopysurge.service
EnvironmentFile=/etc/adcopysurge/production.env
```

### 2. Production Debug Mode Disable

**Backend Configuration Fix**
```python
# Update backend/app/core/config.py
# Add this validator to force production settings:

@validator('DEBUG', pre=True)
def force_production_debug_off(cls, v, values):
    environment = values.get('ENVIRONMENT', 'development')
    if environment == 'production':
        return False
    return v

# Add docs_url conditional
def create_app():
    app = FastAPI(
        title="AdCopySurge API",
        docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
        redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc"
    )
```

**Environment Variable Fix**
```bash
# Update production deployment scripts
export ENVIRONMENT=production
export DEBUG=false
export DOCS_ENABLED=false
```

### 3. Dependency Vulnerability Fixes

**Update requirements-production.txt**
```txt
# Fix identified vulnerabilities
pypdf2==3.0.1  # VULNERABLE - UPDATE TO 4.0.0+
anyio==3.7.1    # VULNERABLE - UPDATE TO 4.4.0+  
regex==2024.5.15 # VULNERABLE - UPDATE TO 2025.2.10+
ecdsa==0.19.1   # VULNERABLE - REPLACE WITH cryptography

# Replace with secure alternatives:
pypdf4==3.1.0  # or PyPDF4
anyio==4.4.0
regex==2025.2.10
# Remove ecdsa, use cryptography for signing operations
```

## Phase 1: Critical Security Fixes (Week 1-2)

### Authentication & Authorization Hardening

**1. Standardize Authentication Flow**
```python
# backend/app/auth/dependencies.py - Simplified secure version
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Standardized Supabase-only authentication"""
    try:
        # Use only Supabase JWT validation
        payload = supabase.auth.get_user(token)
        user = get_user_by_supabase_id(db, payload.user.id)
        
        if not user or not user.is_active:
            raise HTTPException(401, "Invalid or inactive user")
            
        return user
    except Exception:
        raise HTTPException(401, "Invalid authentication token")
```

**2. Implement Proper Session Management**
```python
# Add to backend/app/core/config.py
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)  # Reduce from 60
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)     # Reduce from 30

# Add session tracking
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    device_info = Column(String)
    ip_address = Column(String)
```

### Input Validation & Rate Limiting

**1. Implement Comprehensive Rate Limiting**
```python
# backend/app/middleware/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"]
)

# Add to main.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to sensitive endpoints
@router.post("/analyze")
@limiter.limit("10/minute")  # Strict limit on AI analysis
async def analyze_ad_copy(request: Request, ...):
    pass
```

**2. Enhanced Input Validation**
```python
# backend/app/models/requests.py
class AdAnalysisRequest(BaseModel):
    ad_text: str = Field(..., max_length=5000, min_length=10)
    platform: Literal["facebook", "google", "linkedin", "tiktok"]
    
    @validator('ad_text')
    def sanitize_ad_text(cls, v):
        # Remove potentially malicious content
        import bleach
        return bleach.clean(v, tags=[], strip=True)

# Add file upload validation
class FileUploadConfig:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.txt', '.doc', '.docx', '.pdf'}
    SCAN_FOR_MALWARE = True
```

### CSRF Protection Implementation

**Frontend (React)**
```javascript
// src/utils/csrf.js
import axios from 'axios';

// Configure axios with CSRF token handling
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

// Add request interceptor for CSRF
axios.interceptors.request.use(
  (config) => {
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (token) {
      config.headers['X-CSRF-TOKEN'] = token;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Backend (FastAPI)**
```python
# backend/app/middleware/csrf.py
from starlette.middleware.base import BaseHTTPMiddleware
import secrets

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            csrf_token = request.headers.get("X-CSRF-TOKEN")
            session_token = request.session.get("csrf_token")
            
            if not csrf_token or csrf_token != session_token:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token missing or invalid"}
                )
        
        response = await call_next(request)
        
        # Generate CSRF token for GET requests
        if request.method == "GET":
            token = secrets.token_urlsafe(32)
            request.session["csrf_token"] = token
            response.headers["X-CSRF-TOKEN"] = token
            
        return response
```

## Phase 2: Infrastructure Hardening (Week 3-4)

### Web Application Firewall (WAF) Implementation

**Nginx Security Configuration**
```nginx
# /etc/nginx/sites-available/adcopysurge-api
server {
    listen 443 ssl http2;
    server_name api.adcopysurge.com;

    # Enhanced security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.adcopysurge.com;" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Block suspicious requests
    location /api/auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        # Block common attack patterns
        if ($request_uri ~* "(union|select|insert|delete|update|drop|exec|script)") {
            return 403;
        }
        
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoring & Alerting Setup

**Security Logging Implementation**
```python
# backend/app/middleware/security_logging.py
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        handler = logging.FileHandler("/var/log/adcopysurge/security.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.WARNING)

    def log_failed_auth(self, ip: str, user_agent: str):
        self.logger.warning(json.dumps({
            "event": "failed_authentication",
            "ip": ip,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat()
        }))

    def log_suspicious_activity(self, ip: str, endpoint: str, details: dict):
        self.logger.error(json.dumps({
            "event": "suspicious_activity", 
            "ip": ip,
            "endpoint": endpoint,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }))
```

**Automated Alerting Setup**
```bash
# Install and configure fail2ban for automated response
sudo apt install fail2ban

# Create custom jail for API
cat > /etc/fail2ban/jail.d/adcopysurge.conf << 'EOF'
[adcopysurge-auth]
enabled = true
filter = adcopysurge-auth
logpath = /var/log/adcopysurge/security.log
maxretry = 5
findtime = 300
bantime = 3600
action = iptables-multiport[name=adcopysurge-auth, port="80,443", protocol=tcp]

[adcopysurge-suspicious]
enabled = true
filter = adcopysurge-suspicious
logpath = /var/log/adcopysurge/security.log
maxretry = 3
findtime = 600
bantime = 7200
EOF

# Create filters
cat > /etc/fail2ban/filter.d/adcopysurge-auth.conf << 'EOF'
[Definition]
failregex = ^.*"event": "failed_authentication".*"ip": "<HOST>".*$
ignoreregex =
EOF
```

## Phase 3: Advanced Security & Compliance (Week 5-8)

### Database Security Enhancements

**Row Level Security (RLS) Policies Review**
```sql
-- Audit existing RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public';

-- Enhanced user data isolation
CREATE POLICY "Users can only access own data" ON user_analyses
FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Admins can access all data" ON user_analyses 
FOR ALL USING (
  auth.jwt() ->> 'email' IN (
    SELECT email FROM admin_users
  )
);

-- Audit logging for sensitive operations
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $audit_trigger$
BEGIN
    INSERT INTO audit_log(
        table_name, operation, user_id, old_data, new_data, timestamp
    ) VALUES (
        TG_TABLE_NAME, TG_OP, auth.uid(), 
        row_to_json(OLD), row_to_json(NEW), NOW()
    );
    RETURN NULL;
END;
$audit_trigger$ LANGUAGE plpgsql;
```

### GDPR Compliance Implementation

**Data Processing Records**
```python
# backend/app/models/gdpr.py
class DataProcessingRecord(Base):
    __tablename__ = "data_processing_records"
    
    id = Column(String, primary_key=True)
    data_subject_id = Column(String, ForeignKey("users.id"))
    processing_purpose = Column(String)  # "ad_analysis", "billing", "support"
    legal_basis = Column(String)  # "consent", "contract", "legitimate_interest"
    data_categories = Column(JSON)  # ["personal", "usage", "content"]
    retention_period = Column(Integer)  # Days
    created_at = Column(DateTime, default=datetime.utcnow)
    
class DataSubjectRequest(Base):
    __tablename__ = "data_subject_requests"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    request_type = Column(String)  # "access", "portability", "erasure", "rectification"
    status = Column(String, default="pending")  # "pending", "in_progress", "completed"
    submitted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    response_data = Column(JSON)
```

**Automated DSR Processing**
```python
# backend/app/services/gdpr_service.py
class GDPRService:
    async def process_data_access_request(self, user_id: str):
        """Generate user data export (Article 15)"""
        user_data = {
            "profile": await self.get_user_profile(user_id),
            "analyses": await self.get_user_analyses(user_id),
            "billing": await self.get_billing_history(user_id),
            "usage_logs": await self.get_usage_logs(user_id)
        }
        
        # Create encrypted export
        export_data = json.dumps(user_data, indent=2)
        encrypted_data = self.encrypt_export(export_data)
        
        return {
            "export_file": encrypted_data,
            "generated_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30)
        }

    async def process_erasure_request(self, user_id: str):
        """Process right to be forgotten (Article 17)"""
        # Anonymize instead of delete for legal compliance
        await self.anonymize_user_data(user_id)
        await self.delete_non_essential_data(user_id)
        await self.log_erasure_completion(user_id)
```

### Secure CI/CD Pipeline Implementation

**GitHub Actions Security Workflow**
```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
          
      - name: Python Security Check
        run: |
          pip install safety bandit
          safety check -r backend/requirements-production.txt
          bandit -r backend/ -f json -o bandit-report.json
          
      - name: Node Security Check  
        run: |
          cd frontend
          npm audit --audit-level moderate
          
      - name: Secret Scanning
        run: |
          pip install detect-secrets
          detect-secrets scan --all-files --force-use-all-plugins
```

**Deployment Security Checks**
```bash
#!/bin/bash
# scripts/secure-deploy.sh

set -euo pipefail

echo "🔍 Pre-deployment security validation..."

# Check for secrets in code
if grep -r "SUPABASE_SERVICE_ROLE_KEY\|JWT_SECRET" . --exclude-dir=.git; then
    echo "❌ Found hardcoded secrets in code!"
    exit 1
fi

# Validate environment variables
if [ -z "${SECRET_KEY:-}" ] || [ -z "${DATABASE_URL:-}" ]; then
    echo "❌ Required environment variables not set!"
    exit 1
fi

# Check SSL certificate expiration
if ! openssl s_client -connect api.adcopysurge.com:443 -servername api.adcopysurge.com 2>/dev/null | \
   openssl x509 -noout -checkend 2592000; then
    echo "⚠️ SSL certificate expires within 30 days!"
fi

# Verify database connection with limited privileges
if ! python -c "
import os
import psycopg2
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute('SELECT current_user')
print('✅ Database connection verified')
"; then
    echo "❌ Database connection failed!"
    exit 1
fi

echo "✅ Security validation passed. Proceeding with deployment..."
```

## Testing & Validation Schedule

### Week 9-10: Security Testing

**Automated Security Testing**
```bash
# Install OWASP ZAP
docker pull owasp/zap2docker-stable

# Run automated security scan
docker run -t owasp/zap2docker-stable \
  zap-baseline.py -t https://api.adcopysurge.com/api \
  -J zap-report.json

# Run SQLmap for injection testing (on staging only)
sqlmap -u "https://staging-api.adcopysurge.com/api/ads/analyze" \
  --data="ad_text=test&platform=facebook" \
  --headers="Authorization: Bearer $TEST_TOKEN" \
  --batch --level=3
```

**Manual Penetration Testing Checklist**
- [ ] Authentication bypass attempts
- [ ] Authorization testing (horizontal/vertical privilege escalation)
- [ ] Input validation (XSS, SQLi, NoSQLi, command injection)
- [ ] Session management (fixation, hijacking, timeout)
- [ ] Business logic flaws
- [ ] API abuse (rate limiting, parameter pollution)
- [ ] File upload vulnerabilities
- [ ] Infrastructure testing (ports, services, configurations)

### Week 11-12: Compliance Audit

**GDPR Compliance Checklist**
- [ ] Data processing records complete
- [ ] Privacy policy updated with all processing activities
- [ ] Consent mechanisms implemented (where required)
- [ ] Data subject rights automated (access, portability, erasure)
- [ ] Breach notification procedures documented
- [ ] Data Protection Impact Assessment (DPIA) completed
- [ ] Data retention policies implemented
- [ ] Staff training on data protection completed

## Success Metrics & KPIs

### Security Metrics
- **Vulnerability Count**: Target < 5 medium/high severity vulnerabilities
- **Secret Exposure**: 0 hardcoded secrets in version control
- **Authentication**: 100% of endpoints protected with proper auth
- **Rate Limiting**: 100% of critical endpoints rate-limited
- **SSL Score**: A+ rating on SSL Labs test
- **Security Headers Score**: A rating on SecurityHeaders.com

### Compliance Metrics
- **DSR Response Time**: < 30 days (legal requirement)
- **Data Breach Detection**: < 72 hours (GDPR requirement)
- **Audit Trail Coverage**: 100% of sensitive operations logged
- **Backup Success Rate**: 100% with encryption
- **Incident Response Time**: < 2 hours for critical incidents

## Cost Breakdown

### Phase 1 (Weeks 1-2): $8,000
- Senior security engineer: 40 hours × $150/hour = $6,000
- Tools & licenses (Safety, Snyk, security tools): $500
- Emergency response time: $1,000
- SSL certificate renewal: $100
- Monitoring setup: $400

### Phase 2 (Weeks 3-4): $12,000
- Security engineer: 60 hours × $150/hour = $9,000
- WAF implementation: $1,500
- Monitoring tools (Datadog/NewRelic): $500/month × 3 = $1,500

### Phase 3 (Weeks 5-8): $18,000
- Security engineer: 80 hours × $150/hour = $12,000
- Penetration testing: $4,000
- Compliance consulting: $2,000

**Total Estimated Cost**: $38,000

### Ongoing Costs (Monthly)
- Security monitoring: $500/month
- Vulnerability scanning: $200/month
- Compliance tools: $300/month
- **Total Monthly**: $1,000

## Risk Assessment Matrix

| Risk | Likelihood | Impact | Current Risk | Post-Remediation Risk |
|------|------------|--------|--------------|----------------------|
| Secret Exposure | High | Critical | **CRITICAL** | Low |
| Account Takeover | Medium | High | **HIGH** | Low |
| Data Breach | Medium | Critical | **HIGH** | Medium |
| Service Disruption | Medium | High | **HIGH** | Low |
| Compliance Violation | High | High | **HIGH** | Low |

## Next Steps & Approval Required

### Immediate Actions (No Approval Needed)
1. [ ] Rotate exposed secrets (can be done immediately)
2. [ ] Disable debug mode in production
3. [ ] Update vulnerable dependencies

### Actions Requiring Approval
1. [ ] Budget approval for $38,000 security investment
2. [ ] Penetration testing approval (may cause temporary service disruption)
3. [ ] Database schema changes for audit logging
4. [ ] Third-party security tools procurement

### Timeline Approval
1. [ ] 2-week critical fix window (requires deployment freeze)
2. [ ] 4-week development window for Phase 2
3. [ ] 4-week testing and compliance window for Phase 3

---

**Document Status**: DRAFT - Pending Review and Approval
**Last Updated**: October 11, 2025
**Next Review**: Weekly during implementation

*This roadmap should be reviewed and approved by technical leadership, security team, and legal/compliance teams before implementation begins.*