from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Optional

class RAGPersistenceHandler:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
    def save_rag_system(self, retriever_instance: SingletonRetriever) -> None:
        """Save the RAG system to disk"""
        # ChromaDBに永続化
        db = Chroma(
            embedding_function=retriever_instance.embeddings,
            persist_directory=self.persist_directory
        )
        
        # ドキュメントを保存
        db.add_documents(retriever_instance.chunked_documents)
        db.persist()
        
        print(f"RAG system saved to {self.persist_directory}")
    
    def load_rag_system(self, embedding_model_name: str) -> Optional[SingletonRetriever]:
        """Load the RAG system from disk"""
        if not Path(self.persist_directory).exists():
            print("No saved RAG system found")
            return None
            
        # 埋め込みモデルの初期化
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        
        # 保存されたChromaDBを読み込む
        db = Chroma(
            embedding_function=embeddings,
            persist_directory=self.persist_directory
        )
        
        # SingletonRetrieverのインスタンスを作成
        retriever = SingletonRetriever.__new__(SingletonRetriever)
        retriever._initialized = True
        retriever.embeddings = embeddings
        retriever.retriever = db.as_retriever()
        
        print("RAG system loaded successfully")
        return retriever