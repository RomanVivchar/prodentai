"""
Database migration script to add missing columns
Run this script to update the database schema
"""
import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://prodentai:prodentai_password@localhost:5432/prodentai"
)


async def migrate_database():
    """Add missing columns to existing tables"""
    engine = create_async_engine(
        DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        print("Checking and adding missing columns...")

        # Check if hashed_password column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='hashed_password'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding hashed_password column to users table...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS hashed_password VARCHAR
            """))
            print("✓ Added hashed_password column")
        else:
            print("✓ hashed_password column already exists")

        # Check if first_name column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='first_name'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding first_name column to users table...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS first_name VARCHAR
            """))
            print("✓ Added first_name column")
        else:
            print("✓ first_name column already exists")

        # Check if last_name column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='last_name'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding last_name column to users table...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_name VARCHAR
            """))
            print("✓ Added last_name column")
        else:
            print("✓ last_name column already exists")

        # Check if is_active column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='is_active'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding is_active column to users table...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE
            """))
            print("✓ Added is_active column")
        else:
            print("✓ is_active column already exists")

        # ===== REMINDERS TABLE MIGRATIONS =====
        print("\n--- Checking reminders table ---")

        # Check if reminder_type column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reminders' AND column_name='reminder_type'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding reminder_type column to reminders table...")
            await conn.execute(text("""
                ALTER TABLE reminders 
                ADD COLUMN IF NOT EXISTS reminder_type VARCHAR
            """))
            print("✓ Added reminder_type column")
        else:
            print("✓ reminder_type column already exists")

        # Check if date column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reminders' AND column_name='date'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding date column to reminders table...")
            await conn.execute(text("""
                ALTER TABLE reminders 
                ADD COLUMN IF NOT EXISTS date VARCHAR
            """))
            print("✓ Added date column")
        else:
            print("✓ date column already exists")

        # Check if message column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reminders' AND column_name='message'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding message column to reminders table...")
            await conn.execute(text("""
                ALTER TABLE reminders 
                ADD COLUMN IF NOT EXISTS message TEXT
            """))
            print("✓ Added message column")
        else:
            print("✓ message column already exists")

        # Check if enabled column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reminders' AND column_name='enabled'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding enabled column to reminders table...")
            await conn.execute(text("""
                ALTER TABLE reminders 
                ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT TRUE
            """))
            print("✓ Added enabled column")
        else:
            print("✓ enabled column already exists")

        # Check if is_active column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='reminders' AND column_name='is_active'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding is_active column to reminders table...")
            await conn.execute(text("""
                ALTER TABLE reminders 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE
            """))
            print("✓ Added is_active column")
        else:
            print("✓ is_active column already exists")

        # ===== RISK_ASSESSMENTS TABLE MIGRATIONS =====
        print("\n--- Checking risk_assessments table ---")

        # Check if assessment_data column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='risk_assessments' AND column_name='assessment_data'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding assessment_data column to risk_assessments table...")
            await conn.execute(text("""
                ALTER TABLE risk_assessments 
                ADD COLUMN IF NOT EXISTS assessment_data TEXT
            """))
            print("✓ Added assessment_data column")
        else:
            print("✓ assessment_data column already exists")

        # Check if risk_scores column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='risk_assessments' AND column_name='risk_scores'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding risk_scores column to risk_assessments table...")
            await conn.execute(text("""
                ALTER TABLE risk_assessments 
                ADD COLUMN IF NOT EXISTS risk_scores TEXT
            """))
            print("✓ Added risk_scores column")
        else:
            print("✓ risk_scores column already exists")

        # Check if recommendations column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='risk_assessments' AND column_name='recommendations'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding recommendations column to risk_assessments table...")
            await conn.execute(text("""
                ALTER TABLE risk_assessments 
                ADD COLUMN IF NOT EXISTS recommendations TEXT
            """))
            print("✓ Added recommendations column")
        else:
            print("✓ recommendations column already exists")

        # ===== PSYCHOLOGY_SESSIONS TABLE MIGRATIONS =====
        print("\n--- Checking psychology_sessions table ---")

        # Check if session_type column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='psychology_sessions' AND column_name='session_type'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding session_type column to psychology_sessions table...")
            await conn.execute(text("""
                ALTER TABLE psychology_sessions 
                ADD COLUMN IF NOT EXISTS session_type VARCHAR DEFAULT 'general'
            """))
            print("✓ Added session_type column")
        else:
            print("✓ session_type column already exists")

        # Check if user_message column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='psychology_sessions' AND column_name='user_message'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding user_message column to psychology_sessions table...")
            await conn.execute(text("""
                ALTER TABLE psychology_sessions 
                ADD COLUMN IF NOT EXISTS user_message TEXT
            """))
            print("✓ Added user_message column")
        else:
            print("✓ user_message column already exists")

        # Check if ai_response column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='psychology_sessions' AND column_name='ai_response'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding ai_response column to psychology_sessions table...")
            await conn.execute(text("""
                ALTER TABLE psychology_sessions 
                ADD COLUMN IF NOT EXISTS ai_response TEXT
            """))
            print("✓ Added ai_response column")
        else:
            print("✓ ai_response column already exists")

        # Check if sentiment_score column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='psychology_sessions' AND column_name='sentiment_score'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None

        if not exists:
            print("Adding sentiment_score column to psychology_sessions table...")
            await conn.execute(text("""
                ALTER TABLE psychology_sessions 
                ADD COLUMN IF NOT EXISTS sentiment_score FLOAT
            """))
            print("✓ Added sentiment_score column")
        else:
            print("✓ sentiment_score column already exists")

        print("\n✓ Database migration completed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(migrate_database())
        sys.exit(0)
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        sys.exit(1)

