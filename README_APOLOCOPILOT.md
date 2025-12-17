# 🚀 ApoloCopilot

Plataforma completa para profissionais de saúde com verificação, geolocalização, calendário, fórum e sistema de plantões.

## ✨ Features

### 📱 **WhatsApp Verification**
- Integração com Twilio
- Envio de código de verificação de 6 dígitos
- Validação de número de telefone

### 📄 **Document Verification**
- Upload de documentos (RG, CNH, comprovante de residência)
- Sistema de barreira impeditiva (funcionalidades bloqueadas até aprovação)
- Processamento e otimização de imagens

### 📍 **GPS & Location**
- Rastreamento de localização do usuário
- Busca por proximidade (estilo Uber)
- Geocoding e reverse geocoding
- Interface de mapa integrada

### 📅 **Google Calendar Integration**
- Sincronização automática com Google Calendar
- Listagem de eventos futuros
- OAuth 2.0 authentication

### 💬 **Forum System**
- Threads e posts
- Categorias personalizadas
- Sistema de visualizações
- Moderação (pin, lock)

### 🤖 **AI Chatbot**
- Integração com OpenEvidence.com
- Respostas baseadas em evidências científicas
- Histórico de conversas
- WebSocket para chat em tempo real

### 🏅 **Gamification**
- **Badges**: Sistema de conquistas e reconhecimentos
- **Trust/Karma**: Sistema de reputação inspirado no Reddit
- **Avatares**: Personalizáveis tipo Reddit
- **Upvote/Downvote**: Sistema de votação em posts e threads

### 🏥 **Medical Shifts (Plantões)**
- Busca e filtro de oportunidades de plantões médicos
- Candidatura a plantões
- Filtros salvos personalizados
- Integração futura com Google Jobs e apps especializados

## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite com SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **WhatsApp**: Twilio API
- **Calendar**: Google Calendar API
- **AI**: OpenEvidence integration
- **Frontend**: HTML5, CSS3, JavaScript

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

1. **Clone the repository**
```bash
git clone <repo-url>
cd ApoloCopilot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Initialize database**
```bash
python init_database.py
```

5. **Start the server**
```bash
# Option 1: Using the startup script
./start.sh

# Option 2: Direct Python
python app_main.py

# Option 3: Using Uvicorn
python -m uvicorn app_main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Access the application**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- API Reference: http://localhost:8000/redoc

## 🔑 API Keys Required

### Twilio (WhatsApp)
1. Create account at https://twilio.com
2. Get Account SID and Auth Token
3. Configure WhatsApp sandbox
4. Add to `.env`:
```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Google Calendar API
1. Go to https://console.cloud.google.com
2. Create a project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Add to `.env`:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/callback
```

### OpenEvidence (Optional)
1. Contact OpenEvidence for API access
2. Add to `.env`:
```
OPENEVIDENCE_API_KEY=your_api_key
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `GET /api/auth/status` - Get verification status

### WhatsApp Endpoints
- `POST /api/whatsapp/send-code` - Send verification code
- `POST /api/whatsapp/verify-code` - Verify code
- `POST /api/whatsapp/resend-code` - Resend code

### Document Endpoints
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/my-documents` - Get my documents
- `GET /api/documents/required` - Get required documents list

### Location Endpoints
- `POST /api/location/save` - Save location
- `GET /api/location/my-location` - Get my location
- `GET /api/location/nearby` - Search nearby
- `POST /api/location/geocode` - Convert address to coordinates

### Calendar Endpoints
- `GET /api/calendar/auth-url` - Get Google OAuth URL
- `GET /api/calendar/callback` - OAuth callback
- `GET /api/calendar/events` - Get synced events

### Chat Endpoints
- `POST /api/chat/send` - Send message to AI
- `GET /api/chat/history` - Get chat history
- `WebSocket /api/chat/ws` - Real-time chat

