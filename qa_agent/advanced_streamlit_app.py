import streamlit as st
import os
from enhanced_qa_agent_backup import AdvancedCaseStudyQAAgent
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ConvoTrack Business Intelligence Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .question-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_qa_agent():
    """Initialize the Advanced Q&A agent"""
    scraped_path = "../extractContent/scraped_articles_selenium"
    
    if not os.path.exists(scraped_path):
        st.error(f"Scraped articles not found at: {scraped_path}")
        return None
    
    try:
        return AdvancedCaseStudyQAAgent(scraped_path)
    except Exception as e:
        st.error(f"Failed to initialize Advanced Q&A agent: {str(e)}")
        return None

def main():
    
    # Sidebar
    with st.sidebar:
        st.header("🚀 Advanced Features")
        st.write("""
        **AI Capabilities:**
        - 🧠 Multi-prompt analysis
        - 🔍 Enhanced context retrieval
        - 📊 Smart question detection
        - 🎯 Business intent recognition
        - 💡 Creative insight generation
        """)
        
        st.header("🔧 Configuration")
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value=os.getenv("GROQ_API_KEY", ""),
            help="Enter your Groq API key"
        )
        
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
        
        st.header("📊 Status")
        if os.path.exists("../extractContent/scraped_articles_selenium"):
            num_files = len([f for f in os.listdir("../extractContent/scraped_articles_selenium") if f.endswith('.txt')])
            st.metric("Case Studies", num_files)
            st.metric("Agent Mode", "🧠 Advanced")
    
    # Main content
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar.")
        st.info("Get your API key at https://console.groq.com/")
        return
    
    # Initialize agent
    with st.spinner("🧠 Initializing Advanced Business Intelligence Agent..."):
        qa_agent = initialize_qa_agent()
        if qa_agent:
            st.session_state.qa_agent = qa_agent
    
    if not qa_agent:
        st.error("Failed to initialize the agent.")
        return
    
    st.success("✅ Advanced Business Intelligence Agent ready!")
    
    # Show capabilities
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🎯 **Creative Analysis**\\nInnovative business perspectives")
    with col2:
        st.info("⚡ **Practical Solutions**\\nActionable recommendations")  
    with col3:
        st.info("🔍 **Effective Understanding**\\nAdvanced NLP comprehension")
    
    # Question input
    st.header("💼 Ask Your Business Question")
    
    # Enhanced sample questions
    sample_questions = [
        "What are the most effective marketing strategies for beauty brands?",
        "Compare social media engagement rates between platforms",
        "What emerging trends are driving growth in the food industry?",
        "Which content types generate the highest conversion rates?",
        "How do different age groups respond to wellness marketing?",
        "What metrics indicate successful brand campaigns?",
    ]
    
    # Tabs for question types
    tab1, tab2, tab3 = st.tabs(["🎯 Strategic", "📊 Comparative", "🔮 Trends"])
    
    with tab1:
        strategic_q = st.selectbox("Strategic Questions:", 
            [""] + [q for q in sample_questions if any(word in q.lower() for word in ['strategy', 'effective', 'metrics'])])
    with tab2:
        comparative_q = st.selectbox("Comparative Questions:",
            [""] + [q for q in sample_questions if 'compare' in q.lower() or 'between' in q.lower()])
    with tab3:
        trend_q = st.selectbox("Trend Questions:",
            [""] + [q for q in sample_questions if any(word in q.lower() for word in ['trend', 'emerging', 'growth'])])
    
    selected_sample = strategic_q or comparative_q or trend_q
    
    user_question = st.text_area(
        "Your Business Intelligence Question:",
        value=selected_sample,
        height=120,
        placeholder="Ask about consumer insights, marketing strategies, brand performance, trends...",
        help="💡 I use advanced NLP to provide tailored analysis!"
    )
    
    # Analysis button
    if st.button("🧠 Generate Advanced Analysis", type="primary", use_container_width=True):
        if user_question.strip():
            with st.spinner("🔬 Performing advanced analysis..."):
                response = qa_agent.ask(user_question.strip())
            
            # Display question
            st.markdown(f"""
            <div class="question-box">
                <strong>🎯 Question:</strong> {response["question"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Show metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Type", response.get("agent_type", "N/A").replace("_", " ").title())
            with col2:
                st.metric("Confidence", response.get("confidence", "N/A").upper())
            with col3:
                st.metric("Intent", response.get("intent", "N/A").replace("_", " ").title())
            with col4:
                st.metric("Sources", len(response.get("sources", [])))
            
            # Display analysis
            agent_type = response.get("agent_type", "advanced_analysis")
            
            if agent_type == "advanced_analysis":
                st.markdown("## 🧠 Advanced Business Intelligence Analysis")
                st.success("✅ Comprehensive analysis completed!")
            elif agent_type == "scope_guidance":
                st.markdown("## 🎯 Intelligent Guidance")
                st.info("ℹ️ Let me help you ask better business questions.")
            else:
                st.markdown("## 📝 Response")
            
            # Full response
            st.markdown("### 📊 Complete Analysis:")
            st.markdown(response["answer"])
            
            # Copy section
            with st.expander("📋 Copy Full Analysis", expanded=False):
                st.text_area(
                    "Complete response:",
                    value=response["answer"],
                    height=300,
                    help="Select all to copy"
                )
            
            # Response metrics
            char_count = len(response["answer"])
            word_count = len(response["answer"].split())
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", word_count)
            with col2:
                st.metric("Characters", char_count)
            with col3:
                st.metric("Categories", len(response.get("categories", [])))
            
            # Sources
            if response["sources"]:
                st.markdown("## 📚 Source Intelligence")
                
                for i, source in enumerate(response["sources"], 1):
                    relevance = source.get('relevance', 'Unknown')
                    with st.expander(f"📄 Source {i}: Case Study {source['article_number']} - {relevance} Relevance"):
                        st.write(f"**URL:** {source['source_url']}")
                        st.write(f"**Content:**")
                        st.write(source['content'])
                        if 'relevance_score' in source:
                            st.metric("Relevance Score", source['relevance_score'])
            else:
                st.info("💡 Analysis based on general business intelligence patterns.")
        else:
            st.warning("📝 Please enter a business question.")
    
    # Advanced features
    st.header("🚀 Advanced Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Strategic Opportunities", use_container_width=True):
            if user_question.strip():
                with st.spinner("🔍 Analyzing strategic opportunities..."):
                    opportunity_query = f"Strategic opportunities from: {user_question.strip()}"
                    similar_docs = qa_agent.search_similar_content(opportunity_query)
                
                st.subheader("🎯 Strategic Opportunities:")
                for i, doc in enumerate(similar_docs, 1):
                    with st.expander(f"Opportunity {i}"):
                        st.write(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
                        content = doc.page_content[:300] + "..."
                        st.write(content)
                        
                        if any(word in content.lower() for word in ['growth', 'success', 'opportunity']):
                            st.success("💡 Positive indicator")
                        elif any(word in content.lower() for word in ['challenge', 'problem']):
                            st.warning("⚠️ Challenge area")
    
    with col2:
        if st.button("📊 Executive Summary", use_container_width=True):
            with st.spinner("📊 Generating executive summary..."):
                summary_response = qa_agent.ask("Provide comprehensive executive summary of key business insights and strategic recommendations")
                
                st.subheader("📊 Executive Summary:")
                st.markdown(summary_response["answer"])
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <h4>🧠 ConvoTrack Advanced Business Intelligence Agent</h4>
        <p><strong>Creative Analysis • Practical Solutions • Effective Understanding</strong></p>
        <p>Powered by Advanced NLP | Enhanced Context Retrieval | Multi-Prompt Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
