import os
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from document_loader import setup_knowledge_base

load_dotenv()


class ResearchAgent:
    """
    Specialized agent for retrieving relevant information from the knowledge base.
    Its only job is to find the best possible context for a given question.
    """
    def __init__(self, retriever: PineconeVectorStore.as_retriever):
        self.retriever = retriever

    def gather_context(self, question: str) -> List[Document]:
        """
        Performs a similarity search on the vector store to find relevant documents.
        """
        print("Research Agent: Gathering context from knowledge base...")
        return self.retriever.get_relevant_documents(question)

class AnalysisAgent:
    """
    Specialized agent for performing deep analysis on a given topic using
    the context provided by the Research Agent.
    """
    def __init__(self, llm: ChatGroq, prompt_templates: Dict[str, PromptTemplate]):
        self.llm = llm
        self.prompt_templates = prompt_templates

    def generate_analysis(self, question: str, context: List[Document], analysis_type: str) -> str:
        """
        Generates a detailed, raw analysis by feeding the question and context
        into a specialized prompt template.
        """
        print(f"Analysis Agent: Generating '{analysis_type}' analysis...")
        prompt = self.prompt_templates.get(analysis_type, self.prompt_templates["default"])
        
        # This chain simply combines the context and question into the prompt
        analysis_chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Format the retrieved documents into a single string for the prompt
        context_str = "\n\n---\n\n".join([doc.page_content for doc in context])
        
        # Run the analysis
        result = analysis_chain.run(context=context_str, question=question)
        return result

class SynthesizerAgent:
    """
    Specialized agent for formatting and polishing the raw analysis into a final, user-friendly response.
    """
    def craft_final_response(self, raw_analysis: str, analysis_type: str) -> str:
        """
        Takes the raw text from the Analysis Agent and adds headers, footers,
        and other formatting to make it clear and presentable.
        """
        print("Synthesizer Agent: Formatting final response...")
        
        type_headers = {
            "strategic": "**Detailed Strategic Business Analysis**\n",
            "trends": "**In-Depth Trend Analysis & Future Outlook**\n", 
            "comparative": "**Comprehensive Comparative Market Analysis**\n",
            "executive": "**Actionable Executive Business Brief**\n",
            "default": "**Detailed Business Intelligence Analysis**\n"
        }
        header = type_headers.get(analysis_type, type_headers["default"])
        
        footers = {
            "strategic": "\n\n---\n*This multi-agent strategic analysis focuses on long-term positioning, competitive advantage, and sustainable growth models based on the provided context.*",
            "trends": "\n\n---\n*This multi-agent trend analysis provides forward-looking insights into market evolution, backed by data points from the source material.*",
            "comparative": "\n\n---\n*This multi-agent comparative analysis uses performance benchmarks and qualitative data for a comprehensive market positioning assessment.*",
            "executive": "\n\n---\n*This multi-agent executive summary is designed for high-level, C-suite decision making, focusing on actionable insights and strategic imperatives.*",
        }
        footer = footers.get(analysis_type, "")
        
        return header + raw_analysis + footer


class AdvancedCaseStudyQAAgent:
    """
    The main Manager Agent that orchestrates the workflow between the specialized
    worker agents to produce a detailed and logical response.
    """
    
    def __init__(self, scraped_articles_path: str, groq_api_key: str = None):
        """
        Initializes the entire multi-agent system, including the LLM,
        vector store, and all worker agents.
        """
        self.agent_name = "ConvoTrack Multi-Agent System"
        
        # Initialize the Groq Language Model
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found.")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            temperature=0.2, 
            model_name="llama-3.3-70b-versatile",
        )
        
        # Set up the knowledge base and retriever
        self.vectorstore = setup_knowledge_base(scraped_articles_path)
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 15}  
        )
        
        # Create and store all necessary prompt templates
        self.prompt_templates = self._create_prompt_templates()
        
        # Initialize worker agents and provide them with the necessary tools
        self.research_agent = ResearchAgent(self.retriever)
        self.analysis_agent = AnalysisAgent(self.llm, self.prompt_templates)
        self.synthesizer_agent = SynthesizerAgent()

    def _create_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """
        Creates and returns a dictionary of all specialized prompt templates.
        """
        # Router prompt to classify the user's question
        router_template = PromptTemplate(
            input_variables=["question"],
            template="""You are an expert request router. Your job is to analyze a user's business question and classify it into one of the following categories based on its intent.

Here are the available categories:
- **strategic**: For questions about long-term planning, competitive advantage, market positioning, or business models.
- **trends**: For questions about market evolution, future predictions, emerging patterns, or changes over time.
- **comparative**: For questions that compare two or more items, strategies, or performance metrics.
- **executive**: For questions seeking high-level, concise summaries, financial implications, or C-level decision support.
- **default**: For general business intelligence questions, performance analysis, or when no other category fits perfectly.

Based on the question below, provide ONLY the single category ID that best fits. Do not add any explanation or punctuation.

Question: "{question}"
Category ID:"""
        )

        # Enhanced Default/Analysis Prompt for deep, logical reasoning
        detailed_analysis_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a world-class business analyst and strategist. Your task is to provide a deeply logical and highly detailed analysis based on the provided case study intelligence. Your response must be structured, evidence-based, and demonstrate a clear chain of reasoning.

