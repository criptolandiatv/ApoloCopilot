# 🚀 ApoloCopilot - Guia de Deployment

## ✅ Status do Projeto

**Tudo pronto para produção!** ✨

- ✅ Dependências instaladas
- ✅ Database inicializado
- ✅ Seed data completo
- ✅ AI Chatbox integrado
- ✅ Frontend responsivo
- ✅ API REST completa
- ✅ Código commitado no Git

---

## 🏁 Quick Start (Replit)

### Opção 1: Script Automático
```bash
./start.sh
```

### Opção 2: Manual
```bash
# 1. Instalar dependências (se necessário)
pip install -r requirements.txt

# 2. Inicializar database
python init_database.py

# 3. Popular com dados iniciais
python seed_data.py

# 4. Iniciar servidor
python app_main.py
```

### Opção 3: Uvicorn Direto
```bash
python -m uvicorn app_main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 URLs de Acesso

Quando o servidor estiver rodando:

```
🏠 Página Principal:     http://localhost:8000
✨ Onboarding:           http://localhost:8000/onboarding
📚 API Docs:             http://localhost:8000/docs
📖 API Reference:        http://localhost:8000/redoc
💓 Health Check:         http://localhost:8000/health
```

**No Replit**, substitua `localhost:8000` pela sua URL do Replit:
```
https://[seu-projeto].replit.dev
```

---

## 🤖 AI Chatbox - Como Funciona

### Funcionalidades

✅ **Discreto** - Botão flutuante no canto inferior
✅ **Responsivo** - Adapta-se a mobile e desktop
✅ **OpenEvidence** - Respostas baseadas em evidências
✅ **Real-time** - Indicador de digitação
✅ **Histórico** - Carrega conversas anteriores (se logado)
✅ **Markdown** - Suporta formatação de texto

### Localização

O chatbox aparece **automaticamente** em todas as páginas que incluem:
```html
<script src="/static/js/ai-chatbox.js"></script>
```

Páginas com chatbox:
- ✅ `/` (index.html)
- ✅ `/onboarding` (onboarding.html)

### Personalização

Edite `/frontend/js/ai-chatbox.js` para customizar:

```javascript
// Exemplo de customização
window.apoloChat = new ApoloCopilotChat({
    position: 'bottom-left',     // ou 'bottom-right'
    primaryColor: '#FF4500',     // Cor principal
    apiEndpoint: '/api/chat/send' // Endpoint da API
});
```

---

## 🔐 Configuração de APIs

### 1. WhatsApp (Twilio)

Edite o arquivo `.env`:

```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Como obter:**
1. Acesse https://twilio.com
2. Crie uma conta (trial gratuito disponível)
3. Vá em Console → Account Info
4. Copie Account SID e Auth Token
5. Configure WhatsApp Sandbox

### 2. Google Calendar

```bash
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/callback
```

**Como obter:**
1. Acesse https://console.cloud.google.com
2. Crie um projeto
3. Ative a Google Calendar API
4. Crie credenciais OAuth 2.0
5. Adicione redirect URI

### 3. OpenEvidence (Chatbot)

```bash
OPENEVIDENCE_API_KEY=your_api_key_here
OPENEVIDENCE_BASE_URL=https://openevidence.com/api
```

**Como obter:**
1. Visite https://openevidence.com
2. Entre em contato para API access
3. Obtenha sua API key

**Nota:** O chatbot funciona mesmo sem a API (modo fallback)

---

## 📊 Dados Iniciais (Seed Data)

Após rodar `python seed_data.py`, você terá:

### Badges (7)
- 🌱 Novato
- ✅ Verificado
- ⭐ Confiável
- 🤝 Ajudante
- 🎓 Especialista
- 🏆 Veterano
- 🛡️ Moderador

### Categorias do Fórum (6)
- 💬 Geral
- 🏥 Plantões
- ❓ Dúvidas Técnicas
- 💡 Sugestões
- 📢 Anúncios
- 🤝 Networking

### Plantões de Exemplo (4)
- Emergência - Hospital São Paulo
- UTI - Hospital Albert Einstein
- Pediatria - Hospital Infantil Sabará
- Cirurgia - Hospital Sírio-Libanês

---

## 🧪 Testando a Plataforma

