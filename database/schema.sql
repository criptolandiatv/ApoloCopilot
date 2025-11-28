-- =====================================================
-- N8N MONITORING SYSTEM - DATABASE SCHEMA
-- =====================================================
-- Sistema de monitoramento e biblioteca de conhecimento
-- para acompanhar evolução do n8n e gerar workflows
-- de forma inteligente e resiliente.
-- =====================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =====================================================
-- TABELA 1: n8n_updates
-- =====================================================
-- Armazena atualizações diárias do ecossistema n8n
-- (docs, changelog, forum, GitHub releases)
-- =====================================================

CREATE TABLE IF NOT EXISTS n8n_updates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    update_date DATE NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'docs', 'changelog', 'forum', 'github', 'blog'

    -- Informações do item
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT, -- Conteúdo completo quando relevante
    url TEXT,

    -- Metadados estruturados
    impact_level VARCHAR(20), -- 'critical', 'high', 'medium', 'low'
    category VARCHAR(50), -- 'node_update', 'feature', 'bug_fix', 'best_practice', 'breaking_change'
    tags TEXT[], -- Array de tags: ['llm', 'webhook', 'error-handling', etc]

    -- Análise de impacto
    affected_nodes TEXT[], -- Nodes afetados por essa mudança
    use_cases TEXT[], -- Casos de uso relacionados
    migration_notes TEXT, -- Notas de migração se for breaking change

    -- Metadados de processamento
    processed BOOLEAN DEFAULT FALSE,
    embedded BOOLEAN DEFAULT FALSE, -- Se já foi enviado para embeddings

    -- Índices para busca
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('portuguese', coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(content, ''))
    ) STORED
);

-- Índices para performance
CREATE INDEX idx_n8n_updates_date ON n8n_updates(update_date DESC);
CREATE INDEX idx_n8n_updates_source ON n8n_updates(source_type);
CREATE INDEX idx_n8n_updates_impact ON n8n_updates(impact_level);
CREATE INDEX idx_n8n_updates_category ON n8n_updates(category);
CREATE INDEX idx_n8n_updates_tags ON n8n_updates USING GIN(tags);
CREATE INDEX idx_n8n_updates_search ON n8n_updates USING GIN(search_vector);
CREATE INDEX idx_n8n_updates_processed ON n8n_updates(processed) WHERE NOT processed;

-- =====================================================
-- TABELA 2: n8n_knowledge
-- =====================================================
-- Base vetorial (RAG) com conhecimento destilado
-- sobre n8n, consultável por LLMs
-- =====================================================

CREATE TABLE IF NOT EXISTS n8n_knowledge (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Referência ao update original (se aplicável)
    source_update_id UUID REFERENCES n8n_updates(id) ON DELETE SET NULL,

    -- Tipo de conhecimento
    knowledge_type VARCHAR(50) NOT NULL, -- 'node_spec', 'workflow_pattern', 'best_practice', 'troubleshooting', 'integration_guide'

    -- Conteúdo
    title TEXT NOT NULL,
    content TEXT NOT NULL, -- Texto destilado e otimizado para RAG
    metadata JSONB, -- Estrutura flexível para metadados específicos por tipo

    -- Categorização
    tags TEXT[],
    nodes_involved TEXT[], -- Nodes relacionados
    n8n_version VARCHAR(20), -- Versão do n8n (quando relevante)

    -- Embeddings (OpenAI ada-002 = 1536 dims, ou outro modelo)
    embedding vector(1536),

    -- Relevância e qualidade
    relevance_score FLOAT DEFAULT 1.0, -- Score de relevância (pode ser ajustado)
    usage_count INTEGER DEFAULT 0, -- Quantas vezes foi usado em consultas
    last_used_at TIMESTAMPTZ,

    -- Status
    active BOOLEAN DEFAULT TRUE,
    verified BOOLEAN DEFAULT FALSE -- Marcado como verificado/confiável
);

-- Índices para performance
CREATE INDEX idx_n8n_knowledge_type ON n8n_knowledge(knowledge_type);
CREATE INDEX idx_n8n_knowledge_tags ON n8n_knowledge USING GIN(tags);
CREATE INDEX idx_n8n_knowledge_nodes ON n8n_knowledge USING GIN(nodes_involved);
CREATE INDEX idx_n8n_knowledge_active ON n8n_knowledge(active) WHERE active;
CREATE INDEX idx_n8n_knowledge_embedding ON n8n_knowledge USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_n8n_knowledge_metadata ON n8n_knowledge USING GIN(metadata);

-- =====================================================
-- TABELA 3: workflow_blueprints
-- =====================================================
-- Blueprints intermediários gerados pelo Maestro
-- antes de criar o JSON final
-- =====================================================

