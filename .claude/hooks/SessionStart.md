---
description: 🚀 Auto-setup ao iniciar sessão Claude Code
---

# Session Start Hook - ApoloCopilot

Executando setup automático...

## 1. Environment Check ✅
- Python version: {{ python --version }}
- Node version: {{ node --version }}
- Database status: {{ ls -lh database/*.db | tail -1 }}

## 2. Git Status 📊
{{ git status --short }}

## 3. Recent Changes 📝
{{ git log --oneline -5 }}

## 4. Server Health 💓
Verificando se o servidor está rodando...
{{ curl -s http://localhost:8000/health 2>/dev/null || echo "⚠️ Servidor não está rodando" }}

## 5. Quick Commands Available 🎯

Use estes comandos para máxima produtividade:

- `/optimize` - Analisa performance do código
- `/ui-component` - Cria componente UI completo
- `/dashboard` - Cria dashboard com gráficos
- `/test-suite` - Gera testes automatizados
- `/medical-api` - Cria endpoint médico
- `/cost-optimize` - Analisa custos de API
- `/cicd` - Setup CI/CD pipeline
- `/review` - Code review com IA
- `/monitoring` - Setup observabilidade
- `/design-system` - Aplica design profissional
- `/medical-feature` - Feature médica completa

## 6. Produtividade Tips 💡

**Atalhos úteis:**
- Ctrl+K → Busca rápida
- Ctrl+P → Abrir arquivo
- Ctrl+Shift+P → Comandos

**Best Practices:**
- Commit frequentemente
- Teste antes de push
- Use type hints
- Documente APIs

## 7. Próximos Passos Sugeridos 🎯

Baseado no estado atual do projeto:

1. Executar testes: `pytest`
2. Verificar lint: `flake8 . --count`
3. Atualizar deps: `pip list --outdated`
4. Review de código: `/review`

---

✨ **Pronto para desenvolver com maestria!**

Digite `/help` para ver mais comandos ou comece a codificar!
