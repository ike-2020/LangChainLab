from db.driver.SingletonDatabase import SingletonDatabase
from sqlalchemy import create_engine, MetaData, Table
from typing import List, Dict, Any

class ArticleTableBase:

    def __init__(self,schemaname):
        db=SingletonDatabase()
        self.session=db.get_session()
        self.engine=db.get_engine()
        self.table=None
        self._metadata=MetaData()
        self._schemaname=schemaname

    def createTableObj(self):
        pass  

    def insert(self,element):
        pass

    def getSession(self):
        return self.session
    
    def getEngine(self):
        return self.engine
    
    def getMetadata(self):
        return self._metadata
    
    def getSchemaname(self):
        pass
    
    def load_all_articles(self) -> List[Dict[str, Any]]:

        if self.table is None:
            self.createTableObj()
        
        query = select(self.table)
        result = self.session.execute(query)
        
        return [dict(row._mapping) for row in result]
