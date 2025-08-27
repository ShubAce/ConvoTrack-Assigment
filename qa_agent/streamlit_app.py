import streamlit as st
import os
from qa_agent import CaseStudyQAAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ConvoTrack Case Studies Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .answer-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        max-height: none;
        overflow: visible;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .source-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    .full-response {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        font-size: 1.1rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-width: 100%;
        overflow-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_qa_agent():
    """Initialize the Q&A agent (cached for performance)"""
    scraped_path = "../extractContent/scraped_articles_selenium"
    
    if not os.path.exists(scraped_path):
        st.error(f"Scraped articles not found at: {scraped_path}")
        return None
    
    try:
        return CaseStudyQAAgent(scraped_path)
    except Exception as e:
        st.error(f"Failed to initialize Q&A agent: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 ConvoTrack Case Studies Q&A Agent</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📚 About")
        st.write("""
        This Q&A agent can answer questions about ConvoTrack case studies using AI.
        
        **Features:**
        - Natural language questions
        - AI-powered answers
        - Source citations
        - Topic suggestions
        """)
        
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value=os.getenv("GROQ_API_KEY", ""),
            help="Enter your Groq API key. You can get one from https://console.groq.com/"
        )
        
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
        
        st.header("📊 Quick Stats")
        if os.path.exists("../extractContent/scraped_articles_selenium"):
            num_files = len([f for f in os.listdir("../extractContent/scraped_articles_selenium") if f.endswith('.txt')])
            st.metric("Case Studies", num_files)
        
    # Main content
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar to continue.")
        st.info("""
        To get a Groq API key:
        1. Visit https://console.groq.com/
        2. Sign up for a free account
        3. Navigate to API Keys section
        4. Create a new API key
        5. Copy and paste it in the sidebar
        """)
        return
    
    # Initialize Q&A agent
    with st.spinner("Initializing Q&A agent..."):
        qa_agent = initialize_qa_agent()
    
    if not qa_agent:
        st.error("Failed to initialize Q&A agent. Please check your setup.")
        return
    
    st.success("✅ Q&A Agent initialized successfully!")
    
    # Get available topics
    with st.spinner("Loading case study topics..."):
        topics = qa_agent.get_case_study_topics()
    
    # Topics section
    if topics:
        with st.expander("📋 Available Case Study Topics", expanded=False):
            cols = st.columns(3)
            for i, topic in enumerate(topics):
                with cols[i % 3]:
                    st.write(f"• {topic}")
    
    # Question input
    st.header("💬 Ask a Question")
    
    # Sample questions
    sample_questions = [
        "What are the key trends in ice cream innovation?",
        "How do consumers engage with DIY content in beauty brands?",
        "What are the main insights about health-conscious consumer behavior?",
        "Which social media platforms are most effective for engagement?",
        "What are the emerging trends in skincare market?",
    ]
    
    selected_sample = st.selectbox(
        "Choose a sample question or type your own:",
        [""] + sample_questions
    )
    
    user_question = st.text_area(
        "Your Question:",
        value=selected_sample,
        height=100,
        placeholder="Ask anything about the ConvoTrack case studies..."
    )
    
    # Search button
    if st.button("🔍 Get Answer", type="primary"):
        if user_question.strip():
            with st.spinner("Processing your question..."):
                response = qa_agent.ask(user_question.strip())
            
            # Display question
            st.markdown(f'<div class="question-box"><strong>❓ Question:</strong> {response["question"]}</div>', 
                       unsafe_allow_html=True)
            
            # Display answer - Use multiple methods to ensure full output is shown
            st.markdown("## 🤖 AI Assistant Answer")
            
            # Method 1: Use st.write for full text display
            st.write("**Complete Response:**")
            st.write(response["answer"])
            
            # Method 2: Also show in an expandable text area for easy copying
            with st.expander("📋 Copy Full Response", expanded=False):
                st.text_area(
                    "Full response text (select all to copy):",
                    value=response["answer"],
                    height=300,
                    help="You can select all text and copy it from here"
                )
            
            # Method 3: Show character/word count for verification
            char_count = len(response["answer"])
            word_count = len(response["answer"].split())
            st.caption(f"📊 Response length: {word_count} words, {char_count} characters")
            
            # Display sources
            if response["sources"]:
                st.header("📚 Sources")
                for i, source in enumerate(response["sources"], 1):
                    with st.expander(f"Source {i}: Article {source['article_number']}"):
                        st.write(f"**URL:** {source['source_url']}")
                        st.write(f"**Content Preview:**")
                        st.write(source['content'])
            else:
                st.info("No specific sources found for this answer.")
        else:
            st.warning("Please enter a question.")
    
    # Additional features
    st.header("🔍 Advanced Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Search Similar Content"):
            if user_question.strip():
                with st.spinner("Searching for similar content..."):
                    similar_docs = qa_agent.search_similar_content(user_question.strip())
                
                st.subheader("Similar Content Found:")
                for i, doc in enumerate(similar_docs, 1):
                    with st.expander(f"Result {i}"):
                        st.write(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
                        st.write(f"**Content:**")
                        st.write(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
    
    with col2:
        if st.button("📊 Show All Topics"):
            st.subheader("All Available Topics:")
            for topic in topics:
                st.write(f"• {topic}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>ConvoTrack Case Studies Q&A Agent | Powered by LangChain & Groq</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
