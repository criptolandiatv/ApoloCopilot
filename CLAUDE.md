# ApoloCopilot - N8N Workflow Documentation System

## Overview

ApoloCopilot is a high-performance n8n workflow documentation and search system that manages **2,053 automation workflows** with sub-100ms search capabilities. It combines a massive workflow collection with an intelligent categorization engine and a modern web interface.

**Primary Purpose**: Provide instant discovery, search, and import capabilities for n8n workflow templates across 365+ service integrations.

## Repository Structure

```
ApoloCopilot/
├── api_server.py          # FastAPI backend server (560 lines)
├── workflow_db.py         # SQLite database layer with FTS5 (752 lines)
├── run.py                 # Main CLI launcher script (176 lines)
├── create_categories.py   # Workflow categorization engine (247 lines)
├── import_workflows.py    # N8N workflow importer (203 lines)
│
├── src/                   # Node.js alternative implementation
│   ├── server.js          # Express server (368 lines)
│   ├── database.js        # SQLite management (670 lines)
│   ├── index-workflows.js # Workflow indexer (96 lines)
│   └── init-db.js         # Database initialization (44 lines)
│
├── workflows/             # 2,060 workflow JSON files (31MB)
│   └── [category]/        # 187 service-based subdirectories
│       └── *.json         # Individual workflow files
│
├── context/               # Categorization metadata
│   ├── def_categories.json      # Service-to-category mappings (725 defs)
│   ├── search_categories.json   # Generated categorization data
│   └── unique_categories.json   # 16 unique use case categories
│
├── static/                # Web interface assets
│   ├── index.html         # Main UI (Python/FastAPI version)
│   └── index-nodejs.html  # Alternative UI (Node.js version)
│
├── Documentation/         # 19 markdown files by category
│   ├── api-endpoints.md
│   ├── category-structure.md
│   ├── troubleshooting.md
│   └── [category-name].md # Per-category workflow docs
│
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── Dockerfile             # Python containerization
├── docker-compose.yml     # Docker compose config
├── README.md              # Main documentation
└── README_ZH.md           # Chinese documentation
```

## Technology Stack

### Primary Stack (Python)
- **FastAPI** - Async web framework with automatic OpenAPI docs
- **Uvicorn** - ASGI server
- **SQLite3** - Database with FTS5 full-text search
- **Pydantic** - Data validation

### Alternative Stack (Node.js)
- **Express.js** - Web framework
- **SQLite3** - Database driver
- **Helmet** - Security headers
- **Compression** - Gzip middleware

### Frontend
- **HTML5** with embedded CSS/JavaScript
- **Mermaid.js** - Workflow diagram generation
- **Responsive design** - Mobile-optimized

## Core Modules

### `api_server.py` - REST API Server
FastAPI server providing all API endpoints:
- `GET /` - Web interface
- `GET /api/workflows` - Search with FTS5
- `GET /api/stats` - Database statistics
- `GET /api/categories` - Category listing
- `GET /api/workflows/{filename}` - Workflow details
- `GET /api/workflows/{filename}/download` - JSON download
- `GET /api/workflows/{filename}/diagram` - Mermaid visualization

### `workflow_db.py` - Database Layer
High-performance SQLite with:
- FTS5 virtual table for full-text search
- WAL mode for concurrency
- MD5 change detection for efficient reindexing
- Automatic triggers for FTS sync

### `run.py` - CLI Launcher
Entry point with command-line options:
```bash
python run.py                    # Start server on localhost:8000
python run.py --host 0.0.0.0     # Listen on all interfaces
python run.py --port 3000        # Custom port
python run.py --reindex          # Force database reindexing
python run.py --dev              # Development mode with auto-reload
```

### `create_categories.py` - Categorization Engine
Maps workflow filenames to 16 use case categories:
- AI Agent Development
- Business Process Automation
- Cloud Storage & File Management
- Communication & Messaging
- CRM & Sales
- Data Processing & Analysis
- E-commerce & Retail
- Financial & Accounting
- Marketing & Advertising Automation
- Project Management
- Social Media Management
- Technical Infrastructure & DevOps
- Web Scraping & Data Extraction
- Creative Design Automation
- Creative Content & Video Automation
- Uncategorized

### `import_workflows.py` - Workflow Importer
Validates and imports workflows into n8n:
- JSON structure validation
- Required field checking (`nodes`, `connections`)
- Integration with `npx n8n import:workflow`
- Automatic categorization update

## Development Commands

