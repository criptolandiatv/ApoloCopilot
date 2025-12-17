#!/usr/bin/env python3
"""Initialize database with all tables"""
import sys

try:
    print("📊 Initializing ApoloCopilot Database...")

    # Import database and models
    from database import init_db

    # Create all tables
    init_db()

    print("✅ Database initialized successfully!")
    print("📋 All tables created")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
