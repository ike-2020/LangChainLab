#from langchain_community.document_loaders import DataFrameLoader
from langchain_community.document_loaders import SQLDatabaseLoader        
#import pandas as pd
from sqlalchemy import text
from langchain.schema import Document
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
        
    def load_documents(self):
        engine = self.db.get_engine()
        
        # SQLクエリを文字列として定義
        query_str = f"""
        SELECT h.article_date, h.edition_no, h.article_edition,
            h.article_title, h.article_subtitle, c.article
        FROM {self.schema_name}.article_header h
        JOIN {self.schema_name}.article_contents c
        ON h.article_id = c.article_id
        ORDER BY h.article_date,
                 CASE 
                    WHEN h.article_edition = 'morning' THEN 1
                    WHEN h.article_edition = 'evening' THEN 2
                 END, 
                 h.edition_no        
        """

        with engine.connect() as connection:
            result = connection.execute(text(query_str))
            
            documents = []
            for row in result:
                metadata = {
                    "article_date": str(row[0]),
                    "edition_no": str(row[1]),
                    "article_edition": row[2],
                    "article_title": row[3],
                    "article_subtitle": row[4]
                }
                
                doc = Document(
                    page_content=row[5],  # article content
                    metadata=metadata
                )
                documents.append(doc)
                
        return documents
  
