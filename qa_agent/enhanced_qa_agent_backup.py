import os
import re
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from document_loader import setup_knowledge_base

# Load environment variables
load_dotenv()

class AdvancedCaseStudyQAAgent:
    """
    Advanced ConvoTrack Business Intelligence Agent
    Features: Creative analysis, practical insights, effective natural language understanding
    """
    
    def __init__(self, scraped_articles_path: str, groq_api_key: str = None):
        self.scraped_articles_path = scraped_articles_path
        self.agent_name = "ConvoTrack Business Intelligence Specialist"
        
        # Set up Groq LLM with advanced parameters
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in .env file or pass as parameter")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            temperature=0.3,  # Balanced for creativity and accuracy
            model_name="llama-3.3-70b-versatile",
        )
        
        # Set up knowledge base
        self.vectorstore = setup_knowledge_base(scraped_articles_path)
        
        # Create advanced retriever with multiple search strategies
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}  # Retrieve more documents for comprehensive analysis
        )
        
        # Enhanced business intelligence keywords
        self.business_keywords = {
            'strategy': ['strategy', 'strategic', 'plan', 'planning', 'approach', 'method'],
            'marketing': ['marketing', 'campaign', 'promotion', 'advertising', 'branding', 'content'],
            'consumer': ['consumer', 'customer', 'user', 'audience', 'demographic', 'behavior'],
            'performance': ['performance', 'metrics', 'kpi', 'roi', 'conversion', 'engagement', 'results'],
            'trends': ['trend', 'trending', 'popular', 'emerging', 'growth', 'increase', 'rise'],
            'analysis': ['analysis', 'insight', 'finding', 'data', 'research', 'study', 'report'],
            'innovation': ['innovation', 'new', 'creative', 'unique', 'novel', 'breakthrough'],
            'competitive': ['competitive', 'competition', 'competitor', 'market share', 'advantage']
        }
        
        # Question types for intelligent routing
        self.question_types = {
            'comparison': ['vs', 'versus', 'compare', 'difference', 'better', 'best', 'worst'],
            'trend': ['trend', 'change', 'evolving', 'future', 'prediction', 'forecast'],
            'how_to': ['how to', 'how can', 'ways to', 'methods', 'approach', 'strategy for'],
            'metrics': ['metrics', 'measure', 'kpi', 'performance', 'roi', 'success rate'],
            'recommendation': ['recommend', 'suggest', 'advice', 'should', 'best practice']
        }
        
        # Create dynamic prompt templates for different question types
        self.create_prompt_templates()
        
        # Initialize conversation context
        self.conversation_history = []
        
        # Create the QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={
                "prompt": self.default_prompt
            },
            return_source_documents=True
        )
    
    def create_prompt_templates(self):
        """Create specialized prompt templates for different types of questions"""
        
        # Default comprehensive analysis template
        self.default_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an elite ConvoTrack Business Intelligence Specialist with expertise in consumer psychology, market analysis, and strategic business insights.

MISSION: Transform raw case study data into actionable business intelligence that drives real-world results.

CASE STUDY INTELLIGENCE:
{context}

BUSINESS INQUIRY: {question}

COMPREHENSIVE ANALYSIS:
Provide a strategic business analysis that includes:

🎯 **Executive Summary**: Key takeaway in 2-3 sentences
📊 **Data-Driven Insights**: Specific findings from the case studies with numbers/percentages when available
🚀 **Strategic Implications**: What this means for business strategy and market positioning
💡 **Actionable Recommendations**: 3-4 specific, implementable actions
🔮 **Future Outlook**: Trends and predictions based on the data
⚠️ **Risk Considerations**: Potential challenges or limitations to consider

Write in a professional yet engaging tone. Use business terminology appropriately but ensure accessibility. Back up every claim with evidence from the case studies."""
        )
        
        # Comparison analysis template
        self.comparison_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a comparative business analyst specializing in market intelligence and competitive analysis.

COMPARATIVE INTELLIGENCE DATA:
{context}

COMPARISON REQUEST: {question}

COMPARATIVE ANALYSIS:
🔍 **Comparison Framework**: Establish clear criteria for comparison
📊 **Side-by-Side Analysis**: Detailed comparison with specific metrics
🏆 **Winner/Leader Analysis**: Which approach/strategy/brand performs better and why
📈 **Performance Gaps**: Quantify differences where possible
🎯 **Strategic Recommendations**: Which approach to adopt and why
⚖️ **Trade-offs**: Pros and cons of each option

Provide specific data points, percentages, and concrete examples from the case studies."""
        )
        
        # Trend analysis template
        self.trend_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a trend forecasting expert specializing in consumer behavior and market evolution.

