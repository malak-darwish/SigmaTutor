import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

# Paths
LECTURES_PATH = Path(__file__).parent / "data" / "knowledge"
CHROMA_PATH = Path(__file__).parent / "data" / "chroma_db"

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

def load_pdfs():
    """Load all PDFs from the knowledge folder"""
    documents = []
    pdf_files = list(LECTURES_PATH.glob("**/*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            documents.extend(docs)
            print(f"✅ Loaded: {pdf_path.name}")
        except Exception as e:
            print(f"❌ Error loading {pdf_path.name}: {e}")
    
    return documents

def create_vector_store():
    """Create ChromaDB vector store from PDFs"""
    print("Loading PDFs...")
    documents = load_pdfs()
    
    if not documents:
        print("No documents found!")
        return None
    
    print(f"Splitting {len(documents)} pages into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    
    print("Creating vector store...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_PATH)
    )
    
    print("✅ Vector store created successfully!")
    return vector_store

def get_vector_store():
    """Load existing vector store or create new one"""
    if CHROMA_PATH.exists():
        print("Loading existing vector store...")
        vector_store = Chroma(
            persist_directory=str(CHROMA_PATH),
            embedding_function=embeddings
        )
        return vector_store
    else:
        print("No existing vector store found. Creating new one...")
        return create_vector_store()

def search_documents(query: str, k: int = 4):
    """Search the vector store for relevant documents"""
    try:
        vector_store = get_vector_store()
        if vector_store is None:
            return []
        
        results = vector_store.similarity_search(query, k=k)
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

def format_search_results(results):
    """Format search results into a string"""
    if not results:
        return "No relevant content found in lectures."
    
    formatted = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', 'Unknown')
        formatted.append(f"[Source {i}: {Path(source).name}, Page {page}]\n{doc.page_content}")
    
    return "\n\n".join(formatted)

# Run this to build the vector store
if __name__ == "__main__":
    print("Building RAG vector store from lectures...")
    create_vector_store()
    print("Done! Vector store is ready.")