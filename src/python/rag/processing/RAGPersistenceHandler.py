from pathlib import Path
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Optional
import chromadb
from rag.document.SingletonRetriever import SingletonRetriever
from util.PropertyManager import PropertyManager

class RAGPersistenceHandler:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        # ChromaDBクライアントの初期化
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.propetymanager = PropertyManager()
        
    def save_rag_system(self, retriever_instance: SingletonRetriever) -> None:
        """Save the RAG system to disk"""
        # ChromaDBに永続化
        db = Chroma(
            client=self.client,
            embedding_function=retriever_instance.embeddings,
        )
        
        # documentsを直接参照
        if not hasattr(retriever_instance, 'documents') or not retriever_instance.documents:
            print("No documents to save")
            return
            
        batch_size = 5000
        total_docs = len(retriever_instance.documents)

        for i in range(0, total_docs, batch_size):
            batch = retriever_instance.documents[i:i + batch_size]
            print(f"Saving batch {i//batch_size + 1}: documents {i} to {min(i + batch_size, total_docs)}")
            db.add_documents(batch)
           
    
    def load_rag_system(self, embedding_model_name: str) -> Optional[SingletonRetriever]:
        """Load the RAG system from disk"""
        if not Path(self.persist_directory).exists():
            print("No saved RAG system found")
            return None
            
        # 埋め込みモデルの初期化
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        
        # 保存されたChromaDBを読み込む
        db = Chroma(
            client=self.client,
            embedding_function=embeddings,
        )
        
        # SingletonRetrieverのインスタンスを作成
        retriever = SingletonRetriever.__new__(SingletonRetriever)
        retriever._initialized = True
        retriever.embeddings = embeddings
        
        # retrieverの設定
        retriever.set_retriever(db.as_retriever())
        return retriever
    
    def add_documents(self, documents: list) -> None:
        """Add new documents to the existing Chroma database"""
        embeddings = HuggingFaceEmbeddings(model_name=self.propetymanager.embedding_model_name)
        db = Chroma(
            client=self.client,
            embedding_function=embeddings,
        )
        
        # バッチサイズに分けて追加
        batch_size = 1000
        total_docs = len(documents)
        
        print(f"Adding {total_docs} documents to ChromaDB")
        
        #chromadb.PersistentClient(path=persist_directory)で、ローカルファイルから読み込んだ変数をバインドしたdbオブジェクトにaddしているため、save_rag_systemは不要
        for i in range(0, total_docs, batch_size):
            end_idx = min(i + batch_size, total_docs)
            batch = documents[i:end_idx]
            print(f"Processing documents {i+1} to {end_idx} of {total_docs}")
            db.add_documents(batch)
        
