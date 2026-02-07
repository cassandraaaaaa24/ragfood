# 🚀 Upstash Vector Database Migration Plan
## RAG-Food: ChromaDB → Upstash Vector Migration

**Document Version:** 1.0  
**Date:** January 2, 2026  
**Status:** Design Phase

---

## 📋 Table of Contents

1. [Architecture Comparison](#architecture-comparison)
2. [Detailed Implementation Plan](#detailed-implementation-plan)
3. [Code Changes Required](#code-changes-required)
4. [API Differences & Implications](#api-differences--implications)
5. [Error Handling Strategy](#error-handling-strategy)
6. [Performance Considerations](#performance-considerations)
7. [Cost Analysis](#cost-analysis)
8. [Security Considerations](#security-considerations)
9. [Migration Checklist](#migration-checklist)

---

## 🏗️ Architecture Comparison

### Current Architecture (ChromaDB)

```
┌─────────────────────────────────────────────────────────┐
│                    RAG-Food Application                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Food Data (JSON)                                    │
│     ↓                                                    │
│  2. Embedding Generation (Ollama API)                   │
│     ↓                                                    │
│  3. Manual Embedding Process                            │
│     • request.post → http://localhost:11434             │
│     • 768-1024 dimensional vectors                       │
│     • Per-item embedding call (latency)                 │
│     ↓                                                    │
│  4. ChromaDB (Local Storage)                            │
│     • Persistent client (chroma_db/)                    │
│     • In-memory + SQLite backend                        │
│     • No authentication needed                           │
│     ↓                                                    │
│  5. Vector Search & Retrieval                           │
│     • Cosine similarity search                          │
│     • Top-K results (k=3)                               │
│     ↓                                                    │
│  6. LLM Response Generation (Ollama)                    │
│     • Context injection                                 │
│     • llama3.2 model inference                          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Zero latency for embeddings (local Ollama)
- ✅ No API costs or rate limits
- ✅ No network dependency
- ✅ Full data privacy (local storage)
- ✅ Easy development/testing

**Cons:**
- ❌ Requires Ollama + specific models installed locally
- ❌ Requires 8GB+ RAM for model inference
- ❌ Manual embedding generation code required
- ❌ Scaling requires local infrastructure
- ❌ No managed backups

---

### Proposed Architecture (Upstash Vector)

```
┌──────────────────────────────────────────────────────────┐
│                    RAG-Food Application                   │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  1. Food Data (JSON)                                     │
│     ↓                                                     │
│  2. Environment Config (.env)                            │
│     • UPSTASH_VECTOR_REST_URL                           │
│     • UPSTASH_VECTOR_REST_TOKEN                         │
│     ↓                                                     │
│  3. Upstash Vector Client Initialization                │
│     • from upstash_vector import Index                  │
│     • REST API endpoint                                  │
│     • Token-based authentication                         │
│     ↓                                                     │
│  4. Automatic Embedding (Upstash-Side)                  │
│     • Model: mixedbread-ai/mxbai-embed-large-v1        │
│     • 1024 dimensions, 512 seq length                   │
│     • MTEB score: 64.68                                 │
│     • Automatic during upsert                           │
│     ↓                                                     │
│  5. Upstash Vector Cloud Storage                         │
│     • Serverless vector database                         │
│     • Managed infrastructure                             │
│     • Automatic scaling                                  │
│     • Built-in backups & replication                    │
│     ↓                                                     │
│  6. Vector Search & Retrieval                           │
│     • Cloud-based similarity search                      │
│     • Single API call (raw text query)                  │
│     • Top-K results (k=3)                               │
│     ↓                                                     │
│  7. LLM Response Generation (Ollama)                    │
│     • Context injection                                  │
│     • llama3.2 model inference (local)                  │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ No local embedding service required
- ✅ Serverless & cloud-managed
- ✅ Simpler code (no embedding logic)
- ✅ Automatic scaling & high availability
- ✅ Built-in disaster recovery
- ✅ No local infrastructure overhead

**Cons:**
- ❌ Network latency (minor, ~100-200ms per call)
- ❌ Monthly costs (~$0.30/month free tier, $25+/month pro)
- ❌ API rate limits (free tier: 300 req/day)
- ❌ Requires internet connectivity
- ❌ Data stored in cloud (privacy consideration)

---

## 📐 Detailed Implementation Plan

### Phase 1: Preparation & Setup

#### 1.1 Environment Configuration
- ✅ **Already done:** Credentials added to `.env` file
- **Verify:** Check `.env` file contains:
  ```
  UPSTASH_VECTOR_REST_URL=https://...
  UPSTASH_VECTOR_REST_TOKEN=...
  ```
- **Install:** `pip install upstash-vector python-dotenv`

#### 1.2 Index Creation
- Create Upstash Vector index through dashboard or API
- Select embedding model: `mixedbread-ai/mxbai-embed-large-v1`
- Configure index parameters:
  - Similarity metric: Cosine (default)
  - Dimension: 1024 (auto-configured)
  - Max size: Start with 10K vectors (scalable)

### Phase 2: Code Refactoring

#### 2.1 Dependency Changes
```python
# Remove these imports:
- chromadb
- requests (for Ollama embeddings)

# Add these imports:
+ from upstash_vector import Index
+ from dotenv import load_dotenv
```

#### 2.2 Client Initialization
```python
# OLD (ChromaDB):
import chromadb
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# NEW (Upstash):
from upstash_vector import Index
import os
from dotenv import load_dotenv

load_dotenv()
upstash_index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)
```

#### 2.3 Data Upsert Changes
```python
# OLD (ChromaDB with manual embedding):
for item in new_items:
    enriched_text = item["text"]
    if "region" in item:
        enriched_text += f" This food is popular in {item['region']}."
    if "type" in item:
        enriched_text += f" It is a type of {item['type']}."
    
    emb = get_embedding(enriched_text)  # Manual embedding call
    collection.add(
        documents=[item["text"]],
        embeddings=[emb],
        ids=[item["id"]]
    )

# NEW (Upstash with automatic embedding):
vectors_to_upsert = []
for item in new_items:
    enriched_text = item["text"]
    if "region" in item:
        enriched_text += f" This food is popular in {item['region']}."
    if "type" in item:
        enriched_text += f" It is a type of {item['type']}."
    
    # Upstash automatically embeds the text
    vectors_to_upsert.append({
        "id": item["id"],
        "data": enriched_text,  # Raw text, not pre-embedded
        "metadata": {
            "original_text": item["text"],
            "region": item.get("region", ""),
            "type": item.get("type", "")
        }
    })

# Batch upsert (more efficient)
if vectors_to_upsert:
    upstash_index.upsert(vectors=vectors_to_upsert)
```

#### 2.4 Query Changes
```python
# OLD (ChromaDB):
q_emb = get_embedding(question)  # Manual embedding
results = collection.query(query_embeddings=[q_emb], n_results=3)
top_docs = results['documents'][0]
top_ids = results['ids'][0]

# NEW (Upstash):
# Upstash handles embedding automatically
results = upstash_index.query(
    data=question,  # Raw text query
    top_k=3,
    include_metadata=True,
    include_vectors=False  # No need for vector values
)

# Parse results
top_docs = [result["data"] for result in results]
top_ids = [result["id"] for result in results]
top_scores = [result["score"] for result in results]
```

### Phase 3: Testing & Validation

#### 3.1 Unit Tests
- ✅ Verify Upstash connection with credentials
- ✅ Test data upsert with 5-10 sample items
- ✅ Test query with known documents
- ✅ Verify metadata retrieval

#### 3.2 Integration Tests
- ✅ Run complete RAG flow end-to-end
- ✅ Compare results: ChromaDB vs Upstash
- ✅ Verify answer quality unchanged
- ✅ Test error scenarios (network down, rate limits)

#### 3.3 Performance Testing
- ✅ Latency measurement: embedding + search time
- ✅ Throughput: queries per second
- ✅ Memory usage: local Python process
- ✅ Cost calculation: API calls per day

### Phase 4: Cleanup & Documentation

#### 4.1 Remove ChromaDB
- Delete `chroma_db/` directory
- Remove ChromaDB import & dependency
- Update `requirements.txt`

#### 4.2 Update Documentation
- Update README.md with Upstash setup
- Document `.env` configuration
- Update architecture diagram
- Add cost considerations section

---

## 💻 Code Changes Required

### File Structure (Before vs After)

**Before:**
```
ragfood/
├── rag_run.py              # Uses ChromaDB + Ollama embedding
├── foods.json              # Data
├── chroma_db/              # Local vector storage ← DELETE
└── README.md
```

**After:**
```
ragfood/
├── rag_run.py              # Uses Upstash Vector + Ollama LLM
├── foods.json              # Data
├── .env                     # Upstash credentials ← NEW
├── requirements.txt        # Updated dependencies
└── README.md
```

### Detailed Code Changes

#### `rag_run.py` - Complete Refactor

```python
# ==============================================================================
# RAG-Food with Upstash Vector Database
# ==============================================================================

import os
import json
from dotenv import load_dotenv
from upstash_vector import Index
import requests

# Load environment variables
load_dotenv()

# Constants
JSON_FILE = "foods.json"
LLM_MODEL = "llama3.2"
OLLAMA_API_URL = "http://localhost:11434"

# Initialize Upstash Vector Index
upstash_index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
)

# Load food data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Function: Get existing IDs from Upstash
def get_existing_ids():
    """Fetch all existing document IDs from Upstash"""
    try:
        # Fetch all vectors (paginated if needed)
        all_vectors = upstash_index.fetch(ids=[item["id"] for item in food_data])
        return set([v["id"] for v in all_vectors if v])
    except:
        return set()

# Prepare and upsert data
existing_ids = get_existing_ids()
new_items = [item for item in food_data if item["id"] not in existing_ids]

if new_items:
    print(f"🆕 Adding {len(new_items)} new documents to Upstash Vector...")
    
    vectors_to_upsert = []
    for item in new_items:
        # Enrich text with metadata
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."
        
        vectors_to_upsert.append({
            "id": item["id"],
            "data": enriched_text,
            "metadata": {
                "original_text": item["text"],
                "region": item.get("region", ""),
                "type": item.get("type", "")
            }
        })
    
    # Batch upsert
    try:
        upstash_index.upsert(vectors=vectors_to_upsert)
        print(f"✅ Successfully added {len(new_items)} documents to Upstash.")
    except Exception as e:
        print(f"❌ Error upserting documents: {e}")
        raise
else:
    print("✅ All documents already in Upstash Vector.")

# Function: RAG Query
def rag_query(question):
    """
    Perform RAG query:
    1. Embed question (Upstash handles this)
    2. Search for relevant documents
    3. Generate answer using context + Ollama LLM
    """
    try:
        # Step 1: Query Upstash Vector (automatic embedding)
        print("\n🧠 Retrieving relevant information to reason through your question...\n")
        
        results = upstash_index.query(
            data=question,
            top_k=3,
            include_metadata=True,
            include_vectors=False
        )
        
        if not results:
            return "⚠️ No relevant documents found in the knowledge base."
        
        # Step 2: Extract documents and metadata
        top_docs = []
        top_ids = []
        top_scores = []
        
        for i, result in enumerate(results):
            top_docs.append(result.get("data", ""))
            top_ids.append(result.get("id", f"unknown_{i}"))
            top_scores.append(result.get("score", 0))
        
        # Step 3: Display retrieved sources
        for i, (doc, score) in enumerate(zip(top_docs, top_scores)):
            print(f"🔹 Source {i + 1} (ID: {top_ids[i]}, Score: {score:.3f}):")
            print(f"    \"{doc}\"\n")
        
        print("📚 These seem to be the most relevant pieces of information.\n")
        
        # Step 4: Build prompt with context
        context = "\n".join(top_docs)
        prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""
        
        # Step 5: Generate answer with local Ollama
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return f"❌ Error calling Ollama: {response.text}"
        
        answer = response.json()["response"].strip()
        
        # Step 6: Return result
        return answer
        
    except requests.exceptions.ConnectionError:
        return "❌ Error: Cannot connect to Ollama. Make sure Ollama is running on http://localhost:11434"
    except Exception as e:
        return f"❌ Error during RAG query: {str(e)}"

# Interactive CLI
if __name__ == "__main__":
    print("\n🧠 RAG-Food is ready. Ask a question (type 'exit' to quit):\n")
    
    while True:
        try:
            question = input("You: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ["exit", "quit", "bye"]:
                print("👋 Goodbye!")
                break
            
            answer = rag_query(question)
            print(f"🤖: {answer}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
```

#### `requirements.txt` - Updated

**Before:**
```
chromadb>=0.4.0
requests>=2.31.0
```

**After:**
```
upstash-vector>=0.3.0
python-dotenv>=1.0.0
requests>=2.31.0
```

#### `.env` - New File

```env
# Upstash Vector Credentials (from dashboard)
UPSTASH_VECTOR_REST_URL=https://<your-endpoint>.upstash.io
UPSTASH_VECTOR_REST_TOKEN=Bearer <your-token>
```

#### `README.md` - Update Installation Section

**Remove:**
```markdown
### ✅ Ollama Models Needed

Run these in your terminal to install them:

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```
```

**Replace with:**
```markdown
### ✅ Upstash Vector Setup

1. Create account at [Upstash Console](https://console.upstash.com)
2. Create Vector Index:
   - Name: `ragfood` (or your preference)
   - Embedding Model: `mixedbread-ai/mxbai-embed-large-v1`
3. Copy REST URL and Token to `.env` file (see below)

### ✅ Ollama Setup (LLM only)

Run these in your terminal to install the model:

```bash
ollama pull llama3.2
```

> Note: We've moved embeddings to Upstash, so we only need the LLM now.
```

---

## 🔄 API Differences & Implications

| Feature | ChromaDB | Upstash Vector |
|---------|----------|-----------------|
| **Authentication** | None (local) | API Token + URL (REST) |
| **Embedding** | Manual via Ollama API | Automatic during upsert |
| **Embedding Model** | `mxbai-embed-large` (Ollama) | `mixedbread-ai/mxbai-embed-large-v1` |
| **Dimensions** | 768 | 1024 (higher quality) |
| **MTEB Score** | ~64.0 | 64.68 (slightly better) |
| **Query Input** | Pre-embedded vector | Raw text (auto-embedded) |
| **Latency** | ~50-100ms (local) | ~100-200ms (network) |
| **Rate Limits** | None (local) | 300 req/day (free), unlimited (pro) |
| **Cost** | $0 (local hardware) | ~$0 free, $25+/month pro |
| **Storage** | Local disk | Cloud managed |
| **Backup** | Manual | Automatic |
| **Scalability** | Limited by hardware | Automatic (serverless) |

### Implementation Implications

#### 1. **Error Handling Changes**
- ChromaDB: Local errors only (memory, disk)
- Upstash: Network errors, API rate limits, authentication failures

#### 2. **Dependency Changes**
- Remove: `chromadb`, Ollama embedding calls
- Add: `upstash-vector`, environment variable loading
- Keep: `requests` (for Ollama LLM), `python-dotenv`

#### 3. **Data Enrichment**
- ChromaDB: Embed BEFORE storage
- Upstash: Embed at storage time (no difference in final quality)

#### 4. **Batch Operations**
- ChromaDB: Loop-based (item by item)
- Upstash: Batch API calls (more efficient)

---

## 🛡️ Error Handling Strategy

### Error Categories & Handling

#### 1. **Authentication Errors**
```python
try:
    index = Index(url=url, token=token)
    index.query(data="test")
except Exception as e:
    if "401" in str(e) or "unauthorized" in str(e):
        print("❌ Invalid Upstash credentials. Check UPSTASH_VECTOR_REST_URL and UPSTASH_VECTOR_REST_TOKEN")
```

#### 2. **Network Errors**
```python
try:
    results = upstash_index.query(data=question, top_k=3)
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Upstash. Check internet connection.")
```

#### 3. **Rate Limit Errors**
```python
try:
    upstash_index.upsert(vectors=vectors)
except Exception as e:
    if "429" in str(e) or "rate limit" in str(e):
        print("⚠️ Rate limit exceeded. Try again later or upgrade plan.")
```

#### 4. **Missing Credentials**
```python
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("UPSTASH_VECTOR_REST_URL")
token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")

if not url or not token:
    raise ValueError("❌ Missing Upstash credentials in .env file")
```

#### 5. **Query Result Handling**
```python
results = upstash_index.query(data=question, top_k=3)

if not results or len(results) == 0:
    return "⚠️ No relevant documents found in knowledge base"

if all(result.get("score", 0) < 0.3 for result in results):
    print("⚠️ Low confidence results. Consider adding more training data.")
```

### Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def query_with_retry(question):
    return upstash_index.query(data=question, top_k=3)
```

---

## ⚡ Performance Considerations

### Latency Analysis

**ChromaDB (Current):**
- Ollama embedding request: ~50-100ms
- ChromaDB local search: ~5-10ms
- Total per query: ~55-110ms
- **Advantage:** Predictable, no network

**Upstash Vector (Proposed):**
- Network round-trip to Upstash: ~50-100ms
- Upstash embedding: ~20-50ms
- Upstash search: ~10-30ms
- Return results: ~20-50ms
- Total per query: ~100-230ms
- **Advantage:** Automatic embedding (no extra API call)

**Net Impact:** +45-120ms per query (acceptable for interactive use)

### Throughput Comparison

| Metric | ChromaDB | Upstash (Free) | Upstash (Pro) |
|--------|----------|----------------|---------------|
| Queries/day | Unlimited | 300 | Unlimited |
| Upserts/day | Unlimited | 300 | Unlimited |
| Latency | ~50-110ms | ~100-230ms | ~100-230ms |
| Concurrent | Limited (1 disk) | High (serverless) | High (serverless) |

### Memory Impact

**Before (ChromaDB + Ollama):**
- Ollama + llama3.2 model: ~4-8GB RAM
- ChromaDB in-memory index: ~100-500MB
- Python process: ~100MB
- **Total: ~4.2-8.6GB**

**After (Upstash Vector + Ollama):**
- Ollama + llama3.2 model: ~4-8GB RAM
- Upstash client library: ~10MB
- Python process: ~100MB
- **Total: ~4.1-8.1GB**
- **Savings: ~100-500MB** (the in-memory ChromaDB index)

---

## 💰 Cost Analysis

### Current Setup (ChromaDB)

| Component | Cost/Month |
|-----------|-----------|
| Ollama (local) | $0 |
| ChromaDB (local) | $0 |
| Electricity (~500W, 8h/day, $0.15/kWh) | ~$18 |
| **Total** | **~$18/month** |

### Proposed Setup (Upstash)

#### Free Tier
| Component | Cost/Month |
|-----------|-----------|
| Ollama (local) | $0 |
| Upstash Vector (free tier) | $0 |
| Electricity (~350W, 8h/day, $0.15/kWh) | ~$12 |
| **Total** | **~$12/month** |

**Limits:** 300 requests/day, 1GB vectors, 1 index

#### Pro Tier (if needed)
| Component | Cost/Month |
|-----------|-----------|
| Ollama (local) | $0 |
| Upstash Vector (pro) | $25 (base) |
| Electricity (~350W, 8h/day, $0.15/kWh) | ~$12 |
| **Total** | **~$37/month** |

**Benefits:** Unlimited requests, 1TB vectors, multiple indices, priority support

### Cost Decision Matrix

| Use Case | Recommendation | Reason |
|----------|-----------------|--------|
| Personal project, <300 req/day | **Upstash Free** | Saves electricity, $6-12/month |
| Small team, <1000 req/day | **Upstash Pro** | Better ROI than keeping servers warm |
| Enterprise, high throughput | **Upstash Enterprise** | Unlimited scaling, dedicated support |
| Offline/isolated environment | **ChromaDB** | Network not available |

---

## 🔐 Security Considerations

### 1. **API Credentials Management**

```python
# ❌ WRONG: Hardcoding credentials
UPSTASH_URL = "https://..."
UPSTASH_TOKEN = "Bearer ..."

# ✅ RIGHT: Using environment variables
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("UPSTASH_VECTOR_REST_URL")
token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
```

### 2. **`.env` File Protection**

```
# Add to .gitignore
.env
.env.local
*.env
```

### 3. **Token Rotation**

- ✅ Use Upstash dashboard to regenerate tokens
- ✅ Store multiple token pairs for rotation
- ✅ Audit log API calls in Upstash console

### 4. **Data Privacy**

| Aspect | ChromaDB | Upstash |
|--------|----------|---------|
| **Storage Location** | Local disk | Upstash cloud (Google Cloud) |
| **Encryption in Transit** | N/A (local) | TLS 1.3 (standard) |
| **Encryption at Rest** | Filesystem encryption | AES-256 (available) |
| **Compliance** | Your responsibility | SOC2, GDPR ready |
| **Data Retention** | Your control | Configurable |

### 5. **Best Practices**

1. **Never commit `.env`** to Git
2. **Rotate tokens** periodically
3. **Use readonly tokens** if possible (Upstash feature)
4. **Monitor API usage** for unusual activity
5. **Restrict index access** in Upstash dashboard
6. **Use strong passwords** for Upstash account
7. **Enable 2FA** on Upstash account

### 6. **Network Security**

- Upstash uses TLS 1.3 by default
- All API calls are HTTPS-encrypted
- No credentials exposed in logs
- Rate limiting prevents abuse

---

## ✅ Migration Checklist

### Pre-Migration
- [ ] Review this design document
- [ ] Verify `.env` file has Upstash credentials
- [ ] Backup current `foods.json` and data
- [ ] Backup ChromaDB directory (`chroma_db/`)
- [ ] Test Ollama is still working

### Code Migration
- [ ] Install `upstash-vector` and `python-dotenv`
- [ ] Create new `rag_run.py` with Upstash implementation
- [ ] Test Upstash connection
- [ ] Test data upsert to Upstash
- [ ] Test vector search (without LLM first)
- [ ] Test full RAG flow with sample questions
- [ ] Compare results: ChromaDB vs Upstash
- [ ] Implement error handling & retry logic

### Testing & Validation
- [ ] Unit tests: Upstash client
- [ ] Integration tests: End-to-end RAG
- [ ] Load testing: Multiple queries
- [ ] Edge cases: Empty queries, rate limits
- [ ] Fallback testing: Network error handling

### Cleanup
- [ ] Delete `chroma_db/` directory
- [ ] Remove ChromaDB imports
- [ ] Update `requirements.txt`
- [ ] Update `README.md` with new setup
- [ ] Add `.env.example` with placeholder values

### Documentation
- [ ] Update README.md
- [ ] Document `.env` setup
- [ ] Document error scenarios
- [ ] Update architecture diagrams
- [ ] Add cost considerations section

### Deployment
- [ ] Push changes to GitHub
- [ ] Update deployment docs
- [ ] Monitor API usage
- [ ] Set up alerts for rate limits
- [ ] Plan token rotation schedule

---

## 🎯 Success Criteria

### Functional
- ✅ All questions return relevant answers
- ✅ Answer quality >= current ChromaDB
- ✅ Error handling for network failures
- ✅ Graceful degradation if Upstash unavailable

### Performance
- ✅ Query latency < 500ms (including Ollama)
- ✅ No significant increase in response time
- ✅ Reliable under normal load (100 req/day)

### Reliability
- ✅ 99% uptime (Upstash SLA)
- ✅ Automatic backups
- ✅ Retry logic for transient failures

### Cost
- ✅ ✅ Free tier sufficient for personal use
- ✅ Predictable costs if scaling needed
- ✅ Better total cost than keeping Ollama server always-on

---

## 📞 Support & Resources

- **Upstash Docs:** https://upstash.com/docs/vector
- **Upstash Python SDK:** https://github.com/upstash/vector-python
- **Community:** Discord, GitHub Discussions
- **Status:** https://status.upstash.com

---

**Document Version:** 1.0 | **Last Updated:** January 2, 2026 | **Status:** Ready for Implementation