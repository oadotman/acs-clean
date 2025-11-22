# Fix Systemd Service Configuration Error

## Error
```
/etc/systemd/system/adcopysurge.service:13: Missing '='.
Failed to load properly: Invalid argument.
```

## Quick Fix

### Step 1: View the Service File

```bash
cat /etc/systemd/system/adcopysurge.service
```

Look at **line 13** - it should have a syntax error (missing `=` sign).

### Step 2: Edit the Service File

```bash
sudo nano /etc/systemd/system/adcopysurge.service
```

### Common Systemd Syntax Errors on Line 13

**Wrong:**
```ini
WorkingDirectory /var/www/acs-clean/backend    # Missing =
```

**Correct:**
```ini
WorkingDirectory=/var/www/acs-clean/backend    # Has =
```

**Wrong:**
```ini
Environment = "PATH=/var/www/acs-clean/backend/venv/bin:/usr/bin"    # Space before =
```

**Correct:**
```ini
Environment="PATH=/var/www/acs-clean/backend/venv/bin:/usr/bin"    # No space before =
```

### Example Correct Service File

Here's a complete working example:

```ini
[Unit]
Description=AdCopySurge FastAPI Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/acs-clean/backend
Environment="PATH=/var/www/acs-clean/backend/venv/bin:/usr/bin:/usr/local/bin"
Environment="PYTHONPATH=/var/www/acs-clean/backend"
ExecStart=/var/www/acs-clean/backend/venv/bin/gunicorn main_production:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 3: Reload Systemd

After fixing the file:

```bash
# Reload systemd to pick up the fixed configuration
sudo systemctl daemon-reload

# Verify the file loads correctly
sudo systemctl status adcopysurge
# Should NOT show "Missing '='" error
```

### Step 4: Start the Service

```bash
# Start the service
sudo systemctl start adcopysurge

# Check status
sudo systemctl status adcopysurge

# Should show:
#   Loaded: loaded (/etc/systemd/system/adcopysurge.service; enabled)
#   Active: active (running)
```

### Step 5: Enable Auto-Start (if not enabled)

```bash
sudo systemctl enable adcopysurge
```

## If You Can't Find Line 13

Show line numbers:

```bash
cat -n /etc/systemd/system/adcopysurge.service
```

Or use nano with line numbers:

```bash
sudo nano -c /etc/systemd/system/adcopysurge.service
# -c flag shows line numbers
```

## Systemd Syntax Rules

1. **No spaces around `=`**
   - ✅ `WorkingDirectory=/path`
   - ❌ `WorkingDirectory = /path`

2. **No trailing spaces**
   - ✅ `User=www-data`
   - ❌ `User=www-data   `

3. **Quote complex values**
   - ✅ `Environment="PATH=/usr/bin:/bin"`
   - ❌ `Environment=PATH=/usr/bin:/bin` (works but not recommended)

4. **One directive per line**
   - ✅
     ```
     Environment="PATH=/usr/bin"
     Environment="PYTHONPATH=/app"
     ```
   - ❌ `Environment="PATH=/usr/bin" "PYTHONPATH=/app"`

## Complete Fix Commands

Run these on your VPS:

```bash
# 1. View current file (note line 13)
cat -n /etc/systemd/system/adcopysurge.service

# 2. Edit the file
sudo nano /etc/systemd/system/adcopysurge.service
# Fix line 13 - ensure proper syntax (see examples above)
# Save: Ctrl+X, Y, Enter

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Start service
sudo systemctl start adcopysurge

# 5. Check status
sudo systemctl status adcopysurge

# 6. If running, check logs
sudo journalctl -u adcopysurge -f
```

## Expected Output After Fix

```bash
$ sudo systemctl status adcopysurge
● adcopysurge.service - AdCopySurge FastAPI Application
   Loaded: loaded (/etc/systemd/system/adcopysurge.service; enabled; vendor preset: enabled)
   Active: active (running) since Wed 2025-11-19 19:00:00 UTC; 10s ago
 Main PID: 12345 (gunicorn)
    Tasks: 5 (limit: 4915)
   Memory: 250.0M
   CGroup: /system.slice/adcopysurge.service
           ├─12345 /var/www/acs-clean/backend/venv/bin/python3 /var/www/.../gunicorn
           ├─12346 /var/www/acs-clean/backend/venv/bin/python3 /var/www/.../gunicorn
           └─...

Nov 19 19:00:00 v44954 systemd[1]: Started AdCopySurge FastAPI Application.
Nov 19 19:00:01 v44954 gunicorn[12345]: [INFO] Starting gunicorn 21.2.0
Nov 19 19:00:01 v44954 gunicorn[12345]: [INFO] Listening at: unix:/run/adcopysurge/gunicorn.sock
Nov 19 19:00:02 v44954 gunicorn[12346]: [INFO] Worker spawned (pid: 12346)
```

✅ Key indicators:
- `Loaded: loaded` (not "error")
- `Active: active (running)` (not "failed")
- Workers spawned
- No error messages

## Still Not Working?

### Check the Exact Error

```bash
# Show only the error lines
sudo systemctl status adcopysurge 2>&1 | grep -i error

# Or check systemd journal
sudo journalctl -xe -u adcopysurge
```

### Create a New Service File

If the file is too corrupted, create a fresh one:

```bash
# Backup the broken file
sudo cp /etc/systemd/system/adcopysurge.service /etc/systemd/system/adcopysurge.service.broken

# Create new file
sudo nano /etc/systemd/system/adcopysurge.service
```

Paste this complete working configuration:

```ini
[Unit]
Description=AdCopySurge FastAPI Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/acs-clean/backend
Environment="PATH=/var/www/acs-clean/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/var/www/acs-clean/backend"
ExecStart=/var/www/acs-clean/backend/venv/bin/gunicorn main_production:app --config gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=10
PrivateTmp=true
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Adjust paths if your installation is different.

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl start adcopysurge
sudo systemctl enable adcopysurge
sudo systemctl status adcopysurge
```
