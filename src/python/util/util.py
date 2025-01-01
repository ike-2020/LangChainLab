from datetime import datetime
import pyperclip
import configparser
from typing import Iterator
import re
import os


#propertyから各種値を取得する
class PropertyManager:
    def __init__(self):
        self.config_file_path = os.getenv('PYTHON_CONFIG_FILE')

    @property
    def database_info(self):
        database_info = self._get_property("Paths", "database_info")
        if database_info:
            return database_info
        return ''

    def _get_property(self, section, option):
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file_path, encoding='utf-8')
            return config.get(section, option)
        except configparser.Error as e:
            print(f"Error reading config file: {e}")
            return None

