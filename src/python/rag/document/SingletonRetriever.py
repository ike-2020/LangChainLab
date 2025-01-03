from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever

from rag.document.TextSplitExecutor import TextSplitExecutor

class SingletonRetriever:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonRetriever, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, embeddings, article_loader):
        if not self._initialized:
            if not isinstance(embeddings, HuggingFaceEmbeddings):
                embeddings = HuggingFaceEmbeddings(model_name=embeddings)

            self.embeddings = embeddings
            self.article_loader = article_loader
            self.documents = self.article_loader.load_documents()
            

            self.text_splitter = TextSplitExecutor()
            self._setup_retriever()
            self._initialized = True

    def _setup_retriever(self):
        try:
            BATCH_SIZE = 1000  # バッチサイズの設定
            analyzed_documents = []
            total_docs = len(self.documents)
            
            print(f"Starting document processing... Total documents: {total_docs}")
            
            # バッチ処理の実装
            for i in range(0, total_docs, BATCH_SIZE):
                batch_end = min(i + BATCH_SIZE, total_docs)
                print(f"Processing batch {i//BATCH_SIZE + 1}: documents {i} to {batch_end}")
                
                batch_documents = []
                for doc_idx in range(i, batch_end):
                    try:
                        doc = self.documents[doc_idx]
                        semantic_results = self.text_splitter.split_article(
                            doc.page_content,
                            doc.metadata
                        )
                        
                        for chunk in semantic_results:
                            semantic_analysis = chunk['semantic_analysis']
                            flattened_metadata = {
                                **doc.metadata,  # 元のメタデータ
                                'contains_economic_terms': str(chunk['contains_economic_terms']),
                                'has_new_terms': str(semantic_analysis['new_terms']),
                                'has_first_terms': str(semantic_analysis['first_terms']),
                                'has_most_terms': str(semantic_analysis['most_terms']),
                                'has_hatsu_terms': str(semantic_analysis['hatsu_terms']),
                                'has_ten_terms': str(semantic_analysis['ten_terms']),
                                'has_datsu_terms': str(semantic_analysis['datsu_terms']),
                                'has_kai_terms': str(semantic_analysis['kai_terms'])
                            }
                            
                            new_doc = Document(
                                page_content=chunk['text'],
                                metadata=flattened_metadata
                            )
                            batch_documents.append(new_doc)
                            
                    except Exception as e:
                        print(f"Error processing document {doc_idx}: {str(e)}")
                        continue  # 個別のドキュメントの失敗を許容
                
                # バッチごとにChromaに追加
                if batch_documents:
                    print(f"Adding batch of {len(batch_documents)} documents to Chroma")
                    if not analyzed_documents:
                        # 最初のバッチ：DBを作成
                        db = Chroma.from_documents(batch_documents, self.embeddings)
                    else:
                        # 後続のバッチ：既存のDBに追加
                        db.add_documents(batch_documents)
                    
                    analyzed_documents.extend(batch_documents)
                    print(f"Total processed documents: {len(analyzed_documents)}")
                
                # メモリ解放のためのガベージコレクション
                import gc
                gc.collect()
                
            if not analyzed_documents:
                raise RuntimeError("No documents were successfully processed")
                
            print("Setting up retriever...")
            self.retriever: BaseRetriever = db.as_retriever()
            print("Retriever setup completed")
            
        except Exception as e:
            print(f"Fatal error in _setup_retriever: {str(e)}")
            raise

    def update_documents(self, article_loader, persist_directory: str, start_date=None, end_date=None):
        """
        既存のChromaDBに新しいドキュメントを追加する
        
        Args:
            article_loader: 新しいドキュメントを読み込むためのローダー
            persist_directory: ChromaDBの保存ディレクトリ
            start_date (datetime, optional): 開始日
            end_date (datetime, optional): 終了日
        """
        try:
            # 日付範囲を指定してドキュメントを読み込む
            self.documents = article_loader.load_documents(
                start_date=start_date,
                end_date=end_date
            ) if (start_date or end_date) else article_loader.load_documents()
            
            # 既存のDBに新しいドキュメントを追加
            self._setup_retriever(
                persist_directory=persist_directory,
                add_to_existing=True
            )
            
        except Exception as e:
            print(f"Error updating documents: {str(e)}")
            raise

    def get_retriever(self) -> BaseRetriever:
        return self.retriever
    
    def set_retriever(self,object) -> BaseRetriever:
        self.retriever = object