TREND INTELLIGENCE DATA:
{context}

TREND INQUIRY: {question}

TREND ANALYSIS:
📈 **Current State**: What the data shows about the present situation
🔄 **Evolution Pattern**: How things have changed over time
🚀 **Emerging Trends**: New developments and patterns identified
📊 **Trend Drivers**: What's causing these changes (consumer behavior, technology, etc.)
🎯 **Business Impact**: How these trends affect business strategy
🔮 **Future Projections**: Where trends are heading (next 1-2 years)
💰 **Revenue Opportunities**: How businesses can capitalize on these trends

Include specific examples and data points from case studies to support trend analysis."""
        )

    def _analyze_question_type(self, question: str) -> str:
        """Analyze question type for intelligent routing"""
        question_lower = question.lower()
        
        for q_type, keywords in self.question_types.items():
            if any(keyword in question_lower for keyword in keywords):
                return q_type
        
        return 'general'
    
    def _extract_business_intent(self, question: str) -> Tuple[str, List[str]]:
        """Extract business intent and relevant categories from question"""
        question_lower = question.lower()
        detected_categories = []
        primary_intent = "general_inquiry"
        
        # Detect business categories
        for category, keywords in self.business_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_categories.append(category)
        
        # Determine primary intent
        if 'strategy' in detected_categories or 'competitive' in detected_categories:
            primary_intent = "strategic_analysis"
        elif 'performance' in detected_categories or 'analysis' in detected_categories:
            primary_intent = "performance_analysis"
        elif 'trends' in detected_categories or 'innovation' in detected_categories:
            primary_intent = "trend_analysis"
        elif 'marketing' in detected_categories or 'consumer' in detected_categories:
            primary_intent = "marketing_analysis"
        
        return primary_intent, detected_categories
    
    def _enhance_context_retrieval(self, question: str) -> List[Document]:
        """Enhanced context retrieval with query expansion"""
        
        # Get primary documents
        primary_docs = self.retriever.get_relevant_documents(question)
        
        # Extract key terms for query expansion
        question_terms = re.findall(r'\b\w+\b', question.lower())
        business_terms = []
        
        for term in question_terms:
            for category, keywords in self.business_keywords.items():
                if term in keywords:
                    business_terms.extend(keywords[:3])  # Add related terms
        
        # Secondary retrieval with expanded terms
        if business_terms:
            expanded_query = question + " " + " ".join(set(business_terms))
            secondary_docs = self.retriever.get_relevant_documents(expanded_query)
            
            # Combine and deduplicate
            all_docs = primary_docs + secondary_docs
            seen_content = set()
            unique_docs = []
            
            for doc in all_docs:
                content_hash = hash(doc.page_content[:100])  # Use first 100 chars as identifier
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    unique_docs.append(doc)
                    
            return unique_docs[:12]  # Return top 12 unique documents
        
        return primary_docs[:8]  # Return top 8 if no expansion needed

    def _is_business_related_query(self, question: str) -> bool:
        """Enhanced business query validation"""
        question_lower = question.lower()
        
        # Check for direct business keywords
        for category, keywords in self.business_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                return True
        
        # Check for business question patterns
        business_patterns = [
            'how to improve', 'what strategy', 'best practices', 'market analysis',
            'consumer insights', 'brand performance', 'campaign effectiveness',
            'competitive advantage', 'growth opportunities', 'business impact'
        ]
        
        for pattern in business_patterns:
            if pattern in question_lower:
                return True
        
        # Check if question has business context (length and complexity)
        if len(question.split()) > 4 and any(word in question_lower for word in 
            ['business', 'market', 'customer', 'brand', 'product', 'service', 'company']):
            return True
        
        return False

    def _generate_smart_response(self, question: str) -> str:
        """Generate intelligent response for out-of-scope queries"""
        intent, categories = self._extract_business_intent(question)
        
        response = f"""🤖 **ConvoTrack Business Intelligence Specialist**

I noticed your question: "{question}"

While I specialize in business intelligence from ConvoTrack case studies, I can help you reframe this question to get actionable insights.