CREATE TABLE IF NOT EXISTS workflow_blueprints (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Identificação
    name TEXT NOT NULL,
    description TEXT,
    user_request TEXT, -- Pedido original do usuário

    -- Estrutura do blueprint
    goal TEXT, -- Objetivo principal
    inputs TEXT[], -- Entradas esperadas
    outputs TEXT[], -- Saídas esperadas
    nodes JSONB, -- Array de nodes no formato simplificado
    connections JSONB, -- Mapa de conexões

    -- Contexto de geração
    knowledge_sources UUID[], -- IDs de n8n_knowledge consultados
    n8n_version_target VARCHAR(20), -- Versão do n8n alvo

    -- Status de implementação
    status VARCHAR(30) DEFAULT 'draft', -- 'draft', 'reviewed', 'implemented', 'tested', 'production'
    json_generated BOOLEAN DEFAULT FALSE,
    workflow_json JSONB, -- JSON do workflow n8n quando gerado

    -- Feedback e aprendizado
    success_rating INTEGER, -- 1-5, feedback do usuário
    issues_encountered TEXT,
    optimization_notes TEXT,

    -- Tags e categorização
    tags TEXT[],
    category VARCHAR(50) -- 'content_creation', 'data_pipeline', 'monitoring', 'integration', etc
);

-- Índices
CREATE INDEX idx_blueprints_status ON workflow_blueprints(status);
CREATE INDEX idx_blueprints_category ON workflow_blueprints(category);
CREATE INDEX idx_blueprints_tags ON workflow_blueprints USING GIN(tags);
CREATE INDEX idx_blueprints_created ON workflow_blueprints(created_at DESC);

-- =====================================================
-- TABELA 4: maestro_conversations
-- =====================================================
-- Histórico de conversas com o Maestro
-- para aprendizado e melhoria contínua
-- =====================================================

CREATE TABLE IF NOT EXISTS maestro_conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Relacionamento
    blueprint_id UUID REFERENCES workflow_blueprints(id) ON DELETE CASCADE,

    -- Conversa
    messages JSONB, -- Array de mensagens [{"role": "user"|"assistant", "content": "..."}]
    tools_used TEXT[], -- Ferramentas que o Maestro usou
    knowledge_consulted UUID[], -- IDs de n8n_knowledge consultados

    -- Resultado
    outcome VARCHAR(30), -- 'blueprint_created', 'clarification_needed', 'not_feasible', 'abandoned'
    user_satisfaction INTEGER -- 1-5
);

-- Índices
CREATE INDEX idx_maestro_conv_blueprint ON maestro_conversations(blueprint_id);
CREATE INDEX idx_maestro_conv_created ON maestro_conversations(created_at DESC);

-- =====================================================
-- TABELA 5: radar_execution_log
-- =====================================================
-- Log de execuções do workflow "Radar n8n"
-- para monitorar a saúde do sistema
-- =====================================================

CREATE TABLE IF NOT EXISTS radar_execution_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    executed_at TIMESTAMPTZ DEFAULT NOW(),

    -- Estatísticas da execução
    sources_checked JSONB, -- {"docs": true, "forum": true, "github": false, ...}
    items_found INTEGER,
    items_processed INTEGER,
    items_embedded INTEGER,

    -- Status
    status VARCHAR(30), -- 'success', 'partial', 'failed'
    errors TEXT[],
    execution_time_seconds INTEGER,

    -- Próxima execução
    next_scheduled TIMESTAMPTZ
);

-- Índice
CREATE INDEX idx_radar_log_executed ON radar_execution_log(executed_at DESC);

-- =====================================================
-- VIEWS ÚTEIS
-- =====================================================

-- View: Updates recentes por categoria
CREATE OR REPLACE VIEW recent_updates_by_category AS
SELECT
    category,
    impact_level,
    COUNT(*) as count,
    MAX(update_date) as last_update,
    array_agg(DISTINCT unnest(tags)) as all_tags
FROM n8n_updates
WHERE update_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category, impact_level
ORDER BY count DESC;

-- View: Knowledge mais utilizado
CREATE OR REPLACE VIEW top_knowledge AS
SELECT
    id,
    title,
    knowledge_type,
    tags,
    usage_count,
    relevance_score,
    last_used_at
FROM n8n_knowledge
WHERE active = true
ORDER BY usage_count DESC, relevance_score DESC
LIMIT 50;

-- View: Blueprints em produção
CREATE OR REPLACE VIEW production_blueprints AS
SELECT
    id,
    name,
    description,
    category,
    tags,
    success_rating,
    created_at,
    updated_at
FROM workflow_blueprints
WHERE status = 'production'
ORDER BY success_rating DESC NULLS LAST, updated_at DESC;

-- =====================================================
-- FUNÇÕES UTILITÁRIAS
-- =====================================================

