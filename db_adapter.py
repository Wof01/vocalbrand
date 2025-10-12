"""Database adapter for VocalBrand - supports both SQLite and PostgreSQL.

This module provides a unified interface for database operations that works
with both SQLite (local development) and PostgreSQL (production on Render).
"""
from __future__ import annotations
import os
import sqlite3
from typing import Any, Optional, Tuple, List
from contextlib import contextmanager

# Determine database type from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vocalbrand.db")
USE_POSTGRES = DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

if USE_POSTGRES:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from psycopg2 import sql
        POSTGRES_AVAILABLE = True
    except ImportError:
        POSTGRES_AVAILABLE = False
        print("[WARNING] PostgreSQL requested but psycopg2 not installed. Falling back to SQLite.")
        USE_POSTGRES = False
        DATABASE_URL = "sqlite:///vocalbrand.db"
else:
    POSTGRES_AVAILABLE = False

# Parse database path/connection string
if USE_POSTGRES and POSTGRES_AVAILABLE:
    DB_CONN_STRING = DATABASE_URL
    # Handle render.com's postgres:// prefix (psycopg2 needs postgresql://)
    if DB_CONN_STRING.startswith("postgres://"):
        DB_CONN_STRING = DB_CONN_STRING.replace("postgres://", "postgresql://", 1)
else:
    DB_PATH = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite:///") else "vocalbrand.db"


class DatabaseAdapter:
    """Unified database adapter supporting both SQLite and PostgreSQL."""
    
    def __init__(self):
        self.use_postgres = USE_POSTGRES and POSTGRES_AVAILABLE
        
    @contextmanager
    def get_connection(self):
        """Get a database connection (context manager)."""
        if self.use_postgres:
            conn = psycopg2.connect(DB_CONN_STRING)
            try:
                yield conn
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA journal_mode=WAL;")
            try:
                yield conn
            finally:
                conn.close()
    
    def execute(self, query: str, params: tuple = (), fetch: str = None):
        """Execute a query and optionally fetch results.
        
        Args:
            query: SQL query string (use ? for SQLite, %s for PostgreSQL placeholders)
            params: Query parameters
            fetch: None, 'one', or 'all' to specify fetch type
            
        Returns:
            For fetch='one': single row or None
            For fetch='all': list of rows
            For fetch=None: None (INSERT/UPDATE/DELETE)
        """
        with self.get_connection() as conn:
            # Convert placeholders if needed
            if self.use_postgres and '?' in query:
                # Convert SQLite ? placeholders to PostgreSQL %s
                query = query.replace('?', '%s')
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()
            else:
                result = None
                
            conn.commit()
            cursor.close()
            return result
    
    def get_schema_sql(self) -> str:
        """Get the appropriate schema SQL for the current database type."""
        if self.use_postgres:
            return """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    subscription_active INTEGER DEFAULT 0,
                    stripe_customer_id TEXT,
                    stripe_subscription_id TEXT,
                    free_generations_used INTEGER DEFAULT 0,
                    minutes_balance INTEGER DEFAULT 0,
                    setup_credits INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS processed_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    kind TEXT,
                    amount_cents INTEGER,
                    currency TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON processed_sessions(session_id);
            """
        else:
            return """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    subscription_active INTEGER DEFAULT 0,
                    stripe_customer_id TEXT,
                    stripe_subscription_id TEXT,
                    free_generations_used INTEGER DEFAULT 0,
                    minutes_balance INTEGER DEFAULT 0,
                    setup_credits INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS processed_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    kind TEXT,
                    amount_cents INTEGER,
                    currency TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
    
    def column_exists(self, table: str, column: str) -> bool:
        """Check if a column exists in a table."""
        try:
            if self.use_postgres:
                query = """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s
                """
                result = self.execute(query, (table, column), fetch='one')
                return result is not None
            else:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
                    return True
        except Exception:
            return False
    
    def add_column(self, table: str, column: str, column_type: str, default: Any = None):
        """Add a column to a table if it doesn't exist."""
        if not self.column_exists(table, column):
            if self.use_postgres:
                default_clause = f" DEFAULT {default}" if default is not None else ""
                query = f"ALTER TABLE {table} ADD COLUMN {column} {column_type}{default_clause}"
            else:
                default_clause = f" DEFAULT {default}" if default is not None else ""
                query = f"ALTER TABLE {table} ADD COLUMN {column} {column_type}{default_clause}"
            
            self.execute(query)
            print(f"[DB] Added column {column} to {table}")


# Global adapter instance
db_adapter = DatabaseAdapter()


def get_db_type() -> str:
    """Get the current database type."""
    return "PostgreSQL" if db_adapter.use_postgres else "SQLite"


def get_db_info() -> dict:
    """Get database information for diagnostics."""
    return {
        "type": get_db_type(),
        "url": DATABASE_URL if not db_adapter.use_postgres else "postgresql://[hidden]",
        "path": DB_PATH if not db_adapter.use_postgres else None,
        "postgres_available": POSTGRES_AVAILABLE,
    }
