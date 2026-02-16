#!/usr/bin/env python3
"""Benchmark script for local RAG version (ChromaDB + Ollama)"""

import os
import json
import time
import sys
import chromadb
import requests
from pathlib import Path

# Constants
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "foods_benchmark"
EMBED_MODEL = "mxbai-embed-large"
LLM_MODEL = "llama3.2"

script_dir = Path(__file__).resolve().parent
JSON_FILE = script_dir / "data" / "foods.json"

print("\n" + "="*60)
print("LOCAL RAG BENCHMARK (ChromaDB + Ollama)")
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

# 2. Setup ChromaDB
print("\n2️⃣  Setting up ChromaDB...")
start = time.time()
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    setup_time = time.time() - start
    print(f"   ✅ ChromaDB setup in {setup_time:.3f}s")
except Exception as e:
    print(f"   ❌ Failed to setup ChromaDB: {e}")
    sys.exit(1)

# 3. Test Ollama embedding
print("\n3️⃣  Testing Ollama embedding...")
test_text = "What is biryani?"
start = time.time()
try:
    response = requests.post("http://localhost:11434/api/embeddings", json={
        "model": EMBED_MODEL,
        "prompt": test_text
    }, timeout=30)
    response.raise_for_status()
    embed_time = time.time() - start
    embedding_size = len(response.json()["embedding"])
    print(f"   ✅ Embedding generated in {embed_time:.3f}s ({embedding_size} dimensions)")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Cannot connect to Ollama at localhost:11434")
    print(f"      Please start Ollama: ollama serve")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Embedding failed: {e}")
    sys.exit(1)

# 4. Upsert documents (sample)
print("\n4️⃣  Upserting 10 sample documents...")
sample_foods = food_data[:10]
upsert_times = []

for i, food in enumerate(sample_foods):
    item_start = time.time()
    try:
        # Get embedding
        embed_response = requests.post("http://localhost:11434/api/embeddings", json={
            "model": EMBED_MODEL,
            "prompt": food["text"]
        }, timeout=30)
        embed_response.raise_for_status()
        embedding = embed_response.json()["embedding"]
        
        # Upsert to ChromaDB
        collection.add(
            ids=[str(food["id"])],
            documents=[food["text"]],
            embeddings=[embedding],
            metadatas=[{"region": food.get("region", ""), "type": food.get("type", "")}]
        )
        
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

# 5. Test query with embedding
print("\n5️⃣  Testing query with 3 items...")
test_queries = [
    "What is Indian food?",
    "Tell me about spicy dishes",
    "What are some vegetarian options?"
]

query_times = []
for query in test_queries:
    query_start = time.time()
    try:
        # Get embedding for query
        embed_response = requests.post("http://localhost:11434/api/embeddings", json={
            "model": EMBED_MODEL,
            "prompt": query
        }, timeout=30)
        embed_response.raise_for_status()
        query_embedding = embed_response.json()["embedding"]
        
        # Query ChromaDB
        results = collection.query(query_embeddings=[query_embedding], n_results=3)
        
        query_time = time.time() - query_start
        query_times.append(query_time)
        print(f"   ✅ Query '{query[:30]}...' in {query_time:.3f}s")
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        sys.exit(1)

avg_query_time = sum(query_times) / len(query_times)

# 6. Summary
print("\n" + "="*60)
print("LOCAL VERSION BENCHMARK SUMMARY")
print("="*60)
print(f"Data loading:           {load_time:.3f}s")
print(f"ChromaDB setup:         {setup_time:.3f}s")
print(f"Single embedding time:  {embed_time:.3f}s")
print(f"Upsert (per item):      {avg_upsert_time:.3f}s")
print(f"Query (per query):      {avg_query_time:.3f}s")
print(f"Total ops time:         {total_upsert + sum(query_times):.3f}s")
print("="*60)
print()

# Cleanup
try:
    chroma_client.delete_collection(name=COLLECTION_NAME)
except:
    pass