-- Função: Busca semântica em n8n_knowledge
CREATE OR REPLACE FUNCTION search_n8n_knowledge(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    content TEXT,
    knowledge_type VARCHAR(50),
    tags TEXT[],
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        k.id,
        k.title,
        k.content,
        k.knowledge_type,
        k.tags,
        1 - (k.embedding <=> query_embedding) AS similarity
    FROM n8n_knowledge k
    WHERE
        k.active = true
        AND (filter_type IS NULL OR k.knowledge_type = filter_type)
        AND 1 - (k.embedding <=> query_embedding) > match_threshold
    ORDER BY k.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Função: Atualizar contador de uso
CREATE OR REPLACE FUNCTION increment_knowledge_usage(knowledge_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE n8n_knowledge
    SET
        usage_count = usage_count + 1,
        last_used_at = NOW()
    WHERE id = knowledge_id;
END;
$$ LANGUAGE plpgsql;

-- Função: Obter estatísticas do Radar
CREATE OR REPLACE FUNCTION get_radar_stats(days INTEGER DEFAULT 30)
RETURNS TABLE (
    total_executions BIGINT,
    success_rate FLOAT,
    avg_items_found FLOAT,
    last_execution TIMESTAMPTZ,
    total_knowledge_added BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_executions,
        (COUNT(*) FILTER (WHERE status = 'success')::FLOAT / NULLIF(COUNT(*), 0) * 100)::FLOAT as success_rate,
        AVG(items_found)::FLOAT as avg_items_found,
        MAX(executed_at) as last_execution,
        (SELECT COUNT(*) FROM n8n_knowledge WHERE created_at >= CURRENT_DATE - days * INTERVAL '1 day')::BIGINT as total_knowledge_added
    FROM radar_execution_log
    WHERE executed_at >= CURRENT_DATE - days * INTERVAL '1 day';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_n8n_knowledge_updated_at
    BEFORE UPDATE ON n8n_knowledge
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_blueprints_updated_at
    BEFORE UPDATE ON workflow_blueprints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- POLÍTICAS RLS (Row Level Security) - OPCIONAL
-- =====================================================
-- Descomente se quiser ativar RLS para segurança multi-tenant

-- ALTER TABLE n8n_updates ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE n8n_knowledge ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE workflow_blueprints ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE maestro_conversations ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- DADOS INICIAIS (SEEDS)
-- =====================================================

-- Inserir categorias e tipos comuns para referência
INSERT INTO n8n_knowledge (knowledge_type, title, content, tags, verified, relevance_score)
VALUES
(
    'best_practice',
    'Princípio: Use HTTP Request para máxima estabilidade',
    'Em vez de nodes de integração específicos, prefira o node HTTP Request quando possível. Isso reduz a dependência de mudanças em nodes de terceiros e dá maior controle sobre requests, headers e error handling. Especialmente útil para APIs REST.',
    ARRAY['http-request', 'stability', 'best-practice', 'api'],
    true,
    1.0
),
(
    'best_practice',
    'Padrão: Error Handling robusto',
    'Todo workflow de produção deve ter error handling em cada ponto crítico. Use nodes IF para checar respostas, Set nodes para normalizar dados antes de salvar, e Stop nodes com mensagens claras. Evite deixar o workflow "explodir" silenciosamente.',
    ARRAY['error-handling', 'reliability', 'best-practice'],
    true,
    1.0
),
(
    'workflow_pattern',
    'Padrão: Data Pipeline com validação',
    'Estrutura comum: Trigger → Fetch → Validate → Transform → Store → Notify. Sempre valide dados antes de transformar, e normalize antes de armazenar. Use Set nodes para criar objetos limpos e previsíveis.',
    ARRAY['data-pipeline', 'pattern', 'etl'],
    true,
    0.9
),
(
    'troubleshooting',
    'Solução: Node travando sem erro',
    'Se um node trava sem mostrar erro, verifique: 1) timeout settings, 2) variáveis de ambiente, 3) JSON inválido em expressions. Use Code node com console.log() para debug. Ative execução passo-a-passo no n8n para ver exatamente onde para.',
    ARRAY['debugging', 'troubleshooting', 'timeout'],
    true,
    0.8
)
ON CONFLICT DO NOTHING;

-- =====================================================
-- COMENTÁRIOS FINAIS
-- =====================================================

COMMENT ON TABLE n8n_updates IS 'Armazena atualizações diárias do ecossistema n8n coletadas pelo Radar';
COMMENT ON TABLE n8n_knowledge IS 'Base vetorial (RAG) com conhecimento destilado sobre n8n para consulta por LLMs';
COMMENT ON TABLE workflow_blueprints IS 'Blueprints intermediários de workflows gerados pelo Maestro';
COMMENT ON TABLE maestro_conversations IS 'Histórico de conversas com o Maestro para aprendizado';
COMMENT ON TABLE radar_execution_log IS 'Log de execuções do workflow Radar n8n para monitoramento';

COMMENT ON FUNCTION search_n8n_knowledge IS 'Busca semântica em knowledge base usando embeddings vetoriais';
COMMENT ON FUNCTION get_radar_stats IS 'Retorna estatísticas do sistema Radar nos últimos N dias';