```bash
# Python Server
pip install -r requirements.txt
python run.py

# Node.js Alternative
npm install
npm start

# Docker
docker-compose up

# Reindex Database
python run.py --reindex

# Regenerate Categories
python create_categories.py
```

## Workflow JSON Format

Each workflow file contains:
```json
{
  "name": "Workflow Name",
  "nodes": [
    {
      "id": "unique-node-id",
      "name": "Node Name",
      "type": "n8n-nodes-base.nodetype",
      "parameters": {...},
      "position": [x, y]
    }
  ],
  "connections": {
    "Node Name": {
      "main": [[{"node": "Next Node", "type": "main", "index": 0}]]
    }
  },
  "settings": {...},
  "staticData": null,
  "tags": [],
  "active": false,
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

## Database Schema

```sql
CREATE TABLE workflows (
    id INTEGER PRIMARY KEY,
    filename TEXT UNIQUE,
    name TEXT,
    active BOOLEAN,
    trigger_type TEXT,      -- Manual, Webhook, Scheduled, Complex
    complexity TEXT,        -- Low (≤5), Medium (6-15), High (16+)
    node_count INTEGER,
    integrations TEXT,      -- JSON array of services
    description TEXT,
    tags TEXT,
    file_hash TEXT,         -- MD5 for change detection
    analyzed_at TIMESTAMP,
    json_content TEXT
);

CREATE VIRTUAL TABLE workflows_fts USING fts5(
    filename, name, description, integrations, tags,
    content='workflows', content_rowid='id'
);
```

## Key Statistics

- **Total Workflows**: 2,053 automation templates
- **Total Nodes**: 29,445 (avg 14.3 per workflow)
- **Unique Integrations**: 365 different services
- **Active Workflows**: 215 (10.5%)
- **Trigger Distribution**:
  - Complex (multi-trigger): 831 (40.5%)
  - Webhook: 519 (25.3%)
  - Manual: 477 (23.2%)
  - Scheduled: 226 (11.0%)

## AI Assistant Guidelines

### For Code Modifications

1. **Python Code** (`api_server.py`, `workflow_db.py`, `run.py`):
   - Follow FastAPI patterns for new endpoints
   - Maintain FTS5 indexing consistency
   - Use async where applicable
   - Handle database connections properly

2. **JavaScript Code** (`src/`):
   - Follow Express.js patterns
   - Maintain SQLite connection pooling
   - Use Helmet security middleware

3. **Frontend** (`static/index.html`):
   - Embedded CSS/JS - no external dependencies
   - Maintain dark/light theme support
   - Keep responsive design intact

### For Workflow Analysis

1. **Parse JSON structure** to understand workflow purpose
2. **Examine node chains** to determine data flow
3. **Identify integrations** by inspecting node types
4. **Check trigger types** (webhook, cron, manual)
5. **Note complexity** based on node count and branching

### For Documentation Tasks

1. **Verify against actual implementation** before documenting
2. **Document business purpose**, not just technical details
3. **List external dependencies** and API integrations
4. **Note error handling** patterns used
5. **Update `Documentation/` folder** for category-specific docs

### For Adding New Workflows

1. Export workflow JSON from n8n
2. Remove sensitive data (credentials, URLs)
3. Place in appropriate `workflows/[category]/` subdirectory
4. Run `python create_categories.py` to update categorization
5. Run `python run.py --reindex` to update database

### Common Troubleshooting

- **Search not finding results**: Check FTS5 index, run `--reindex`
- **Categories not updating**: Re-run `create_categories.py`
- **Server won't start**: Check port availability, Python version 3.7+
- **Database locked**: Ensure single writer, check WAL mode

## File Naming Convention

Workflows follow this pattern:
```
[ID]_[Service1]_[Service2]_[Purpose]_[Trigger].json
```

Example: `2051_Telegram_Webhook_Automation_Webhook.json`
- ID: 2051
- Services: Telegram
- Purpose: Webhook Automation
- Trigger: Webhook

The system auto-converts to display names:
- `2051_Telegram_Webhook_Automation_Webhook.json` → "Telegram Webhook Automation"

## Security Considerations

- Workflow files may contain webhook URLs - review before sharing
- Credentials are stored in n8n, not in workflow files
- API server has CORS configured - restrict in production
- No authentication by default - add if exposing publicly

## Version Information

- **Python**: 3.7+
- **n8n Compatibility**: 1.0+
- **Node.js** (alternative): 14+

---

[中文](./CLAUDE_ZH.md)
