import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DB = None

try:
    database_URL = os.getenv("DB_URL")
    if not database_URL:
        raise ValueError("DB_URL is missing from .env")

    DB = psycopg2.connect(database_URL)
    print("Successfully connected to the database")

    cur = DB.cursor()
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            bio VARCHAR(150) DEFAULT 'Hey there! I am using Secure Messaging App.',
            profile_picture_url TEXT DEFAULT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        ); """)
    print("\n1. The Users table has been created successfully")


    cur.execute("""CREATE TABLE IF NOT EXISTS user_status (
            status_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,
            is_online BOOLEAN DEFAULT FALSE,
            last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            ); """)
    print("2. The User Status table has been created successfully")


    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
            message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            sender_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
            receiver_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
            encrypted_content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            ); """)
    print("3. The Messages table has been created successfully")


    cur.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sender_receiver ON messages(sender_id, receiver_id);")

    DB.commit()
    cur.close()


except Exception as e:
    print(f"An error occurred: {e}")
    if DB is not None:
        DB.rollback()

finally:
    if DB is not None:
        DB.close()
        print("The connection has been safely closed")