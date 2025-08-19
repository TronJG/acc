import os
from datetime import timedelta

ALLOWED_ORIGINS = [s.strip() for s in os.getenv("ALLOWED_ORIGINS", "*").split(",") if s.strip()]

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "43200"))
JWT_EXPIRE = timedelta(minutes=JWT_EXPIRE_MIN)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://neondb_owner:PASS@ep-rapid-moon-a12f8rmt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

APP_SECRET = os.getenv("APP_SECRET", "appsecret")
