@echo off
echo 🚀 AdCopySurge - Push and Deploy Script

echo 📝 Committing local changes...
git add .
git commit -m "Deploy: %date% %time% - Production update with fixes"

echo 📤 Pushing to GitHub...
git push origin main

echo ✅ Changes pushed to GitHub!
echo 🔄 Now run the deployment script on the VPS:
echo.
echo SSH Command: ssh root@46.247.108.207
echo Then run: bash /root/deploy-adcopysurge.sh
echo.
pause