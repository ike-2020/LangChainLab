from langchain_community.document_loaders import DataFrameLoader
import pandas as pd
from db.table.ArticleHeaderTable import ArticleHeaderTable
from db.table.ArticleContentsTable import ArticleContentsTable
from db.driver.SingletonDatabase import SingletonDatabase


class ArticleRAGLoader:
    def __init__(self, schema_name: str):
        self.schema_name = schema_name
        self.header_table = ArticleHeaderTable(schema_name)
        self.contents_table = ArticleContentsTable(schema_name)
        self.db = SingletonDatabase()
        
    def setup_tables(self):
        """Initialize both tables"""
        #self.header_table.createTableObj()
        #self.contents_table.createTableObj()
        return self
        
    def create_loader(self):
        engine = self.db.get_engine()
        
        # SQLクエリを文字列として定義
        query_str = f"""
        SELECT h.article_id, h.article_date, h.article_edition,
            h.article_title, h.article_subtitle, c.article
        FROM {self.schema_name}.article_header h
        JOIN {self.schema_name}.article_contents c
        ON h.article_id = c.article_id
        """

        df = pd.read_sql_query(query_str, engine)
        
        
        # DataFrameLoaderを使用してドキュメントを作成し、直接結果を返す
        loader = DataFrameLoader(
            df,
            page_content_column="article"
        )
        
        return loader
    
    def load_documents(self):
        """Load documents using the configured loader"""
        loader = self.create_loader()
        return loader.load()