### 1. Testar API REST

```bash
# Health check
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/api/stats

# Badges
curl http://localhost:8000/api/gamification/badges

# Forum categories
curl http://localhost:8000/api/forum/categories

# Shifts
curl http://localhost:8000/api/shifts/search
```

### 2. Testar Frontend

1. Abra http://localhost:8000
2. Clique em "Começar agora" (modal aparece)
3. Navegue pelos feature cards
4. Teste o chatbox no canto inferior

### 3. Testar Onboarding

1. Abra http://localhost:8000/onboarding
2. Explore as animações
3. Clique nos feature cards (modais aparecem)
4. Teste a navegação por tabs

### 4. Testar Chatbox

1. Clique no botão 🤖 no canto inferior
2. Digite uma pergunta
3. Aguarde a resposta (pode ser fallback se não configurado)
4. Teste o histórico de conversas

---

## 📱 Mobile Testing

O design é **totalmente responsivo**. Teste em:

- 📱 iPhone (375px)
- 📱 Android (360px)
- 💻 Tablet (768px)
- 🖥️ Desktop (1440px+)

---

## 🔍 Troubleshooting

### Erro: "Module not found"

```bash
pip install -r requirements.txt
```

### Erro: "No such table"

```bash
python init_database.py
python seed_data.py
```

### Erro: "Port already in use"

```bash
pkill -f "python.*app_main"
# ou
lsof -ti:8000 | xargs kill -9
```

### Chatbox não aparece

Verifique se o script está incluído:
```html
<script src="/static/js/ai-chatbox.js"></script>
```

E se o servidor está servindo arquivos estáticos:
```
http://localhost:8000/static/js/ai-chatbox.js
```

---

## 🚀 Deploy em Produção

### Replit (Recomendado para testes)

1. Clone o repositório no Replit
2. Configure as variáveis de ambiente (Secrets)
3. Execute `./start.sh`
4. Acesse a URL do Replit

### Docker

```bash
docker build -t apolocopilot .
docker run -p 8000:8000 --env-file .env apolocopilot
```

### Heroku

```bash
heroku create apolocopilot
heroku config:set $(cat .env | xargs)
git push heroku main
```

### VPS (Ubuntu)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Clone repo
git clone <repo-url>
cd ApoloCopilot

# Setup
pip3 install -r requirements.txt
python3 init_database.py
python3 seed_data.py

# Run with systemd
sudo nano /etc/systemd/system/apolocopilot.service
```

---

## 🔒 Segurança

### Checklist Antes de Produção

- [ ] Alterar `SECRET_KEY` no `.env`
- [ ] Remover `DEBUG=True`
- [ ] Configurar CORS apropriadamente
- [ ] Usar HTTPS
- [ ] Configurar rate limiting
- [ ] Backup regular do banco de dados
- [ ] Monitoramento de logs
- [ ] Firewall configurado

---

## 📈 Monitoramento

### Logs

```bash
# Ver logs do servidor
tail -f server.log

# Logs em tempo real
python app_main.py 2>&1 | tee -a server.log
```

### Métricas

Acesse:
- `/health` - Status do servidor
- `/api/stats` - Estatísticas da plataforma
- `/docs` - Documentação interativa

---

## 🆘 Suporte

### Documentação
- README principal: `README_APOLOCOPILOT.md`
- API Docs: http://localhost:8000/docs

### Links Úteis
- Twilio Docs: https://www.twilio.com/docs
- Google Calendar API: https://developers.google.com/calendar
- OpenEvidence: https://openevidence.com
- FastAPI Docs: https://fastapi.tiangolo.com

---

## ✨ Features Implementadas

✅ **10+ Features principais**
- WhatsApp Verification
- Document Verification
- GPS & Location
- Google Calendar
- Forum System
- AI Chatbot
- Badges & Trust
- Avatars
- Medical Shifts
- Voting System

✅ **Frontend Moderno**
- Design responsivo
- Animações suaves
- Dark theme
- Chatbox discreto

✅ **Backend Robusto**
- FastAPI REST API
- SQLAlchemy ORM
- JWT Authentication
- WebSocket ready

---

**🎉 Tudo pronto para usar! Boa sorte com o ApoloCopilot!**
