# 🗄️ NOTION SETUP - Databases Completas

Configuração detalhada das 3 databases do Notion com estrutura visual e templates.

---

## 📊 VISÃO GERAL

O sistema usa **3 databases interconectadas**:

```
🔍 REGISTRO_DEFEITOS
    ↓ (relação)
🦠 PLANOS_REPARO
    ↓ (validação)
📈 EVOLUÇÃO_TAXA_ERRO
```

---

## DATABASE 1: 🔍 REGISTRO_DEFEITOS

**Descrição:** Todos os defeitos críticos identificados pelos 3 Caçadores

### Estrutura Completa

| Nome | Tipo | Opções/Config | Descrição |
|------|------|---------------|-----------|
| **ID** | Title | - | Identificador único (ex: DEF_1737890123_0) |
| **Categoria** | Select | MODELO_NEGOCIO<br>PRODUTO_COMUNIDADE<br>CULTURA_EXECUCAO<br>EFEITO_COLATERAL | Origem do defeito detectado |
| **Caçador** | Select | CAÇADOR #1<br>CAÇADOR #2<br>CAÇADOR #3 | Qual agente detectou |
| **Severidade** | Select | CRÍTICA<br>ALTA<br>MÉDIA | Nível de gravidade |
| **Defeito** | Text | Long text habilitado | Descrição concisa do problema |
| **Probabilidade Colapso %** | Number | Format: Percent<br>0-100 | Chance de morte do negócio |
| **Prazo Morte (meses)** | Number | - | Tempo estimado até colapso |
| **Análise Completa** | Text | Long text habilitado | Output completo JSON do Caçador |
| **Status** | Select | AGUARDANDO_BACTERIAS<br>EM_REPARO<br>VALIDADO<br>REJEITADO | Estado atual do defeito |
| **Data Detecção** | Date | Include time | Timestamp de criação |
| **Bactérias Ativadas Em** | Date | Include time | Quando reparo iniciou |
| **Total Ações Criadas** | Number | - | Quantas tasks foram geradas |
| **Prioridade Atribuída** | Select | P1<br>P2<br>P3 | Prioridade do reparo |

### Views Recomendadas

#### 1. 🔴 CRÍTICOS ATIVOS (Table)

**Filtros:**
- Status ≠ VALIDADO
- Severidade = CRÍTICA

**Ordenação:**
- Probabilidade Colapso % (descendente)
- Prazo Morte (ascendente)

**Propriedades visíveis:**
- ID, Categoria, Defeito, Probabilidade Colapso %, Prazo Morte, Status

#### 2. ⏳ AGUARDANDO REPARO (Board)

**Agrupado por:** Categoria

**Filtro:**
- Status = AGUARDANDO_BACTERIAS

**Ordenação:**
- Probabilidade Colapso % (descendente)

#### 3. 🔧 EM REPARO (Timeline)

**Timeline por:** Data Detecção

**Filtro:**
- Status = EM_REPARO

**Exibir:**
- Barra de tempo com deadline baseado em Prazo Morte

#### 4. ✅ VALIDADOS (Gallery)

**Filtro:**
- Status = VALIDADO

**Gallery preview:** Defeito

**Ordenação:**
- Data Detecção (descendente)

#### 5. 📊 Por Categoria (Table)

**Agrupado por:** Categoria

**Sem filtros** (mostra tudo)

**Subtotais:**
- Count de defeitos por categoria
- Média de Probabilidade Colapso %

### Configuração de Cores

**Status:**
- 🟡 AGUARDANDO_BACTERIAS → Amarelo
- 🔵 EM_REPARO → Azul
- 🟢 VALIDADO → Verde
- 🔴 REJEITADO → Vermelho

**Severidade:**
- 🔴 CRÍTICA → Vermelho
- 🟠 ALTA → Laranja
- 🟡 MÉDIA → Amarelo

**Categoria:**
- 🔴 MODELO_NEGOCIO → Vermelho
- 🟣 PRODUTO_COMUNIDADE → Roxo
- 🔵 CULTURA_EXECUCAO → Azul
- ⚠️ EFEITO_COLATERAL → Cinza

### Template de Entrada

Use este template ao criar defeitos manualmente:

```
ID: DEF_[timestamp]_[index]
Categoria: [escolher]
Caçador: [escolher]
Severidade: CRÍTICA
Defeito: [descrição de 1-2 linhas]
Probabilidade Colapso %: [0-100]
Prazo Morte (meses): [número]
Análise Completa: [JSON completo do Claude]
Status: AGUARDANDO_BACTERIAS
Data Detecção: [hoje]
```

---

## DATABASE 2: 🦠 PLANOS_REPARO

**Descrição:** Ações obsessivas de correção criadas pelas Bactérias

### Estrutura Completa

