import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from document_loader import setup_knowledge_base

# Load environment variables
load_dotenv()

class CaseStudyQAAgent:
    """
    Q&A Agent for ConvoTrack case studies using LangChain and Groq
    """
    
    def __init__(self, scraped_articles_path: str, groq_api_key: str = None):
        self.scraped_articles_path = scraped_articles_path
        
        # Set up Groq LLM
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in .env file or pass as parameter")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            temperature=0.1,
        )
        
        # Set up knowledge base
        self.vectorstore = setup_knowledge_base(scraped_articles_path)
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retrieve top 5 most relevant chunks
        )
        
        # Create custom prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful AI assistant that answers questions about ConvoTrack case studies. 
Use the following context from the case studies to answer the question. If you don't know the answer based on the provided context, say so.

Context from case studies:
{context}

Question: {question}

Answer: Provide a detailed and informative answer based on the case studies. Include specific insights, metrics, and recommendations when available. If referencing specific case studies, mention them clearly."""
        )
        
        # Create the QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={
                "prompt": self.prompt_template
            },
            return_source_documents=True
        )
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question and get an answer with sources
        """
        try:
            result = self.qa_chain({"query": question})
            
            # Format the response
            response = {
                "question": question,
                "answer": result["result"],
                "sources": []
            }
            
            # Add source information
            for doc in result.get("source_documents", []):
                source_info = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "source_url": doc.metadata.get("source", "Unknown"),
                    "article_number": doc.metadata.get("article_number", "Unknown")
                }
                response["sources"].append(source_info)
            
            return response
            
        except Exception as e:
            return {
                "question": question,
                "answer": f"Error processing question: {str(e)}",
                "sources": []
            }
    
    def get_case_study_topics(self) -> List[str]:
        """
        Get a list of case study topics for reference
        """
        try:
            # For Pinecone, we'll get topics from the original documents
            # Since we can't easily query all metadata, we'll use the document loader
            from document_loader import DocumentLoader
            
            loader = DocumentLoader(self.scraped_articles_path)
            documents = loader.load_documents()
            
            topics = []
            sources = set()
            
            for doc in documents:
                source = doc.metadata.get("source", "")
                if source and "case-studies/" in source:
                    sources.add(source)
            
            # Extract topic from URL
            for source in sources:
                if "case-studies/" in source:
                    topic = source.split("case-studies/")[-1].replace("/", "").replace("-", " ").title()
                    topics.append(topic)
            
            return sorted(topics)
            
        except Exception as e:
            print(f"Error getting topics: {e}")
            return []
    
    def search_similar_content(self, query: str, k: int = 3) -> List[Document]:
        """
        Search for similar content without generating an answer
        """
        try:
            docs = self.retriever.get_relevant_documents(query)
            return docs[:k]
        except Exception as e:
            print(f"Error searching content: {e}")
            return []

def main():
    """
    Main function to test the Q&A agent
    """
    # Path to scraped articles
    scraped_path = "../extractContent/scraped_articles_selenium"
    
    try:
        # Initialize the Q&A agent
        print("Initializing ConvoTrack Case Study Q&A Agent...")
        qa_agent = CaseStudyQAAgent(scraped_path)
        print("Q&A Agent initialized successfully!")
        
        # Get available topics
        topics = qa_agent.get_case_study_topics()
        print(f"\nAvailable case study topics ({len(topics)}):")
        for i, topic in enumerate(topics[:10], 1):  # Show first 10
            print(f"{i}. {topic}")
        if len(topics) > 10:
            print(f"... and {len(topics) - 10} more")
        
        # Interactive Q&A loop
        print("\n" + "="*50)
        print("ConvoTrack Case Study Q&A Agent")
        print("Ask questions about the case studies!")
        print("Type 'quit' to exit")
        print("="*50)
        
        while True:
            question = input("\nYour question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Thank you for using the Q&A Agent!")
                break
            
            if not question:
                continue
            
            print("\nProcessing your question...")
            response = qa_agent.ask(question)
            
            print(f"\nQuestion: {response['question']}")
            print(f"\nAnswer: {response['answer']}")
            
            if response['sources']:
                print(f"\nSources:")
                for i, source in enumerate(response['sources'], 1):
                    print(f"{i}. Article {source['article_number']}")
                    print(f"   URL: {source['source_url']}")
                    print(f"   Preview: {source['content']}")
                    print()
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have:")
        print("1. Set GROQ_API_KEY in your .env file")
        print("2. Installed all required packages: pip install -r requirements.txt")
        print("3. Scraped articles available at the specified path")

if __name__ == "__main__":
    main()
