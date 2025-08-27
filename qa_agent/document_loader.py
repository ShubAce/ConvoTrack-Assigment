import os
import glob
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from pinecone import Pinecone, ServerlessSpec
import time

class DocumentLoader:
    """
    Loads and processes the scraped case study documents
    """
    
    def __init__(self, scraped_articles_path: str):
        self.scraped_articles_path = scraped_articles_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        """
        Load all scraped case study documents
        """
        documents = []
        
        # Get all .txt files from the scraped articles directory
        txt_files = glob.glob(os.path.join(self.scraped_articles_path, "*.txt"))
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Extract source URL from the content
                lines = content.split('\n')
                source_url = ""
                actual_content = content
                
                if lines and lines[0].startswith("Source URL:"):
                    source_url = lines[0].replace("Source URL:", "").strip()
                    # Find the content after the separator line
                    separator_idx = -1
                    for i, line in enumerate(lines):
                        if "=" in line and len(line) > 10:
                            separator_idx = i
                            break
                    
                    if separator_idx != -1:
                        actual_content = '\n'.join(lines[separator_idx + 1:]).strip()
                
                # Extract article number from filename
                filename = os.path.basename(file_path)
                article_num = filename.replace("article_", "").replace(".txt", "")
                
                # Create document with metadata
                doc = Document(
                    page_content=actual_content,
                    metadata={
                        "source": source_url,
                        "file_path": file_path,
                        "article_number": article_num,
                        "filename": filename
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        print(f"Loaded {len(documents)} documents")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for better retrieval
        """
        chunks = self.text_splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        return chunks

class VectorStoreManager:
    """
    Manages the Pinecone vector store for document retrieval
    """
    
    def __init__(self, index_name: str = "convotrack-casestudies"):
        self.index_name = index_name
        
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        self.pc = Pinecone(api_key=api_key)
        
        # Use HuggingFace API-based embeddings
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not hf_token:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")
        
        self.embeddings = HuggingFaceEndpointEmbeddings(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=hf_token
        )
        
        # Create or get index
        self._setup_index()
    
    def _setup_index(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # all-MiniLM-L6-v2 embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait for index to be ready
            time.sleep(10)
        
        self.index = self.pc.Index(self.index_name)
    
    def create_vectorstore(self, documents: List[Document]) -> PineconeVectorStore:
        """
        Create a new vector store from documents
        """
        # Create embeddings and store in Pinecone
        vectorstore = PineconeVectorStore.from_documents(
            documents=documents,
            embedding=self.embeddings,
            index_name=self.index_name
        )
        
        print(f"Created Pinecone vector store with {len(documents)} documents")
        return vectorstore
    
    def load_vectorstore(self) -> PineconeVectorStore:
        """
        Load existing vector store
        """
        vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )
        
        return vectorstore
    
    def vectorstore_exists(self) -> bool:
        """
        Check if vector store has data
        """
        try:
            stats = self.index.describe_index_stats()
            return stats.total_vector_count > 0
        except Exception:
            return False
    
    def clear_vectorstore(self):
        """
        Clear all vectors from the index
        """
        self.index.delete(delete_all=True)
        print("Cleared all vectors from Pinecone index")

def setup_knowledge_base(scraped_articles_path: str, force_rebuild: bool = False):
    """
    Set up the knowledge base from scraped articles using Pinecone
    """
    vectorstore_manager = VectorStoreManager()
    
    # Check if we need to rebuild the vector store
    if force_rebuild or not vectorstore_manager.vectorstore_exists():
        print("Building knowledge base with Pinecone...")
        
        if force_rebuild and vectorstore_manager.vectorstore_exists():
            print("Clearing existing vectors...")
            vectorstore_manager.clear_vectorstore()
            time.sleep(5)  # Wait for deletion to complete
        
        # Load documents
        loader = DocumentLoader(scraped_articles_path)
        documents = loader.load_documents()
        
        if not documents:
            raise ValueError("No documents found to load")
        
        # Split documents into chunks
        chunks = loader.split_documents(documents)
        
        # Create vector store
        vectorstore = vectorstore_manager.create_vectorstore(chunks)
        print("Knowledge base built successfully with Pinecone!")
    else:
        print("Loading existing Pinecone knowledge base...")
        vectorstore = vectorstore_manager.load_vectorstore()
        print("Pinecone knowledge base loaded successfully!")
    
    return vectorstore

if __name__ == "__main__":
    # Test the document loading
    scraped_path = "../extractContent/scraped_articles_selenium"
    
    if os.path.exists(scraped_path):
        vectorstore = setup_knowledge_base(scraped_path, force_rebuild=True)
        print(f"Pinecone vector store created successfully!")
        
        # Test search
        test_results = vectorstore.similarity_search("ice cream innovation", k=2)
        print(f"Test search returned {len(test_results)} results")
    else:
        print(f"Scraped articles path not found: {scraped_path}")
