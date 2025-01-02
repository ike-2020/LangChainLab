from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever

class SingletonRetriever:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonRetriever, cls).__new__(cls)
            
        return cls._instance

    def __init__(self, embeddings, article_loader, breakpoint_threshold_type="percentile"):
        if not self._initialized:
            if not isinstance(embeddings, HuggingFaceEmbeddings):
                embeddings = HuggingFaceEmbeddings(model_name=embeddings)

            self.embeddings = embeddings
            self.article_loader = article_loader
            self.documents = self.article_loader.load_documents()
            
            text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type=breakpoint_threshold_type)
            self.chunked_documents = text_splitter.create_documents([doc.page_content for doc in self.documents])
            self.setup_retriever()
            self._initialized = True

    def setup_retriever(self):
        db = Chroma.from_documents(self.chunked_documents, self.embeddings)
        self.retriever: BaseRetriever = db.as_retriever()

    def get_retriever(self) -> BaseRetriever:
        return self.retriever
    
    def set_retriever(self,object) -> BaseRetriever:
        self.retriever = object

