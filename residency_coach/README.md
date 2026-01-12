# RESIDENCY COACH

Sistema completo de preparação para residência médica com IA, gamificação e algoritmo de aprendizado adaptativo.

## Arquitetura

```
residency_coach/
├── schemas/
│   └── supabase_schema.sql      # Schema completo do banco de dados
│
├── langchain/
│   └── coach_agent.py           # Agente LangChain com ferramentas
│
├── prompts/
│   └── system_instruction.md    # System prompt do Coach
│
├── gamification/
│   └── engine.py                # BetCoins, Show do Milhão, Achievements
│
├── api/
│   └── main.py                  # FastAPI backend
│
├── landing_page/
│   └── index.html               # Landing page dark sci-fi
│
└── docs/
    └── ...                      # Documentação adicional
```

## Stack Tecnológico

- **Backend**: FastAPI + Python
- **Database**: Supabase (PostgreSQL)
- **AI/LLM**: LangChain + Claude Sonnet / GPT-4
- **Frontend**: Next.js (dashboard), HTML puro (landing)

## Funcionalidades Core

### 1. Sistema de Questões (Bullets)

- Compressão de questões em formato tático
- Tags de alta especificidade (3-6 por questão)
- Debriefing com análise de armadilhas

### 2. Algoritmo de Ponderação (Outliers)

```python
priority_weight = (
    base_error_rate *
    exposure_factor *
    recency_factor *
    exam_weight *
    (2.0 - mastery_level)
)
```

Baseado em:
- Taxa de erro do usuário por tag
- Tempo desde última revisão (spaced repetition)
- Perfil da prova-alvo (USP, Unicamp, ENARE)
- Nível de maestria calculado

### 3. Gamificação

- **BetCoins**: Moeda virtual para apostas em questões
- **Show do Milhão**: Quiz com 15 perguntas, checkpoints, lifelines
- **Achievements**: Sistema de conquistas desbloqueáveis
- **Streaks**: Sequência de dias de estudo
- **Daily Challenges**: Desafios diários com recompensas

### 4. Coach IA

Três personas integradas:
1. **Mentor Rigoroso** (60%): Técnico, guidelines, precisão
2. **Stanford Tech Optimist** (30%): Mindset de crescimento, IA como alavanca
3. **Apresentador de TV** (10%): Show do Milhão, tensão, celebração

Modos de operação:
- `BULLET`: Respostas compactas e táticas
- `DEBRIEFING`: Análise profunda de erros
- `SHOW_MILHAO`: Modo quiz dramático
- `OUTLIER`: Deep dive em temas fracos
- `VARZEA`: Descompressão e curiosidades

## API Endpoints

### Usuários
- `POST /api/users` - Criar usuário
- `GET /api/users/{id}` - Perfil e stats
- `POST /api/users/{id}/daily-login` - Login diário (streak + bonus)

### Questões
- `GET /api/questions` - Listar com filtros
- `POST /api/questions` - Criar questão
- `POST /api/questions/{id}/answer` - Responder questão
- `POST /api/questions/weighted` - **Algoritmo de ponderação**

### Show do Milhão
- `POST /api/show-milhao/start` - Iniciar sessão
- `GET /api/show-milhao/{id}/question` - Próxima pergunta
- `POST /api/show-milhao/{id}/answer` - Responder
- `POST /api/show-milhao/{id}/lifeline` - Usar ajuda
- `POST /api/show-milhao/{id}/stop` - Parar e levar prêmio

### Chat
- `POST /api/chat` - Conversar com o Coach

### Gamificação
- `GET /api/users/{id}/betcoins` - Saldo e histórico
- `GET /api/users/{id}/achievements` - Conquistas
- `GET /api/users/{id}/daily-challenge` - Desafio do dia
- `GET /api/leaderboard` - Ranking

## Setup

### 1. Banco de Dados

```bash
# Executar no Supabase SQL Editor
cat schemas/supabase_schema.sql | psql
```

### 2. Variáveis de Ambiente

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 3. Executar API

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Landing Page

```bash
cd landing_page
python -m http.server 3000
```

## Métricas de Sucesso

| Métrica | Target |
|---------|--------|
| Taxa de aprovação | > 90% |
| Retenção D7 | > 60% |
| Questões/dia/usuário | > 30 |
| Tempo médio de resposta | < 45s |
| NPS | > 70 |

## Modelo de Negócio

1. **Freemium**: 50 questões/mês grátis
2. **Basic**: R$ 97/mês - Acesso ilimitado
3. **Elite**: R$ 297/mês - Coach IA + Mentoria
4. **B2B**: Integração com Wellhub/TotalPass

---

**Powered by AI. Built for Outliers.**
