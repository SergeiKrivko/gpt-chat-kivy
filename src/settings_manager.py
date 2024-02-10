import json
import os.path

from src import config
from src.commands import read_json, write_file


class SettingsManager:
    def __init__(self, path):
        super().__init__()
        self._dir = path
        self._path = os.path.join(path, 'settings.json')
        self.temp_dir = os.path.join(path, 'temp')
        self._settings: dict = read_json(self._path)

    @property
    def user_data_path(self):
        if not (uid := self.get('user_id')):
            return f"{self._dir}/default_user"
        return f"{self._dir}/users/{uid}"

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def remove(self, key):
        self._settings.pop(key)
        self.save()

    def set(self, key, value):
        self._settings[key] = value
        self.save()

    def save(self):
        write_file(self._path, json.dumps(self._settings, indent=2))

