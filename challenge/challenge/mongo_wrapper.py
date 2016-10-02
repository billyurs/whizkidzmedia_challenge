__author__ = 'madhu'
from django.conf import settings
from pymongo import MongoClient
class MongoWrapper:
    def __init__(self):
        pass
    def get_connection(self):
        client = MongoClient(settings.MONGO_DB_CONFIG.get('film_database_string', ''))
        mongo_collection = client.film_db
        film_mongo_connect = mongo_collection.film
        return film_mongo_connect