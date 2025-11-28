"""
🎼 MAESTRO N8N - Tools Implementation

Implementação das ferramentas (tools) do Maestro para consulta à base de conhecimento n8n.
Conecta-se ao Supabase/Postgres e implementa busca semântica, validação, e geração de workflows.

Requisitos:
    pip install openai supabase pgvector python-dotenv

Variáveis de ambiente necessárias (.env):
    SUPABASE_URL=https://xxx.supabase.co
    SUPABASE_KEY=xxx
    OPENAI_API_KEY=xxx
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import openai
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar clientes
openai.api_key = os.getenv("OPENAI_API_KEY")
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


# =====================================================
# TOOL 1: search_n8n_docs
# =====================================================

def search_n8n_docs(
    query: str,
    filter_type: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Busca semântica na base de conhecimento de n8n.

    Args:
        query: Pergunta ou termo de busca
        filter_type: Filtrar por tipo (node_spec, workflow_pattern, etc)
        limit: Número máximo de resultados

    Returns:
        Lista de documentos relevantes com título, conteúdo, tipo, tags e similaridade
    """
    # Gerar embedding da query
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    query_embedding = response.data[0].embedding

    # Construir query SQL com busca vetorial
    query_sql = f"""
        SELECT
            id,
            title,
            content,
            knowledge_type,
            tags,
            nodes_involved,
            metadata,
            relevance_score,
            1 - (embedding <=> ARRAY[{','.join(map(str, query_embedding))}]::vector) AS similarity
        FROM n8n_knowledge
        WHERE active = true
            {f"AND knowledge_type = '{filter_type}'" if filter_type else ""}
        ORDER BY embedding <=> ARRAY[{','.join(map(str, query_embedding))}]::vector
        LIMIT {limit}
    """

    # Executar query
    result = supabase.rpc('exec_sql', {'query': query_sql}).execute()

    # Atualizar contador de uso
    for row in result.data:
        supabase.rpc('increment_knowledge_usage', {'knowledge_id': row['id']}).execute()

    return result.data


# =====================================================
# TOOL 2: search_n8n_forum
# =====================================================

