from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, TEXT
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "job_portal")

client: AsyncIOMotorClient = None

def get_db():
    return client[DB_NAME]

async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # ── Indexes ──────────────────────────────────────────────
    # Users: unique email
    await db.users.create_index([("email", ASCENDING)], unique=True)

    # Jobs: text index for full-text search
    await db.jobs.create_index(
        [("title", TEXT), ("description", TEXT), ("skills", TEXT)],
        name="jobs_text_search",
    )
    # Jobs: filter indexes
    await db.jobs.create_index([("location", ASCENDING)])
    await db.jobs.create_index([("job_type", ASCENDING)])
    await db.jobs.create_index([("category", ASCENDING)])
    await db.jobs.create_index([("is_active", ASCENDING)])
    await db.jobs.create_index([("host_id", ASCENDING)])
    await db.jobs.create_index([("posted_at", ASCENDING)])

    print(f"✅  Connected to MongoDB — database: {DB_NAME}")

async def close_db():
    global client
    if client:
        client.close()
        print("🔌  MongoDB connection closed")
