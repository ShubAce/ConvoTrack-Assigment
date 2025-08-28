# 🤖 ConvoTrack - Business Intelligence Assistant

<div align="center">

![ConvoTrack Logo](https://img.shields.io/badge/ConvoTrack-Business%20Intelligence-blue?style=for-the-badge&logo=robot)

**Advanced QA Agent for Business Intelligence Analysis**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

</div>

## � Overview

ConvoTrack is an advanced business intelligence assistant that analyzes case studies to provide actionable insights for consumer behavior, marketing strategies, and business trends. Built with a modern tech stack featuring FastAPI backend and React frontend.

## ✨ Features

### 🧠 Intelligent Analysis

-   **Multiple Analysis Types**: Strategic, Trend, Comparative, Executive, and General analysis
-   **Advanced NLP**: Powered by Groq LLM with intelligent question routing
-   **Context-Aware**: Understands business intent and provides relevant insights

### 📊 Rich Data Processing

-   **Vector Search**: Pinecone-powered semantic search across case studies
-   **Smart Retrieval**: Enhanced context retrieval with query expansion
-   **Source Attribution**: Detailed source tracking with relevance scoring

### � Modern UI/UX

-   **Responsive Design**: Beautiful, mobile-first interface with Tailwind CSS
-   **Real-time Chat**: Interactive conversation interface with typing indicators
-   **Data Visualization**: Confidence scores, source counts, and analytics
-   **Dark Theme**: Modern glassmorphism design with smooth animations

### 🔍 Business Intelligence

-   **Consumer Insights**: Deep analysis of consumer behavior patterns
-   **Marketing Analytics**: Campaign effectiveness and strategy optimization
-   **Trend Analysis**: Market trends and future outlook predictions
-   **Competitive Analysis**: Comparative market positioning insights

## 🚀 Quick Start

### Prerequisites

-   🐍 Python 3.8+
-   📦 Node.js 16+ and npm
-   🔑 API Keys (Groq, HuggingFace, Pinecone)

### 🎯 One-Click Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/ShubAce/ConvoTrack-Assignment.git
    cd ConvoTrack
    ```

2. **Set up API keys**
   Create `qa_agent/.env` file:

    ```env
    GROQ_API_KEY=your_groq_api_key_here
    HUGGINGFACE_API_TOKEN=your_huggingface_token_here
    PINECONE_API_KEY=your_pinecone_api_key_here
    ```

3. **Launch the application**

    ```bash
    # Windows
    start_convotrack.bat

    # Or manually start both servers:
    # Backend: cd qa_agent && python fastapi_server.py
    # Frontend: cd frontend && npm run dev
    ```

4. **Access the application**
    - 🌐 Frontend: http://localhost:5173
    - 📖 API Docs: http://localhost:8000/docs
    - 🔍 Health Check: http://localhost:8000/health

## 🏗️ Architecture

```
ConvoTrack/
├── 🔧 qa_agent/                    # FastAPI Backend
│   ├── fastapi_server.py          # Main API server
│   ├── qa_agent.py                # Advanced QA logic
│   ├── document_loader.py         # Document processing
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # API keys (create this)
├── 🎨 frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.jsx                # Main React component
│   │   ├── App.css                # Custom styles
│   │   └── index.css              # Global styles
│   ├── package.json               # Node dependencies
│   └── vite.config.js             # Vite configuration
├── 📄 extractContent/             # Data Processing
│   ├── selenium_scraper.py        # Web scraping
│   └── scraped_articles_selenium/ # Case study articles
└── 🚀 start_convotrack.bat       # Launch script
```

## 🔧 API Endpoints

### Core Endpoints

-   `POST /ask` - Process business questions with analysis
-   `GET /topics` - Get available case study topics
-   `GET /analysis-types` - Get supported analysis types
-   `GET /insights` - Get conversation analytics
-   `POST /search` - Search similar content

### Analysis Types

1. **📊 General Business Analysis** - Comprehensive insights and recommendations
2. **🎯 Strategic Analysis** - Long-term strategic planning insights
3. **📈 Trend Analysis** - Market trends and future outlook
4. **📊 Comparative Analysis** - Side-by-side performance comparisons
5. **📋 Executive Summary** - C-level decision making insights

## 🎯 Usage Examples

### Business Strategy Questions

```
"What are the most effective marketing strategies for beauty brands?"
"How do consumer preferences compare between different age groups?"
"What trends are emerging in the food industry?"
```

### Performance Analysis

```
"Compare social media engagement rates across platforms"
"What metrics indicate successful brand campaigns?"
"Analyze ROI differences between digital marketing channels"
```

### Market Intelligence

```
"What consumer behavior patterns drive brand loyalty?"
"How do seasonal trends affect purchase decisions?"
"Identify growth opportunities in emerging markets"
```

## 🛠️ Development

### Backend Development

```bash
cd qa_agent
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python fastapi_server.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Required in `qa_agent/.env`:

```env
# LLM API
GROQ_API_KEY=gsk_your_groq_api_key

# Embeddings API
HUGGINGFACE_API_TOKEN=hf_your_huggingface_token

# Vector Database
PINECONE_API_KEY=pcsk_your_pinecone_api_key
```

## 🎨 UI Features

### Modern Design Elements

-   **Glassmorphism Effects** - Translucent backgrounds with blur effects
-   **Gradient Animations** - Smooth color transitions and hover effects
-   **Responsive Layout** - Mobile-first design with breakpoint optimization
-   **Interactive Components** - Animated buttons, loading states, and transitions

### User Experience

-   **Real-time Status** - API connection status with visual indicators
-   **Smart Suggestions** - Topic-based question suggestions
-   **Progressive Disclosure** - Collapsible sections for better information hierarchy
-   **Accessibility** - WCAG compliant with keyboard navigation support

## 📊 Analytics & Insights

### Conversation Analytics

-   Question categorization and intent analysis
-   Response confidence scoring
-   Source relevance tracking
-   Usage pattern analysis

### Business Intelligence Metrics

-   Engagement rate analysis
-   Conversion rate tracking
-   Market share comparisons
-   ROI calculations with projections

## 🚨 Troubleshooting

### Common Issues

**Backend not starting:**

-   Check if all API keys are properly set in `.env`
-   Verify Python version (3.8+)
-   Install dependencies: `pip install -r requirements.txt`

**Frontend build errors:**

-   Check Node.js version (16+)
-   Clear node_modules: `rm -rf node_modules && npm install`
-   Update dependencies: `npm update`

**Vector store issues:**

-   Verify Pinecone API key and permissions
-   Check if case study files exist in the correct directory
-   Force rebuild: Set `force_rebuild=True` in `setup_knowledge_base()`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## � Acknowledgments

-   **Groq** - High-performance LLM inference
-   **Pinecone** - Vector database for semantic search
-   **HuggingFace** - Pre-trained embedding models
-   **FastAPI** - Modern Python web framework
-   **React** - Frontend framework
-   **Tailwind CSS** - Utility-first CSS framework

---

<div align="center">

**Built with ❤️ for Business Intelligence**

[Report Bug](https://github.com/ShubAce/ConvoTrack-Assignment/issues) · [Request Feature](https://github.com/ShubAce/ConvoTrack-Assignment/issues) · [Documentation](https://github.com/ShubAce/ConvoTrack-Assignment/wiki)

</div>