| Nome | Tipo | Opções/Config | Descrição |
|------|------|---------------|-----------|
| **ID Reparo** | Title | - | Identificador único (ex: REPARO_1737890456_0) |
| **Defeito Origem** | Relation | → REGISTRO_DEFEITOS<br>Show on REGISTRO_DEFEITOS | Link para defeito que gerou este reparo |
| **Categoria** | Rollup | Relation: Defeito Origem<br>Property: Categoria<br>Calculate: Show original | Categoria herdada do defeito |
| **Prioridade** | Select | P1 (0-3m)<br>P2 (3-12m)<br>P3 (12m+) | Urgência baseada em risco |
| **Score Letalidade** | Number | Format: 0.0<br>Range: 0-10 | Risco de morte (calculado pelas Bactérias) |
| **Ação** | Text | Long text habilitado | Tarefa específica a executar |
| **Prazo (dias)** | Number | - | Tempo para executar |
| **Data Limite** | Date | Include time | Deadline calculado (Data Criação + Prazo dias) |
| **Responsável** | Person | - | Quem executa (geralmente ADMIN) |
| **Resultado Esperado** | Text | Long text habilitado | Output tangível esperado |
| **Métrica Sucesso** | Text | - | Número que PROVA correção |
| **Critério Sucesso** | Text | Long text habilitado | Como saberemos que funcionou |
| **Status** | Select | PENDENTE<br>EM_EXECUÇÃO<br>CONCLUÍDO<br>VALIDADO<br>REJEITADO | Estado da tarefa |
| **Data Criação** | Created time | Include time | Auto-gerado pelo Notion |
| **Validado Em** | Date | Include time | Quando validação aprovou |
| **Rejeitado Em** | Date | Include time | Quando validação reprovou |
| **Motivo Rejeição** | Text | Long text habilitado | Por que foi rejeitado |
| **Validação** | Text | Long text habilitado | Output do Claude validador |

### Views Recomendadas

#### 1. 🔥 P1 - COLAPSO IMINENTE (Table)

**Filtros:**
- Prioridade = P1 (0-3m)
- Status ≠ VALIDADO

**Ordenação:**
- Score Letalidade (descendente)
- Data Limite (ascendente)

**Highlight:**
- Data Limite < Hoje → Vermelho

#### 2. ⚡ EM EXECUÇÃO (Kanban)

**Board por:** Status

**Colunas:**
- PENDENTE
- EM_EXECUÇÃO
- CONCLUÍDO
- VALIDADO
- REJEITADO

**Filtro:**
- Nenhum (mostra tudo)

**Cartão mostra:**
- Ação
- Prazo (dias)
- Prioridade badge
- Responsável

#### 3. ✅ CONCLUÍDOS (Table)

**Filtro:**
- Status = CONCLUÍDO

**Ordenação:**
- Data Limite (descendente)

**Propriedades:**
- ID Reparo, Ação, Resultado Esperado, Métrica Sucesso

#### 4. ⏰ Timeline por Prazo (Timeline)

**Timeline por:** Data Limite

**Filtro:**
- Status ≠ VALIDADO
- Status ≠ REJEITADO

**Cores por:** Prioridade

#### 5. 📋 Por Categoria (Table)

**Agrupado por:** Categoria (via Rollup)

**Ordenação:**
- Prioridade
- Score Letalidade

**Subtotais:**
- Count por categoria
- Média Score Letalidade

### Configuração de Cores

**Prioridade:**
- 🔴 P1 (0-3m) → Vermelho escuro
- 🟠 P2 (3-12m) → Laranja
- 🟡 P3 (12m+) → Amarelo

**Status:**
- ⚪ PENDENTE → Cinza
- 🔵 EM_EXECUÇÃO → Azul
- 🟢 CONCLUÍDO → Verde claro
- ✅ VALIDADO → Verde escuro
- 🔴 REJEITADO → Vermelho

### Template de Entrada

```
ID Reparo: REPARO_[timestamp]_[index]
Defeito Origem: [selecionar da database REGISTRO_DEFEITOS]
Prioridade: [P1/P2/P3]
Score Letalidade: [0-10]
Ação: [ação específica e executável]
Prazo (dias): [número]
Data Limite: [auto-calculado]
Responsável: [pessoa]
Resultado Esperado: [output tangível]
Métrica Sucesso: [número que prova correção]
Critério Sucesso: [como saberemos - número não opinião]
Status: PENDENTE
```

---

## DATABASE 3: 📈 EVOLUÇÃO_TAXA_ERRO

**Descrição:** Métrica primária - ERRAR CADA VEZ MENOS

### Estrutura Completa

