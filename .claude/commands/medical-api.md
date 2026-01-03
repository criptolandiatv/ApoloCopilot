---
description: 🏥 Cria endpoint médico completo com validação
---

Crie um endpoint REST API médico profissional:

**Estrutura:**
```python
@router.post("/medical/{resource}")
async def create_{resource}(
    data: {Resource}Create,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
```

**Validações:**
- Pydantic models com validators
- Business rules (medical protocols)
- HIPAA compliance checks
- Data sanitization

**Segurança:**
- JWT authentication
- Role-based access (médico, enfermeiro, admin)
- Audit logging
- Data encryption at rest

**Documentação:**
- OpenAPI schema completo
- Request/response examples
- Error codes documentados
- Rate limiting info

**Features:**
- Pagination
- Filtering
- Sorting
- Search
- Export (PDF/Excel)

**Compliance:**
- HIPAA
- LGPD
- ISO 27001

Recurso médico: ${1:patient/appointment/prescription/exam}
