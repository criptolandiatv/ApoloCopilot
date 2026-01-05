# ⚡ Quick Start Guide - Templates Escaláveis

> **Do zero ao deploy em 15 minutos**

---

## 🎯 Escolha Seu Template (2 min)

### Por Use Case

| Use Case | Template Recomendado | Tempo de Setup |
|----------|---------------------|----------------|
| **AI/Chatbots** | 01 - AI Intelligence Engine | 10 min |
| **Data Processing** | 02 - Data Pipeline | 15 min |
| **Team Communication** | 03 - Command Center | 12 min |
| **User Growth** | 04 - Viral Growth Engine | 15 min |
| **DevOps/CI/CD** | 05 - Test & Deploy | 20 min |
| **Innovation/Research** | 06 - Rebel Integrations | 10 min |

### Por Complexidade

| Nível | Templates | Ideal Para |
|-------|-----------|-----------|
| **Iniciante** | 01, 03 | Primeiros workflows |
| **Intermediário** | 02, 04 | Já tem experiência |
| **Avançado** | 05, 06 | Expert em n8n |

---

## 🚀 Setup em 3 Passos

### Passo 1: Instalar n8n (5 min)

```bash
# Opção A: Docker (Recomendado)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Opção B: npm
npm install -g n8n
n8n start

# Opção C: n8n Cloud
# https://n8n.io/cloud
```

### Passo 2: Configurar Credentials (5 min)

**No n8n UI:**
1. Abra `http://localhost:5678`
2. Vá para **Settings → Credentials**
3. Adicione suas credentials:

#### Template 01 - AI Intelligence
```
✓ OpenAI API
✓ Anthropic API
✓ Airtable API
```

#### Template 02 - Data Pipeline
```
✓ PostgreSQL
✓ MongoDB
✓ AWS Credentials
✓ Telegram Bot
```

#### Template 03 - Command Center
```
✓ Telegram Bot
✓ Slack API
✓ Discord Bot
✓ MS Teams OAuth2
✓ MongoDB
```

#### Template 04 - Viral Growth
```
✓ PostgreSQL
✓ Twitter OAuth
✓ LinkedIn OAuth2
✓ Telegram Bot
✓ SMTP
✓ MongoDB
```

#### Template 05 - CI/CD
```
✓ GitHub API
✓ Slack API
```

#### Template 06 - Rebel Integrations
```
✓ OpenAI API
✓ Anthropic API
✓ Groq API
✓ Replicate API
✓ Airtable API
✓ Notion API
```

### Passo 3: Importar & Ativar (5 min)

**No n8n UI:**
1. Clique no **Menu (☰)** → **Import workflow**
2. Selecione o arquivo `.json` do template
3. Configure as credentials nos nós
4. Clique em **Save** e **Activate**

**Pronto! 🎉**

---

## 🧪 Testar Seus Templates

### Template 01 - AI Intelligence Engine

```bash
# Test endpoint
curl -X POST http://localhost:5678/webhook/ai-process \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate",
    "prompt": "Explain AI in simple terms"
  }'

# Expected response time: < 2s
# Expected format: JSON with best_response
```

### Template 02 - Data Pipeline

```bash
# Test webhook ingest
curl -X POST http://localhost:5678/webhook/data-ingest \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "value": 123.45,
    "category": "sales",
    "status": "active",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Check PostgreSQL
psql -d n8n_data -c "SELECT COUNT(*) FROM data_warehouse;"

# Expected: Record inserted successfully
```

### Template 03 - Command Center

```bash
# Test via Telegram
# Send message to your bot:
/status all

# Expected: Status response
# Response time: < 500ms
```

### Template 04 - Viral Growth Engine

```bash
# Test user action
curl -X POST http://localhost:5678/webhook/user-action \
  -H "Content-Type: application/json" \
  -d '{
    "type": "share",
    "user_id": "user123",
    "connections": 10,
    "engagement": 0.8
  }'

# Expected: Referral links generated
# K-Factor calculated
```

