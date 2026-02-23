# 🍜 RAG Food Web Application

A modern web interface for querying food information using Retrieval-Augmented Generation (RAG) with Groq LLM and optional Upstash Vector search.

## 🚀 Quick Start

```bash
cd web-app
npm install
cp .env.example .env.local
# Fill in your Groq API key in .env.local
npm run dev
```

Visit `http://localhost:3000` 🎉

## 📋 Prerequisites

- Node.js 18+ and npm
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Optional: Upstash Vector account (for advanced search)

## ✨ Features

- **Modern UI**: Clean, responsive design built with React and Tailwind CSS
- **Fast LLM**: Powered by Groq's fast inference API (LLaMA 3.1)
- **Smart Search**: Searches local food dataset + Groq knowledge
- **Example Questions**: 8 pre-loaded questions to get started
- **Error Handling**: Graceful error messages and retry logic
- **Production Ready**: Optimized for Vercel serverless deployment

## 🛠️ Local Development

### 1. Install Dependencies

```bash
cd web-app
npm install
```

### 2. Set Environment Variables

```bash
cp .env.example .env.local
```

Edit `.env.local` and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) ✅

## 🚀 Deploy to Vercel

**Read the full [DEPLOYMENT.md](DEPLOYMENT.md) guide for detailed instructions.**

### Quick Deploy:

```bash
npm install -g vercel
vercel --prod
```

Or connect your GitHub repo to Vercel for automatic deployments.

## 📚 API Routes

### POST `/api/search`

Search for food information.

**Request:**
```json
{
  "query": "What is masala dosa?"
}
```

**Response:**
```json
{
  "answer": "Masala dosa is...",
  "context": "Context from vector search",
  "sources": ["Vector DB", "Local Dataset"]
}
```

## 🏗️ Project Structure

```
web-app/
├── app/
│   ├── api/
│   │   └── search/
│   │       └── route.ts          # Search API endpoint
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home page
│   └── globals.css               # Global styles
├── components/
│   ├── SearchBox.tsx             # Search input component
│   ├── ResultCard.tsx            # Result display component
│   ├── LoadingSpinner.tsx        # Loading animation
│   └── ExampleQuestions.tsx      # Example questions grid
├── package.json
├── next.config.js
├── tsconfig.json
├── tailwind.config.js
├── .env.example
└── README.md
```

## 🔧 Configuration

### Tailwind CSS

Customize colors and fonts in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#FF6B6B',    // Red
      secondary: '#4ECDC4',  // Teal
    }
  }
}
```

### Next.js

Configure Next.js options in `next.config.js`:

- Max API timeout
- Public API URL
- Runtime config

## 🛠️ Development

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Create production build
npm start        # Run production server
npm run lint     # Run ESLint
```

### Adding New Components

1. Create `.tsx` file in `components/`
2. Use `'use client'` directive for client components
3. Export as default
4. Import in `app/page.tsx` or other pages

## 🚀 Production Optimization

The app is optimized for production:

- ✅ Server-side rendering
- ✅ Static generation where possible
- ✅ Image optimization
- ✅ Code splitting
- ✅ CSS minification
- ✅ JavaScript compression

## 📝 Troubleshooting

### API Errors

Check that all environment variables are set correctly:

```bash
# Check if variables exist
echo $GROQ_API_KEY
echo $UPSTASH_VECTOR_REST_URL
echo $UPSTASH_VECTOR_REST_TOKEN
```

### Build Fails

```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

### Port Already in Use

```bash
npm run dev -- -p 3001  # Use different port
```

## 📄 License

MIT

## 🤝 Support

For issues with:

- **Groq API**: https://console.groq.com/docs
- **Upstash Vector**: https://upstash.com/docs/redis/features/vector
- **Next.js**: https://nextjs.org/docs

---

**Happy coding! 🚀**
