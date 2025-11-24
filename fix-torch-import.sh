#!/bin/bash
# Fix PyTorch import issue in production

echo "=========================================="
echo "Fixing PyTorch Import Issue"
echo "=========================================="
echo ""

echo "ISSUE:"
echo "----------------------------------------"
echo "Backend is crash-looping because PyTorch import fails"
echo "Error: KeyboardInterrupt during torch._C import"
echo ""

echo "SOLUTION OPTIONS:"
echo "----------------------------------------"
echo "1. Reinstall PyTorch in the correct venv"
echo "2. Comment out the transformers import (fallback mode)"
echo "3. Check if wrong venv is being used"
echo ""

cd /var/www/acs-clean/backend

echo "STEP 1: Check which venv PM2 is using..."
echo "----------------------------------------"
pm2 describe acs-backend | grep "script path"
echo ""

echo "Expected: /var/www/acs-clean/backend/venv/bin/python"
echo ""

echo "STEP 2: Check if PyTorch is installed..."
echo "----------------------------------------"
source /var/www/acs-clean/backend/venv/bin/activate
python -c "import torch; print('✅ PyTorch version:', torch.__version__)" 2>&1 || echo "❌ PyTorch not installed or broken"
echo ""

echo "STEP 3: Check if transformers is installed..."
echo "----------------------------------------"
python -c "import transformers; print('✅ Transformers version:', transformers.__version__)" 2>&1 || echo "❌ Transformers not installed or broken"
echo ""

echo "STEP 4: Try importing the problematic module..."
echo "----------------------------------------"
python -c "
import sys
sys.path.insert(0, '/var/www/acs-clean/backend')
try:
    from transformers import pipeline
    print('✅ Import successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
" 2>&1
echo ""

echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="
echo ""
echo "If PyTorch is broken, run:"
echo "  pip uninstall torch torchvision torchaudio transformers -y"
echo "  pip install torch --index-url https://download.pytorch.org/whl/cpu"
echo "  pip install transformers"
echo ""
echo "Or to run without transformers (faster, uses fallback):"
echo "  Set environment: DISABLE_TRANSFORMERS=true"