### Template 05 - CI/CD Pipeline

```bash
# Configure GitHub webhook
# Settings → Webhooks → Add webhook
# URL: http://your-n8n.com/webhook/github-events
# Events: Push, Pull Request

# Test: Push to repository
git push origin develop

# Expected: Auto-deploy triggered
# Notifications sent to Slack
```

### Template 06 - Rebel Integrations

```bash
# Test multi-AI request
curl -X POST http://localhost:5678/webhook/rebel-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a creative story about AI",
    "image_prompt": "Futuristic AI cityscape"
  }'

# Expected: Responses from 4+ AI providers
# Best response ranked
# Response time: 3-5s
```

---

## 🎛 Configurações Avançadas

### Environment Variables

Crie arquivo `.env` na raiz do n8n:

```bash
# AI Providers
OPENAI_API_KEY=sk-proj-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GROQ_API_KEY=gsk_xxx

# Databases
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=n8n_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

MONGODB_URI=mongodb://localhost:27017/n8n

# AWS
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1

# Communication
TELEGRAM_BOT_TOKEN=123456:ABC...
SLACK_TOKEN=xoxb-...
DISCORD_BOT_TOKEN=MTAx...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_REPO=username/repo
GITHUB_REPO_URL=https://github.com/username/repo.git

# Docker & K8s
DOCKER_IMAGE=your-registry/your-app
APP_NAME=your-app

# Notification Channels
SLACK_DEPLOY_CHANNEL=C0XXXXXXX
TELEGRAM_ADMIN_CHAT=123456789
GROWTH_TEAM_CHAT=987654321

# Health Check
HEALTH_CHECK_URL=https://your-app.com/health

# Database IDs
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
NOTION_DATABASE_ID=abc123...

# Queue URLs
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/xxx/queue
```

### Executar com Environment Variables

```bash
# Opção 1: Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  --env-file .env \
  n8nio/n8n

# Opção 2: npm
export $(cat .env | xargs)
n8n start

# Opção 3: n8n Cloud
# Configure no UI: Settings → Environment Variables
```

---

## 🔧 Troubleshooting

### Problema: "Credential not found"

**Solução:**
```bash
# 1. Verifique se credential foi criada
# Settings → Credentials → Busque pelo nome

# 2. Reconecte no nó
# Clique no nó → Credential → Select → Save

# 3. Teste a conexão
# Clique em "Test" no credential
```

### Problema: "Webhook timeout"

**Solução:**
```bash
# Aumente timeout no nó Webhook
# Webhook → Settings → Response timeout → 30000ms

# Configure timeout no servidor
export N8N_WEBHOOK_TIMEOUT=30000
```

### Problema: "Rate limit exceeded"

**Solução:**
```javascript
// Adicione rate limiting
// Settings → Execution Settings
{
  "executions.concurrency": 5,
  "executions.timeout": 60
}

// Ou use queue mode
export EXECUTIONS_MODE=queue
export QUEUE_BULL_REDIS_HOST=localhost
```

### Problema: "Database connection failed"

**Solução:**
```bash
# Verifique se DB está rodando
docker ps | grep postgres
docker ps | grep mongo

# Teste conexão manualmente
psql -h localhost -U postgres -d n8n_data
mongo mongodb://localhost:27017

# Verifique firewall/security groups
```

### Problema: "AI API error"

**Solução:**
```bash
# Verifique API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Verifique billing/credits
# https://platform.openai.com/account/billing

# Use modelo alternativo
# gpt-4 → gpt-4o-mini (mais barato)
```

---

## 📊 Monitoring & Logs

### n8n Built-in

```bash
# Acesse executions history
# n8n UI → Executions

# Filtros úteis:
- Status: Failed
- Time range: Last 24h
- Workflow: Specific template

# Export logs
# Executions → Select → Download
```

### External Monitoring

