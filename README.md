# Helpy

## 🌟 Overview

Helpy includes: 

- **AI-Powered Mental Health Assesment**: WhatsApp-based conversational agent for mental health assessment
- **Diagnosis Engine**: Multi-agent AI system for clinical decision support  
- **Healthcare Management API**: Complete patient, doctor, and appointment management
- **Modern Web Interface**: React/Next.js frontend for healthcare providers
- **Real-time Communication**: WebSocket support for live interactions

### Core Components

#### 1. **Frontend** (`/frontend`)
- **Technology**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Features**: Modern healthcare provider dashboard, patient management, appointment scheduling
- **UI Components**: Radix UI components with custom theming
- **Key Features**:
  - Doctor registration and management
  - Real-time appointment scheduling
  - Patient data visualization
  - Responsive design for all devices

#### 2. **Backend API** (`/backend`)  
- **Technology**: Django 5.2, Django REST Framework, PostgreSQL
- **Architecture**: Modular app-based structure
- **Apps**:
  - `authentication` - User management and JWT authentication
  - `patient` - Patient profiles and medical history
  - `doctor` - Doctor profiles, specialties, and availability
  - `appointment` - Appointment scheduling and management
  - `rooms` - Hospital room and equipment management
  - `schedule` - Doctor scheduling and time slot management
  - `conversation` - Chat and communication features

#### 3. **WhatsApp Bot** (`/whatsapp_bot`)
- **Technology**: FastAPI, WhatsApp Business API
- **Purpose**: Mental health triage through conversational interface
- **Features**:
  - Informed consent process (Colombian Law 1581/2012 compliant)
  - 13-question mental health assessment
  - Dynamic follow-up questions based on AI analysis
  - Integration with external diagnosis API
  - Session management and conversation flow

#### 4. **Diagnosis Engine** (`/diagnose-bot`)
- **Technology**: FastAPI, LangChain, Google AI/OpenAI
- **Purpose**: AI-powered clinical decision support
- **Features**:
  - Multi-agent system for comprehensive analysis
  - Risk assessment and priority scoring
  - Clinical recommendations generation
  - Integration with healthcare databases

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/auto_triage.git
   cd auto_triage
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Configure environment variables
   cp .env.example .env
   # Edit .env with your database and API credentials
   
   # Run migrations
   python manage.py migrate
   python manage.py createsuperuser
   
   # Start development server
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Start development server
   npm run dev
   ```

4. **WhatsApp Bot Setup**
   ```bash
   cd whatsapp_bot
   pip install -r requirements.txt
   
   # Configure WhatsApp Business API credentials
   cp env.example .env
   # Edit .env with your WhatsApp credentials
   
   # Start bot server
   uvicorn main:app --reload
   ```

5. **Diagnosis Bot Setup**
   ```bash
   cd diagnose-bot
   pip install -r requirements.txt
   
   # Start diagnosis engine
   uvicorn app:app --reload --port 8001
   ```

### Docker Deployment

For production deployment with Docker:

```bash
# WhatsApp Bot with Docker
cd whatsapp_bot
docker-compose up -d --build

