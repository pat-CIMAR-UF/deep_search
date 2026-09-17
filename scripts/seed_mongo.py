"""Load the mock pharmaceutical data into MongoDB.

Usage: uv run python scripts/seed_mongo.py
Reads MONGODB_URI and MONGODB_DATABASE (default pharma_db) from .env, replaces the
drugs / inventory / sales_records collections with mongo/seed/*.json, and creates indexes.
Idempotent: running it again produces the same collections.
"""
import os
import sys
from pathlib import Path

from bson.json_util import loads
from dotenv import find_dotenv, load_dotenv
from pymongo import ASCENDING, MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = PROJECT_ROOT / "mongo" / "seed"
COLLECTIONS = ("drugs", "inventory", "sales_records")
INDEXES = {
    "drugs": [([("drug_id", ASCENDING)], {"unique": True})],
    "inventory": [([("inventory_id", ASCENDING)], {"unique": True}), ([("drug_id", ASCENDING)], {})],
    "sales_records": [([("sale_id", ASCENDING)], {"unique": True}), ([("drug_id", ASCENDING)], {}),
                      ([("sale_date", ASCENDING)], {})],
}


def main() -> int:
    load_dotenv(find_dotenv())
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("MONGODB_URI is not set. Add it to .env first.", file=sys.stderr)
        return 1
    database_name = os.getenv("MONGODB_DATABASE", "pharma_db")
    client = MongoClient(uri, serverSelectionTimeoutMS=20000)
    try:
        db = client[database_name]
        for name in COLLECTIONS:
            documents = loads((SEED_DIR / f"{name}.json").read_text(encoding="utf-8"))
            db[name].drop()
            db[name].insert_many(documents)
            for keys, options in INDEXES[name]:
                db[name].create_index(keys, **options)
            print(f"{name}: {db[name].count_documents({})} documents")
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
