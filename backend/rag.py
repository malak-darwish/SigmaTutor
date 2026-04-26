import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

LECTURES_PATH = Path(__file__).parent / "data" / "knowledge"
CHROMA_PATH = Path(__file__).parent / "data" / "chroma_db"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_pdfs():
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
    print("Loading PDFs...")
    documents = load_pdfs()
    if not documents:
        print("No documents found!")
        return None
    print(f"Splitting {len(documents)} pages into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
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
    if CHROMA_PATH.exists():
        print("Loading existing vector store...")
        return Chroma(
            persist_directory=str(CHROMA_PATH),
            embedding_function=embeddings
        )
    else:
        print("No existing vector store found. Creating new one...")
        return create_vector_store()

def search_documents(query: str, k: int = 1):
    try:
        vector_store = get_vector_store()
        if vector_store is None:
            return []
        return vector_store.similarity_search(query, k=k)
    except Exception as e:
        print(f"Search error: {e}")
        return []

def format_search_results(results):
    if not results:
        return "No relevant content found in lectures."
    formatted = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', 'Unknown')
        # Truncate to 500 chars max
        content = doc.page_content[:500]
        formatted.append(f"[Source {i}: {Path(source).name}, Page {page}]\n{content}")
    return "\n\n".join(formatted)

def add_document(file_path: str):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        vector_store = get_vector_store()
        vector_store.add_documents(chunks)
        print(f"✅ Added {file_path} to vector store")
        return True
    except Exception as e:
        print(f"❌ Error adding document: {e}")
        return False

def get_stats():
    try:
        vector_store = get_vector_store()
        collection = vector_store._collection
        count = collection.count()
        return {"total_chunks": count, "status": "ready"}
    except Exception as e:
        return {"total_chunks": 0, "status": "error", "error": str(e)}

if __name__ == "__main__":
    print("Building RAG vector store from lectures...")
    create_vector_store()
    print("Done! Vector store is ready.")