def search_n8n_forum(
    query: str,
    min_engagement: int = 3,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Busca tópicos relevantes no fórum da comunidade n8n.

    Args:
        query: Tópico ou problema a buscar
        min_engagement: Mínimo de engajamento (likes + respostas)
        limit: Número máximo de tópicos

    Returns:
        Lista de tópicos do fórum com título, resumo, url, tags e engajamento
    """
    # Gerar embedding da query
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    query_embedding = response.data[0].embedding

    # Buscar em n8n_knowledge com filtro de fórum
    query_sql = f"""
        SELECT
            k.id,
            k.title,
            k.content as summary,
            k.metadata->>'original_url' as url,
            k.tags,
            k.metadata->>'engagement' as engagement,
            1 - (k.embedding <=> ARRAY[{','.join(map(str, query_embedding))}]::vector) AS similarity
        FROM n8n_knowledge k
        WHERE k.active = true
            AND k.knowledge_type IN ('best_practice', 'workflow_pattern')
            AND k.metadata->>'source' = 'forum'
            AND COALESCE((k.metadata->>'engagement')::int, 0) >= {min_engagement}
        ORDER BY k.embedding <=> ARRAY[{','.join(map(str, query_embedding))}]::vector
        LIMIT {limit}
    """

    result = supabase.rpc('exec_sql', {'query': query_sql}).execute()

    return result.data


# =====================================================
# TOOL 3: check_node_compatibility
# =====================================================

def check_node_compatibility(
    node_name: str,
    n8n_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verifica se um node existe e sua compatibilidade.

    Args:
        node_name: Nome do node (ex: 'OpenAI', 'HTTP Request')
        n8n_version: Versão específica do n8n (opcional)

    Returns:
        Dict com exists, type_version, parameters, warnings, alternatives
    """
    # Buscar informações do node na base de conhecimento
    search_query = f"node {node_name} specification parameters"

    result = search_n8n_docs(
        query=search_query,
        filter_type="node_spec",
        limit=3
    )

    if not result:
        return {
            "exists": False,
            "type_version": None,
            "parameters": [],
            "deprecation_warning": None,
            "alternative": None,
            "recent_changes": []
        }

    # Processar resultado
    node_info = result[0]

    # Extrair informações estruturadas
    metadata = node_info.get('metadata', {})

    return {
        "exists": True,
        "type_version": metadata.get('type_version', 'unknown'),
        "parameters": metadata.get('parameters', []),
        "deprecation_warning": metadata.get('deprecation_warning'),
        "alternative": metadata.get('alternative'),
        "recent_changes": metadata.get('recent_changes', []),
        "documentation": node_info.get('content', ''),
        "tags": node_info.get('tags', [])
    }


# =====================================================
# TOOL 4: suggest_workflow_structure
# =====================================================

def suggest_workflow_structure(
    goal: str,
    inputs: List[str],
    outputs: List[str],
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Gera estrutura inicial (blueprint) de workflow.

    Args:
        goal: Objetivo do workflow
        inputs: Lista de entradas esperadas
        outputs: Lista de saídas esperadas
        constraints: Restrições opcionais (budget, complexity, etc)

    Returns:
        Blueprint com nodes, connections, alternatives, warnings, recommendations
    """
    constraints = constraints or {}

    # Buscar padrões similares na base de conhecimento
    similar_patterns = search_n8n_docs(
        query=f"{goal} workflow pattern",
        filter_type="workflow_pattern",
        limit=5
    )

    # Buscar best practices relevantes
    best_practices = search_n8n_docs(
        query=f"{goal} best practices error handling",
        filter_type="best_practice",
        limit=3
    )

    # Usar LLM para gerar blueprint baseado no conhecimento encontrado
    context = {
        "goal": goal,
        "inputs": inputs,
        "outputs": outputs,
        "constraints": constraints,
        "similar_patterns": [p['content'] for p in similar_patterns],
        "best_practices": [bp['content'] for bp in best_practices]
    }

    llm_prompt = f"""
Com base no conhecimento abaixo, crie um blueprint estruturado de workflow n8n.

OBJETIVO: {goal}
ENTRADAS: {', '.join(inputs)}
SAÍDAS: {', '.join(outputs)}
RESTRIÇÕES: {json.dumps(constraints, indent=2)}

PADRÕES SIMILARES ENCONTRADOS:
{json.dumps([p['title'] for p in similar_patterns], indent=2)}

BEST PRACTICES:
{json.dumps([bp['title'] for bp in best_practices], indent=2)}

Retorne um JSON com esta estrutura:
{{
    "blueprint": {{
        "nodes": [
            {{
                "id": "node-1",
                "type": "n8n-nodes-base.webhook",
                "name": "Trigger",
                "role": "input",
                "parameters": {{}},
                "rationale": "Por que esse node foi escolhido"
            }}
        ],
        "connections": {{
            "node-1": [["node-2"]]
        }}
    }},
    "warnings": [
        "Ponto de atenção 1",
        "Ponto de atenção 2"
    ],
    "recommendations": [
        "Recomendação 1",
        "Recomendação 2"
    ],
    "alternatives": {{
        "node-2": {{
            "current": "HTTP Request",
            "alternative": "OpenAI node",
            "reason": "HTTP Request é mais estável"
        }}
    }}
}}
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um especialista em n8n. Gere blueprints estruturados de workflows baseados em conhecimento atualizado."},
            {"role": "user", "content": llm_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    blueprint_data = json.loads(response.choices[0].message.content)

    # Adicionar referências usadas
    blueprint_data['references'] = {
        'patterns': [{'title': p['title'], 'url': p.get('metadata', {}).get('original_url')} for p in similar_patterns],
        'best_practices': [{'title': bp['title'], 'url': bp.get('metadata', {}).get('original_url')} for bp in best_practices]
    }

    return blueprint_data


# =====================================================
# TOOL 5: generate_n8n_json
# =====================================================

def generate_n8n_json(
    blueprint: Dict[str, Any],
    target_version: Optional[str] = None,
    include_comments: bool = True
) -> Dict[str, Any]:
    """
    Gera JSON completo do workflow n8n.

    Args:
        blueprint: Blueprint estruturado do workflow
        target_version: Versão alvo do n8n
        include_comments: Se deve incluir comentários explicativos

    Returns:
        Dict com workflow_json, import_instructions, credentials_needed, env_vars_needed
    """
    # Estrutura base do workflow n8n
    workflow = {
        "name": blueprint.get('name', 'Novo Workflow'),
        "nodes": [],
        "connections": {},
        "settings": {
            "executionOrder": "v1",
            "saveManualExecutions": True,
            "callerPolicy": "workflowsFromSameOwner"
        },
        "staticData": None,
        "tags": [],
        "triggerCount": 0,
        "updatedAt": datetime.utcnow().isoformat(),
        "versionId": "1"
    }

    # Converter nodes do blueprint para formato n8n
    position_x = 240
    position_y = 300
    credentials_needed = []
    env_vars_needed = []

    for i, node in enumerate(blueprint['nodes']):
        n8n_node = {
            "parameters": node.get('parameters', {}),
            "id": node['id'],
            "name": node['name'],
            "type": node['type'],
            "typeVersion": node.get('typeVersion', 1),
            "position": [position_x, position_y]
        }

        # Adicionar credenciais se necessário
        if 'credentials' in node:
            n8n_node['credentials'] = node['credentials']
            credentials_needed.append({
                'node': node['name'],
                'type': list(node['credentials'].keys())[0],
                'id': list(node['credentials'].values())[0]['id']
            })

        # Adicionar comentários se solicitado
        if include_comments and 'rationale' in node:
            n8n_node['notes'] = node['rationale']

        workflow['nodes'].append(n8n_node)

        # Atualizar posição para próximo node
        position_x += 220
        if (i + 1) % 5 == 0:  # Nova linha a cada 5 nodes
            position_x = 240
            position_y += 200

    # Adicionar conexões
    workflow['connections'] = blueprint.get('connections', {})

    # Gerar instruções de importação
    import_instructions = """
# Como Importar este Workflow

1. Abra sua instância do n8n
2. Vá em **Workflows** > **Import from File** (ou pressione Ctrl+O)
3. Selecione o arquivo JSON deste workflow
4. Configure as credenciais necessárias (veja abaixo)
5. Teste o workflow em modo manual primeiro
6. Ative o workflow quando estiver pronto

## Credenciais Necessárias
"""

    for cred in credentials_needed:
        import_instructions += f"\n- **{cred['type']}** (usado em '{cred['node']}')\n"
        import_instructions += f"  - ID esperado: `{cred['id']}`\n"
        import_instructions += f"  - Configure em: Settings > Credentials > Add Credential\n"

    if env_vars_needed:
        import_instructions += "\n## Variáveis de Ambiente\n"
        for env_var in env_vars_needed:
            import_instructions += f"\n- `{env_var['name']}`: {env_var['description']}\n"

    return {
        "workflow_json": workflow,
        "import_instructions": import_instructions,
        "credentials_needed": credentials_needed,
        "env_vars_needed": env_vars_needed
    }


# =====================================================
# TOOL 6: validate_workflow_json
# =====================================================

def validate_workflow_json(
    workflow_json: Dict[str, Any],
    check_credentials: bool = True,
    check_connections: bool = True,
    strict_mode: bool = False
) -> Dict[str, Any]:
    """
    Valida JSON de workflow n8n.

    Args:
        workflow_json: JSON do workflow
        check_credentials: Se deve validar credenciais
        check_connections: Se deve validar conexões
        strict_mode: Se warnings devem ser tratados como erros

    Returns:
        Dict com valid, errors, warnings, suggestions
    """
    errors = []
    warnings = []
    suggestions = []

    # Validação 1: Campos obrigatórios
    required_fields = ['name', 'nodes', 'connections']
    for field in required_fields:
        if field not in workflow_json:
            errors.append(f"Campo obrigatório ausente: '{field}'")

    # Validação 2: Nodes válidos
    if 'nodes' in workflow_json:
        node_ids = set()
        for i, node in enumerate(workflow_json['nodes']):
            # Campos obrigatórios de node
            for field in ['id', 'name', 'type', 'parameters']:
                if field not in node:
                    errors.append(f"Node {i}: campo obrigatório ausente: '{field}'")

            # IDs únicos
            if 'id' in node:
                if node['id'] in node_ids:
                    errors.append(f"Node {i}: ID duplicado '{node['id']}'")
                node_ids.add(node['id'])

            # Credenciais (se check_credentials)
            if check_credentials and 'credentials' in node:
                for cred_type, cred_data in node['credentials'].items():
                    if 'id' not in cred_data:
                        warnings.append(f"Node '{node['name']}': credencial '{cred_type}' sem ID definido")

    # Validação 3: Conexões válidas
    if check_connections and 'connections' in workflow_json and 'nodes' in workflow_json:
        node_ids_list = [node['id'] for node in workflow_json['nodes']]

        for source_id, targets in workflow_json['connections'].items():
            if source_id not in node_ids_list:
                errors.append(f"Conexão inválida: node fonte '{source_id}' não existe")

            for target_list in targets:
                for target in target_list:
                    if isinstance(target, dict) and 'node' in target:
                        if target['node'] not in node_ids_list:
                            errors.append(f"Conexão inválida: node destino '{target['node']}' não existe")

    # Validação 4: Boas práticas
    if 'nodes' in workflow_json:
        # Checar se tem error handling
        has_error_handling = any(
            'onError' in node.get('parameters', {}) or
            node.get('type') == 'n8n-nodes-base.if' or
            'continueOnFail' in node.get('parameters', {})
            for node in workflow_json['nodes']
        )

        if not has_error_handling:
            suggestions.append("Considere adicionar error handling (nodes IF, Stop, ou continueOnFail)")

        # Checar se nodes têm nomes descritivos
        for node in workflow_json['nodes']:
            if node.get('name', '').startswith('Node ') or len(node.get('name', '')) < 3:
                warnings.append(f"Node '{node.get('id')}' tem nome pouco descritivo")

    # Determinar se é válido
    valid = len(errors) == 0
    if strict_mode:
        valid = valid and len(warnings) == 0

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "validation_summary": f"{len(errors)} erros, {len(warnings)} avisos, {len(suggestions)} sugestões"
    }


# =====================================================
# TOOL 7: get_recent_n8n_changes
# =====================================================

def get_recent_n8n_changes(
    days: int = 7,
    filter_impact: Optional[List[str]] = None,
    filter_category: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Obtém mudanças recentes no n8n.

    Args:
        days: Número de dias atrás
        filter_impact: Filtrar por impacto (critical, high, medium, low)
        filter_category: Filtrar por categoria

    Returns:
        Lista de mudanças recentes
    """
    # Data de corte
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    # Construir query
    query = supabase.table('n8n_updates') \
        .select('*') \
        .gte('update_date', cutoff_date) \
        .order('update_date', desc=True)

    if filter_impact:
        query = query.in_('impact_level', filter_impact)

    if filter_category:
        query = query.in_('category', filter_category)

    result = query.execute()

    return result.data


# =====================================================
# TOOL 8: save_blueprint
# =====================================================

def save_blueprint(
    name: str,
    blueprint: Dict[str, Any],
    category: str,
    description: Optional[str] = None,
    user_request: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Salva blueprint no banco de dados.

    Args:
        name: Nome do workflow
        blueprint: Blueprint completo
        category: Categoria
        description: Descrição
        user_request: Pedido original do usuário
        tags: Tags para categorização

    Returns:
        Blueprint salvo com ID
    """
    data = {
        'name': name,
        'description': description,
        'user_request': user_request,
        'goal': blueprint.get('goal'),
        'inputs': blueprint.get('inputs', []),
        'outputs': blueprint.get('outputs', []),
        'nodes': blueprint.get('nodes', []),
        'connections': blueprint.get('connections', {}),
        'category': category,
        'tags': tags or [],
        'status': 'draft',
        'json_generated': False
    }

    result = supabase.table('workflow_blueprints').insert(data).execute()

    return result.data[0] if result.data else {}


# =====================================================
# TOOL 9: search_existing_blueprints
# =====================================================

def search_existing_blueprints(
    query: str,
    category: Optional[str] = None,
    min_rating: int = 3,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Busca blueprints similares já criados.

    Args:
        query: Descrição do workflow buscado
        category: Filtrar por categoria
        min_rating: Mínimo de rating (1-5)
        limit: Número máximo de blueprints

    Returns:
        Lista de blueprints similares
    """
    # Buscar blueprints
    query_builder = supabase.table('workflow_blueprints') \
        .select('*') \
        .gte('success_rating', min_rating) \
        .order('success_rating', desc=True) \
        .limit(limit)

    if category:
        query_builder = query_builder.eq('category', category)

    # Filtro textual simples (em produção, usar busca vetorial)
    query_builder = query_builder.ilike('description', f'%{query}%')

    result = query_builder.execute()

    return result.data


# =====================================================
# EXEMPLO DE USO
# =====================================================

if __name__ == "__main__":
    # Teste 1: Buscar documentação
    print("🔍 Teste 1: Buscar documentação sobre OpenAI node")
    docs = search_n8n_docs("OpenAI node configuration", limit=2)
    for doc in docs:
        print(f"  - {doc['title']} (similaridade: {doc['similarity']:.2f})")

    # Teste 2: Buscar no fórum
    print("\n🔍 Teste 2: Buscar best practices de error handling no fórum")
    forum_topics = search_n8n_forum("error handling best practices", limit=2)
    for topic in forum_topics:
        print(f"  - {topic['title']} ({topic['url']})")

    # Teste 3: Checar compatibilidade de node
    print("\n🔍 Teste 3: Verificar compatibilidade do node HTTP Request")
    compat = check_node_compatibility("HTTP Request")
    print(f"  - Existe: {compat['exists']}")
    print(f"  - Versão: {compat['type_version']}")

    # Teste 4: Sugerir estrutura de workflow
    print("\n🔍 Teste 4: Sugerir estrutura de workflow")
    blueprint = suggest_workflow_structure(
        goal="Transcrever áudio e gerar resumo com IA",
        inputs=["Audio file URL"],
        outputs=["Transcription", "Summary"],
        constraints={"budget": "medium", "complexity": "simple"}
    )
    print(f"  - Nodes sugeridos: {len(blueprint['blueprint']['nodes'])}")
    print(f"  - Warnings: {len(blueprint['warnings'])}")
    print(f"  - Recommendations: {len(blueprint['recommendations'])}")

    print("\n✅ Todos os testes concluídos!")
