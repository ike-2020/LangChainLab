import sys
import argparse
from datetime import datetime
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
            PropertyManager().embedding_model_name,
            ArticleRAGLoader("articleschema").setup_tables()
        )
        
        persistence_handler = RAGPersistenceHandler(persist_dir)
        persistence_handler.save_rag_system(retriever)
        return retriever
    
    @staticmethod
    def load_saved_rag(persist_dir: str = manager.persist_dir):
        # 保存されたRAGシステムを読み込む
        persistence_handler = RAGPersistenceHandler(persist_dir)
        retriever = persistence_handler.load_rag_system(
            embedding_model_name=PropertyManager().embedding_model_name
        )
        
        if retriever is None:
            raise ValueError("No saved RAG system found")
            
        return retriever
    
    @staticmethod
    def update_rag(persist_dir: str = manager.persist_dir, from_date: str = None, to_date: str = None):
        """既存のRAGシステムに新しいデータを追加する"""
        try:
            # 日付文字列をdatetimeオブジェクトに変換
            start_date = None
            end_date = None
            
            if from_date:
                start_date = datetime.strptime(from_date, '%Y%m%d')
                print(f"From date: {start_date.strftime('%Y-%m-%d')}")
            
            if to_date:
                end_date = datetime.strptime(to_date, '%Y%m%d')
                print(f"To date: {end_date.strftime('%Y-%m-%d')}")
            
            # 新しいデータを読み込む
            article_loader = ArticleRAGLoader("articleschema").setup_tables()
            new_documents = article_loader.load_documents(
                start_date=start_date,
                end_date=end_date
            )

            # RAGPersistenceHandlerを使用して既存のデータベースに追加
            persistence_handler = RAGPersistenceHandler(persist_dir)
            persistence_handler.add_documents(new_documents)
            
        except ValueError as ve:
            print(f"Invalid date format or missing RAG system: {str(ve)}")
            raise
        except Exception as e:
            print(f"Error updating RAG system: {str(e)}")
            raise


    @staticmethod
    def _validate_date_format(date_str: str) -> bool:
        """日付文字列がYYYYMMDD形式かを検証する"""
        if not date_str:
            return True
        try:
            datetime.strptime(date_str, '%Y%m%d')
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RAG System Management')
    parser.add_argument('--mode', choices=['initialize', 'load', 'update'], required=True,
                       help='initialize: Create new RAG system, load: Load existing RAG system, update: Add new data to existing system')
    parser.add_argument('--persist-dir', default=PropertyManager().persist_dir,
                       help='Directory for persistent storage')
    parser.add_argument('--from-date', 
                       help='Start date for update (format: YYYYMMDD)')
    parser.add_argument('--to-date',
                       help='End date for update (format: YYYYMMDD)')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'initialize':
            retriever = RagExecutor.initialize_rag(args.persist_dir)
            print("RAG system initialized and saved")
        elif args.mode == 'update':
            # 日付形式の検証
            if not RagExecutor._validate_date_format(args.from_date):
                raise ValueError("Invalid from-date format. Use YYYYMMDD")
            if not RagExecutor._validate_date_format(args.to_date):
                raise ValueError("Invalid to-date format. Use YYYYMMDD")
                
            retriever = RagExecutor.update_rag(
                args.persist_dir,
                args.from_date,
                args.to_date
            )
            print("RAG system updated successfully")
        else:
            retriever = RagExecutor.load_saved_rag(args.persist_dir)
            if retriever:
                print("RAG system loaded successfully")
            else:
                print("Failed to load RAG system")
    except Exception as e:
        print(f"Operation failed: {str(e)}")
        sys.exit(1)