**Here's how I can help:**"""

        if categories:
            response += f"\n\n**Detected business areas**: {', '.join(categories)}"
            response += f"\n\n**Suggested business questions:**"
            
            if 'marketing' in categories:
                response += "\n• What marketing strategies show the highest engagement rates?"
                response += "\n• How do different content types perform across demographics?"
            
            if 'consumer' in categories:
                response += "\n• What consumer behavior patterns emerge from the case studies?"
                response += "\n• Which demographic segments show the strongest brand loyalty?"
            
            if 'performance' in categories:
                response += "\n• What metrics indicate successful campaigns in our case studies?"
                response += "\n• How do conversion rates vary across different platforms?"
        else:
            response += """

**My expertise areas:**
• Consumer Behavior Analysis & Market Trends
• Brand Performance & Marketing Effectiveness  
• Strategic Business Insights & Competitive Analysis
• Social Media & Digital Marketing Analytics
• Product Innovation & Market Research

**Try asking:**
• "What are the most effective marketing strategies for beauty brands?"
• "How do consumer preferences vary across different age groups?"
• "What trends are driving growth in the food industry?"
• "Which social media platforms show the best ROI?"

Ready to provide actionable business intelligence! 🚀"""
        
        return response

    def ask(self, question: str) -> Dict[str, Any]:
        """Advanced question processing with intelligent routing and enhanced responses"""
        try:
            # Clean and validate the question
            clean_question = question.strip()
            
            if not clean_question:
                return {
                    "question": "Empty question",
                    "answer": "🤖 Please provide a specific business question. I'm ready to analyze consumer insights, marketing strategies, and business trends from our case studies!",
                    "sources": [],
                    "agent_type": "validation_response",
                    "confidence": "low"
                }
            
            # Extract business intent and categories
            intent, categories = self._extract_business_intent(clean_question)
            question_type = self._analyze_question_type(clean_question)
            
            # Check if question is business-related
            if not self._is_business_related_query(clean_question):
                return {
                    "question": clean_question,
                    "answer": self._generate_smart_response(clean_question),
                    "sources": [],
                    "agent_type": "scope_guidance",
                    "confidence": "medium",
                    "intent": intent,
                    "categories": categories
                }
            
            # Enhanced context retrieval
            enhanced_docs = self._enhance_context_retrieval(clean_question)
            
            # Select appropriate prompt based on question type
            if question_type == 'comparison':
                prompt = self.comparison_prompt
            elif question_type == 'trend' or intent == 'trend_analysis':
                prompt = self.trend_prompt
            else:
                prompt = self.default_prompt
            
            # Create enhanced QA chain with selected prompt
            enhanced_qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                chain_type_kwargs={
                    "prompt": prompt
                },
                return_source_documents=True
            )
            
            # Process the business-related question
            result = enhanced_qa_chain({"query": clean_question})
            
            # Calculate confidence based on source relevance
            confidence = "high" if len(result.get("source_documents", [])) >= 5 else "medium"
            
            # Enhance the answer with context and agent personality
            enhanced_answer = f"""{result['result']}

---
**📊 Analysis Metadata:**
• Intent: {intent.replace('_', ' ').title()}
• Categories: {', '.join(categories) if categories else 'General Business'}
• Question Type: {question_type.replace('_', ' ').title()}
• Confidence Level: {confidence.upper()}
• Sources Analyzed: {len(result.get("source_documents", []))} case study segments

*🤖 Analysis by {self.agent_name} | Specialized in Consumer Research & Business Strategy*"""
            
            # Format the response
            response = {
                "question": clean_question,
                "answer": enhanced_answer,
                "sources": [],
                "agent_type": "advanced_analysis",
                "confidence": confidence,
                "intent": intent,
                "categories": categories,
                "question_type": question_type
            }
            
            # Add enhanced source information
            for i, doc in enumerate(result.get("source_documents", []), 1):
                # Calculate relevance score based on content length and keywords
                relevance_score = len([kw for category in self.business_keywords.values() 
                                     for kw in category if kw in doc.page_content.lower()])
                relevance = "High" if relevance_score >= 3 else "Medium" if relevance_score >= 1 else "Low"
                
                source_info = {
                    "content": doc.page_content[:400] + "..." if len(doc.page_content) > 400 else doc.page_content,
                    "source_url": doc.metadata.get("source", "Unknown"),
                    "article_number": doc.metadata.get("article_number", f"Source_{i}"),
                    "relevance": relevance,
                    "relevance_score": relevance_score,
                    "content_length": len(doc.page_content)
                }
                response["sources"].append(source_info)
            
            # Add conversation to history
            self.conversation_history.append({
                "question": clean_question,
                "intent": intent,
                "categories": categories,
                "sources_count": len(response["sources"])
            })
            
            return response
            
        except Exception as e:
            return {
                "question": clean_question if 'clean_question' in locals() else question,
                "answer": f"""🚨 **Technical Analysis Issue**

I encountered a technical challenge while processing your business question. However, I'm still here to help!

**Error Context:** {str(e)}

**What I can help you with right now:**
• Market trends and consumer behavior analysis
• Marketing strategy effectiveness studies  
• Brand engagement and performance insights
• Social media and digital marketing analytics
• Product innovation and competitive analysis
• Industry-specific research findings

**Quick Business Questions to Try:**
• "What are the top performing marketing strategies?"
• "How do consumer preferences differ by demographics?"
• "What social media trends are most effective?"
• "Which product features drive the most engagement?"

Let's get you the business intelligence you need! 🎯""",
                "sources": [],
                "agent_type": "error_response",
                "confidence": "low",
                "error": str(e)
            }
    
    def get_case_study_topics(self) -> List[str]:
        """Enhanced topic extraction with categorization"""
        try:
            from document_loader import DocumentLoader
            
            loader = DocumentLoader(self.scraped_articles_path)
            documents = loader.load_documents()
            
            topics = []
            sources = set()
            
            for doc in documents:
                source = doc.metadata.get("source", "")
                if source and "case-studies/" in source:
                    sources.add(source)
            
            # Extract and categorize topics
            for source in sources:
                if "case-studies/" in source:
                    topic = source.split("case-studies/")[-1].replace("/", "").replace("-", " ").title()
                    
                    # Add business context to topics
                    if any(keyword in topic.lower() for keyword in ['beauty', 'skin', 'cosmetic']):
                        topic = f"🧴 {topic} (Beauty & Skincare)"
                    elif any(keyword in topic.lower() for keyword in ['food', 'ice cream', 'beverage']):
                        topic = f"🍦 {topic} (Food & Beverage)"
                    elif any(keyword in topic.lower() for keyword in ['health', 'wellness', 'fitness']):
                        topic = f"💪 {topic} (Health & Wellness)"
                    elif any(keyword in topic.lower() for keyword in ['social', 'media', 'digital']):
                        topic = f"📱 {topic} (Digital Marketing)"
                    else:
                        topic = f"📊 {topic} (Business Analysis)"
                    
                    topics.append(topic)
            
            return sorted(topics)
            
        except Exception as e:
            print(f"Error getting enhanced topics: {e}")
            return ["📊 Business Strategy Analysis", "🧴 Beauty & Consumer Trends", "🍦 Food Industry Insights"]
    
    def search_similar_content(self, query: str, k: int = 5) -> List[Document]:
        """Enhanced similarity search with business context"""
        try:
            # Use enhanced retrieval for better results
            docs = self._enhance_context_retrieval(query)
            return docs[:k]
        except Exception as e:
            print(f"Error in enhanced search: {e}")
            return []
    
    def get_conversation_insights(self) -> Dict[str, Any]:
        """Analyze conversation patterns for insights"""
        if not self.conversation_history:
            return {"message": "No conversation history available"}
        
        # Analyze question patterns
        intents = [conv["intent"] for conv in self.conversation_history]
        categories = []
        for conv in self.conversation_history:
            categories.extend(conv.get("categories", []))
        
        from collections import Counter
        intent_counts = Counter(intents)
        category_counts = Counter(categories)
        
        return {
            "total_questions": len(self.conversation_history),
            "top_intents": dict(intent_counts.most_common(3)),
            "top_categories": dict(category_counts.most_common(5)),
            "avg_sources_per_question": sum(conv["sources_count"] for conv in self.conversation_history) / len(self.conversation_history)
        }

