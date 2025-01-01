from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from util.util import PropertyManager

class SingletonDatabase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.util = PropertyManager()
            cls._instance.engine = create_engine(cls._instance.util.database_info)
            Session = sessionmaker(bind=cls._instance.engine)
            cls._instance.session = Session()
        return cls._instance


    def get_session(self):
        return self._instance.session
    
    def get_engine(self):
        return self._instance.engine
    