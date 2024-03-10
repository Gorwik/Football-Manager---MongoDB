import os
from pymongo import MongoClient


class MongoDB:
    _login = os.getenv("MDB_login")
    _password = os.getenv("MDB_pass")
    _db_name = os.getenv("MDB_db_name")
    _connection_string = f"mongodb+srv://{_login}:{_password}@{_db_name}.lilxs5r.mongodb.net/?retryWrites=true&w=majority&authSource=admin"

    def __init__(
        self,
    ):
        self._client = MongoClient(self._connection_string)
        self._football_db = self._client["football"]
        self._players_collection = self._football_db["players"]
        self._leagues_collection = self._football_db["leagues"]
        self._club_teams_collection = self._football_db["club_teams"]

    @property
    def football_db(self):
        return self._football_db

    @property
    def players(self):
        return self._players_collection

    @property
    def leagues(self):
        return self._leagues_collection

    @property
    def clubs(self):
        return self._club_teams_collection
