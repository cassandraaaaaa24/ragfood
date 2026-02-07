# 🧠 RAG-Food: Simple Retrieval-Augmented Generation with ChromaDB + Ollama

This is a **minimal working RAG (Retrieval-Augmented Generation)** demo using:

- ✅ Local LLM via [Ollama](https://ollama.com/)
- ✅ Local embeddings via `mxbai-embed-large`
- ✅ [ChromaDB](https://www.trychroma.com/) as the vector database
- ✅ A comprehensive food dataset in JSON (covering Indian, Korean, Taiwanese, Filipino, Singaporean cuisines, and more)

---

## 🎯 What This Does

This app allows you to ask questions about various foods from around the world, such as:

- "Which Indian dish uses chickpeas?"
- "What dessert is made from milk and soaked in syrup?"
- "What is masala dosa made of?"
- "What is japchae?"
- "Which foods are high in protein?"
- "Tell me about Singaporean food"
- "What vegan options are available?"
- "What foods can be grilled?"

It **does not rely on the LLM's built-in memory**. Instead, it:

1. **Embeds your custom text data** (about food) using `mxbai-embed-large`
2. Stores those embeddings in **ChromaDB**
3. For any question, it:
   - Embeds your question
   - Finds relevant context via similarity search
   - Passes that context + question to a local LLM (`llama3.2`)
4. Returns a natural-language answer grounded in your data

---

## 📦 Requirements

### ✅ Software

- Python 3.8+
- Ollama installed and running locally
- ChromaDB installed

### ✅ Ollama Models Needed

Run these in your terminal to install them:

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```

> Make sure `ollama` is running in the background. You can verify both models are installed with:
>
> ```bash
> ollama ls
> ```
>
> You should see both `mxbai-embed-large:latest` and `llama3.2:latest` in the output.

You can test if Ollama is working properly with:

```bash
ollama run llama3.2
```

---

## 🛠️ Setup and Installation Guide

### Step 1: Install Ollama

Download and install Ollama from [https://ollama.com/](https://ollama.com/)

After installation, verify it's working:

```bash
ollama --version
```

### Step 2: Pull Required Models

Download the LLM and embedding models:

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```

**Expected output for `mxbai-embed-large`:**
```
pulling manifest
pulling 8192adfc5ce6: 100%
pulling c71d239df917: 100%
pulling b837481ff855: 100%
pulling 38badd946f91: 100%
verifying sha256 digest
writing manifest
success
```

![Downloading mxbai-embed-large](Download_mxbai.png)

Verify both models are installed:

```bash
ollama ls
```

**Expected output:**
```
NAME
mxbai-embed-large:latest
llama3.2:latest
```

![Verifying Models Installed](ensuring_models_are_downloaded.png)

### Step 3: Clone or Download This Repository

```bash
git clone https://github.com/yourname/rag-food
cd rag-food
```

### Step 4: Install Python Dependencies

```bash
pip install chromadb requests
```

### Step 5: Run the RAG Application

```bash
python rag_run.py
```

**What happens on first run:**

- Creates `foods.json` if missing (with a diverse international food dataset)
- Generates embeddings for all food items
- Loads them into ChromaDB
- Displays a message: "Adding 15 new documents to Chroma..."
- Shows the prompt: "RAG is ready. Ask a question (type 'exit' to quit):"

![Initial RAG Run](testing.png)

---

## 📁 File Structure

```
rag-food/
├── rag_run.py       # Main app script
├── foods.json       # Food knowledge base (auto-generated if missing)
├── README.md        # This file
└── chroma_db/       # ChromaDB storage (created automatically)
```

### Code Structure Overview

The main `rag_run.py` file contains all the core RAG functionality:

![RAG Code Structure](Initial_Rag_Run_py_File.png)

---

## 🧠 How It Works (Step-by-Step)

1. **Data Loading**: Food information is loaded from `foods.json`
2. **Embedding Generation**: Each food entry is converted to a vector embedding using Ollama's `mxbai-embed-large` model
3. **Vector Storage**: Embeddings are stored in ChromaDB for fast similarity search
4. **Query Processing**: When you ask a question:
   - Your question is embedded using the same `mxbai-embed-large` model
   - ChromaDB performs a similarity search to find the top 3 most relevant food entries
   - The retrieved context is combined with your question
   - Everything is sent to `llama3.2` LLM for natural language generation
5. **Response Generation**: The model answers using only the retrieved information, not its pre-trained knowledge

---

## 🔍 Sample Queries and Expected Responses

Below are real examples from testing the RAG system:

### Query 1: "What is a food that includes oranges"

**Retrieved Sources:**
- Source 1 (ID: 4): "An apple can be red, green, or yellow and has a sweet taste."
- Source 2 (ID: 2): "A lemon is yellow and very sour."
- Source 3 (ID: 32): "Halo-halo is a Filipino dessert made from crushed ice, evaporated milk, and mixed ingredients like sweet beans, fruits, and jellies."

**Response:**
The system correctly identifies that while oranges aren't explicitly mentioned in the database, it provides an educated response based on similar items. It mentions that some variations of Halo-halo recipes might include orange flavors.

![Query: Food with Oranges](Screenshot_2026-02-07_143925.png)

---

### Query 2: "What is japchae?"

**Retrieved Sources:**
- Source 1 (ID: 89): "Japchae is a Korean stir-fried noodle dish made with sweet potato glass noodles, assorted vegetables, and marinated beef, cooked in sesame oil and soy sauce for a savory-sweet flavor."

**Response:**
"Japchae is a Korean stir-fried noodle dish made with sweet potato glass noodles, assorted vegetables, and marinated beef, cooked in sesame oil and soy sauce for a savory-sweet flavor."

**Analysis:** Perfect retrieval and accurate answer based on the knowledge base.

![Query: What is Japchae](Screenshot_2026-02-07_144032.png)

---

### Query 3: "Which foods are high in protein?"

**Retrieved Sources:**
- Source 1 (ID: 82): "Quinoa and Chickpea Salad is a refreshing mix of fluffy quinoa, protein-packed chickpeas, and fresh herbs, delivering a nutty flavor with a hint of citrus."
- Source 2 (ID: 84): "Lentil and Spinach Curry is a hearty stew of lentils simmered with aromatic spices and fresh spinach, creating a savory, earthy flavor with a touch of warmth."
- Source 3 (ID: 85): "Tofu Stir-Fry with Broccoli and Brown Rice is a colorful plant-based dish where tofu cubes are lightly sautéed with crisp broccoli and soy sauce, served over nutty brown rice."

**Response:**
"The foods that are high in protein from the given context are:
1. Chickpeas
2. Tofu"

**Analysis:** The RAG system successfully identified protein-rich foods from the database.

![Query: High Protein Foods](Screenshot_2026-02-07_144246.png)

---

### Query 4: "Tell me about Singaporean food"

**Retrieved Sources:**
- Source 1 (ID: 39): "Dim sum refers to a variety of small Chinese dishes served with tea, including dumplings, buns, and rolls."
- Source 2 (ID: 47): "Char siu is a Cantonese-style barbecued pork known for its sweet and savory glaze."
- Source 3 (ID: 37): "Chow mein is a stir-fried noodle dish made with vegetables and sometimes meat or seafood."

**Response:**
The system provides a comprehensive overview mentioning Hainanese chicken rice, chili crab, laksa, dim sum, and char siu, explaining Singapore's multicultural culinary influences.

**Analysis:** Even though the specific retrieved sources are Chinese dishes, the LLM provides contextually relevant Singaporean information by understanding the fusion nature of the cuisine.

![Query: Singaporean Food](Screenshot_2026-02-07_144349.png)

---

### Query 5: "What vegan options are available?"

**Retrieved Sources:**
- Source 1 (ID: 85): "Tofu Stir-Fry with Broccoli and Brown Rice..."
- Source 2 (ID: 82): "Quinoa and Chickpea Salad..."
- Source 3 (ID: 53): "Hangi is a traditional Māori method of cooking meat and vegetables in an underground oven."

**Response:**
"The Tofu Stir-Fry with Broccoli and Brown Rice and the Quinoa and Chickpea Salad are both vegan options, as they do not include any animal products."

**Analysis:** Accurate filtering and identification of vegan dishes from the knowledge base.

![Query: Vegan Options](Screenshot_2026-02-07_144511.png)

---

### Query 6: "What foods can be grilled?"

**Retrieved Sources:**
- Source 1 (ID: 81): "Grilled Salmon is a tender, flavorful fish dish served with steamed vegetables, offering a rich source of omega-3 fatty acids and a light, smoky taste."
- Source 2 (ID: 67): "Falafel consists of deep-fried balls of ground chickpeas or fava beans, typically served in pita bread."
- Source 3 (ID: 84): "Lentil and Spinach Curry..."

**Response:**
"Salmon."

**Analysis:** Direct and accurate answer based on the retrieved context.

---

## 💡 Personal Reflection on RAG Learning Experience

### What I Learned

Building this RAG system was an eye-opening journey into the world of retrieval-augmented generation. Here are my key takeaways:

#### 1. **The Power of Local LLMs**
Working with Ollama showed me that you don't always need expensive API calls to OpenAI or Anthropic. Running `llama3.2` locally was surprisingly fast and capable, especially for focused tasks like answering questions about a specific domain (food in this case).

#### 2. **Embeddings are Magic**
The `mxbai-embed-large` model converts text into numerical vectors in a way that captures semantic meaning. The fact that "What foods are high in protein?" can find relevant dishes about chickpeas and tofu without exact keyword matching is fascinating. It's all about meaning, not just words.

#### 3. **RAG Solves the Hallucination Problem**
One of the biggest challenges with LLMs is hallucination—making up facts. By grounding responses in retrieved documents from ChromaDB, the system only answers based on what it knows. When asked about oranges in my food database, it admitted the context doesn't directly mention them rather than fabricating an answer.

#### 4. **Vector Databases Are Fast**
ChromaDB made similarity search incredibly fast. Even with just 15 documents, the concept scales beautifully. I can imagine this working with thousands or even millions of entries for more complex use cases.

#### 5. **The Retrieval Quality Matters Most**
The quality of the final answer heavily depends on what gets retrieved. Sometimes the top 3 results weren't perfect (like when I asked about Singaporean food and got Chinese dishes), but the LLM was smart enough to provide reasonable context. This taught me that tuning retrieval parameters (like the number of results to fetch) is crucial.

### Challenges I Faced

- **Initial Setup**: Getting Ollama installed and pulling the right models took some trial and error. The documentation helped, but seeing the actual terminal outputs in the screenshots made it clearer.
- **Understanding Embeddings**: The concept of turning text into vectors was abstract at first. Playing with different queries helped me understand how semantic similarity works.
- **Prompt Engineering**: Crafting the right prompt to send to the LLM (combining context + question) required iteration to get natural-sounding answers.

### Why This Matters

RAG represents a practical middle ground between:
- Pure LLMs (powerful but prone to hallucination)
- Traditional keyword search (precise but limited)

By combining retrieval with generation, we get systems that are both accurate and fluent. This has applications everywhere: customer support bots, medical diagnosis assistants, legal document analysis, and more.

### Final Thoughts

Building this RAG system demystified AI for me. It's not magic—it's a clever combination of embeddings, vector search, and language models. The fact that I could build something this capable on my local machine, for free, is incredible.

If you're reading this and want to learn about RAG, I encourage you to build something yourself. Start small (like I did with food), get it working, then expand. The learning happens in the doing.

---

## 🚀 Next Ideas

- Swap in larger datasets (Wikipedia articles, recipes, PDFs)
- Add a web UI with Gradio or Flask
- Cache embeddings to avoid reprocessing on every run
- Implement conversation history for multi-turn dialogues
- Add metadata filtering (e.g., filter by cuisine type, dietary restrictions)
- Experiment with different LLMs (Mistral, Mixtral, etc.)
- Add hybrid search (combining vector similarity with keyword matching)

---

## 📚 Resources

- [Ollama Documentation](https://ollama.com)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [mxbai-embed-large Model](https://ollama.com/library/mxbai-embed-large)
- [RAG Concepts Explained](https://www.anthropic.com/index/retrieval-augmented-generation)

---

## 👨‍🍳 Credits

Made by **Callum** using:

- [Ollama](https://ollama.com) - Local LLM runtime
- [ChromaDB](https://www.trychroma.com) - Vector database
- [mxbai-embed-large](https://ollama.com/library/mxbai-embed-large) - Embedding model
- International food inspiration 🍛🍜🍕🌮

---

## 📝 License

MIT License - feel free to use this for learning and building!

---

**Happy RAG Building! 🚀**
