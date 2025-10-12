# AdCopySurge - AI-Powered Ad Copy Analysis Platform

![AdCopySurge Logo](docs/logo.png)

AdCopySurge is a comprehensive SaaS platform that analyzes ad creatives and predicts their performance using artificial intelligence. It helps agencies, SMBs, and freelance marketers create better-performing ads by providing detailed scoring, competitor benchmarking, and AI-generated alternatives.

## 🚀 Features

### Core Analysis Features
- **Readability & Clarity Scoring** - Analyzes text complexity and readability
- **Persuasion Analysis** - Detects power words and persuasive elements
- **Emotion Analysis** - Measures emotional impact and tone
- **CTA Strength Evaluation** - Scores call-to-action effectiveness
- **Platform Optimization** - Tailored analysis for Facebook, Google, LinkedIn, TikTok

### AI-Powered Generation
- **Alternative Variations** - Generate persuasive, emotional, stats-heavy variants
- **Platform-Specific Optimization** - Customized for each advertising platform
- **Performance Prediction** - AI-driven engagement scoring

### Business Features
- **Competitor Benchmarking** - Compare against top-performing ads
- **PDF Report Generation** - Professional reports for agencies
- **Usage Analytics** - Track performance improvements over time
- **Subscription Management** - Tiered pricing ($49-99/month)

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Configuration & database
│   ├── models/        # SQLAlchemy models
│   ├── services/      # Business logic
│   └── utils/         # Helper functions
├── requirements.txt
├── Dockerfile
└── main.py
```

### Frontend (React)
```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Route components
│   ├── services/      # API client & auth
│   └── utils/         # Helper functions
├── package.json
├── Dockerfile
└── public/
```

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL (Supabase), Redis
- **AI/ML**: OpenAI GPT, Hugging Face Transformers, scikit-learn
- **Frontend**: React 18, Material-UI, React Query (Deployed on Netlify)
- **Authentication**: JWT with Supabase Auth
- **Background Tasks**: Celery with Redis broker
- **Payments**: Paddle Billing integration
- **Deployment**: VPS with systemd, Nginx, Gunicorn + Uvicorn

## 📦 Installation

### Prerequisites

**For Development:**
- Python 3.11+
- Node.js 18+
- Redis 7+ (for local development)
- Docker & Docker Compose (optional)

**For Production (VPS):**
- Ubuntu 22.04 VPS (2GB+ RAM recommended)
- Python 3.11+ with venv support
- Nginx
- Redis 7+
- Domain name with DNS pointing to VPS
- SSL certificate (Let's Encrypt recommended)

**External Services:**
- Supabase PostgreSQL database
- Netlify (for frontend hosting)

### Python 3.12 Compatibility
This application is configured for Python 3.12 compatibility to ensure optimal deployment on Railway. The package dependencies are carefully managed using:
- **constraints-py312.txt**: Ensures all packages use Python 3.12 compatible wheels
- **runtime.txt**: Specifies exact Python version for deployment
- **Updated package versions**: All dependencies use versions with pre-built Python 3.12 wheels

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/adcopysurge.git
cd adcopysurge
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Manual Installation

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
# For local development
pip install -r requirements.txt

# For production/Railway deployment (recommended)
pip install -r requirements.txt -c constraints-py312.txt --prefer-binary
```

3. **Set up database**
```bash
# Create PostgreSQL database
createdb adcopysurge

# Run migrations
alembic upgrade head
```

4. **Start the server**
```bash
uvicorn main:app --reload
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start development server**
```bash
npm start
```

## 🔧 Configuration

### Environment Variables

⚠️ **Important**: Proper environment configuration is critical for the application to run successfully.

📖 **See [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) for complete configuration guide.**

**Quick Setup:**
1. Copy the example environment file: `cp backend/.env.example backend/.env`
2. Edit `backend/.env` and set the **required variables**:
   - `SECRET_KEY` (minimum 32 characters)
   - `DATABASE_URL`
3. Test configuration: `cd backend && python -c "from app.core.config import settings; print('✅ Config loaded!')"`

**Required Variables (minimum):**
```env
# backend/.env
SECRET_KEY=your-super-secret-key-change-this-min-32-chars
DATABASE_URL=sqlite:///./adcopysurge.db
```

**Optional but Recommended:**
```env
# AI Services
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key

# Email Configuration
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📝 API Documentation

The API follows RESTful conventions and includes comprehensive documentation.

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/token` - Login and get access token
- `GET /api/auth/me` - Get current user info

### Analysis Endpoints
- `POST /api/ads/analyze` - Analyze ad copy
- `GET /api/ads/history` - Get analysis history
- `GET /api/ads/analysis/{id}` - Get specific analysis
- `POST /api/ads/generate-alternatives` - Generate ad variants

### Subscription Endpoints
- `GET /api/subscriptions/plans` - Get available plans
- `POST /api/subscriptions/upgrade` - Upgrade subscription
- `POST /api/subscriptions/cancel` - Cancel subscription

### Full API documentation available at `/api/docs` when running the server.

## 💰 Subscription Tiers

### Free Plan
- 5 analyses per month
- Basic scoring
- Limited alternatives

### Basic Plan ($49/month)
- 100 analyses per month
- Full AI analysis
- Unlimited alternatives
- Competitor benchmarking
- PDF reports

### Pro Plan ($99/month)
- 500 analyses per month
- Premium AI models
- Advanced competitor analysis
- White-label reports
- API access
- Priority support

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --build
```

## 🚀 Deployment

### Architecture Overview

**Current Production Setup:**
- **Frontend**: Deployed on Netlify (Static React SPA)
- **Backend**: VPS deployment with Ubuntu 22.04
- **Database**: Supabase PostgreSQL (managed)
- **File Storage**: Integrated with Supabase

### VPS Production Deployment

🚀 **Deploy to Traditional VPS - Full control and cost-effective!**

📖 **See [VPS_DEPLOYMENT.md](./VPS_DEPLOYMENT.md) for complete VPS deployment guide.**

**Quick VPS Setup:**
```bash
# On your VPS (Ubuntu 22.04)
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv redis-server nginx

# Clone and setup
cd /home/deploy
git clone https://github.com/yourusername/adcopysurge.git
cd adcopysurge/backend

# Install dependencies
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure services
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo cp deploy/celery.service /etc/systemd/system/
sudo systemctl enable gunicorn celery
```

**Services Architecture:**
- **Gunicorn + Uvicorn**: ASGI server for FastAPI
- **Celery Worker**: Background task processing
- **Redis**: Message broker and caching
- **Nginx**: Reverse proxy with SSL termination
- **Systemd**: Process management and auto-restart

### Development Deployment

1. **Set development environment variables**
```bash
cp backend/.env.example backend/.env
# Edit .env with your configuration
```

2. **Run with Docker Compose**
```bash
docker-compose up -d
```

## 📊 Analytics & Monitoring

The platform includes built-in analytics for:
- User engagement metrics
- Analysis performance trends
- Subscription conversion rates
- API usage statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [API Documentation](http://localhost:8000/api/docs)
- [Frontend Demo](http://localhost:3000)
- [Issue Tracker](https://github.com/yourusername/adcopysurge/issues)

## 📞 Support

For support and questions:
- Email: support@adcopysurge.com
- Discord: [AdCopySurge Community](https://discord.gg/adcopysurge)
- Documentation: [docs.adcopysurge.com](https://docs.adcopysurge.com)

---

Built with ❤️ for better ad performance
