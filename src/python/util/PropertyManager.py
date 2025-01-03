from datetime import datetime
import pyperclip
import configparser
from typing import Iterator
import re
import os


#propertyから各種値を取得する
class PropertyManager:
    def __init__(self):
        self.config_file_path = os.getenv('PYTHON_CONFIG_FILE_LANG_CHAIN')

    @property
    def database_info(self):
        database_info = self._get_property("Paths", "database_info")
        if database_info:
            return database_info
        return ''

    @property
    def persist_dir(self):
        persist_dir = self._get_property("Paths", "persist_dir")
        if persist_dir:
            return persist_dir
        return ''

    @property
    def select_keyword(self):
        select_keyword = self._get_property("Paths", "select_keyword")
        if select_keyword:
            return select_keyword
        return ''

    @property
    def embedding_model_name(self):
        embedding_model_name = self._get_property("Paths", "embedding_model_name")
        if embedding_model_name:
            return embedding_model_name
        return ''   
    

    def _get_property(self, section, option):
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file_path, encoding='utf-8')
            return config.get(section, option)
        except configparser.Error as e:
            print(f"Error reading config file: {e}")
            return None