```bash
# Prometheus + Grafana
# Adicione métricas ao workflow:

# Node: HTTP Request
GET http://pushgateway:9091/metrics/job/n8n
Body: workflow_executions_total{status="success"} 1

# Dashboard templates:
# https://grafana.com/dashboards
```

### Log Aggregation

```bash
# Loki + Promtail
# Configure log shipping:

docker run -d \
  --name promtail \
  -v /var/log:/var/log \
  grafana/promtail:latest \
  -config.file=/etc/promtail/config.yml
```

---

## 🎓 Recursos de Aprendizado

### Documentação Official
- [n8n Docs](https://docs.n8n.io/) - Docs completos
- [n8n Community](https://community.n8n.io/) - Forum
- [n8n YouTube](https://youtube.com/n8n) - Video tutorials

### Templates & Examples
- [n8n Workflows](https://n8n.io/workflows/) - 1000+ templates
- [GitHub n8n-io](https://github.com/n8n-io/n8n) - Source code
- [Reddit r/n8n](https://reddit.com/r/n8n) - Community

### Cursos & Tutorials
- [n8n Academy](https://n8n.io/academy/) - Free courses
- [YouTube Tutorials](https://youtube.com/results?search_query=n8n+tutorial)
- [Medium Articles](https://medium.com/tag/n8n)

---

## 🚀 Próximos Passos

### Nível 1: Básico ✅
- [x] Instalar n8n
- [x] Importar 1 template
- [x] Configurar credentials
- [x] Testar workflow
- [x] Ativar workflow

### Nível 2: Intermediário 🔄
- [ ] Customizar template
- [ ] Adicionar error handling
- [ ] Configurar monitoring
- [ ] Deploy em produção
- [ ] Documentar mudanças

### Nível 3: Avançado 🎯
- [ ] Criar custom nodes
- [ ] Implementar CI/CD
- [ ] Scale horizontally
- [ ] Otimizar performance
- [ ] Contribuir templates

---

## 💡 Tips Rápidos

### Performance
```javascript
// 1. Use batching
{ batchSize: 1000 }

// 2. Parallel execution
{ mode: "parallel" }

// 3. Cache responses
{ cache: { ttl: 3600 } }
```

### Segurança
```javascript
// 1. Rotate credentials mensalmente
// 2. Use diferentes keys por ambiente
// 3. Limite access por IP
// 4. Enable 2FA em todas accounts
```

### Cost Optimization
```javascript
// 1. Use modelos baratos quando possível
// gpt-4o-mini vs gpt-4: 10x cheaper

// 2. Cache AI responses
// Reduce API calls 80%

// 3. Batch processing
// Reduce overhead 90%
```

---

## ✅ Checklist de Produção

Antes de ir para produção:

### Segurança
- [ ] Credentials em vault/secrets manager
- [ ] API keys rotacionadas
- [ ] HTTPS configurado
- [ ] Firewall rules aplicadas
- [ ] Rate limiting configurado

### Performance
- [ ] Load testing executado
- [ ] Caching implementado
- [ ] Database indexes criados
- [ ] Timeouts ajustados
- [ ] Connection pooling configurado

### Reliability
- [ ] Error handling completo
- [ ] Retry logic implementada
- [ ] Health checks configurados
- [ ] Alertas configurados
- [ ] Backup strategy definida

### Monitoring
- [ ] Logs centralizados
- [ ] Métricas coletadas
- [ ] Dashboards criados
- [ ] Alertas configurados
- [ ] SLA definidos

### Documentation
- [ ] README atualizado
- [ ] API docs geradas
- [ ] Runbooks criados
- [ ] Incident procedures definidos
- [ ] Team training completado

---

**Pronto para escalar! 🚀**

*Tempo total estimado: 15-30 minutos*

---

**Need help? Join our community!**
- Discord: [n8n Community](https://discord.gg/n8n)
- Forum: [community.n8n.io](https://community.n8n.io)
- GitHub: [Issues](https://github.com/n8n-io/n8n/issues)
