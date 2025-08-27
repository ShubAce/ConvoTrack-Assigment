# ConvoTrack Case Studies Q&A Agent

A sophisticated AI-powered Q&A system that can answer natural language questions about ConvoTrack case studies using LangChain and Groq.

## 🚀 Features

-   **Natural Language Q&A**: Ask questions in plain English about the case studies
-   **AI-Powered Answers**: Uses Groq's powerful LLMs (Mixtral-8x7B) for intelligent responses
-   **Source Citations**: Provides references to specific case studies for transparency
-   **Pinecone Vector Store**: Fast, scalable vector search using Pinecone's cloud service
-   **HuggingFace Embeddings**: High-quality embeddings via HuggingFace API
-   **Web Interface**: Beautiful Streamlit-based web app
-   **Command Line Interface**: Simple CLI for quick queries
-   **Topic Discovery**: Browse available case study topics

## 📋 Prerequisites

-   Python 3.8 or higher
-   **Groq API key** (free from [console.groq.com](https://console.groq.com/))
-   **HuggingFace API token** (free from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))
-   **Pinecone API key** (free tier available from [pinecone.io](https://www.pinecone.io/))
-   Scraped case study content (from the selenium scraper)

## 🛠️ Installation

### 1. Quick Setup

Run the automated setup script:

```bash
cd f:/ConvoTrack/qa_agent
python setup.py
```

This will:

-   Check your Python version
-   Verify scraped content exists
-   Install all dependencies
-   Create environment files
-   Test the installation

### 2. Manual Setup

If you prefer manual installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your GROQ_API_KEY
```

### 3. Get Your API Keys

#### Groq API Key

1. Visit [console.groq.com](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to "API Keys"
4. Create a new API key

#### HuggingFace API Token

1. Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Sign up/login to your account
3. Create a new token with "Read" permission

#### Pinecone API Key

1. Visit [pinecone.io](https://www.pinecone.io/)
2. Sign up for a free account (includes 100K vectors)
3. Go to "API Keys" in your dashboard
4. Copy your API key

Add all keys to your `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

## 🎯 Usage

### Web Interface (Recommended)

Launch the Streamlit web app:

```bash
streamlit run streamlit_app.py
```

Features:

-   🎨 Beautiful, intuitive interface
-   📱 Responsive design
-   🔍 Sample questions for inspiration
-   📚 Source citations with previews
-   🎯 Advanced search capabilities

### Command Line Interface

For quick queries from the terminal:

```bash
python cli.py
```

Commands:

-   Type any question directly
-   `help` - Show available commands
-   `topics` - List all case study topics
-   `search <query>` - Find similar content
-   `quit` - Exit the application

### Python API

Use the Q&A agent in your own Python code:

```python
from qa_agent import CaseStudyQAAgent

# Initialize the agent
agent = CaseStudyQAAgent("../extractContent/scraped_articles_selenium")

# Ask a question
response = agent.ask("What are the key trends in ice cream innovation?")

print(f"Answer: {response['answer']}")
print(f"Sources: {len(response['sources'])} case studies referenced")
```

## 📊 Example Questions

Try these sample questions to explore the case studies:

### General Insights

-   "What are the main consumer trends across all case studies?"
-   "Which industries show the most innovation potential?"
-   "What are common challenges brands face in digital engagement?"

### Specific Categories

-   "What are the key trends in ice cream innovation?"
-   "How do beauty brands leverage influencer partnerships?"
-   "What insights exist about health-conscious consumer behavior?"

### Strategic Analysis

-   "Which social media platforms are most effective for engagement?"
-   "What are the emerging trends in skincare market?"
-   "How do brands successfully enter new markets?"

### Content Strategy

-   "What types of content drive the highest engagement?"
-   "How important is DIY content for consumer brands?"
-   "What role do micro-influencers play in brand strategy?"

## 🏗️ Architecture

### Components

1. **Document Loader** (`document_loader.py`)

    - Loads scraped case study files
    - Splits content into searchable chunks
    - Creates vector embeddings using sentence transformers

2. **Q&A Agent** (`qa_agent.py`)

    - Main AI agent using LangChain and Groq
    - Handles question processing and answer generation
    - Manages retrieval and source citation

3. **Web Interface** (`streamlit_app.py`)

    - Streamlit-based web application
    - User-friendly interface with advanced features

4. **CLI** (`cli.py`)
    - Command-line interface for quick access

### Technology Stack

-   **LangChain**: Framework for building AI applications
-   **Groq**: Fast LLM inference (Mixtral-8x7B model)
-   **Pinecone**: Cloud-based vector database for document storage
-   **HuggingFace**: API-based text embeddings for similarity search
-   **Streamlit**: Web interface framework

### Data Flow

1. **Indexing**: Case studies → Text chunks → HuggingFace embeddings → Pinecone vector store
2. **Query**: User question → Vector search in Pinecone → Relevant chunks → Groq LLM → Answer + Sources

## 📁 Project Structure

```
qa_agent/
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── setup.py                 # Automated setup script
├── document_loader.py       # Document processing and vector store
├── qa_agent.py             # Main Q&A agent
├── streamlit_app.py        # Web interface
├── cli.py                  # Command line interface
├── test_setup.py             # Test script for API connections
├── README.md                 # This file
└── (Pinecone cloud storage)  # Vector database (cloud-hosted)
```

## 🔧 Configuration

### Environment Variables

-   `GROQ_API_KEY`: Your Groq API key (required)
-   `HUGGINGFACE_API_TOKEN`: Your HuggingFace API token (required)
-   `PINECONE_API_KEY`: Your Pinecone API key (required)
-   `OPENAI_API_KEY`: Optional, for using OpenAI instead of Groq

### Customization

You can customize various parameters in `qa_agent.py`:

```python
# LLM settings
model_name="mixtral-8x7b-32768"  # or "llama2-70b-4096"
temperature=0.1                   # Lower = more focused answers
max_tokens=1024                   # Response length limit

# Retrieval settings
search_kwargs={"k": 5}           # Number of relevant chunks to retrieve
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

2. **API Key Issues**

    - Verify your Groq API key is correct
    - Check the `.env` file format
    - Ensure the API key has sufficient credits

3. **No Scraped Content**

    - Run the selenium scraper first: `python selenium_scraper.py`
    - Verify files exist in `../extractContent/scraped_articles_selenium/`

4. **ChromaDB Issues**
    - Delete the `chroma_db` folder and rebuild: `rm -rf chroma_db`
    - Restart the application to rebuild the vector store

### Performance Tips

-   First run takes longer due to vector store creation
-   Subsequent runs are much faster (vector store is cached)
-   Use shorter, specific questions for better results
-   The system works best with questions about insights, trends, and strategies

## 📈 Future Enhancements

-   [ ] Support for additional LLM providers
-   [ ] Advanced filtering by industry or topic
-   [ ] Export functionality for answers and sources
-   [ ] Conversation history and follow-up questions
-   [ ] Integration with more document formats
-   [ ] Analytics dashboard for usage patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

-   **LangChain** for the excellent AI framework
-   **Groq** for fast and reliable LLM inference
-   **ChromaDB** for efficient vector storage
-   **Streamlit** for the beautiful web interface

---

**Need help?** Check the troubleshooting section or raise an issue in the repository.