# Full system deployment (customize docker-compose.yml as needed)
docker-compose up -d --build
```

## 📊 Key Features

### 🤖 AI-Powered Triage
- **Conversational Interface**: Natural language interaction via WhatsApp
- **Mental Health Assessment**: Comprehensive 13-question evaluation
- **Dynamic Follow-up**: AI-generated personalized questions
- **Risk Stratification**: Automated priority scoring and recommendations
- **Legal Compliance**: GDPR and Colombian data protection law compliant

### 🏥 Healthcare Management
- **Patient Management**: Complete medical history and document storage
- **Doctor Scheduling**: Advanced availability management with templates
- **Appointment System**: Conflict-free scheduling with room assignment
- **Equipment Tracking**: Hospital resource management
- **Multi-specialty Support**: Configurable medical specialties

### 🔒 Security & Compliance
- **JWT Authentication**: Secure API access with token rotation
- **Data Encryption**: End-to-end encryption for sensitive health data
- **Audit Logging**: Comprehensive activity tracking
- **CORS Configuration**: Secure cross-origin resource sharing
- **AWS S3 Integration**: Secure file storage and backup

### 📱 Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live appointment and patient status updates
- **Intuitive UX**: Healthcare provider-focused user experience
- **Accessibility**: WCAG compliant interface design

## 🔌 API Documentation

### Authentication Endpoints
```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/refresh/        # Token refresh
POST /api/auth/logout/         # User logout
```

### Patient Management
```
GET    /api/patients/          # List patients
POST   /api/patients/          # Create patient
GET    /api/patients/{id}/     # Get patient details
PUT    /api/patients/{id}/     # Update patient
DELETE /api/patients/{id}/     # Delete patient
POST   /api/patients/intake/   # Patient intake form
```

### Doctor Management
```
GET    /api/doctors/           # List doctors
POST   /api/doctors/           # Create doctor profile
GET    /api/doctors/{id}/      # Get doctor details
PUT    /api/doctors/{id}/      # Update doctor
GET    /api/doctors/{id}/availability/  # Get availability
```

### Appointment System
```
GET    /api/appointments/      # List appointments
POST   /api/appointments/      # Create appointment
GET    /api/appointments/{id}/ # Get appointment details
PUT    /api/appointments/{id}/ # Update appointment
DELETE /api/appointments/{id}/ # Cancel appointment
```

### WhatsApp Bot Endpoints
```
GET    /webhook               # Webhook verification
POST   /webhook               # Receive WhatsApp messages
GET    /sessions              # List active sessions
DELETE /sessions/{phone}      # Reset user session
```

## 🛠️ Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DB_NAME=auto_triage
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

#### WhatsApp Bot (.env)
```env
# WhatsApp Business API
WHATSAPP_TOKEN=your_whatsapp_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_verify_token
GRAPH_API_VERSION=v20.0

# External APIs
EXTERNAL_API_URL=https://your-diagnosis-api.com
DATABASE_API_URL=http://your-backend-api.com/api/patients/intake/
DATABASE_API_TOKEN=your_api_token
```

## 📈 Monitoring & Analytics

### Health Checks
- **API Health**: `/health/` endpoint for service monitoring
- **Database Connectivity**: Automatic database health checks
- **External API Status**: WhatsApp and diagnosis API monitoring

### Logging
- **Structured Logging**: JSON formatted logs for analysis
- **Error Tracking**: Comprehensive error reporting
- **Performance Metrics**: Response time and throughput monitoring

## 🔄 Development Workflow

### Code Structure
```
auto_triage/
├── backend/                 # Django REST API
│   ├── auto_triage/        # Django project settings
│   ├── authentication/     # User auth app
│   ├── patient/           # Patient management
│   ├── doctor/            # Doctor management
│   ├── appointment/       # Appointment system
│   ├── rooms/             # Room management
│   ├── schedule/          # Scheduling system
│   └── conversation/      # Chat features
├── frontend/               # Next.js web app
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── hooks/             # Custom hooks
│   └── lib/               # Utilities
├── whatsapp_bot/          # WhatsApp integration
│   ├── app/               # Bot application
│   ├── config/            # Configuration
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
└── diagnose-bot/          # AI diagnosis engine
    ├── src/               # Source code
    ├── api/               # API endpoints
    ├── model/             # AI models
    └── utils/             # Utilities
```

### Testing
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests  
cd frontend
npm test

# Bot tests
cd whatsapp_bot
pytest
```

## 🚀 Deployment

### Production Checklist
- [ ] Configure production database (PostgreSQL)
- [ ] Set up AWS S3 for file storage
- [ ] Configure WhatsApp Business API
- [ ] Set up SSL/TLS certificates
- [ ] Configure environment variables
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies
- [ ] Test all integrations

### Scaling Considerations
- **Database**: Use read replicas for high-traffic scenarios
- **API**: Implement caching (Redis) for frequently accessed data
- **Files**: Use CDN for static file delivery
- **Bot**: Implement message queuing for high-volume WhatsApp traffic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive tests
- Update documentation for new features
- Follow semantic versioning

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Disclaimers

- **Medical Use**: This system is designed for triage support only and should not replace professional medical assessment or emergency services
- **Data Privacy**: Ensure compliance with local healthcare regulations (HIPAA, GDPR, etc.)
- **Emergency Cases**: Always provide clear pathways to emergency services for critical situations
- **Professional Oversight**: AI recommendations should always be reviewed by qualified healthcare professionals

## 🆘 Support

For technical issues, feature requests, or clinical integration questions:

- **Documentation**: Check the `/docs` directory for detailed guides
- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support

---

**Built with ❤️ in 24 Hours for AI Hackthon 2025**

