#!/bin/bash

# AdCopySurge Security Hardening Script
# Run this script to harden the production server

set -e

echo "🔒 Starting AdCopySurge Security Hardening..."

# Update system packages
echo "📦 Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install security tools
echo "🛡️ Installing security tools..."
apt-get install -y \
    ufw \
    fail2ban \
    unattended-upgrades \
    logwatch \
    rkhunter \
    chkrootkit \
    aide

# Configure UFW firewall
echo "🔥 Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (adjust port if changed)
ufw allow ssh
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable UFW
ufw --force enable

# Configure fail2ban
echo "🚫 Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log

[adcopysurge-api]
enabled = true
filter = adcopysurge-api
logpath = /var/log/adcopysurge/app.log
maxretry = 5
findtime = 300
bantime = 1800
EOF

# Create custom fail2ban filter for API
cat > /etc/fail2ban/filter.d/adcopysurge-api.conf << 'EOF'
[Definition]
failregex = ^.*ERROR.*Analysis failed.*<HOST>.*$
            ^.*ERROR.*Authentication failed.*<HOST>.*$
            ^.*WARNING.*Rate limit exceeded.*<HOST>.*$
ignoreregex =
EOF

# Configure automatic security updates
echo "🔄 Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

# Configure unattended upgrades for security updates only
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id} ESMApps:${distro_codename}-apps-security";
    "${distro_id} ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::Package-Blacklist {
};

Unattended-Upgrade::DevRelease "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";

Unattended-Upgrade::Mail "admin@adcopysurge.com";
Unattended-Upgrade::MailOnlyOnError "true";
EOF

# Secure SSH configuration
echo "🔑 Securing SSH configuration..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Create secure SSH config
cat > /etc/ssh/sshd_config.d/99-adcopysurge.conf << 'EOF'
# AdCopySurge SSH Security Configuration
Protocol 2
Port 22
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no
PrintMotd no
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxStartups 2
LoginGraceTime 30
EOF

# Set proper file permissions
echo "📁 Setting file permissions..."
chmod 600 /etc/ssh/sshd_config.d/99-adcopysurge.conf

# Secure the application directory
chown -R www-data:www-data /var/www/adcopysurge
find /var/www/adcopysurge -type d -exec chmod 755 {} \;
find /var/www/adcopysurge -type f -exec chmod 644 {} \;
chmod 600 /var/www/adcopysurge/backend/.env

# Secure log directory
mkdir -p /var/log/adcopysurge
chown -R www-data:adm /var/log/adcopysurge
chmod 750 /var/log/adcopysurge

# Configure log rotation for security logs
cat > /etc/logrotate.d/adcopysurge-security << 'EOF'
/var/log/adcopysurge/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 www-data adm
    postrotate
        systemctl reload adcopysurge
    endscript
}
EOF

# Install and configure AIDE (Advanced Intrusion Detection Environment)
echo "👁️ Configuring intrusion detection..."
aide --init
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Add daily AIDE check
cat > /etc/cron.daily/aide-check << 'EOF'
#!/bin/bash
/usr/bin/aide --check | mail -s "AIDE Report $(hostname)" admin@adcopysurge.com
EOF
chmod +x /etc/cron.daily/aide-check

# Configure system limits
echo "⚡ Configuring system limits..."
cat > /etc/security/limits.d/99-adcopysurge.conf << 'EOF'
# AdCopySurge security limits
www-data soft nofile 65536
www-data hard nofile 65536
www-data soft nproc 4096
www-data hard nproc 4096
EOF

# Configure sysctl for security
echo "⚙️ Configuring kernel security parameters..."
cat > /etc/sysctl.d/99-adcopysurge-security.conf << 'EOF'
# IP Spoofing protection
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 1

# Ignore Directed pings
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable IPv6 if not needed
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1

# TCP SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5
EOF

# Apply sysctl settings
sysctl -p /etc/sysctl.d/99-adcopysurge-security.conf

# Create security monitoring script
cat > /usr/local/bin/security-check.sh << 'EOF'
#!/bin/bash
# Security monitoring script for AdCopySurge

echo "=== AdCopySurge Security Status Report ==="
echo "Date: $(date)"
echo ""

echo "🔥 Firewall Status:"
ufw status verbose
echo ""

echo "🚫 Fail2ban Status:"
fail2ban-client status
echo ""

echo "📊 System Load:"
uptime
echo ""

echo "💾 Disk Usage:"
df -h
echo ""

echo "🔍 Recent Failed Login Attempts:"
grep "Failed password" /var/log/auth.log | tail -5
echo ""

echo "📋 Active Connections:"
netstat -tuln | grep LISTEN
echo ""

echo "🏃 Running Processes:"
ps aux | grep -E "(nginx|uvicorn|python)" | grep -v grep
echo ""
EOF

chmod +x /usr/local/bin/security-check.sh

# Add to daily cron
echo "0 6 * * * root /usr/local/bin/security-check.sh | mail -s 'AdCopySurge Security Report' admin@adcopysurge.com" >> /etc/crontab

# Restart services
echo "🔄 Restarting security services..."
systemctl restart fail2ban
systemctl restart ssh
systemctl enable fail2ban
systemctl enable ufw

# Final security check
echo "✅ Running final security verification..."
/usr/local/bin/security-check.sh

echo ""
echo "🔒 Security hardening completed!"
echo ""
echo "✅ Configured services:"
echo "  - UFW Firewall (enabled)"
echo "  - Fail2ban (monitoring SSH, Nginx, API)"
echo "  - Automatic security updates"
echo "  - SSH hardening"
echo "  - File permission security"
echo "  - Intrusion detection (AIDE)"
echo "  - System monitoring"
echo ""
echo "⚠️  Important next steps:"
echo "  1. Change default SSH port if needed"
echo "  2. Set up SSH key authentication"
echo "  3. Configure monitoring email alerts"
echo "  4. Run regular security audits"
echo "  5. Keep system updated"
echo ""
echo "📋 Run 'security-check.sh' daily to monitor security status"
