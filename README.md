# Reddit Feedback AI 

A sophisticated Reddit feedback analysis tool with AI-powered insights, featuring a modern dark glassmorphism UI with liquid design elements.

![Reddit Feedback AI](https://img.shields.io/badge/Reddit%20Feedback-AI-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge)

## 🌟 Features

### Core Functionality
- **Reddit Scraping**: Automated data collection from subreddits with resumable scraping
- **RAG System**: Advanced semantic search with persistent embeddings
- **AI Chat Interface**: Real-time streaming responses powered by GPT-3.5
- **Smart Indexing**: Incremental embedding updates for new data

### UI/UX Enhancements
- **Dark Glassmorphism Design**: Modern glass effects with backdrop blur
- **Liquid Animations**: Smooth, organic animations throughout
- **Real-time Streaming**: Live AI responses with typing indicators
- **Responsive Layout**: Fully adaptive design for all screen sizes

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Reddit API credentials
- OpenAI API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name
```

4. Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
OPENAI_API_KEY=your_openai_api_key
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

4. Start the frontend:
```bash
npm run dev
```

## 📊 Usage

### Scraping Reddit Data
```bash
curl -X POST http://localhost:8000/bulk_scrape/patreon
```

### Querying the System
Simply type your question in the chat interface:
- "What are the common complaints about Patreon?"
- "What features do users want most?"
- "How do creators feel about monetization?"

## 🏗️ Architecture

### Backend Components
- **FastAPI**: High-performance API framework
- **PRAW**: Reddit API wrapper for data collection
- **SentenceTransformers**: State-of-the-art embeddings
- **RAG Manager**: Custom embedding persistence system

### Frontend Stack
- **Next.js 15**: React framework with App Router
- **Vercel AI SDK**: Streaming AI responses
- **Tailwind CSS**: Utility-first styling
- **React Markdown**: Rich text rendering

## 🎨 Design System

### Color Palette
- Background: `#0a0a0a` (Deep black)
- Glass: `rgba(255, 255, 255, 0.05-0.1)`
- Accent: Blue to purple gradient
- Text: High contrast whites and grays

### Effects
- Backdrop blur for glass panels
- Smooth animations with cubic bezier
- Glow effects on interactive elements
- Liquid morphing animations

## 🔧 API Endpoints

### Backend API
- `POST /bulk_scrape/{subreddit}` - Scrape subreddit data
- `POST /query` - Query the RAG system
- `GET /rag/stats` - Get indexing statistics
- `POST /rag/refresh` - Manually refresh embeddings
- `GET /health` - Health check

## 📈 Performance Optimizations

- **Embedding Persistence**: Cached embeddings for instant queries
- **Incremental Updates**: Only process new data
- **Streaming Responses**: Real-time AI output
- **Optimized Animations**: GPU-accelerated CSS transforms

## 🐛 Troubleshooting

### Common Issues

1. **Streaming not working**: Ensure CORS is enabled and using fetch API
2. **No embeddings found**: Run scraper first to collect data
3. **Slow responses**: Check if embeddings are persisted properly

### Debug Commands
```bash
# Check backend health
curl http://localhost:8000/health

# View RAG statistics
curl http://localhost:8000/rag/stats

# Refresh embeddings
curl -X POST http://localhost:8000/rag/refresh
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

---

Built with ❤️ using modern web technologies and AI