| Nome | Tipo | Opções/Config | Descrição |
|------|------|---------------|-----------|
| **Período** | Title | - | Data ou descrição (ex: "2025-W03" para semana 3) |
| **Taxa Erro Atual** | Number | - | Defeitos detectados no período atual |
| **Taxa Erro Anterior** | Number | - | Defeitos do período anterior (para comparação) |
| **Melhoria %** | Formula | `round(((prop("Taxa Erro Anterior") - prop("Taxa Erro Atual")) / prop("Taxa Erro Anterior")) * 100)` | Redução percentual de erros |
| **Status Evolução** | Select | 📈 EVOLUINDO<br>➡️ ESTAGNADO<br>📉 REGREDINDO | Tendência |
| **Total Histórico** | Number | - | Defeitos acumulados desde início |
| **Última Atualização** | Date | Include time | Timestamp da última execução |

### Views Recomendadas

#### 1. 📊 Gráfico Evolução (Table → Convert to Chart)

**Tipo:** Line chart

**X-axis:** Período

**Y-axis:** Taxa Erro Atual, Taxa Erro Anterior

**Ordenação:**
- Período (ascendente)

**Exibir:**
- Linha Taxa Atual (azul)
- Linha Taxa Anterior (cinza)
- Área de melhoria entre linhas (verde se melhorou)

#### 2. 📈 Tabela Completa (Table)

**Ordenação:**
- Período (descendente)

**Propriedades:**
- Todas visíveis

**Highlight:**
- Melhoria % > 0 → Verde
- Melhoria % < 0 → Vermelho
- Melhoria % = 0 → Amarelo

#### 3. 🎯 Últimos 3 Meses (Table)

**Filtro:**
- Última Atualização > 90 dias atrás

**Ordenação:**
- Período (descendente)

**Limit:** 12 (se semanal) ou 3 (se mensal)

### Configuração de Cores

**Status Evolução:**
- 📈 EVOLUINDO → Verde
- ➡️ ESTAGNADO → Amarelo
- 📉 REGREDINDO → Vermelho

### Template de Entrada

```
Período: [YYYY-Www] (ex: 2025-W03)
Taxa Erro Atual: [número de defeitos desta semana]
Taxa Erro Anterior: [número de defeitos semana passada]
Melhoria %: [auto-calculado]
Status Evolução: [auto-determinado pelo workflow]
Total Histórico: [soma acumulada]
Última Atualização: [agora]
```

---

## 🎨 DASHBOARD PRINCIPAL

Crie uma página Notion com este layout:

### Estrutura da Página

```markdown
# 🦠 SISTEMA CAÇADORES + BACTÉRIAS

## 📊 MÉTRICA PRIMÁRIA: ERRAR CADA VEZ MENOS

[Linked Database: EVOLUÇÃO_TAXA_ERRO]
[View: Gráfico Evolução]
[Display: Full width]

---

### Status Atual

> 📉 **Taxa de Erro Atual:** [property]
> 📊 **Taxa Mês Anterior:** [property]
> 📈 **Melhoria:** [property]%
> [Status badge]

---

## 🔍 DEFEITOS CRÍTICOS ATIVOS

[Linked Database: REGISTRO_DEFEITOS]
[View: CRÍTICOS ATIVOS]
[Display: Table]

**Resumo:**
- 🔴 Críticos: [rollup count where Severidade = CRÍTICA]
- ⏳ Aguardando Reparo: [rollup count where Status = AGUARDANDO_BACTERIAS]
- 🔧 Em Reparo: [rollup count where Status = EM_REPARO]

---

## 🦠 REPAROS EM EXECUÇÃO

[Linked Database: PLANOS_REPARO]
[View: EM EXECUÇÃO (Kanban)]
[Display: Board]

**Por Prioridade:**
- 🔴 P1 (Colapso Iminente 0-3m): [rollup count where Prioridade = P1]
- 🟠 P2 (Morte Lenta 3-12m): [rollup count where Prioridade = P2]
- 🟡 P3 (Fragilidade Crônica 12m+): [rollup count where Prioridade = P3]

---

## 🧬 PRINCÍPIOS DO SISTEMA

1. **Pensamento positivo = lixo**
2. **Realidade brutal > ilusão reconfortante**
3. **Margem > volume**
4. **Comunidade > produto**
5. **Paranoia produtiva diária**
6. **Cultura forte > genialidade**

**MANTRA:** *"Errar cada vez menos para sempre"*

---

## 🔗 LINKS RÁPIDOS

- [🔍 Ver Todos Defeitos](link-database-1)
- [🦠 Ver Todos Reparos](link-database-2)
- [📊 Histórico Completo](link-database-3)
- [⚙️ Configurar Workflows N8N](link-n8n)

---

## 📝 COMO USAR

### Para Executivos
1. Abra **Dashboard** toda segunda 9am
2. Leia **DEFEITOS CRÍTICOS ATIVOS**
3. Priorize **P1** imediatamente
4. Delegue **P2** e **P3** para equipe

### Para Equipe
1. Verifique **REPAROS EM EXECUÇÃO**
2. Mova cards para **EM_EXECUÇÃO** ao começar
3. Complete e mova para **CONCLUÍDO**
4. Aguarde validação semanal

### Para Founders
1. Aceite críticas brutais
2. Não negue defeitos
3. Execute reparos obsessivamente
4. Celebre métrica "Melhoria %" > 0

---

*Última atualização: [auto]*
```