def main():
    """Test the advanced Q&A agent"""
    scraped_path = "../extractContent/scraped_articles_selenium"
    
    try:
        print("🚀 Initializing Advanced ConvoTrack Business Intelligence Agent...")
        qa_agent = AdvancedCaseStudyQAAgent(scraped_path)
        print("✅ Advanced Q&A Agent initialized successfully!")
        
        # Test questions
        test_questions = [
            "What are the most effective marketing strategies for beauty brands?",
            "How do consumer preferences compare between different age groups?",
            "What trends are emerging in the food industry?",
            "Compare social media engagement rates across platforms",
            "What metrics indicate successful brand campaigns?"
        ]
        
        print(f"\n🧪 Testing with sample questions...")
        for i, question in enumerate(test_questions[:2], 1):  # Test first 2
            print(f"\n{'='*60}")
            print(f"Test {i}: {question}")
            print(f"{'='*60}")
            
            response = qa_agent.ask(question)
            print(f"Intent: {response.get('intent', 'N/A')}")
            print(f"Categories: {response.get('categories', 'N/A')}")
            print(f"Confidence: {response.get('confidence', 'N/A')}")
            print(f"Sources: {len(response.get('sources', []))}")
            print(f"\nAnswer Preview: {response['answer'][:200]}...")
        
        # Show conversation insights
        insights = qa_agent.get_conversation_insights()
        print(f"\n📊 Conversation Insights: {insights}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
