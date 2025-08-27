import streamlit as st
import os
from enhanced_qa_agent import AdvancedCaseStudyQAAgent
from dotenv import load_dotenv
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from typing import Dict, List, Any, Optional, Tuple

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="ConvoTrack Synthesized BI Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .results-container {
        background: #FFFFFF;
        padding: 2.5rem;
        border-radius: 20px;
        margin-top: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e0e6ed;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    h2 {
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-top: 2rem;
    }
    h3 {
        color: #764ba2;
    }
</style>
""", unsafe_allow_html=True)

# --- Caching the QA Agent ---
@st.cache_resource
def initialize_qa_agent():
    """Initializes the Q&A agent and caches it for performance."""
    scraped_path = "../extractContent/scraped_articles_selenium"
    if not os.path.exists(scraped_path):
        st.error(f"Data directory not found at: {scraped_path}")
        return None
    try:
        return AdvancedCaseStudyQAAgent(scraped_path)
    except Exception as e:
        st.error(f"Failed to initialize AI agent: {str(e)}")
        return None

# --- Intelligent Data Extraction Functions ---
class DataExtractor:
    """Extracts quantitative data from analysis reports for visualization"""
    
    @staticmethod
    def extract_percentages(text: str) -> Dict[str, float]:
        """Extract percentage values with their context"""
        pattern = r'(\w+(?:\s+\w+)*)\s*(?:is|are|shows?|at|of)?\s*(\d+(?:\.\d+)?)\s*%'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        data = {}
        for context, value in matches:
            # Clean up context
            context = re.sub(r'\b(the|of|in|at|with|for|and|or)\b', '', context, flags=re.IGNORECASE).strip()
            if context and len(context.split()) <= 4:  # Only keep reasonable contexts
                data[context.title()] = float(value)
        
        return data
    
    @staticmethod
    def extract_numerical_comparisons(text: str) -> Dict[str, Dict[str, float]]:
        """Extract comparative numerical data"""
        # Look for patterns like "Brand A: 85%, Brand B: 72%"
        comparison_pattern = r'(\w+(?:\s+\w+)*)\s*[:\-]\s*(\d+(?:\.\d+)?)\s*%?'
        matches = re.findall(comparison_pattern, text)
        
        if len(matches) >= 2:
            comparison_data = {}
            for item, value in matches[:5]:  # Limit to 5 items
                item = item.strip().title()
                if item and not any(skip in item.lower() for skip in ['the', 'this', 'that', 'which']):
                    comparison_data[item] = float(value)
            
            if len(comparison_data) >= 2:
                return {"Comparison": comparison_data}
        
        return {}
    
    @staticmethod
    def extract_time_series_data(text: str) -> Dict[str, float]:
        """Extract time-based data"""
        # Look for year patterns with values
        year_pattern = r'(\d{4})\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%?'
        matches = re.findall(year_pattern, text)
        
        if len(matches) >= 2:
            time_data = {}
            for year, value in matches:
                if 2020 <= int(year) <= 2030:  # Reasonable year range
                    time_data[year] = float(value)
            
            if len(time_data) >= 2:
                return time_data
        
        return {}
    
    @staticmethod
    def extract_growth_rates(text: str) -> Dict[str, float]:
        """Extract growth rate data"""
        growth_pattern = r'(\w+(?:\s+\w+)*)\s*(?:growth|increase|rise|grew)\s*(?:by|of)?\s*(\d+(?:\.\d+)?)\s*%'
        matches = re.findall(growth_pattern, text, re.IGNORECASE)
        
        growth_data = {}
        for context, rate in matches:
            context = context.strip().title()
            if context and len(context.split()) <= 3:
                growth_data[context] = float(rate)
        
        return growth_data

class VisualizationDecider:
    """Decides when and what type of visualization to create with strict criteria"""
    
    @staticmethod
    def should_create_visualization(data: Dict[str, Any], analysis_type: str, question: str) -> bool:
        """Determine if visualization adds value with enhanced criteria"""
        # STRICT RULE 1: Must have sufficient data points
        if not data or len(data) < 2:
            return False
        
        # STRICT RULE 2: Data values must be meaningful numbers (not just random text matches)
        try:
            values = []
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        values.extend(value.values())
                    else:
                        values.append(value)
            
            # Must have at least 2 valid numerical values
            valid_values = [v for v in values if isinstance(v, (int, float)) and v >= 0]
            if len(valid_values) < 2:
                return False
            
            # Values should have some variation (not all the same)
            if len(set(valid_values)) < 2:
                return False
            
            # Values should be in reasonable ranges (0-100000 for percentages/metrics)
            if any(v > 100000 for v in valid_values):
                return False
                
        except Exception:
            return False
        
        # STRICT RULE 3: Check if question/analysis specifically requests or benefits from visualization
        viz_indicators = ['compare', 'comparison', 'trend', 'performance', 'growth', 'rate', 'percentage', 
                         'metrics', 'data', 'chart', 'graph', 'visual', 'show', 'display', 'analyze']
        text_to_check = (question + " " + analysis_type).lower()
        
        has_viz_request = any(indicator in text_to_check for indicator in viz_indicators)
        
        # STRICT RULE 4: Must have contextual relevance
        # Don't create charts for purely strategic/qualitative questions
        qualitative_indicators = ['strategy', 'recommend', 'suggest', 'advice', 'opinion', 'think', 'why', 'how to']
        is_qualitative = any(indicator in text_to_check for indicator in qualitative_indicators)
        
        # STRICT RULE 5: Final decision logic
        # Create visualization ONLY if:
        # - Has sufficient valid data AND
        # - Question indicates need for visualization AND  
        # - NOT purely qualitative question
        return has_viz_request and not is_qualitative
    
    @staticmethod
    def validate_data_quality(data: Dict[str, Any]) -> bool:
        """Additional validation for data quality"""
        if not data:
            return False
            
        # Check for meaningful labels (not just numbers or single characters)
        for key in data.keys():
            if isinstance(key, str) and len(key.strip()) < 2:
                return False
            if key.isdigit() and len(data) < 3:  # Years need at least 3 points for trend
                return False
        
        return True
    
    @staticmethod
    def determine_chart_type(data: Dict[str, Any], context: str) -> str:
        """Determine the best chart type for the data"""
        if isinstance(data, dict):
            # Check if it's comparison data
            if any(word in context.lower() for word in ['compare', 'vs', 'versus', 'between']):
                return "multi_bar" if len(data) > 1 and isinstance(list(data.values())[0], dict) else "bar"
            
            # Check if it's time series data
            if any(key.isdigit() and len(key) == 4 for key in data.keys()):
                return "line"
            
            # Check if it's categorical distribution
            if len(data) >= 3 and all(isinstance(v, (int, float)) for v in data.values()):
                total = sum(data.values())
                if 80 <= total <= 120:  # Looks like percentages that sum to ~100
                    return "pie"
            
            # Default to bar chart for categorical data
            return "bar"
        
        return "bar"

# --- Enhanced Charting Function ---
def create_detailed_chart(chart_type: str, data: Dict, title: str, x_label: str, y_label: str):
    """Create enhanced charts with proper styling and labels"""
    fig = None
    
    if chart_type == "bar":
        fig = px.bar(
            x=list(data.keys()), y=list(data.values()), title=title,
            labels={'x': x_label, 'y': y_label}, color=list(data.values()),
            color_continuous_scale="viridis", text=list(data.values())
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
    
    elif chart_type == "line":
        df = pd.DataFrame(list(data.items()), columns=[x_label, y_label])
        fig = px.line(df, x=x_label, y=y_label, title=title, markers=True, text=y_label)
        fig.update_traces(textposition="top center")
    
    elif chart_type == "multi_bar":
        fig = go.Figure()
        colors = px.colors.qualitative.Plotly
        for i, (category, values) in enumerate(data.items()):
            fig.add_trace(go.Bar(
                name=category, x=list(values.keys()), y=list(values.values()),
                marker_color=colors[i % len(colors)], text=[f"{v}" for v in values.values()],
                textposition='outside'
            ))
        fig.update_layout(barmode='group', title=title, xaxis_title=x_label, yaxis_title=y_label)
    
    elif chart_type == "scatter":
        if isinstance(data, pd.DataFrame):
            fig = px.scatter(data, x=data.columns[0], y=data.columns[1], title=title, 
                           size=data.columns[1], color=data.index)
        else:
            df = pd.DataFrame(list(data.items()), columns=[x_label, y_label])
            fig = px.scatter(df, x=x_label, y=y_label, title=title, text=x_label, size=y_label)
        fig.update_traces(textposition='top center')
    
    elif chart_type == "pie":
        fig = px.pie(values=list(data.values()), names=list(data.keys()), title=title, hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
    
    elif chart_type == "heatmap":
        if isinstance(data, pd.DataFrame):
            fig = px.imshow(data, title=title, labels=dict(x=x_label, y=y_label, color="Value"),
                           aspect="auto", color_continuous_scale="viridis")
        else:
            # Convert dict to simple heatmap
            df = pd.DataFrame([data])
            fig = px.imshow(df, title=title, aspect="auto", color_continuous_scale="viridis")

    if fig:
        fig.update_layout(
            title_font_size=18, title_x=0.5, title_font_weight="bold",
            xaxis_title_font_size=14, yaxis_title_font_size=14,
            xaxis_title_font_weight="bold", yaxis_title_font_weight="bold",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
            height=500, font=dict(family="sans-serif", size=12)
        )
        
        # Add watermark
        fig.add_annotation(
            text="ConvoTrack Business Intelligence",
            xref="paper", yref="paper", x=1, y=0, xanchor='right', yanchor='bottom',
            showarrow=False, font=dict(size=10, color="gray"), opacity=0.5
        )
        
        return fig
    
    return go.Figure()

def generate_intelligent_visualizations(report_text: str, analysis_type: str, question: str) -> List[Tuple[str, Dict, str, str, str]]:
    """Generate visualizations based on actual report content with strict validation"""
    extractor = DataExtractor()
    decider = VisualizationDecider()
    
    visualizations = []
    
    # Extract different types of data
    percentages = extractor.extract_percentages(report_text)
    comparisons = extractor.extract_numerical_comparisons(report_text)
    time_series = extractor.extract_time_series_data(report_text)
    growth_rates = extractor.extract_growth_rates(report_text)
    
    # ENHANCED VALIDATION: Only create visualizations with strict criteria
    
    # 1. Validate and potentially visualize percentages
    if (percentages and 
        decider.validate_data_quality(percentages) and 
        decider.should_create_visualization(percentages, analysis_type, question)):
        chart_type = decider.determine_chart_type(percentages, report_text)
        title = f"Key Performance Metrics from Analysis"
        visualizations.append((chart_type, percentages, title, "Metrics", "Percentage (%)"))
    
    # 2. Validate and potentially visualize comparisons
    if comparisons:
        for comp_name, comp_data in comparisons.items():
            if (comp_data and 
                decider.validate_data_quality(comp_data) and
                decider.should_create_visualization(comp_data, analysis_type, question)):
                chart_type = decider.determine_chart_type(comp_data, report_text)
                title = f"{comp_name} Comparative Analysis"
                visualizations.append((chart_type, comp_data, title, "Categories", "Values"))
    
    # 3. Validate and potentially visualize time series (needs at least 3 points for meaningful trend)
    if (time_series and 
        len(time_series) >= 3 and  # Strict requirement for time trends
        decider.validate_data_quality(time_series) and
        decider.should_create_visualization(time_series, analysis_type, question)):
        title = f"Trend Analysis Over Time"
        visualizations.append(("line", time_series, title, "Year", "Value"))
    
    # 4. Validate and potentially visualize growth rates
    if (growth_rates and 
        decider.validate_data_quality(growth_rates) and
        decider.should_create_visualization(growth_rates, analysis_type, question)):
        title = f"Growth Rate Analysis"
        visualizations.append(("bar", growth_rates, title, "Categories", "Growth Rate (%)"))
    
    # FINAL CHECK: Ensure we have meaningful visualizations
    # Remove any visualization that doesn't meet final quality standards
    validated_visualizations = []
    for viz in visualizations:
        chart_type, data, title, x_label, y_label = viz
        
        # Final data quality check
        if isinstance(data, dict) and len(data) >= 2:
            # Check data variance (values shouldn't all be the same)
            values = []
            if isinstance(list(data.values())[0], dict):
                for sub_dict in data.values():
                    values.extend(sub_dict.values())
            else:
                values = list(data.values())
            
            # Only add if there's meaningful variation in the data
            if len(set(values)) > 1 and max(values) != min(values):
                validated_visualizations.append(viz)
    
    return validated_visualizations

# --- CORE ANALYSIS FUNCTION (ENHANCED FOR SPECIALIZED OUTPUTS) ---
def perform_synthesized_analysis(question, qa_agent, analysis_type):
    """
    Performs specialized analysis based on analysis type:
    1. Gets base analysis using default prompt
    2. Gets specialized analysis using type-specific prompt  
    3. Synthesizes both into a cohesive, type-specific report
    """
    base_query = question.strip()
    
    # Step 1: Get base analysis from the AI
    response = qa_agent.ask(base_query)
    
    # Step 2: Get specialized analysis using analysis-type-specific prompts and queries
    specialized_queries = {
        "strategic": f"""Perform a comprehensive strategic business analysis for: {base_query}
        
        Focus on: Market positioning, competitive advantages, strategic roadmap, investment requirements, 
        partnership opportunities, long-term value creation, scalable business models, and strategic risk assessment.
        
        Provide specific ROI projections, market size opportunities, strategic milestones with timelines, 
        and implementation feasibility scores.""",
        
        "comparative": f"""Conduct a detailed comparative market analysis for: {base_query}
        
        Focus on: Side-by-side performance comparisons, market positioning differences, competitive benchmarking, 
        performance gap analysis, winner/leader identification, and strategic recommendation based on comparisons.
        
        Provide specific performance metrics, percentage differences, comparative advantages, 
        and quantified performance gaps between options.""",
        
        "trends": f"""Generate a forward-looking trend analysis and market evolution report for: {base_query}
        
        Focus on: Current market state, evolution patterns, emerging trends, trend drivers, future projections,
        consumer behavior shifts, technology adoption patterns, and market opportunity forecasting.
        
        Provide specific growth rates, adoption percentages, market penetration data, timeline projections,
        and revenue opportunity assessments.""",
        
        "executive": f"""Create a C-level executive brief and decision-making summary for: {base_query}
        
        Focus on: Business impact assessment, key performance indicators, critical success factors,
        financial implications, risk assessment, implementation priorities, and decision matrix.
        
        Provide concise insights, financial metrics, ROI projections, risk probabilities, 
        and clear action items for executive decision-making."""
    }
    
    specialized_query = specialized_queries.get(analysis_type, base_query)
    
    # Use the new specialized method
    enhanced_response = qa_agent.ask_with_analysis_type(specialized_query, analysis_type)
    
    # Step 3: Synthesize responses with analysis-type-specific synthesis
    synthesis_prompts = {
        "strategic": f"""As a senior strategy consultant, synthesize these analyses into a comprehensive strategic business plan.
        
        Structure with: Strategic Position → Market Opportunities → Competitive Advantages → Implementation Roadmap → Investment Strategy → Risk Management
        
        Emphasize long-term value creation, sustainable competitive advantages, and scalable business models.""",
        
        "comparative": f"""As a comparative market analyst, synthesize these analyses into a definitive comparison report.
        
        Structure with: Comparison Framework → Performance Analysis → Competitive Positioning → Winner Identification → Strategic Recommendations
        
        Emphasize quantified performance differences, clear winners/losers, and data-driven recommendations.""",
        
        "trends": f"""As a trend forecasting expert, synthesize these analyses into a comprehensive trend intelligence report.
        
        Structure with: Current Market State → Evolution Patterns → Emerging Trends → Future Projections → Business Opportunities
        
        Emphasize forward-looking insights, market evolution patterns, and opportunity forecasting.""",
        
        "executive": f"""As a C-level business consultant, synthesize these analyses into an executive decision brief.
        
        Structure with: Executive Summary → Business Impact → Key Metrics → Critical Decisions → Action Plan
        
        Emphasize concise insights, financial implications, and clear decision points for executives."""
    }
    
    base_synthesis = synthesis_prompts.get(analysis_type, f"""Synthesize these analyses into a comprehensive {analysis_type} report.""")
    
    synthesis_prompt = f"""
    {base_synthesis}
    
    Do not simply stack the analyses. Intelligently integrate findings, eliminate redundancy, and create a logical narrative 
    specific to {analysis_type.upper()} analysis requirements.

    **Base Analysis:**
    {response['answer']}

    **Specialized {analysis_type.title()} Analysis:**
    {enhanced_response['answer']}

    Create a single, cohesive, and well-structured {analysis_type} report that leverages the strengths of both analyses.
    """
    
    synthesized_report = qa_agent.ask_with_analysis_type(synthesis_prompt, analysis_type)
    
    return {
        'question': question,
        'answer': synthesized_report['answer'],
        'sources': response.get('sources', []),
        'analysis_type': analysis_type
    }

# --- Main Application Logic ---
def main():
    st.markdown('<h1 class="main-header">✨ ConvoTrack Synthesized BI Agent</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🚀 Agent Configuration")
        api_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""), help="Get your key from https://console.groq.com/")
        if api_key: os.environ["GROQ_API_KEY"] = api_key
        
        st.header("📊 System Status")
        if os.path.exists("../extractContent/scraped_articles_selenium"):
            num_files = len([f for f in os.listdir("../extractContent/scraped_articles_selenium") if f.endswith('.txt')])
            st.metric("Case Studies Analyzed", num_files)
            st.metric("Agent Mode", "✨ Synthesized")

    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar to activate the agent.")
        return

    qa_agent = initialize_qa_agent()
    if not qa_agent: return
    
    st.success("✅ Synthesized Business Intelligence Agent is ready!")

    # State management for analysis type and user question
    if 'analysis_type' not in st.session_state: st.session_state.analysis_type = 'strategic'
    if 'user_question' not in st.session_state: st.session_state.user_question = ''

    # --- Step 1: Analysis Type Selection ---
    st.header("🎯 Step 1: Choose Your Analysis Type")
    
    # Enhanced analysis type descriptions
    analysis_descriptions = {
        "strategic": "🎯 **Strategic Analysis**: Long-term planning, market positioning, competitive advantages, strategic roadmaps, and investment strategies",
        "trends": "🔮 **Trend Analysis**: Market evolution, emerging patterns, future predictions, consumer behavior shifts, and opportunity forecasting", 
        "comparative": "📊 **Comparative Analysis**: Performance benchmarking, side-by-side comparisons, competitive positioning, and winner identification",
        "executive": "📋 **Executive Brief**: C-level insights, key metrics, financial implications, risk assessment, and decision-making summaries"
    }
    
    cols = st.columns(4)
    if cols[0].button("🎯 Strategic", use_container_width=True): st.session_state.analysis_type = "strategic"
    if cols[1].button("🔮 Trends", use_container_width=True): st.session_state.analysis_type = "trends"
    if cols[2].button("📊 Comparative", use_container_width=True): st.session_state.analysis_type = "comparative"
    if cols[3].button("📋 Executive", use_container_width=True): st.session_state.analysis_type = "executive"

    analysis_type = st.session_state.analysis_type
    
    # Show current analysis type with detailed description
    st.info(f"**Current Mode:** {analysis_descriptions[analysis_type]}")
    
    # Analysis-specific example questions
    example_questions = {
        "strategic": [
            "What strategic partnerships should beauty brands pursue for market expansion?",
            "How can we build sustainable competitive advantages in the social media landscape?",
            "What long-term investment strategy should brands adopt for digital transformation?"
        ],
        "trends": [
            "What emerging trends will shape social media marketing in the next 2 years?",
            "How are consumer behaviors evolving in the beauty and fashion industry?",
            "What future opportunities exist in influencer marketing and brand partnerships?"
        ],
        "comparative": [
            "Compare Instagram vs TikTok performance for beauty brand marketing",
            "Analyze engagement rates between different influencer partnership models",
            "Compare traditional advertising vs social media marketing effectiveness"
        ],
        "executive": [
            "What are the key investment priorities for social media marketing ROI?",
            "Summarize the critical success factors for influencer partnership programs",
            "What are the essential metrics and KPIs for measuring brand engagement success?"
        ]
    }
    
    with st.expander(f"💡 Example {analysis_type.title()} Questions"):
        for i, example in enumerate(example_questions[analysis_type], 1):
            st.write(f"{i}. {example}")
            if st.button(f"Use Example {i}", key=f"example_{analysis_type}_{i}"):
                st.session_state.user_question = example

    # --- Step 2: Question Input ---
    st.header("💼 Step 2: Ask Your Business Question")
    
    # Dynamic placeholder based on analysis type
    placeholders = {
        "strategic": "e.g., What strategic partnerships should beauty brands pursue for long-term market expansion?",
        "trends": "e.g., What emerging trends will shape influencer marketing in the next 2 years?",
        "comparative": "e.g., Compare Instagram vs TikTok performance for beauty brand marketing campaigns",
        "executive": "e.g., What are the key investment priorities for maximizing social media marketing ROI?"
    }
    
    st.session_state.user_question = st.text_area(
        f"Your {analysis_type.title()} Question:", 
        value=st.session_state.user_question, 
        height=100,
        placeholder=placeholders[analysis_type]
    )

    # --- Step 3: Generate Report ---
    button_labels = {
        "strategic": "🎯 Generate Strategic Analysis Report",
        "trends": "🔮 Generate Trend Analysis Report", 
        "comparative": "📊 Generate Comparative Analysis Report",
        "executive": "📋 Generate Executive Brief Report"
    }
    
    if st.button(button_labels[analysis_type], type="primary", use_container_width=True):
        if st.session_state.user_question.strip():
            with st.spinner("🔬 Synthesizing comprehensive analysis... This may take a moment."):
                report = perform_synthesized_analysis(st.session_state.user_question, qa_agent, analysis_type)
            
            # --- Display the Single, Unified Report ---
            with st.container():
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                
                # Display Synthesized Text Analysis
                st.markdown(report["answer"])
                
                # --- Generate Intelligent Visualizations ---
                visualizations = generate_intelligent_visualizations(
                    report["answer"], analysis_type, st.session_state.user_question
                )
                
                if visualizations:
                    st.markdown("---")
                    st.markdown("## 📊 Data-Driven Visualizations")
                    st.markdown("*Generated from actual analysis findings*")
                    
                    # Display visualizations in a grid layout
                    if len(visualizations) == 1:
                        chart_type, data, title, x_label, y_label = visualizations[0]
                        fig = create_detailed_chart(chart_type, data, title, x_label, y_label)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif len(visualizations) == 2:
                        col1, col2 = st.columns(2)
                        with col1:
                            chart_type, data, title, x_label, y_label = visualizations[0]
                            fig = create_detailed_chart(chart_type, data, title, x_label, y_label)
                            st.plotly_chart(fig, use_container_width=True)
                        with col2:
                            chart_type, data, title, x_label, y_label = visualizations[1]
                            fig = create_detailed_chart(chart_type, data, title, x_label, y_label)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    else:  # 3 or more visualizations
                        for i in range(0, len(visualizations), 2):
                            cols = st.columns(2)
                            for j, col in enumerate(cols):
                                if i + j < len(visualizations):
                                    with col:
                                        chart_type, data, title, x_label, y_label = visualizations[i + j]
                                        fig = create_detailed_chart(chart_type, data, title, x_label, y_label)
                                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show data extraction info
                    with st.expander("📋 Visualization Data Sources"):
                        st.write(f"**Number of visualizations generated:** {len(visualizations)}")
                        st.write("**Data extracted from:** Analysis report content")
                        st.write("**Visualization criteria:** Numerical data with business relevance")
                        
                        for i, (chart_type, data, title, x_label, y_label) in enumerate(visualizations, 1):
                            st.write(f"**Chart {i}:** {title} ({chart_type.replace('_', ' ').title()})")
                            if isinstance(data, dict):
                                st.json(data)
                
                else:
                    # Enhanced messaging when no meaningful data was found
                    st.markdown("---")
                    st.markdown("## 📊 Visualization Assessment")
                    
                    # Check what data was extracted but didn't meet criteria
                    extractor = DataExtractor()
                    raw_percentages = extractor.extract_percentages(report["answer"])
                    raw_comparisons = extractor.extract_numerical_comparisons(report["answer"])
                    raw_time_series = extractor.extract_time_series_data(report["answer"])
                    raw_growth_rates = extractor.extract_growth_rates(report["answer"])
                    
                    found_some_data = any([raw_percentages, raw_comparisons, raw_time_series, raw_growth_rates])
                    
                    if found_some_data:
                        st.warning("⚠️ **Data Quality Check:** Some numerical data was detected but didn't meet visualization standards:")
                        if raw_percentages and len(raw_percentages) < 2:
                            st.write("• Insufficient percentage data points for meaningful comparison")
                        if raw_time_series and len(raw_time_series) < 3:
                            st.write("• Time series data requires at least 3 points to show trends")
                        if any([raw_percentages, raw_comparisons, raw_growth_rates]):
                            st.write("• Data may lack sufficient variation or business context")
                        
                        st.info("💡 **Tip:** Try asking questions that request specific metrics, comparisons, or performance data for better visualizations.")
                    else:
                        st.info("📊 **No Quantitative Data Found:** This analysis is primarily qualitative and strategic in nature. No numerical data suitable for visualization was detected.")
                        st.markdown("**To get visualizations, try asking questions like:**")
                        st.markdown("• 'Compare engagement rates between different platforms'")
                        st.markdown("• 'Show growth trends over the past few years'") 
                        st.markdown("• 'What are the performance metrics for different strategies?'")

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("📝 Please enter a business question to generate the report.")

if __name__ == "__main__":
    main()