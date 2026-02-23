# 🚀 Vercel Deployment Guide

This guide walks you through deploying the RAG Food app to Vercel.

## Prerequisites

- A **Vercel account** (free at [vercel.com](https://vercel.com))
- **GitHub account** (recommended, for easier deployment)
- Your **Groq API key** from [console.groq.com](https://console.groq.com)
- Your **Upstash credentials** (optional, kept for future use)

---

## Option 1: Deploy via GitHub (Recommended) ✨

### Step 1: Push to GitHub

```bash
cd c:\Users\Chealsy\ragfood\web-app
git init
git add .
git commit -m "Initial commit: RAG Food web app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rag-food-web.git
git push -u origin main
```

### Step 2: Connect to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **Import Git Repository**
3. Select your `rag-food-web` repo
4. Click **Import**

### Step 3: Configure Environment Variables

In the Vercel dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add the following:

| Key                        | Value                              |
|----------------------------|------------------------------------|
| `GROQ_API_KEY`             | Your Groq API key                  |
| `UPSTASH_VECTOR_REST_URL`  | Your Upstash Vector URL (optional) |
| `UPSTASH_VECTOR_REST_TOKEN`| Your Upstash Token (optional)      |

### Step 4: Deploy

Click **Deploy** and wait for completion. Your app will be live at:
```
https://your-project-name.vercel.app
```

---

## Option 2: Deploy via Vercel CLI

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Configure Project

```bash
cd c:\Users\Chealsy\ragfood\web-app
vercel link
```

### Step 3: Add Environment Variables

Create `.env.production.local`:

```env
GROQ_API_KEY=your_groq_api_key
UPSTASH_VECTOR_REST_URL=your_upstash_url
UPSTASH_VECTOR_REST_TOKEN=your_upstash_token
```

### Step 4: Deploy

```bash
vercel --prod
```

---

## Option 3: One-Click Deploy

Click the button below (after pushing to GitHub):

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FYOUR_USERNAME%2Frag-food-web)

---

## Post-Deployment Checks

### 1. Verify Health Check

Visit:
```
https://your-app.vercel.app/api/health
```

Should return:
```json
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "2024-02-23T...",
  "checks": {
    "groq_api_key": "✓"
  }
}
```

### 2. Test the Search API

```bash
curl -X POST https://your-app.vercel.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is masala dosa?"}'
```

### 3. Access the Web Interface

Visit `https://your-app.vercel.app` and test a food query

---

## Troubleshooting

### Issue: "GROQ_API_KEY not configured"

**Solution:** Check that environment variables are set in Vercel dashboard:
1. Go to **Settings** → **Environment Variables**
2. Verify `GROQ_API_KEY` is listed
3. Redeploy with `vercel --prod`

### Issue: "Could not load foods.json"

**Solution:** The `data/foods.json` file is bundled with the deployment. If missing:
1. Verify `data/foods.json` exists in the web-app folder
2. Check `.vercelignore` doesn't exclude it
3. Redeploy: `vercel --prod`

### Issue: API returns error 500

**Solution:** Check Vercel logs:
```bash
vercel logs
```

Common causes:
- Missing environment variables
- Invalid Groq API key
- Timeout on slow networks

---

## Environment Variables Reference

```env
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxx  # From console.groq.com

# Optional (for vector search in future)
UPSTASH_VECTOR_REST_URL=https://xxx.upstash.io
UPSTASH_VECTOR_REST_TOKEN=xxxxxxxxxxxxx

# Automatic (set by Vercel)
VERCEL_ENV=production
NODE_ENV=production
```

---

## Performance Tips

1. **Assets**: Use Vercel's automatic image optimization
2. **Caching**: Set cache headers in `vercel.json`
3. **Functions**: Keep API routes under 12 seconds (default Vercel timeout)
4. **Regions**: Choose closest region to your users in Vercel dashboard

---

## Monitoring & Analytics

In Vercel dashboard:
- **Analytics** tab: View API latency, response times
- **Logs** tab: See recent request logs
- **Deployments** tab: Roll back if needed

---

## Future Improvements

- [ ] Add database for saving favorite searches
- [ ] Implement caching with Redis
- [ ] Add authentication
- [ ] Setup AI-powered search with embeddings
- [ ] Add analytics tracking

---

## Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Groq API Docs**: https://console.groq.com/docs
- **Next.js Deployment**: https://nextjs.org/docs/deployment

---

**Good luck! 🚀**
