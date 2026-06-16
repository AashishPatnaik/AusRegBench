import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

_DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(_DATABASE_URL)


def _enable_pgvector(conn: psycopg2.extensions.connection) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()


if __name__ == "__main__":
    conn = get_connection()
    _enable_pgvector(conn)

    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        pg_version = cur.fetchone()[0]

        cur.execute(
            "SELECT extname FROM pg_extension WHERE extname = 'vector'"
        )
        pgvector_row = cur.fetchone()

    conn.close()

    print(f"Postgres: {pg_version}")
    print(f"pgvector enabled: {pgvector_row is not None}")
