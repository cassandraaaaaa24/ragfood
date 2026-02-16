import os
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
from upstash_vector import Index
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

# Determine project root directory
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

# Load environment variables from .env file
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"❌ No .env file found at {env_file}")
    exit(1)

# Constants
JSON_FILE = project_root / "data" / "foods.json"
if not JSON_FILE.exists():
    print(f"❌ foods.json not found at {JSON_FILE}")
    exit(1)

LLM_MODEL = "llama-3.1-8b-instant"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Initialize clients
UPSTASH_VECTOR_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_VECTOR_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not all([UPSTASH_VECTOR_URL, UPSTASH_VECTOR_TOKEN, GROQ_API_KEY]):
    print("\n❌ Missing required environment variables!")
    print("   Required: UPSTASH_VECTOR_REST_URL, UPSTASH_VECTOR_REST_TOKEN, GROQ_API_KEY")
    print(f"   Please check {env_file}")
    exit(1)

# Initialize Upstash Vector client
try:
    upstash_index = Index(url=UPSTASH_VECTOR_URL, token=UPSTASH_VECTOR_TOKEN)
    print("✅ Connected to Upstash Vector")
except Exception as e:
    print(f"❌ Failed to connect to Upstash Vector: {e}")
    raise

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Retry decorator for cloud operations
def fetch_existing_ids() -> set:
    """Fetch existing document IDs from Upstash Vector."""
    try:
        # Try to fetch vectors - if it fails, assume empty
        # Upstash SDK may not support listing all vectors
        return set()
    except Exception as e:
        print(f"⚠️ Could not fetch existing IDs: {e}")
        return set()

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=RETRY_DELAY, max=10))
def upsert_vectors(vectors_data: List[Dict]) -> None:
    """Upsert vectors to Upstash Vector with retry logic."""
    try:
        # Convert to format expected by Upstash: list of (id, data, metadata)
        formatted_vectors = []
        for vec_data in vectors_data:
            formatted_vectors.append((
                vec_data["id"],
                vec_data["data"],
                vec_data["metadata"]
            ))
        upstash_index.upsert(vectors=formatted_vectors)
    except Exception as e:
        print(f"⚠️ Error upserting vectors, retrying...: {e}")
        raise

# Prepare vectors for Upstash (upsert handles duplicates)
new_items = food_data

if new_items:
    print(f"🆕 Preparing {len(new_items)} new documents for Upstash Vector...")
    vectors_to_upsert = []
    
    for item in new_items:
        # Enhance text with region/type metadata
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."
        
        # Create vector data for Upstash
        vector_data = {
            "id": item["id"],
            "data": enriched_text,  # Raw text for embedding
            "metadata": {
                "text": item["text"],
                "enriched_text": enriched_text,
                "region": item.get("region", ""),
                "type": item.get("type", "")
            }
        }
        vectors_to_upsert.append(vector_data)
    
    try:
        upsert_vectors(vectors_to_upsert)
        print(f"✅ Successfully upserted {len(new_items)} documents to Upstash Vector")
    except Exception as e:
        print(f"❌ Failed to upsert documents after {MAX_RETRIES} retries: {e}")
else:
    print("✅ All documents already in Upstash Vector.")

# RAG query with Upstash Vector and Groq
@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=RETRY_DELAY, max=10))
def query_upstash_vector(question: str, top_k: int = 3) -> List[Dict]:
    """Query Upstash Vector with retry logic."""
    try:
        # Upstash Vector will embed the query automatically
        results = upstash_index.query(data=question, top_k=top_k, include_metadata=True)
        
        # Convert results to standardized format
        formatted_results = []
        if results:
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "metadata": result.metadata if result.metadata else {},
                    "data": result.metadata.get("text", "") if result.metadata else ""
                })
        return formatted_results
    except Exception as e:
        print(f"⚠️ Error querying Upstash Vector, retrying...: {e}")
        raise

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=RETRY_DELAY, max=10))
def generate_answer_groq(context: str, question: str) -> str:
    """Generate answer using Groq API with retry logic."""
    try:
        prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""

        # Use Groq's chat completion API
        message = groq_client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Error calling Groq API, retrying...: {e}")
        raise

def rag_query(question: str) -> Optional[str]:
    """Execute RAG query with error handling and fallback."""
    try:
        # Step 1: Query Upstash Vector
        print("\n🔍 Searching vector database for relevant documents...")
        search_results = query_upstash_vector(question, top_k=3)
        
        if not search_results:
            return "❌ No relevant documents found in the vector database."
        
        # Step 2: Extract documents and metadata
        top_docs = []
        for i, result in enumerate(search_results):
            text_content = result.get("data", result.get("metadata", {}).get("enriched_text", ""))
            if not text_content:
                text_content = result.get("metadata", {}).get("text", "")
            
            top_docs.append(text_content)
            
            print(f"\n🔹 Source {i + 1} (ID: {result['id']}, Score: {result.get('score', 'N/A')}):")
            print(f"    \"{str(text_content)[:100]}...\"")
        
        print("\n📚 Retrieved relevant information to answer your question.\n")
        
        # Step 3: Generate answer with Groq
        print("🤖 Generating answer with Groq...")
        context = "\n".join(str(doc) for doc in top_docs)
        answer = generate_answer_groq(context, question)
        return answer
        
    except Exception as e:
        print(f"❌ Error during RAG query: {e}")
        return f"Sorry, I encountered an error processing your question: {str(e)}"

def fallback_query(question: str) -> str:
    """Fallback function when cloud services fail."""
    try:
        # Simple rule-based response if services unavailable
        keywords = {
            "pizza": "Pizza is a popular Italian dish with cheese and various toppings on a bread base.",
            "sushi": "Sushi is a Japanese dish featuring vinegared rice and raw or cooked seafood.",
            "pasta": "Pasta is an Italian staple made from wheat flour and water, served with various sauces.",
            "tacos": "Tacos are a Mexican dish consisting of fillings wrapped in corn or flour tortillas."
        }
        
        for keyword, response in keywords.items():
            if keyword.lower() in question.lower():
                return f"(Using fallback) {response}"
        
        return "(Using fallback) I don't have specific information about that in my fallback database."
    except Exception as e:
        return f"Fallback also failed: {str(e)}"


# Interactive loop with error handling
print("\n🧠 Cloud RAG is ready. Ask a question (type 'exit' to quit):\n")
while True:
    try:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        if not question:
            print("⚠️ Please enter a question.\n")
            continue
        
        # Try primary RAG query
        answer = rag_query(question)
        
        # If primary fails, use fallback
        if answer and "error" in answer.lower():
            print("⚠️ Primary service failed, using fallback...\n")
            answer = fallback_query(question)
        
        print(f"\n🤖: {answer}\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        break
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Using fallback response...\n")
        answer = fallback_query(question)
        print(f"🤖: {answer}\n")
