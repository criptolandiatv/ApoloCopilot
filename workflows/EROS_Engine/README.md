# 🎯 EROS Engine - Personal Branding para Relacionamento Amoroso

**EROS** = **E**stratégia de **R**elacionamento e **O**timização **S**ocial

Sistema completo de análise comportamental, desenvolvimento pessoal e inteligência estratégica para construção de relacionamentos de alto calibre.

---

## 📋 Visão Geral

O EROS Engine é composto por 4 workflows integrados que trabalham juntos para:

1. **Analisar perfis** de interesse usando arquétipos junguianos
2. **Identificar gaps** no seu desenvolvimento pessoal
3. **Trackear evolução** diária, semanal e mensal
4. **Fornecer insights** estratégicos sobre cada interação

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    EROS ENGINE - Visão Geral                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
   [ANALYZER]           [STRATEGIST]          [EXECUTOR]
  Pattern Recognition   Gap Analysis         Action Plans
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                      [FEEDBACK LOOP]
                    Continuous Learning
```

---

## 📦 Workflows Incluídos

### 1. Profile Pattern Analyzer
**Arquivo:** `0001_Profile_Pattern_Analyzer.json`

**Função:** Análise arquetípica completa de perfis do Instagram

**Input:**
```bash
curl -X POST https://your-n8n-instance.com/webhook/eros/analyze-profile \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_url": "https://instagram.com/username",
    "additional_context": "Conheci no evento X"
  }'
```

**Output:**
- Perfil arquetípico (primário, secundário, terciário)
- Lifestyle markers (classe social, círculo social)
- Padrões inconscientes
- Assinatura estética
- Indicadores de relacionamento
- **Strategic insights** (gatilhos de atração, estratégia de abordagem, conversation hooks)

**Notificação:** Telegram com resumo formatado

---

### 2. Gap Analysis & Action Plan
**Arquivo:** `0002_Gap_Analysis_Action_Plan.json`

**Função:** Análise de compatibilidade e geração de plano de ação personalizado

**Input:**
```bash
curl -X POST https://your-n8n-instance.com/webhook/eros/gap-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "target_profile": { ...resultado do analyzer... },
    "self_assessment": {
      "career_status": "7 - Desenvolvedor senior em startup",
      "financial_security": 8,
      "body_condition": 6,
      "emotional_stability": 7,
      "social_circle_quality": 5
    }
  }'
```

**Output:**
- **Compatibility Score** (0-100) com breakdown
- **Gap Analysis** detalhado por pilar
- **Action Plan** estruturado:
  - Quick Wins (30 dias)
  - Strategic Investments (90 dias)
  - Long-term Building (6-12 meses)
- **Strategic Positioning** (narrative framework, social proof roadmap)
- **Approach Playbook** (primeira interação, progressão, comunicação)
- **Measurement Framework** (KPIs para trackear)

**Notificação:** Telegram com report completo

---

### 3. Personal Brand Tracker
**Arquivo:** `0003_Personal_Brand_Tracker.json`

**Função:** Sistema de tracking diário/semanal/mensal da evolução pessoal

**Triggers:**
- **Automático:** Diariamente às 21:00 (check-in reminder)
- **Manual via Telegram:**
  - `/checkin` - Check-in manual
  - `/weekly` - Review semanal
  - `/monthly` - Deep dive mensal
  - `/stats` - Dashboard de estatísticas

**Daily Check-In Format:**
```
/log 1:S 2:S+jantar com amigos 3:N 4:S 5:S
```
Onde:
1. Academia hoje?
2. Interação social de qualidade?
3. Progresso em projeto pessoal?
4. Autocuidado estético?
5. Momento de vulnerabilidade/profundidade?

**Output:**
- Score diário (/5)
- Streak atual
- Scores por pilar (5 pilares de masculinidade)
- Weekly/Monthly trends
- Insights de evolução

---

### 4. Interaction Intelligence
**Arquivo:** `0004_Interaction_Intelligence.json`

**Função:** Análise estratégica de cada interação com prospects

**Input via Telegram (Quick Log):**
```
/interact @username type:dm energy:8 green:ela riu muito yellow:chegou atrasada next:convite café
```

**Input via Webhook:**
```bash
curl -X POST https://your-n8n-instance.com/webhook/eros/log-interaction \
  -H "Content-Type: application/json" \
  -d '{
    "person": "@username",
    "type": "presencial",
    "energy": 8,
    "topics": ["viagens", "música"],
    "flags": {
      "green": ["ela iniciou contato", "risada genuína"],
      "yellow": ["falou do ex"],
      "red": []
    },
    "next_move": "convite para café"
  }'
