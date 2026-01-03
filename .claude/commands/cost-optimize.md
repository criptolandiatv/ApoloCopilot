---
description: 💰 Analisa custos de API e sugere otimizações
---

Analise o uso de APIs e custos:

**Análise de Custos:**
1. **Tokens Usage**
   - Requests por endpoint
   - Tamanho médio de payload
   - Cache hit rate
   - Custo estimado mensal

2. **OpenAI/Anthropic**
   - Tokens por request
   - Modelo usado (GPT-4, Claude, etc)
   - Oportunidades de usar modelos menores
   - Prompt optimization

3. **Third-party APIs**
   - Twilio calls
   - Google Calendar sync
   - Database queries
   - External services

**Otimizações:**
- [ ] Implementar caching agressivo
- [ ] Usar modelos menores para tarefas simples
- [ ] Batch requests quando possível
- [ ] Comprimir payloads
- [ ] Rate limiting inteligente
- [ ] Retry com exponential backoff

**Economia Estimada:**
- Atual: $XXX/mês
- Otimizado: $YYY/mês
- Economia: $ZZZ/mês (XX%)

Gere relatório detalhado com recomendações específicas.
