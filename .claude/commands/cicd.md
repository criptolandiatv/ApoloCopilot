---
description: 🎯 Setup completo de CI/CD pipeline
---

Crie pipeline CI/CD completo:

**GitHub Actions Workflow:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    - Linting (flake8, eslint)
    - Type checking (mypy, typescript)
    - Unit tests
    - Integration tests
    - Coverage report

  build:
    - Build Docker image
    - Security scan (Trivy)
    - Push to registry

  deploy:
    - Deploy to staging
    - Run smoke tests
    - Deploy to production
    - Health check
    - Rollback on failure

  notify:
    - Slack notification
    - Email on failure
```

**Ferramentas:**
- GitHub Actions / GitLab CI
- Docker / Kubernetes
- Terraform (IaC)
- ArgoCD (GitOps)

**Ambientes:**
- Development
- Staging
- Production

**Monitoring:**
- Sentry (errors)
- DataDog (APM)
- Prometheus + Grafana

Crie os arquivos necessários em `.github/workflows/`
