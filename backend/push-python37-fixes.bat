@echo off
echo Pushing Python 3.7 compatibility fixes...

git add backend/requirements-python37-fixed.txt
git add backend/app/core/config.py
git add backend/app/core/database.py
git commit -m "Add Python 3.7 compatibility fixes for Debian 10 deployment

- Add requirements-python37-fixed.txt with compatible package versions
- Fix config.py to use Pydantic v1 BaseSettings import
- Fix database.py to use SQLAlchemy 1.4 compatible async sessionmaker
- Use python-decouple for environment configuration
- Compatible with Python 3.7 and older SQLAlchemy versions"

git push origin main

echo.
echo Python 3.7 compatibility fixes pushed to GitHub!
echo.
echo Now run these commands on Datalix:
echo.
echo cd /opt
echo rm -rf adcopysurge
echo git clone https://github.com/Adeliyio/acsurge.git adcopysurge
echo cd adcopysurge/backend
echo python3 -m venv venv
echo source venv/bin/activate
echo pip install --upgrade pip
echo pip install -r requirements-python37-fixed.txt
echo.
echo Then copy your .env file with production settings.
pause