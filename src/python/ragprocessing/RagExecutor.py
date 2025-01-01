import sys
sys.path.append('src/python')
from db.base.ArticleRAGLoader import ArticleRAGLoader
from documentprocessing.SingletonRetriever import SingletonRetriever


class RagExecutor:
    if __name__ == "__main__":
        SingletonRetriever("sentence-transformers/all-MiniLM-L6-v2", 
                            ArticleRAGLoader("articleschema").setup_tables()).get_retriever()