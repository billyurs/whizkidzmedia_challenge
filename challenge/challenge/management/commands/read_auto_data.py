__author__ = 'madhu'
from django.core.management.base import BaseCommand
import time
from challenge.views import FilmSearchAPI
from django.core.cache import caches
from challenge.mongo_wrapper import MongoWrapper
rediscon = caches['localcache']
from datetime import datetime
import copy
from challenge.views import current_time_to_string

def daily_read_film_data():
    """
    This function runs on daily basis and grab and reads all the data from remote server
    :return:
    """
    mongo_obj= MongoWrapper()
    film_mongo_connect = mongo_obj.get_connection()
    current_time_text = current_time_to_string(time.time())
    filmobj = FilmSearchAPI()
    film_json = filmobj.get_whole_film_data()
    # Writes the whole json data
    rediscon.set(current_time_text, film_json)
    # Writing it into redis cache
    for filmobj in film_json:
        locations = []
        title_name = filmobj.get('title', '')
        if rediscon.get(title_name):
            place_name = rediscon.get(title_name).get('locations')
            location = filmobj.get('locations')
            if location:
                if isinstance(place_name, unicode):
                    locations.append(location)
                    place_name = copy.copy(locations)
                else:
                    if not place_name:
                        place_name = []
                    place_name.append(location)
                filmobj['locations'] = copy.copy(place_name)
            rediscon.set(title_name, copy.copy(filmobj))
            film_mongo_connect.update({"title": title_name},{ "$set":{'locations': filmobj.get('locations', [])}})
        else:
            rediscon.set(title_name, copy.copy(filmobj))
            film_mongo_connect.insert_one(copy.copy(filmobj))

class Command(BaseCommand):
    def handle(self, *args, **options):
        daily_read_film_data()
