#!/usr/bin/env python3
"""
ApoloCopilot - Main Application
Complete platform with WhatsApp, GPS, Calendar, Forum, Chat, Badges, and Medical Shifts
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pathlib import Path
import os

# Import all routers
from routers import auth, whatsapp, documents, location, calendar, chat, forum
from routers import gamification, shifts

# Import database setup
from database import init_db

# Create FastAPI app
app = FastAPI(
    title="ApoloCopilot",
    description="Plataforma completa com verificação WhatsApp, GPS, Google Calendar, Fórum, Chat IA e Sistema de Plantões",
    version="1.0.0"
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path("frontend")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

uploads_path = Path("uploads")
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include all routers
app.include_router(auth.router)
app.include_router(whatsapp.router)
app.include_router(documents.router)
app.include_router(location.router)
app.include_router(calendar.router)
app.include_router(chat.router)
app.include_router(forum.router)
app.include_router(gamification.router)
app.include_router(shifts.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting ApoloCopilot...")
    print("📊 Checking database...")

    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("⚠️  Continuing anyway...")

    print("✅ ApoloCopilot started successfully!")
    print("📱 Features: WhatsApp, GPS, Calendar, Forum, Chat, Badges, Shifts")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main application page"""
    index_file = Path("frontend/index.html")

    if index_file.exists():
        return FileResponse(index_file)

    # Fallback HTML if frontend doesn't exist
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ApoloCopilot</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3em; margin-bottom: 10px; }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .feature {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .feature-icon { font-size: 2.5em; margin-bottom: 10px; }
            a {
                color: white;
                text-decoration: none;
                background: rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
            }
            a:hover { background: rgba(255, 255, 255, 0.3); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ApoloCopilot</h1>
            <p>Plataforma completa para profissionais de saúde</p>

            <div class="features">
                <div class="feature">
                    <div class="feature-icon">📱</div>
                    <h3>WhatsApp</h3>
                    <p>Verificação via WhatsApp</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📄</div>
                    <h3>Documentos</h3>
                    <p>Verificação de documentos</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📍</div>
                    <h3>GPS</h3>
                    <p>Localização e mapas</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📅</div>
                    <h3>Calendário</h3>
                    <p>Integração Google Calendar</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">💬</div>
                    <h3>Fórum</h3>
                    <p>Discussões comunitárias</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🤖</div>
                    <h3>Chat IA</h3>
                    <p>Assistente inteligente</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🏅</div>
                    <h3>Badges</h3>
                    <p>Sistema de conquistas</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">⭐</div>
                    <h3>Trust/Karma</h3>
                    <p>Sistema de reputação</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🏥</div>
                    <h3>Plantões</h3>
                    <p>Oportunidades médicas</p>
                </div>
            </div>

            <div style="margin-top: 40px; text-align: center;">
                <a href="/docs">📚 Documentação da API</a>
                <a href="/redoc">📖 API Reference</a>
            </div>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "ApoloCopilot is running",
        "features": [
            "WhatsApp Verification",
            "Document Verification",
            "GPS/Location",
            "Google Calendar",
            "Forum",
            "AI Chatbot",
            "Badges & Trust System",
            "Medical Shifts"
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