```

**Output:**
- **Congruence Analysis** (comportamento vs perfil arquetípico)
- **Stage Assessment** (qual estágio do relacionamento)
- **Energy Reading** (nível de interesse, tendência, sinais)
- **Flags Assessment** (green/yellow/red flags validadas)
- **Strategic Recommendation**:
  - Quando fazer próximo contato
  - Tipo de próxima interação
  - Tópicos para explorar
  - Perguntas para fazer
  - Vulnerabilidades para compartilhar
- **Escalation Advice** (pronto para escalar? como testar?)
- **Avaliação do seu movimento** (é uma boa ideia?)

**Notificação:** Telegram com análise completa

---

## 🚀 Setup Inicial

### 1. Pré-requisitos

- n8n instalado e rodando
- Conta Anthropic (Claude API)
- Bot do Telegram criado
- (Opcional) Supabase para persistência de dados

### 2. Importar Workflows

1. Acesse n8n → Workflows → Import from File
2. Importe os 4 arquivos JSON da pasta `EROS_Engine/`
3. Ative cada workflow após importar

### 3. Configurar Credenciais

#### Anthropic API
1. n8n → Credentials → Add Credential
2. Type: "HTTP Header Auth" (ou criar custom)
3. Name: "Anthropic API"
4. Configure header `x-api-key` com sua API key

#### Telegram Bot
1. Crie bot via [@BotFather](https://t.me/botfather)
2. n8n → Credentials → Add Credential
3. Type: "Telegram API"
4. Cole o token do bot
5. **Importante:** Pegue seu Chat ID
   - Envie mensagem para [@userinfobot](https://t.me/userinfobot)
   - Copie seu `Id` numérico
   - Substitua `YOUR_CHAT_ID` em todos os nós Telegram

### 4. Testar Webhooks

Cada workflow gera um webhook URL. Para encontrar:
1. Abra o workflow
2. Clique no nó "Webhook Trigger"
3. Copie a URL de produção
4. Teste com `curl` ou Postman

---

## 📊 Framework de Arquétipos Femininos

O sistema usa 7 arquétipos junguianos adaptados:

### 1. **HETAIRA** (Amante-Companheira)
- **Valores:** Beleza, prazer, conexão, intensidade
- **Indicadores:** Viagens românticas, experiências sensoriais, estética cuidada
- **Atração:** Homens com capital cultural, sensibilidade estética, presença intencional

### 2. **DONZELA** (Inocência-Alegria)
- **Valores:** Leveza, autenticidade, espontaneidade
- **Indicadores:** Natureza, amigos, diversão, otimismo
- **Atração:** Homens genuínos, aventureiros, bem-humorados

### 3. **MÃE** (Nutridora-Protetora)
- **Valores:** Proteção, nutrição, comunidade
- **Indicadores:** Família, causas sociais, cuidado com outros
- **Atração:** Homens estáveis, protetores, com valores familiares

### 4. **AMAZONA** (Guerreira-Conquistadora)
- **Valores:** Independência, conquista, autonomia
- **Indicadores:** Trabalho, esportes, desafios, resultados
- **Atração:** Homens ambiciosos, respeitosos da autonomia dela

### 5. **SACERDOTISA** (Mística-Intuitiva)
- **Valores:** Profundidade, mistério, transformação
- **Indicadores:** Espiritualidade, autoconhecimento, filosofia
- **Atração:** Homens profundos, introspectivos, conscientes

### 6. **MEDUSA** (Sedutora-Manipuladora)
- **Valores:** Controle, poder, sedução
- **Indicadores:** Provocação, jogos de poder, enigma
- **Atração/Cuidado:** Alta química mas potencial toxicidade

### 7. **ATENA** (Estrategista-Intelectual)
- **Valores:** Sabedoria, estratégia, racionalidade
- **Indicadores:** Cultura, conhecimento, análise
- **Atração:** Homens inteligentes, cultos, estratégicos

**Nota:** Ninguém é 100% um arquétipo. A análise identifica os 3 principais com % de manifestação.

---

## 💪 Framework de Masculinidade Atrativa

O sistema avalia você em 5 pilares:

### 1. **EIXO ESTRUTURAL** (Foundation)
- Missão clara além do relacionamento
- Estabilidade financeira
- Autonomia emocional

### 2. **MAGNETISMO SOCIAL** (Presence)
- Sociabilidade calibrada
- Network de valor
- Liderança situacional

### 3. **ESTÉTICA INTENCIONAL** (Presentation)
- Corpo cuidado
- Estilo coerente
- Presença visual

### 4. **PROFUNDIDADE EMOCIONAL** (Depth)
- Auto-conhecimento
- Regulação emocional
- Vulnerabilidade estratégica

### 5. **CAPITAL CULTURAL** (Substance)
- Repertório cultural
- Curiosidade genuína
- Experiências interessantes

**Cada pilar é scored de 1-10 e trackeado continuamente.**

---

## 📈 Fluxo de Uso Recomendado

### Fase 1: Setup (Semana 1)
1. ✅ Importar e configurar workflows
2. ✅ Fazer self-assessment inicial via `/gap`
3. ✅ Analisar 2-3 perfis de teste via analyzer
4. ✅ Começar daily check-ins

### Fase 2: Calibração (Semanas 2-4)
1. 📊 Manter daily check-ins consistentes
2. 📊 Rodar weekly reviews
3. 📊 Ajustar action plan baseado em feedback
4. 📊 Documentar interações reais

### Fase 3: Execução Ativa (Mês 2+)
1. 🎯 Analisar perfis de interesse real
2. 🎯 Usar strategic insights para abordagem
3. 🎯 Logar cada interação no sistema
4. 🎯 Seguir recommendations do Interaction Intelligence
5. 🎯 Re-rodar gap analysis mensalmente

---

## 🔄 Integrações Futuras

O sistema está preparado para integrar com:

- **Supabase**: Persistência de dados (prospects, interactions, tracking)
- **Apify/Phantombuster**: Scraping real de Instagram
- **Google Calendar**: Scheduling de interações
- **Notion**: Dashboard visual de progresso
- **WhatsApp**: Logs via WhatsApp em vez de Telegram

---

## ⚖️ Considerações Éticas

### ✅ O que o EROS Engine É:
- Ferramenta de **autoconhecimento** e desenvolvimento pessoal
- Sistema de **inteligência relacional** para conexões genuínas
- Framework para **comunicação mais efetiva**
- Tracking de **evolução pessoal**

### ❌ O que o EROS Engine NÃO É:
- **NÃO** é ferramenta de manipulação
- **NÃO** incentiva desonestidade
- **NÃO** trata pessoas como objetos
- **NÃO** promete resultados garantidos

### 🎯 Princípios de Uso:
1. **Autenticidade**: Use insights para se comunicar melhor, não para fingir ser quem não é
2. **Respeito**: Toda pessoa tem agência e direito de escolha
3. **Evolução Real**: Foque em se tornar genuinamente melhor, não em "truques"
4. **Consentimento**: Nunca force interação ou escalation não recíproca
5. **Privacidade**: Dados de terceiros devem ser tratados com confidencialidade

---

## 📚 Recursos Adicionais

### Leituras Recomendadas:
- "King, Warrior, Magician, Lover" - Robert Moore
- "The Way of the Superior Man" - David Deida
- "Models" - Mark Manson
- "Attached" - Amir Levine & Rachel Heller

### Conceitos-Chave:
- **Arquétipos Junguianos**: Carl Jung's psychological archetypes
- **Attachment Theory**: Teoria de apego (Bowlby)
- **Masculine Polarity**: David Deida
- **Social Dynamics**: Psicologia social e influência

---

## 🐛 Troubleshooting

### Claude API retorna erro
- Verifique se API key está correta em Credentials
- Confirme que header `x-api-key` está configurado
- Verifique limits de uso da API

### Telegram não envia mensagens
- Confirme que Chat ID está correto (número, não @username)
- Verifique se bot token está válido
- Certifique-se de ter iniciado conversa com o bot

### Scraping de Instagram falha
- Instagram bloqueia scraping fácil - considere usar Apify
- Alternativa: input manual dos dados do perfil
- Ou use serviços especializados (Phantombuster, Bright Data)

### Workflows não executam
- Verifique se estão **Ativos** (toggle no canto superior)
- Para webhooks, acesse a URL ao menos uma vez
- Para schedules, aguarde horário programado ou teste manualmente

---

## 🔐 Segurança e Privacidade

### Dados Sensíveis:
- ⚠️ **Nunca commite** credenciais no código
- ⚠️ Use variáveis de ambiente para API keys
- ⚠️ Proteja webhooks com autenticação se em produção
- ⚠️ Dados de terceiros devem ser criptografados se armazenados

### Sugestão de Stack Seguro:
```
n8n (self-hosted)
  → Supabase (Row Level Security ativado)
  → Claude API (keys em env vars)
  → Telegram (bot privado, sem admin de grupos)
