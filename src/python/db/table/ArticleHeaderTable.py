from sqlalchemy import MetaData, Table, Column, Integer, String, Date
from db.base.ArticleTableBase import ArticleTableBase
from datetime import datetime

class ArticleHeaderTable(ArticleTableBase):

    def createTableObj(self):
        if self.table is None:
            self.table = self.getTable()
        return self.table

    def getTable(self) -> Table:
        if hasattr(self, '_table_instance'):
            return self._table_instance
        
        self._table_instance = Table('article_header', self._metadata,
                   Column('article_id', Integer, primary_key=True),
                   Column('article_date', Date),
                   Column('article_edition', String(20)),
                   Column('edition_no', Integer),
                   Column('article_url', String(100)),
                   Column('article_title', String(100)),
                   Column('article_subtitle', String(100)),
                   Column('reg_date', Date),
                   schema=self._schemaname
                )
        return self._table_instance
    
    def insert(self,element):
        title=element._title.split('(Separated)')
        return self.table.insert().values(
            article_date=element._date,
            article_edition=element._edition,
            edition_no=element._no,
            article_title=title[0],
            article_subtitle=title[1] if len(title)==2 else '',
            article_url=element._url,
            reg_date=datetime.now()    
            )

    