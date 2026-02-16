import os
import json
import chromadb
import requests
from pathlib import Path

# Constants
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "foods"

# Determine the correct path to foods.json
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
JSON_FILE = project_root / "data" / "foods.json"

# Verify the file exists
if not JSON_FILE.exists():
    print(f"❌ Error: foods.json not found at {JSON_FILE}")
    print(f"   Please make sure the file exists in the data folder")
    exit(1)

EMBED_MODEL = "mxbai-embed-large"
LLM_MODEL = "llama3.2"

# Load data
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        food_data = json.load(f)
    print(f"✅ Loaded {len(food_data)} food items from {JSON_FILE}")
except Exception as e:
    print(f"❌ Error loading JSON file: {e}")
    exit(1)

# Setup ChromaDB
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    print(f"✅ Connected to ChromaDB at {CHROMA_DIR}")
except Exception as e:
    print(f"❌ Error setting up ChromaDB: {e}")
    exit(1)

# Ollama embedding function
def get_embedding(text):
    try:
        response = requests.post("http://localhost:11434/api/embeddings", json={
            "model": EMBED_MODEL,
            "prompt": text
        }, timeout=30)
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Ollama on http://localhost:11434")
        print("   Please make sure Ollama is running with: ollama serve")
        exit(1)
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        raise

# Add only new items
try:
    existing_ids = set(collection.get()['ids'])
    print(f"📊 Found {len(existing_ids)} existing documents in ChromaDB")
except Exception as e:
    print(f"❌ Error fetching existing documents: {e}")
    existing_ids = set()

new_items = [item for item in food_data if item['id'] not in existing_ids]

if new_items:
    print(f"🆕 Adding {len(new_items)} new documents to ChromaDB...")
    for idx, item in enumerate(new_items, 1):
        # Enhance text with region/type
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."

        try:
            emb = get_embedding(enriched_text)
            collection.add(
                documents=[item["text"]],  # Use original text as retrievable context
                embeddings=[emb],
                ids=[item["id"]]
            )
            if idx % 10 == 0:
                print(f"  ✅ Processed {idx}/{len(new_items)} documents")
        except Exception as e:
            print(f"❌ Failed to embed document {item['id']}: {e}")
            continue
    print(f"✅ Successfully added all {len(new_items)} documents!")
else:
    print("✅ All documents already in ChromaDB.")

# RAG query
def rag_query(question):
    try:
        # Step 1: Embed the user question
        q_emb = get_embedding(question)

        # Step 2: Query the vector DB
        results = collection.query(query_embeddings=[q_emb], n_results=3)

        # Step 3: Extract documents
        top_docs = results['documents'][0]
        top_ids = results['ids'][0]

        if not top_docs:
            return "❌ No relevant documents found."

        # Step 4: Show friendly explanation of retrieved documents
        print("\n🧠 Retrieving relevant information to reason through your question...\n")

        for i, doc in enumerate(top_docs):
            print(f"🔹 Source {i + 1} (ID: {top_ids[i]}):")
            print(f"    \"{doc}\"\n")

        print("📚 These seem to be the most relevant pieces of information to answer your question.\n")

        # Step 5: Build prompt from context
        context = "\n".join(top_docs)

        prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""

        # Step 6: Generate answer with Ollama
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=60)
        response.raise_for_status()

        # Step 7: Return final result
        return response.json()["response"].strip()
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Ollama on http://localhost:11434")
        print("   Please make sure Ollama is running with: ollama serve")
        return "Connection to Ollama failed. Please start Ollama."
    except Exception as e:
        print(f"❌ Error during RAG query: {e}")
        return f"Error: {str(e)}"


# Interactive loop
print("\n🧠 RAG is ready. Ask a question (type 'exit' to quit):\n")
while True:
    try:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        if not question:
            print("⚠️ Please enter a question.\n")
            continue
        
        answer = rag_query(question)
        print(f"\n🤖: {answer}\n")
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        break
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")

