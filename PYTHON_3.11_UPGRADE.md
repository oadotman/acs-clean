# Upgrade Python to 3.11 on Ubuntu VPS

## Complete Command Sequence

Copy and paste these commands on your VPS:

```bash
# Step 1: Add the deadsnakes PPA for Python 3.11
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Step 2: Install Python 3.11 and required packages
sudo apt install python3.11 python3.11-venv python3.11-dev python3.11-distutils -y

# Step 3: Verify Python 3.11 is installed
python3.11 --version

# Step 4: Navigate to your project
cd /var/www/acs-clean

# Step 5: Remove old Python 3.7 virtual environment
rm -rf venv

# Step 6: Create new virtual environment with Python 3.11
python3.11 -m venv venv

# Step 7: Activate the new virtual environment
source venv/bin/activate

# Step 8: Verify Python version in venv (should show 3.11.x)
python --version

# Step 9: Upgrade pip
pip install --upgrade pip

# Step 10: Install backend dependencies
cd backend
pip install -r requirements.txt

# Step 11: Run database migrations
alembic upgrade head

# Step 12: Test the application
python -m uvicorn main_production:app --host 0.0.0.0 --port 8000
```

## One-Line Installation (if you're confident)

```bash
sudo apt update && sudo apt install software-properties-common -y && sudo add-apt-repository ppa:deadsnakes/ppa -y && sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-dev python3.11-distutils -y && cd /var/www/acs-clean && rm -rf venv && python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && cd backend && pip install -r requirements.txt && alembic upgrade head
```

## After Installation Test

```bash
# Activate venv and test
cd /var/www/acs-clean
source venv/bin/activate
python --version  # Should show Python 3.11.x
python -c "from main_production import app; print('✓ Import successful')"
```

That's it! After running these commands, your VPS will have Python 3.11 and your application should work.