### Forum Endpoints
- `GET /api/forum/categories` - List categories
- `GET /api/forum/threads` - List threads
- `POST /api/forum/threads` - Create thread
- `GET /api/forum/threads/{id}` - Get thread
- `POST /api/forum/threads/{id}/posts` - Create post

### Gamification Endpoints
- `GET /api/gamification/badges` - List all badges
- `GET /api/gamification/my-badges` - Get my badges
- `GET /api/gamification/trust/me` - Get my trust score
- `POST /api/gamification/vote` - Upvote/downvote content
- `GET /api/gamification/avatar/me` - Get my avatar
- `PUT /api/gamification/avatar/customize` - Customize avatar

### Medical Shifts Endpoints
- `GET /api/shifts/search` - Search shifts
- `POST /api/shifts/create` - Create shift
- `GET /api/shifts/{id}` - Get shift details
- `POST /api/shifts/{id}/apply` - Apply to shift
- `GET /api/shifts/my/applications` - My applications
- `GET /api/shifts/types` - Get shift types

## 🗂 Project Structure

```
ApoloCopilot/
├── app_main.py              # Main FastAPI application
├── database.py              # Database configuration
├── init_database.py         # Database initialization script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── models/                  # SQLAlchemy models
│   ├── user.py             # User, phone & document models
│   ├── forum.py            # Forum models
│   ├── chat.py             # Chat & calendar models
│   ├── gamification.py     # Badges, trust, avatars
│   └── shifts.py           # Medical shifts models
├── routers/                # API endpoints
│   ├── auth.py             # Authentication
│   ├── whatsapp.py         # WhatsApp verification
│   ├── documents.py        # Document verification
│   ├── location.py         # GPS & location
│   ├── calendar.py         # Google Calendar
│   ├── chat.py             # AI Chatbot
│   ├── forum.py            # Forum
│   ├── gamification.py     # Badges & trust
│   └── shifts.py           # Medical shifts
├── services/               # Business logic
│   ├── whatsapp_service.py
│   ├── document_service.py
│   ├── calendar_service.py
│   ├── chatbot_service.py
│   └── location_service.py
├── utils/                  # Utilities
│   └── security.py         # JWT & authentication
├── frontend/               # Frontend files
│   └── index.html          # Main page
└── database/               # SQLite database
    └── apolocopilot.db
```

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Document verification barrier
- Phone verification requirement
- Rate limiting (configurable)
- CORS middleware
- Gzip compression

## 🚦 User Journey

1. **Registration** → User creates account
2. **Phone Verification** → WhatsApp code verification
3. **Document Upload** → Upload required documents
4. **Document Review** → Admin reviews and approves
5. **Full Access** → All features unlocked
6. **Earn Badges** → Complete actions to earn achievements
7. **Build Trust** → Participate in community to build karma

## 📊 Database Schema

- **Users**: User accounts with status tracking
- **PhoneVerification**: WhatsApp verification records
- **DocumentVerification**: Uploaded documents
- **UserLocation**: GPS location history
- **ForumCategory, ForumThread, ForumPost**: Forum system
- **ChatMessage**: AI chat history
- **CalendarEvent**: Synced Google Calendar events
- **Badge, UserBadge**: Achievement system
- **TrustScore**: Karma/reputation system
- **Avatar**: User avatar customization
- **Vote**: Upvote/downvote system
- **Shift, ShiftApplication**: Medical shifts

## 🎯 Future Enhancements

- [ ] Mobile app (React Native / Flutter)
- [ ] Push notifications
- [ ] Advanced shift scraping from Google Jobs
- [ ] Integration with more shift platforms
- [ ] Real-time chat between users
- [ ] Video calls
- [ ] Advanced analytics dashboard
- [ ] Machine learning for shift recommendations
- [ ] Stripe payment integration
- [ ] Multi-language support

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

## 📄 License

MIT License

## 👨‍💻 Author

Created with Claude Code

## 🆘 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for healthcare professionals**
