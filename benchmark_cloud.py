#!/usr/bin/env python3
"""Benchmark script for cloud RAG version (Upstash Vector + Groq)"""

import os
import json
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

try:
    from upstash_vector import Index
except ImportError:
    print("❌ upstash-vector not installed. Run: pip install upstash-vector")
    sys.exit(1)

# Setup
script_dir = Path(__file__).resolve().parent
project_root = script_dir
env_file = project_root / ".env"

if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"❌ No .env file found at {env_file}")
    sys.exit(1)

JSON_FILE = project_root / "data" / "foods.json"
if not JSON_FILE.exists():
    print(f"❌ foods.json not found at {JSON_FILE}")
    sys.exit(1)

UPSTASH_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")

if not UPSTASH_URL or not UPSTASH_TOKEN:
    print("❌ Missing Upstash credentials in .env")
    sys.exit(1)

print("\n" + "="*60)
print("CLOUD RAG BENCHMARK (Upstash Vector + Groq)")
print("="*60)

# 1. Load data
print("\n1️⃣  Loading data...")
start = time.time()
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        food_data = json.load(f)
    load_time = time.time() - start
    print(f"   ✅ Loaded {len(food_data)} items in {load_time:.3f}s")
except Exception as e:
    print(f"   ❌ Failed to load data: {e}")
    sys.exit(1)

# 2. Initialize Upstash client
print("\n2️⃣  Initializing Upstash Vector client...")
start = time.time()
try:
    index = Index(url=UPSTASH_URL, token=UPSTASH_TOKEN)
    init_time = time.time() - start
    print(f"   ✅ Upstash client initialized in {init_time:.3f}s")
except Exception as e:
    print(f"   ❌ Failed to initialize Upstash: {e}")
    sys.exit(1)

# 3. Upsert documents (sample)
print("\n3️⃣  Upserting 10 sample documents...")
sample_foods = food_data[:10]
upsert_times = []

for i, food in enumerate(sample_foods):
    item_start = time.time()
    try:
        # Prepare vector data for Upstash SDK format: (id, data, metadata)
        enriched_text = food["text"]
        if "region" in food:
            enriched_text += f" This food is popular in {food['region']}."
        if "type" in food:
            enriched_text += f" It is a type of {food['type']}."
        
        metadata = {
            "text": food["text"],
            "region": food.get("region", ""),
            "type": food.get("type", "")
        }
        
        # Upsert using SDK
        index.upsert(vectors=[
            (str(food["id"]), enriched_text, metadata)
        ])
        
        item_time = time.time() - item_start
        upsert_times.append(item_time)
    except Exception as e:
        print(f"   ❌ Failed to upsert item {i}: {e}")
        sys.exit(1)

avg_upsert_time = sum(upsert_times) / len(upsert_times)
total_upsert = sum(upsert_times)
print(f"   ✅ Upserted {len(sample_foods)} items")
print(f"      Total time: {total_upsert:.3f}s")
print(f"      Average per item: {avg_upsert_time:.3f}s")

# 4. Test query
print("\n4️⃣  Testing query with 3 items...")
test_queries = [
    "What is Indian food?",
    "Tell me about spicy dishes",
    "What are some vegetarian options?"
]

query_times = []
for query in test_queries:
    query_start = time.time()
    try:
        results = index.query(data=query, top_k=3, include_metadata=True)
        
        query_time = time.time() - query_start
        query_times.append(query_time)
        match_count = len(results) if results else 0
        print(f"   ✅ Query '{query[:30]}...' in {query_time:.3f}s ({match_count} matches)")
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        sys.exit(1)

avg_query_time = sum(query_times) / len(query_times) if query_times else 0

# 5. Summary
print("\n" + "="*60)
print("CLOUD VERSION BENCHMARK SUMMARY")
print("="*60)
print(f"Data loading:           {load_time:.3f}s")
print(f"Client initialization:  {init_time:.3f}s")
print(f"Upsert (per item):      {avg_upsert_time:.3f}s")
print(f"Query (per query):      {avg_query_time:.3f}s")
print(f"Total ops time:         {total_upsert + sum(query_times):.3f}s")
print("="*60)
print()

# Cleanup - delete the sample documents
print("5️⃣  Cleaning up sample documents...")
try:
    sample_ids = [str(food["id"]) for food in sample_foods]
    index.delete(ids=sample_ids)
    print(f"   ✅ Deleted {len(sample_ids)} sample documents")
except Exception as e:
    print(f"   ⚠️  Could not delete samples: {e}")
