# 🚀 Guia Rápido de Uso

## Para Começar AGORA (sem instalar nada)

```bash
cd data_analysis
python3 simple_generator.py
```

✅ Isso gera arquivos CSV e JSON que você pode abrir no Excel, Google Sheets, ou qualquer editor de planilhas!

Os arquivos estarão em: `output_simple/`

---

## Para Gerar Excel Completo com Gráficos

### 1️⃣ Instale as dependências

```bash
cd data_analysis
pip3 install -r requirements.txt
```

### 2️⃣ Execute o gerador completo

```bash
python3 main.py
```

✅ Isso gera um workbook Excel profissional com 18 abas, dashboard e gráficos!

O arquivo estará em: `output/Plantoes_App_Blueprint.xlsx`

---

## Scripts Disponíveis

| Script | O que faz | Requer instalação? |
|--------|-----------|-------------------|
| `simple_generator.py` | Gera CSV e JSON | ❌ Não |
| `main.py` | Gera Excel completo com gráficos | ✅ Sim |
| `setup.sh` | Instala tudo automaticamente | ✅ Sim |

---

## Solução de Problemas

### ❌ Erro: "ModuleNotFoundError: No module named 'pandas'"

**Solução:** Use o `simple_generator.py` OU instale as dependências:
```bash
pip3 install pandas matplotlib xlsxwriter
```

### ❌ Erro de rede ao instalar

**Solução:** Use o `simple_generator.py` que não precisa de instalação!

### ❌ Preciso de gráficos mas não consigo instalar

**Solução:**
1. Gere os CSV com `simple_generator.py`
2. Importe os CSV no Excel/Google Sheets
3. Crie gráficos manualmente

---

## Próximos Passos

1. ✅ Você já tem os dados gerados!
2. 📊 Abra os arquivos CSV no Excel ou Google Sheets
3. 🎨 Crie visualizações e dashboards customizados
4. 📈 Use os dados para apresentações e planejamento

---

## Precisa de Ajuda?

Consulte o [README.md](./README.md) completo para documentação detalhada.
