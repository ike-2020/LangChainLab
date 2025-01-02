import sys
import argparse
from pathlib import Path
sys.path.append('src/python')
from util.PropertyManager import PropertyManager
from rag.processing.RAGPersistenceHandler import RAGPersistenceHandler

from db.base.ArticleRAGLoader import ArticleRAGLoader
from rag.document.SingletonRetriever import SingletonRetriever


class RagExecutor:
    manager = PropertyManager()
    @staticmethod
    def initialize_rag(persist_dir: str = "chroma_db"):
        # RAGシステムを初期化して保存
        retriever = SingletonRetriever(
            "sentence-transformers/all-MiniLM-L6-v2",
            ArticleRAGLoader("articleschema").setup_tables()
        )
        
        persistence_handler = RAGPersistenceHandler(persist_dir)
        persistence_handler.save_rag_system(retriever)
        return retriever
    
    @staticmethod
    def load_saved_rag(persist_dir: str = manager.persist_dir):
        # 保存されたRAGシステムを読み込む
        persistence_handler = RAGPersistenceHandler(persist_dir)
        return persistence_handler.load_rag_system("sentence-transformers/all-MiniLM-L6-v2")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='RAG System Management')
    parser.add_argument('--mode', choices=['initialize', 'load'], required=True,
                       help='initialize: Create and save new RAG system, load: Load existing RAG system')
    parser.add_argument('--persist-dir', default=PropertyManager().persist_dir,
                       help='Directory for persistent storage')
    
    args = parser.parse_args()
    
    if args.mode == 'initialize':
        retriever = RagExecutor.initialize_rag(args.persist_dir)
        print("RAG system initialized and saved")
    else:
        retriever = RagExecutor.load_saved_rag(args.persist_dir)
        if retriever:
            print("RAG system loaded successfully")
        else:
            print("Failed to load RAG system")