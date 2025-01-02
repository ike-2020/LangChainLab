from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text,func
from sqlalchemy.dialects.postgresql import TSVECTOR
from db.base.ArticleTableBase import ArticleTableBase
from util.PropertyManager import PropertyManager


class ArticleContentsTable(ArticleTableBase):

    def createTableObj(self):
        if self.table is None:
            self.table = self.getTable()
        self.util = PropertyManager()
        return self.table

    def getTable(self) -> Table:
        if hasattr(self, '_table_instance'):
            return self._table_instance

        self._table_instance = Table('article_contents', self._metadata,
                        Column('article_id', Integer, primary_key=True),
                        Column('article', Text),
                        Column('article_summry1', Text),
                        Column('article_summry2', Text),
                        schema=self._schemaname
                )
        return self._table_instance
    
    def insert(self,element):
        return self.table.insert().values(
            article_id=element._articleid,
            article=self._replaceImagePath(element._article),
            article_summry1=element._summry1,
            article_summry2=element._summry2
            )
    
    def _replaceImagePath(self,original_path: str) -> str:
        # 置換元のパス
        search_string = self.util.data_output_path + self.util.img_output_path
        # 置換後のパス
        replace_string = self.util.img_file_description
        # 文字列を置換
        return original_path.replace(search_string, replace_string)    

    