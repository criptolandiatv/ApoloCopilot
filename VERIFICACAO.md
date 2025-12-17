# ✅ Checklist de Verificação - ApoloCopilot

Use este guia para verificar se tudo está funcionando corretamente.

---

## 📋 Checklist Pré-Deploy

### 1. Dependências
```bash
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|twilio)"
```
✅ Deve mostrar as versões instaladas

### 2. Database
```bash
ls -lh database/apolocopilot.db
```
✅ Arquivo deve existir (tamanho > 100KB)

### 3. Seed Data
```bash
python -c "from database import SessionLocal; from models.gamification import Badge; db = SessionLocal(); print(f'Badges: {db.query(Badge).count()}'); db.close()"
```
✅ Deve mostrar "Badges: 7"

### 4. Estrutura de Arquivos
```bash
tree -L 2 -I '__pycache__|*.pyc|node_modules|.git'
```
✅ Deve mostrar toda a estrutura organizada

---

## 🧪 Testes Funcionais

### Test 1: Server Health
```bash
# Inicie o servidor em background
python app_main.py &
sleep 5

# Teste health endpoint
curl http://localhost:8000/health

# Resultado esperado:
# {"status":"healthy","message":"ApoloCopilot is running","features":[...]}
```

### Test 2: API Stats
```bash
curl http://localhost:8000/api/stats

# Resultado esperado:
# {"total":0,"active":0,"inactive":0,...}
```

### Test 3: Badges
```bash
curl http://localhost:8000/api/gamification/badges

# Resultado esperado: Array com 7 badges
```

### Test 4: Forum Categories
```bash
curl http://localhost:8000/api/forum/categories

# Resultado esperado: Array com 6 categorias
```

### Test 5: Shifts
```bash
curl http://localhost:8000/api/shifts/search

# Resultado esperado: Array com 4 plantões de exemplo
```

### Test 6: Shift Types
```bash
curl http://localhost:8000/api/shifts/types

# Resultado esperado: Lista de tipos de plantão
```

### Test 7: Chat Info
```bash
curl http://localhost:8000/api/chat/info

# Resultado esperado: Informações do chatbot
```

### Test 8: Static Files
```bash
curl -I http://localhost:8000/static/js/ai-chatbox.js

# Resultado esperado: HTTP/1.1 200 OK
```

### Test 9: Frontend Pages
```bash
# Index
curl -I http://localhost:8000/

# Onboarding
curl -I http://localhost:8000/onboarding

# Docs
curl -I http://localhost:8000/docs

# Resultado esperado: HTTP/1.1 200 OK para todos
```

---

## 🎨 Verificação Visual

### Checklist Frontend

#### Página Principal (/)
- [ ] Logo e header carregam
- [ ] Features cards aparecem
- [ ] Botões funcionam
- [ ] Links para /docs e /redoc funcionam
- [ ] Chatbox aparece no canto inferior
- [ ] Design responsivo funciona

#### Onboarding (/onboarding)
- [ ] Animações de background (shapes flutuantes)
- [ ] Hero section com gradient text
- [ ] Stats counters (10+, 100%, ∞)
- [ ] Feature cards com hover effects
- [ ] Modal de onboarding abre ao clicar "Começar agora"
- [ ] Modals de features abrem ao clicar nos cards
- [ ] Code blocks com syntax highlighting
- [ ] Tabs na header funcionam
- [ ] Chatbox integrado

#### AI Chatbox
- [ ] Botão 🤖 visível no canto
- [ ] Pulsa suavemente (animação)
- [ ] Abre ao clicar
- [ ] Modal com design moderno
- [ ] Header com gradiente
- [ ] Mensagem de boas-vindas
- [ ] Input field funciona
- [ ] Botão de enviar funciona
- [ ] Indicador de digitação aparece
- [ ] Link "Powered by OpenEvidence" funciona
- [ ] Fecha com X ou clicando fora
- [ ] ESC fecha o modal
- [ ] Responsivo em mobile

---

## 🔐 Verificação de Segurança

### Checklist de Segurança

- [ ] `.env` não está no Git
- [ ] `.env.example` existe
- [ ] SECRET_KEY não é o padrão
- [ ] Passwords são hashados (bcrypt)
- [ ] JWT tokens têm expiração
- [ ] CORS configurado apropriadamente
- [ ] SQL injection protegido (SQLAlchemy)
- [ ] XSS protection no frontend
- [ ] Rate limiting (se necessário)