```

---

## 🆘 Suporte

Para questões sobre o EROS Engine:
1. Leia este README completamente
2. Verifique logs dos workflows no n8n
3. Teste cada workflow isoladamente
4. Documente erros com screenshots

---

## 📝 Changelog

### v1.0.0 (2025-11-23)
- ✅ Workflow 1: Profile Pattern Analyzer
- ✅ Workflow 2: Gap Analysis & Action Plan
- ✅ Workflow 3: Personal Brand Tracker
- ✅ Workflow 4: Interaction Intelligence
- ✅ Framework completo de arquétipos
- ✅ Sistema de tracking de 5 pilares
- ✅ Integração Claude Sonnet 4.5
- ✅ Notificações via Telegram

---

## 📄 Licença

Este é um projeto open-source para fins educacionais e de desenvolvimento pessoal.

**Disclaimer:** Use com responsabilidade e ética. Os criadores não se responsabilizam por uso inadequado do sistema.

---

## 🎯 Próximos Passos

Depois de configurar o EROS Engine:

1. **Faça seu primeiro profile analysis**
2. **Rode seu gap analysis inicial**
3. **Configure daily check-ins**
4. **Documente primeira interação**
5. **Revise weekly para ajustar estratégia**

**Lembre-se:** O objetivo final não é "hackear" relacionamentos, mas se tornar a melhor versão de si mesmo enquanto entende melhor a dinâmica humana.

Boa jornada! 🚀