**MISSION**: Synthesize the provided context to comprehensively answer the business inquiry. You must connect multiple pieces of information from the context to form a coherent, evidence-based argument. Do not simply state facts; you must explain their strategic implications in detail.

**CASE STUDY INTELLIGENCE (CONTEXT):**
{context}

**BUSINESS INQUIRY:**
{question}

---

**DETAILED LOGICAL ANALYSIS (Your Response):**

**1. Executive Summary:**
   - Begin with a concise, 2-3 sentence summary of the most critical findings and conclusions. This should be direct and impactful.

**2. Deconstruction of the Inquiry:**
   - Break down the user's question into its core analytical components. State these components clearly (e.g., "This question requires us to first analyze X, then evaluate its impact on Y...").

**3. Evidence Synthesis & Chain of Reasoning:**
   - For each component identified above, construct a detailed argument.
   - **Gather Evidence**: Pull specific, relevant data points, quotes, or findings from the provided context. Mention multiple pieces of evidence for each point.
   - **Explain Connections (Chain of Logic)**: This is the most critical part. Do not just list the evidence. Explicitly explain *how* the pieces of evidence connect to each other and lead to your conclusions. Use phrases like:
     - "The fact that [Evidence A] occurred, combined with the metric [Evidence B], strongly suggests that..."
     - "This leads to the logical conclusion that..."
     - "Therefore, we can infer a direct causal link between..."
     - "The implication of this connection is significant because..."
   - **Quantify Where Possible**: Use any numbers, percentages, or metrics from the context to support your reasoning.

**4. Strategic Implications & Second-Order Effects:**
   - Go beyond the immediate answer. Based on your logical conclusions, what are the broader strategic implications for a business?
   - What are the "second-order effects"? (i.e., if the company does X, what is the likely market reaction or subsequent challenge?)
   - Explain *why* this analysis matters from a business strategy perspective.

**5. Actionable, Evidence-Based Recommendations:**
   - Based *only* on the logical analysis above, provide a set of 3-5 specific, actionable recommendations.
   - For each recommendation, briefly state which part of your evidence-based reasoning supports it.

**6. Acknowledgment of Limitations & Counterarguments:**
   - Briefly mention any potential limitations of the analysis based on the provided context. Are there any gaps in the data?
   - Consider one potential counterargument or alternative interpretation and briefly address it. This demonstrates sophisticated, critical thinking.
"""
        )

        return {
            "router": router_template,
            "default": detailed_analysis_prompt,
            "strategic": detailed_analysis_prompt,
            "trends": detailed_analysis_prompt,
            "comparative": detailed_analysis_prompt,
            "executive": detailed_analysis_prompt,
        }

    def _get_analysis_type(self, question: str) -> str:
        """
        Uses the LLM-based router to determine the best analysis type for a question.
        This is the Manager's first decision.
        """
        print("Manager Agent: Routing user question to determine intent...")
        router_chain = LLMChain(llm=self.llm, prompt=self.prompt_templates["router"])
        response = router_chain.run(question)
        analysis_type = response.strip().lower().replace(".", "")
        if analysis_type not in self.prompt_templates:
            print(f"Warning: Router returned unexpected type '{analysis_type}'. Falling back to default.")
            return "default"
        print(f"Manager Agent: Intent classified as '{analysis_type}'.")
        return analysis_type

    def ask(self, question: str) -> Dict[str, Any]:
        """
        The primary method for the Manager Agent. It orchestrates the entire
        multi-agent workflow from question to final answer.
        """
        try:
            clean_question = question.strip()
            if not clean_question:
                return {"answer": "Please provide a question.", "sources": [], "agent_type": "error", "confidence": "low", "analysis_type": "none"}

            # Step 1: Manager determines the user's intent.
            analysis_type = self._get_analysis_type(clean_question)
            
            # Step 2: Manager delegates the research task.
            context_docs = self.research_agent.gather_context(clean_question)
            if not context_docs:
                return {"answer": "I could not find any relevant information in the knowledge base to answer this question.", "sources": [], "agent_type": "no_context", "confidence": "low", "analysis_type": analysis_type}
            
            # Step 3: Manager delegates the analysis task.
            raw_analysis = self.analysis_agent.generate_analysis(clean_question, context_docs, analysis_type)
            
            # Step 4: Manager delegates the final response formatting.
            formatted_answer = self.synthesizer_agent.craft_final_response(raw_analysis, analysis_type)
            
            # Step 5: Manager compiles the final result from all agents' work.
            sources_list = [{
                "content": doc.page_content,
                "url": doc.metadata.get("source", "Unknown"),
                "article_number": doc.metadata.get("article_number", "N/A"),
            } for doc in context_docs]

            return {
                "question": clean_question,
                "answer": formatted_answer,
                "sources": sources_list,
                "agent_type": f"{analysis_type}_analysis",
                "confidence": "high",
                "analysis_type": analysis_type
            }

        except Exception as e:
            print(f"Error in multi-agent workflow: {e}")
            return {
                "question": question,
                "answer": f"The multi-agent system encountered an error: {str(e)}",
                "sources": [], "agent_type": "error_response", "confidence": "low",
                "analysis_type": "error", "error": str(e)
            }