---

## 📊 Verificação de Database

### Tables Criadas
```bash
sqlite3 database/apolocopilot.db ".tables"
```

Deve mostrar:
```
avatars                 shift_applications
badges                  shift_filters
calendar_events         shifts
chat_messages           trust_scores
document_verifications  user_badges
forum_categories        user_locations
forum_posts             users
forum_threads           votes
phone_verifications
```

### Count de Registros
```bash
sqlite3 database/apolocopilot.db "
SELECT
    'badges' as table_name, COUNT(*) as count FROM badges
UNION ALL SELECT 'forum_categories', COUNT(*) FROM forum_categories
UNION ALL SELECT 'shifts', COUNT(*) FROM shifts;
"
```

Resultado esperado:
```
badges|7
forum_categories|6
shifts|4
```

---

## 🚀 Verificação de Performance

### Load Test Simples
```bash
# Instalar ab (Apache Bench) se necessário
# sudo apt-get install apache2-utils

# Teste 100 requests
ab -n 100 -c 10 http://localhost:8000/health

# Deve completar com sucesso
```

### Response Time
```bash
curl -w "\nTime: %{time_total}s\n" -o /dev/null -s http://localhost:8000/api/stats

# Deve ser < 1 segundo
```

---

## 📱 Teste Mobile

### Chrome DevTools
1. F12 → Toggle Device Toolbar
2. Testar em:
   - iPhone SE (375px)
   - iPhone 12 Pro (390px)
   - iPad (768px)
   - Desktop (1440px)

### Checklist Mobile
- [ ] Layout se adapta
- [ ] Chatbox funciona
- [ ] Modals são responsivos
- [ ] Botões são tocáveis (min 44px)
- [ ] Texto legível
- [ ] Performance adequada

---

## 🔗 Verificação de Links

### Links Internos
```bash
# Criar script de teste
cat > test_links.sh << 'EOF'
#!/bin/bash
BASE="http://localhost:8000"

echo "Testing internal links..."
for path in / /onboarding /docs /redoc /health; do
    status=$(curl -s -o /dev/null -w "%{http_code}" $BASE$path)
    echo "$path: $status"
done
EOF

chmod +x test_links.sh
./test_links.sh
```

### Links Externos
- [ ] OpenEvidence link funciona
- [ ] GitHub links funcionam (se houver)
- [ ] Documentação externa funciona

---

## ✅ Checklist Final

### Antes de Considerar Completo

- [ ] Todas as dependências instaladas
- [ ] Database inicializado
- [ ] Seed data populado
- [ ] Servidor inicia sem erros
- [ ] API endpoints respondem
- [ ] Frontend carrega corretamente
- [ ] Chatbox funciona
- [ ] Mobile responsivo
- [ ] Testes passam
- [ ] Performance aceitável
- [ ] Segurança verificada
- [ ] Documentação completa
- [ ] Git commitado e pushed

---

## 🎯 Score

Conte quantos ✅ você conseguiu:

- **80-100%**: 🎉 Excelente! Pronto para produção
- **60-79%**: 😊 Muito bom! Pequenos ajustes necessários
- **40-59%**: 🤔 Funcionando, mas precisa de melhorias
- **< 40%**: 🔧 Revisar instalação e configuração

---

## 🆘 Se Algo Não Funcionar

### 1. Verificar Logs
```bash
tail -f server.log
```

### 2. Reiniciar Database
```bash
rm -f database/apolocopilot.db
python init_database.py
python seed_data.py
```

### 3. Reinstalar Dependências
```bash
pip install --force-reinstall -r requirements.txt
```

### 4. Verificar Portas
```bash
lsof -i :8000
# Se ocupada, matar processo ou usar outra porta
```

### 5. Limpar Cache
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## 📞 Ajuda

Se ainda tiver problemas:

1. Verifique `DEPLOYMENT.md`
2. Verifique `README_APOLOCOPILOT.md`
3. Verifique logs: `server.log`
4. Teste APIs em `/docs`

---

**✨ Boa sorte com o ApoloCopilot!**