### Como Criar o Dashboard

1. **Nova página no Notion**
2. **Título:** 🦠 SISTEMA CAÇADORES + BACTÉRIAS
3. **Ícone:** 🦠
4. **Cover:** Escolha uma imagem dark/industrial

5. **Adicionar databases linkadas:**
   - `/linked` → Selecione EVOLUÇÃO_TAXA_ERRO
   - `/linked` → Selecione REGISTRO_DEFEITOS
   - `/linked` → Selecione PLANOS_REPARO

6. **Configurar cada database:**
   - Escolha a view apropriada
   - Ajuste propriedades visíveis
   - Configure ordenação/filtros

7. **Adicionar texto explicativo:**
   - Use callouts para métricas importantes
   - Toggle lists para princípios
   - Dividers para separar seções

---

## 🔗 CONEXÃO ENTRE DATABASES

### Fluxo de Dados

```
1. CAÇADORES detectam defeito
   ↓
   Cria linha em REGISTRO_DEFEITOS
   Status: AGUARDANDO_BACTERIAS

2. BACTÉRIAS recebem webhook
   ↓
   Analisam defeito
   ↓
   Criam N linhas em PLANOS_REPARO
   (cada linha = 1 ação)
   ↓
   Atualizam REGISTRO_DEFEITOS
   Status: EM_REPARO

3. Equipe executa ações
   ↓
   Move cards em PLANOS_REPARO
   Status: CONCLUÍDO

4. VALIDAÇÃO roda semanalmente
   ↓
   Claude analisa se reparo foi real
   ↓
   Atualiza PLANOS_REPARO
   Status: VALIDADO ou REJEITADO
   ↓
   Se REJEITADO → volta para BACTÉRIAS
   ↓
   Atualiza EVOLUÇÃO_TAXA_ERRO
```

### Relação entre Databases

**REGISTRO_DEFEITOS ←→ PLANOS_REPARO:**
- Relation bidirecional
- Um defeito pode ter N reparos
- Cada reparo pertence a 1 defeito

**PLANOS_REPARO → EVOLUÇÃO_TAXA_ERRO:**
- Não há relation direta
- Workflow calcula métricas lendo ambas

---

## 📦 EXPORT/IMPORT

### Exportar Configuração

Para compartilhar com outro workspace:

1. **Cada database:** `⋯` → **Export** → **Markdown & CSV**
2. Salva estrutura (propriedades + views)
3. Importar em outro workspace: **Import** → Selecione arquivo

### Template Completo (JSON)

```json
{
  "databases": [
    {
      "name": "REGISTRO_DEFEITOS",
      "icon": "🔍",
      "properties": [ /* ver acima */ ]
    },
    {
      "name": "PLANOS_REPARO",
      "icon": "🦠",
      "properties": [ /* ver acima */ ]
    },
    {
      "name": "EVOLUÇÃO_TAXA_ERRO",
      "icon": "📈",
      "properties": [ /* ver acima */ ]
    }
  ]
}
```

---

## ✅ CHECKLIST FINAL

Antes de integrar com n8n, verifique:

- [ ] 3 databases criadas
- [ ] Todas as propriedades com nomes exatos (incluindo acentos)
- [ ] Opções de Select criadas exatamente como especificado
- [ ] Relação PLANOS_REPARO → REGISTRO_DEFEITOS configurada
- [ ] Rollup em PLANOS_REPARO funciona
- [ ] Fórmula em EVOLUÇÃO_TAXA_ERRO calcula corretamente
- [ ] Cada database compartilhada com integração Notion
- [ ] Views principais criadas
- [ ] Dashboard montado e funcional
- [ ] IDs das databases copiados

---

## 🆘 SUPORTE

**Problema comum:** "Propriedade não encontrada pelo n8n"

**Solução:**
1. Verifique nome EXATO (case-sensitive, acentos, espaços)
2. Confirme que database está compartilhada com integração
3. Teste com `Get All` no n8n para ver propriedades disponíveis

**Exemplo:**
```
❌ "Analise Completa" (sem acento)
✅ "Análise Completa" (com acento)
```

---

Agora você tem a estrutura completa do Notion! 🚀

Próximo passo: Volte para `SETUP_RAPIDO.md` e continue no **PASSO 3**.
